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

class diskFormatRoot:
    def __init__(self):
        self.name           = 'root'
        self.trackRange     = range(0,80) #0-79
        self.headRange      = range(0,2)  #0-1
        self.sectorSize     = 512 # bytes
        self.swapsides      = False
        self.imageExtension = 'img'
        self.mfmSyncMarkA1  = '100010010001001' #special mfm sync mark

class diskFormatDOS(diskFormatRoot):
    def __init__(self):
        super().__init__()
        self.name  = 'ibmdos'
        self.mfmFE = '101010101010100' #mfm encoded fe
        self.mfmFB = '101010101000101' #mfm encoded fb
        self.mfm00 = '010101010101010' #mfm encoded 00
        self.expectedSectorsPerTrack = 9
        self.sectorStartMarker     = (('1' + self.mfm00 )*10)[1:] + '0' + ((self.mfmSyncMarkA1 + '0')*3) + self.mfmFE
        self.sectorDataStartMarker = (('1' + self.mfm00 )*6)[1:] + '0' + ((self.mfmSyncMarkA1 + '0')*3) + self.mfmFB
        self.legalOffsetRangeLowerBorder = 704
        self.legalOffsetRangeUpperBorder = 720
        self.legalOffsetRange = range(self.legalOffsetRangeLowerBorder,self.legalOffsetRangeUpperBorder+1)

        #TODO: check value 1320 *8 bits. 512 bytes as data content wrapped in
        #sector meta data bytes, 1320 is just a good guess that just works
        #maybe we can shrink it more
        self.sectorLength = 1320*8

    '''
    def hexString2bitString(self, hexString ):
        bitString = ""
        for nibble in hexString:
            bitString += str(bin(int(nibble,16))[2:]).zfill(4)
        return bitString
    '''

class diskFormat1581(diskFormatDOS):
    def __init__(self):
        super().__init__()
        self.name                   = 'cbm1581'
        self.expectedSectorsPerTrack = 10
        self.swapsides              = True
        self.imageExtension         = 'd81'
