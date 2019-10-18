#!/usr/bin/env python
# coding: utf8

'''
    Copyright (C) 2019  Henning Pingel

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''

import ast
import re
import bitstring
import binascii
import hashlib
from access1581.arduinointerface import *
from access1581.diskformats import *

class IBMDoubleDensityFloppyDiskImager:
    '''
    loops over all 80 tracks using both heads
    and collects all the sector data of all tracks
    to store it into an image file
    '''
    def __init__( self, diskFormat, imagename, retries, serialDevice, storeBitstream = False, stopOnError=False):
        print ("pyAccess1581 - Copyright (C) 2019  Henning Pingel")
        print ("Reusing: Arduino Amiga Floppy Disk Reader/Writer Firmware - Copyright (C) 2019  Robert Smith")
        print ("Selected disk format is " + diskFormat.name + ", we expect " + str(diskFormat.expectedSectorsPerTrack) + " sectors per track")
        print ("Target image file is: " + imagename)
        print ("Serial device is: " + serialDevice)

        image = b''
        trackData = {}
        rawTracks = {}
        trackLength = diskFormat.expectedSectorsPerTrack * diskFormat.sectorSize
        if serialDevice == "simulated":
            with open('raw_debug_image_d81.py', 'r') as f:
                rawTrackData = ast.literal_eval(f.read())
            self.arduino = ArduinoSimulator(diskFormat, rawTrackData)
        else:
            self.arduino = ArduinoFloppyControlInterface(serialDevice, diskFormat)
        self.arduino.openSerialConnection()

        vldtr = SingleTrackSectorListValidator( retries, diskFormat, self.arduino, storeBitstream, stopOnError )
        for trackno in diskFormat.trackRange:
            trackData[ trackno ] = {}
            rawTracks[ trackno ] = {}
            for headno in diskFormat.headRange:
                trackDataTmp = vldtr.processTrack( trackno, headno )
                if not len(trackDataTmp) == trackLength:
                    print ("ERROR track should have " + str(trackLength) + " bytes but has " + str(len(trackData)))
                trackData[ trackno ][ headno ] = trackDataTmp
                image += trackData[ trackno ][ headno ]
                if storeBitstream is True:
                    rawTracks[trackno][headno] = vldtr.getDecompressedBitstream()
        print ("Writing image to file " + imagename)
        with open(imagename, 'wb') as f:
            f.write( image)
        result = hashlib.md5(image)
        print("MD5   : " + result.hexdigest())
        result = hashlib.sha1(image)
        print("SHA1  : " + result.hexdigest())
        result = hashlib.sha256(image)
        print("SHA256: " + result.hexdigest())

        if storeBitstream is True:
            with open('raw_debug_image_d81.py', "w") as f:
                f.write(repr(rawTracks))
        vldtr.printSerialStats()

class SingleTrackSectorListValidator:
    '''
    asks track reader to read a specific track from disk (processTrack). gets
    structured data of all found sectors of one track. validates crc values and
    manages optional read retries.
    '''
    def __init__(self, retries, diskFormat, arduinoInterface, storeBitstream = False, stopOnError = False):
        self.maxRetries = retries
        self.diskFormat = diskFormat
        self.minSectorNumber = 1
        self.validSectorData = {}
        self.storeBitstream = storeBitstream
        self.decompressedBitstream = ""
        self.arduino = arduinoInterface
        self.trackParser = SingleIBMTrackSectorParser(self.diskFormat, self.arduino)
        self.stopOnError = stopOnError
        self.printSectorDebugInfo = False

    def printSerialStats(self):
        self.trackParser.printSerialStats()

    def processTrack(self, trackno, headno):
        trackData = b''
        self.validSectorData = {}
        self.retries = self.maxRetries
        while self.retries > 0:
            if self.retries < self.maxRetries:
                print ("  Repeat track read - attempt " + str( self.maxRetries - self.retries +1 ) + " of " + str(self.maxRetries) )
            self.addValidSectors( self.trackParser.detectSectors(trackno, headno), trackno, headno, (self.retries == 1))
            #also make raw stream accessible for debug or other purposes
            self.decompressedBitstream = self.trackParser.getDecompressedBitstream()
            vsc = len(self.validSectorData)
            print (f"Reading track: {trackno:2d}, head: {headno}. Number of valid sectors found: {vsc}/{self.diskFormat.expectedSectorsPerTrack}")
            if vsc == self.diskFormat.expectedSectorsPerTrack:
                self.retries = 0
            else:
                self.retries = self.retries -1
        if len(self.validSectorData) == self.diskFormat.expectedSectorsPerTrack:
            for sectorno in sorted(self.validSectorData):
                if not len(self.validSectorData[sectorno]) == self.diskFormat.sectorSize * 2:
                    print("  Invalid sector data length." + str(len(self.validSectorData[sectorno])) )
                #print ("Adding sector no " + str(sectorno))
                trackData += binascii.unhexlify(self.validSectorData[sectorno])
        elif len(self.validSectorData) == 0:
            trackData = bytes(chr(0) * self.diskFormat.sectorSize * self.diskFormat.expectedSectorsPerTrack ,'utf-8')
            #print ("bytes: " + str(len(trackData)))
            print("  Notice: Filled up empty track with zeros.");
        else:
            print("  Not enough sectors found.");
        return trackData

    def getDecompressedBitstream(self):
        return self.decompressedBitstream

    def getCRC(self, data):
        '''
        to calculate crc, we can either use binascii.crc_hqx(data, value) or crcmod
        where we have to import crcmod.predefined and install another module via pip

        the following code works fine with crcmod:
        xmodem_crc_func = crcmod.predefined.mkCrcFun('crc-ccitt-false')
        return hex(xmodem_crc_func( binascii.unhexlify(data)))[2:].zfill(4)
        '''
        return hex(binascii.crc_hqx(binascii.unhexlify(data), 0xffff))[2:].zfill(4)

    def isValidCRC(self, sectorprops):
        crc_data_check   = sectorprops["crc_data"] == self.getCRC( sectorprops["datameta"] + sectorprops["data"] )
        crc_header_check = sectorprops["crc_header"] == self.getCRC( sectorprops["headermeta"])
        return (crc_header_check and crc_data_check)

    def handleError(self, msg, sectorprops):
        if self.stopOnError is True:
            crcCheck = self.isValidCRC(sectorprops)
            self.printSectorDebugOutput(sectorprops, crcCheck)
            raise Exception( "  Error: " + msg )
        else:
            print ("  Error: " + msg)
            self.printSectorDebugInfo = True

    def addValidSectors(self, sectors, t, h, lastChance):
        self.printSectorDebugInfo = False
        printDebug = False
        for sectorprops in sectors:
            isSameTrack = True if sectorprops['trackno'] == t else False
            isSameHead  = True if sectorprops['sideno'] == h else False

            if isSameTrack is False:
                self.handleError( "Wrong track number: " + str(sectorprops["trackno"]), sectorprops )
            if isSameHead is False:
                self.handleError( "Wrong head/side number: "+ str(sectorprops["sideno"]) + " Please check that you chose the right disk format (swapsides?).",sectorprops )
            if int(sectorprops["sectorno"]) < self.minSectorNumber or \
                int(sectorprops["sectorno"]) > self.diskFormat.expectedSectorsPerTrack:
                self.handleError( "Sector number is out of expected bounds: "+ str(sectorprops["sectorno"]),sectorprops )

            crcCheck = self.isValidCRC(sectorprops)
            if not sectorprops["sectorno"] in self.validSectorData:
                if not sectorprops["sectorlength"] == 2:
                    self.handleError("Detected a non-512 byte sector length!",sectorprops)
                if crcCheck is False and lastChance is True:
                    print (f'  Invalid CRC for sector found, but adding sector data anyway: Head {h}, Track {t}, sector #{sectorprops["sectorno"]}')
                    self.printSectorDebugInfo = True
                if crcCheck is True or lastChance is True:
                    self.validSectorData[ sectorprops["sectorno"] ] = sectorprops["data"]
            self.printSectorDebugInfo = True

            if self.printSectorDebugInfo is True:
                self.printSectorDebugOutput(sectorprops, crcCheck)

    def printSectorDebugOutput(self, sectorprops, crcCheck):
        infostring =""
        for prop in sectorprops:
            if prop != "datameta" and prop != "data" and prop != "headermeta":
                infostring += prop + ":" + str(sectorprops[prop]) + ", "
        infostring += "CRC check "
        infostring += "FAILED" if crcCheck is False else "SUCCESSFUL"
        print ("  DEBUGINFO - Sector properties: "+ infostring)

class SingleIBMTrackSectorParser:
    '''
    reads the requested track from the disk parses the data into complete
    sectors. discards incomplete sectors and returns data structure with all
    complete sectors of the track without doing crc validation yet.
    '''
    def __init__(self, diskFormat, arduinoFloppyControlInterface):
        self.diskFormat = diskFormat
        self.arduino = arduinoFloppyControlInterface
        self.sectorDataBitSize = self.diskFormat.sectorSize * 16
        self.decompressedBitstream = ""
        self.sectorStartMarkerLength = len(self.diskFormat.sectorStartMarker)

    def detectSectors(self, trackno, headno):
        cnt = 0
        sectors = []
        if self.diskFormat.swapsides is False:
            headno = 1 if headno == 0 else 0
        self.decompressedBitstream = self.arduino.getDecompressedBitstream(trackno, headno)
        (sectorMarkers, dataMarkers) = self.getMarkers()
        for sectorStart in sectorMarkers:
            if len(dataMarkers) <= cnt:
                pass
            elif dataMarkers[cnt] <= sectorStart:
                print ("Datamarker is being ignored. " + str( dataMarkers[cnt] ) + " " + str(sectorStart))
            else:
                sectors.append(self.parseSingleSector(sectorStart, dataMarkers[cnt]))
            cnt += 1
        return sectors

    def getDecompressedBitstream(self):
        return self.decompressedBitstream

    def mfmDecode(self, stream):
        result = ""
        keep = False;
        for char in stream:
            if keep is True:
                result += char
            keep = not keep
        return result

    def convertBitstreamBytes( self, data, flagHexInt ):
        if data is "":
            return ""
        ba = bitstring.BitArray('0b'+data )
        return ba.hex if flagHexInt is True else ba.int

    def grabSectorChunkHex( self, start, length):
        return self.convertBitstreamBytes( self.mfmDecode( self.currentSectorBitstream[ start: start+length ]), True)

    def grabSectorChunkInt( self, start, length):
        sfrom = start*8
        sto = sfrom + length*8
        return self.convertBitstreamBytes( self.mfmDecode( self.currentSectorBitstream[ sfrom: sto ]), False)

    def getMarkers(self):
        sectorMarkers = []
        dataMarkers = []
        dataMarkersTmp = []
        rawSectors = re.split( self.diskFormat.sectorStartMarker, self.decompressedBitstream)
        del rawSectors[-1] #delete last entry
        previousBits = 0
        for rawSector in rawSectors:
            previousBits += len( rawSector ) + self.sectorStartMarkerLength
            sectorMarkers.append( previousBits )
        dataMarkerMatchesIterator = re.finditer( self.diskFormat.sectorDataStartMarker, self.decompressedBitstream)
        if len(sectorMarkers) > 0:
            for dataMarker in dataMarkerMatchesIterator:
                (startPosDataMarker, endPosDataMarker) = (dataMarker.span() )
                if endPosDataMarker >= sectorMarkers[0] + self.diskFormat.legalOffsetRangeLowerBorder:
                    dataMarkersTmp.append(endPosDataMarker)
                #else:
                #    print("Notice: Ignoring datamarker - is in front of first sector marker")
        cnt = 0
        for dataMarker in dataMarkersTmp:
            offset = dataMarker - sectorMarkers[cnt]
            if not offset in self.diskFormat.legalOffsetRange:
                print ("getMarkers / Unusual offset found: "+str(offset))
            #now we check if the sector's data might be cut off at the end
            #of the chunk of the track we have, the added 32 represents
            #the length of the CRC checksum of the sector data
            overshoot = dataMarker + self.sectorDataBitSize + 32
            if overshoot <= len( self.decompressedBitstream ):
                dataMarkers.append( dataMarker )
                cnt+=1
            else:
                #print("Removing sector marker because it overshot the bitstream")
                sectorMarkers.remove(sectorMarkers[cnt])
        return (sectorMarkers, dataMarkers)

    def parseSingleSector(self, sectorStart, dataMarker):
        prelude = 4 * 16 # a1a1a1fe or a1a1a1fb
        dataMarker = prelude + dataMarker - sectorStart
        self.currentSectorBitstream = self.decompressedBitstream[sectorStart - prelude : sectorStart + self.sectorDataBitSize + 32 + dataMarker]
        #rawMfmDecoded = self.mfmDecode( self.currentSectorBitstream)
        #rdl = len(rawMfmDecoded)
        #rawstream = self.convertBitstreamBytes( rawMfmDecoded[0:int(rdl/4)*4], True)

        return {
            "headermeta"   : self.grabSectorChunkHex(  0, 128),#complete raw header data for crc check
            "trackno"      : self.grabSectorChunkInt(  8,  2),
            "sideno"       : self.grabSectorChunkInt( 10,  2),
            "sectorno"     : self.grabSectorChunkInt( 12,  2),
            "sectorlength" : self.grabSectorChunkInt( 15,  1),
            "crc_header"   : self.grabSectorChunkHex( 128, 32),
            "datameta"     : self.grabSectorChunkHex( dataMarker - prelude, prelude), #a1a1a1fb
            "data"         : self.grabSectorChunkHex( dataMarker, self.sectorDataBitSize),
            "crc_data"     : self.grabSectorChunkHex( dataMarker + self.sectorDataBitSize, 32)
        }

    def printSerialStats(self):
        (tdtr,tdtc,tdtd) = self.arduino.getStats()
        print ( "Total duration of all track reads   : " + tdtr + " seconds")
        print ( "Total duration other serial commands: " + tdtc + " seconds")
        print ( "Total duration of all decompressions: " + tdtd + " seconds")
