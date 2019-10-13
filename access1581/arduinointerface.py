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

    CREDITS

    The class ArduinoFloppyControlInterface implements the interface that
    Robert Smith created for the Arduino Amiga Floppy disk reader/writer.
    Robert Smith has released his project under GPL V3. For more information,
    please visit http://amiga.robsmithdev.co.uk/

'''

import time, platform
from serial import Serial

class ArduinoFloppyControlInterface:
    '''
    implements the commands defined by Rob Smith's
    Arduino Amiga Floppy Disk Reader/Writer project
    these commands are sent to an Arduino via serial
    connection running with 2m baud
    compare sourcecode of ArduinoInterface.cpp at:
        https://github.com/RobSmithDev/ArduinoFloppyDiskReader/
        blob/master/ArduinoFloppyReader/lib/ArduinoInterface.cpp
    '''
    def __init__(self, serialDevice, diskFormat):
        self.serialDevice = serialDevice
        self.trackRange = diskFormat.trackRange
        self.hexZeroByte = bytes(chr(0),'utf-8')
        self.decompressMap = { 0: "", 1: "01", 2: "001", 3: "0001"}
        self.connectionEstablished = False
        self.ignoreIndexHole = True
        self.isRunning = False
        self.serial = False
        self.currentTrack = 100
        self.currentHead = 2
        self.total_duration_trackread = 0
        self.total_duration_cmds = 0
        self.total_duration_decompress = 0
        self.cmd = {
            "version"     : ( b'?', "Detecting firmware version" ),
            "motor_on"    : ( b'+', "Switching motor on" ),
            "motor_off"   : ( b'-', "Switching motor off" ),
            "rewind"      : ( b'.', "Rewinding to track 0"),
            "head0"       : ( b'[', "Selecting head 0"),
            "head1"       : ( b']', "Selecting head 1"),
            "select_track": ( b'#', "Selecting track"), # not complete command without track number
            "read_track"  : ( b'<', "Reading track"),
            "read_track_from_index_hole" : ( b'<1', "Reading track from index hole"),  # combined command
            "read_track_ignoring_index_hole" : ( b'<0', "Instantly reading track"),  # combined command
            "write_track" : ( b'>', "Writing track"),
            "enable_write": ( b'~', "Enable writing"),
            "erase_track" : ( b'X', "Erasing track"),
            #"diagnostics" : ( b'&', "Launching diagnostics routines")
        }

    def __del__(self):
        if self.connectionEstablished is True:
            self.sendCommand("rewind")
            self.sendCommand("motor_off")
            self.isRunning = False
            self.serial.close()

    def setIgnoreIndexHole( b ):
        self.ignoreIndexHole = b

    def openSerialConnection(self):
        self.serial = Serial( self.serialDevice, 2000000, timeout=None)
        self.connectionEstablished = True
        print ("Connection to microcontroller established via " + self.serialDevice )
        self.serial.reset_input_buffer()
        self.sendCommand("version")
        self.sendCommand("rewind")
        #print( self.serial.get_settings())

    def connectionIsUsable(self, cmd):
        executeCMD = False
        if cmd == "motor_off":
            self.isRunning = False
            executeCMD = True
        elif cmd == "motor_on":
            self.isRunning = True
            executeCMD = True
        elif self.isRunning is False: #and not cmd == "motor_on":
            self.sendCommand("motor_on")
            executeCMD = True
        elif self.isRunning is True:
            executeCMD=True
        return executeCMD

    def sendCommand(self, cmdname, param=b''):
        (cmd, label) = self.cmd[cmdname]
        if self.connectionEstablished is False:
            self.openSerialConnection()
        if cmdname == "version" or self.connectionIsUsable(cmdname) is True:
            starttime_serialcmd = time.time()
            #print ("...Processing cmd " + cmdname)
            self.serial.reset_input_buffer()
            maxRetries = 1
            retries = maxRetries
            while retries > 0:
                self.serial.write( cmd + param)
                reply = self.serial.read(1)
                if cmdname == "version":
                    firmware = self.serial.read(4)
                    print ("Firmware version on Arduino: " + str(firmware))
                duration_serialcmd = int((time.time() - starttime_serialcmd)*1000)/1000
                self.total_duration_cmds += duration_serialcmd
                if param != b'':
                    label2 = label + " " + str(param)
                else:
                    label2 = label
#                print  ("    Serial cmd duration:                            " + str(duration_serialcmd) + " seconds " + label2)
                if not reply == b'1':
                    retries = retries - 1
                    if retries == 0:
                        retries=0
                        raise Exception ( label2 + ": Something went wrong! Reply was " + str(reply))
                    else:
                        print ( "Retrying: " + label2 + ": Reply was " + str(reply))
                else:
                    retries = 0 #success
                    #print( "   " + label + ": OK")
        else:
            raise Exception ( label + ": Connection was not usable!")

    def selectTrackAndHead(self, track, head):
        if self.currentTrack != track:
            if not track in self.trackRange:
                raise Exception("Error: Track is not in range")
            trs = str(track) if track > 9 else '0'+str(track)
            btrack = bytes( trs,'utf-8' )
            self.sendCommand( "select_track", btrack )# Moving head to track
            self.currentTrack = track
        if self.currentHead != head:
            if head >= 0 and head < 2:
                self.sendCommand("head" + str(head))
                self.currentHead = head
            else:
                print ('ERROR: Head should be 0 or 1!')

    def getCompressedTrackData(self, track, head):
        self.selectTrackAndHead(track, head)
        starttime_trackread = time.time()
        if self.ignoreIndexHole is True:
            self.serial.write(self.cmd["read_track_ignoring_index_hole"][0])
        else:
            self.serial.write(self.cmd["read_track_from_index_hole"][0])
        #speedup for Linux where pyserial seems to be very optimized
        if platform.system() == "Linux":
            trackbytes = self.serial.read_until( self.hexZeroByte , 12200)
        else:
            trackbytes = self.serial.read(10380)
            self.serial.timeout = 0
            trackbytes = trackbytes + self.serial.readline()
            self.serial.timeout = None
        duration_trackread = int((time.time() - starttime_trackread)*1000)/1000
        self.total_duration_trackread += duration_trackread
#        print  ("    Track read duration:                            " + str(duration_trackread) + " seconds")
        tracklength = len(trackbytes)
        if tracklength < 10223:
            print ("Track length suspicously short: " + str(tracklength) + " bytes")
        return trackbytes

    def getDecompressedBitstream(self, track, head):
        compressedBytes = self.getCompressedTrackData(track, head)
        starttime_decompress = time.time()
        decompressedBitstream = ""
        #print( "Length of compressed bitstream: "+ str(len(compressedBitstream)) )
        for byte in compressedBytes:
            bits=bin(byte)[2:].zfill(8)
            for chunk in range(0,4):
                value=int(bits[chunk*2:chunk*2+2])&3
                if value > 3:
                    print ("ERROR decompressBitstream illegal value!")
                decompressedBitstream += self.decompressMap[value]

        duration_decompress = int((time.time() - starttime_decompress)*1000)/1000
#        print  ("    Decompress duration:                            " + str(duration_decompress) + " seconds")
        self.total_duration_decompress += duration_decompress
        return decompressedBitstream
        '''
        Looking for a way to performance-improve this method. Tried to
        experiment with bitstring.Bits(), but that appears to be way slower than
        the code used now. Will come back to this at some point in the future.
        Example code:
            self.decompressMap2 = { '0b00': '', '0b01': '01', '0b10': '001', '0b11': '0001'}
            b = bitstring.Bits(bytes = compressedBytes)
            for bits in b.cut(2):
                decompressedBitstream += self.decompressMap2[str(bits)]
        '''

    def getStats(self):
        tdtr = str(int(self.total_duration_trackread*100)/100)
        tdtc = str(int(self.total_duration_cmds*100)/100)
        tdtd = str(int(self.total_duration_decompress*100)/100)
        return (tdtr, tdtc, tdtd)

class ArduinoSimulator(ArduinoFloppyControlInterface):

    def __init__(self, diskFormat, rawTrackData):
        super().__init__("bla", diskFormat)
        self.rawTrackData = rawTrackData

    def __del__(self):
        pass

    def openSerialConnection(self):
        pass

    def connectionIsUsable(self, cmd):
        return True

    def getDecompressedBitstream(self, track, head):
#        if head == 0:
#            time.sleep(1)
        return self.rawTrackData[track][head]

if __name__ == '__main__':
    main()
