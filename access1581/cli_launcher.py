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

import platform, os
from optparse import OptionParser
from access1581.imager import *

class launcher:

    def __init__(self):
        #my default serial device addresses
        self.serialDeviceAddresses = {
            'Linux' : '/dev/ttyUSB0',
            'Windows' : 'COM5'
        }
        self.diskFormatTypes = {
            "cbm1581" : diskFormat1581,
            "ibmdos"  : diskFormatDOS
        }
        self.defaultDisktype = 'cbm1581'
        self.defaultOutputImageName = \
            'image_' + self.defaultDisktype + '.' + \
            self.diskFormatTypes[self.defaultDisktype]().imageExtension
        self.defaultRetries = 5

        parser = OptionParser("usage: %prog [options] arg")
        parser.add_option("-d", "--disktype",
            dest="disktype",
            help=self.getDocDiskType(),
            default=self.defaultDisktype
        )
        parser.add_option("-o", "--output",
            dest="outputImage",
            help="file path/name of image file to write to, default is "+self.defaultOutputImageName,
            default=self.defaultOutputImageName
        )
        parser.add_option("-s", "--serialdevice",
            dest="serialDeviceName",
            help="device name of the serial device, for example /dev/ttyUSB0 (use value 'simulated' to test functionality)",
            default=self.serialDeviceAddresses[ platform.system() ]
        )
        parser.add_option("-r", "--retries", dest="retries",
            help="number of retries to read disk track again after invalid CRC check, default: "+
            str(self.defaultRetries)+" retries",
            default=self.defaultRetries
        )
        (options, args) = parser.parse_args()

        if options.serialDeviceName != "simulated" and platform.system() != "Windows" and not os.path.exists(options.serialDeviceName):
            raise Exception( "Serial device does not exist: " + options.serialDeviceName )

        if not options.disktype in self.diskFormatTypes.keys():
            raise Exception("Error: disk format " + options.disktype +  " is unknown")
        diskFormat = self.diskFormatTypes[ options.disktype ]()
        options.storeBitstream = False #tmp debug
        IBMDoubleDensityFloppyDiskImager( diskFormat, options.outputImage, int(options.retries), options.serialDeviceName, options.storeBitstream )

    def getDocDiskType(self):
        dft = ''
        for type in self.diskFormatTypes.keys():
            defa = "" if type != self.defaultDisktype else " [default]"
            dft += type + defa + ", "
        dft = dft[0:len(dft)-2]
        return "type of DD disk in floppy drive: " + dft
