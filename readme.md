# pyAccess1581

This is a floppy disk image utility aimed at the Commodore retro computing community.

pyAccess1581 can create disk images of specific double density (DD) floppy disks by using a specific Arduino based hardware interface to communicate with a vintage 3.5" PC floppy drive. The focus is on the floppy disk format of Commodore 1581 disks - and as an added bonus, DOS floppy disks can also be read as long as they are DD. High density disks (HD) are not supported.

Warning: This software is in a highly experimental alpha state - potentially full of bugs and surprises. Don't use it with the intention to create reliable backups of your data. Always write-protect your floppy disks before using it with this tool!

Python code written by Henning Pingel, reusing hardware interface of ["Arduino Amiga Floppy Disk Reader/Writer"](http://amiga.robsmithdev.co.uk/) by Robert Smith

## Software requirements

To run this tool on your PC/Notebook you need to have Python3 language installed. I personally tested it with Python 3.6.x and 3.7.x on Linux and Windows 10. It might run on MacOS (untested).

You need to install a number of Python modules: pyserial, crcmod, bitstring...

## Hardware and Arduino firmware requirements

This tool only works in conjunction with a specific hardware interface that bridges the gap between an ordinary modern PC/Notebook and a vintage 3.5" PC floppy drive. The hardware interface is based on an 16Mhz Arduino running a specific firmware. The modern PC communicates with the Arduino via a serial connection over a USB cable. A FTDI USB adapter is used for this USB tunnelling task. The Arduino communicates with the floppy drive using its GPIO pins.

This mandatory hardware interface and the firmware for the Arduino were already designed long before this Python based project came into existence: They were actually engineered for another open source project created by Robert Smith in 2017 and 2018: The ["Arduino Amiga Floppy Disk Reader/Writer"](http://amiga.robsmithdev.co.uk/). At this time, pyAccess1581 is simply reusing the set of commands that Robert has created to control the floppy drive via a serial connection.

The Arduino Pro Mini 16Mhz 5V that is recommended by Robert is running an ATmega 328. I was also able to make Robert's firmware run on an Arduino Pro Micro running an ATmega 32U4 - with modifications. The additional FTDI adapter is needed anyway.

For further information on the Amiga floppy reader/writer hardware please check [Robert's instructions](http://amiga.robsmithdev.co.uk/instructions). You can find the source code of Robert's project [here](https://github.com/RobSmithDev/ArduinoFloppyDiskReader) (including the firmware to be flashed on to the Arduino Pro Mini):

## Usage

Please call script to display help:
```
$ python3 disk2image.py -h
```
## FAQ

#### I tried to build it and it doesn't work! Who will help?

First of all, you need to own double density disks to test the reader. Ideally you already have an Amiga formatted DD disk with an adf image already correctly written to it. Then you can use Robert's Windows software called ArduinoFloppyReaderWin.exe and launch the excellent "Run diagnostics" menu item to let the software check if you have assembled the hardware correctly. Please don't bother Robert with problems originating from my Python code.

#### Are there any other projects that do the same stuff?

Yes, have a look at the very promising project [Fluxengine](http://cowlark.com/fluxengine/index.html).

#### Is this a finished project?

No, when I find time I want to implement new features. Depending on the complexity of the feature, it will take me some time... Writing a d81 to disk might be possible but it will involve a lot of work.

#### How does it work?

While Robert Smith focussed on Amiga disk images he still had to come up with a floppy disk reader/writer that is able to decode and encode data stored using Modified Frequency Modulation (MFM). The MFM encoding is commonly used by most of other 3.5" floppy disk formats. As a prerequisite of his Amiga project he had to write an MFM reader/writer/encoder/decoder on which this project relies.

#### Do you own a 1581 floppy drive to make sure the tool can really do what it claims?

No, I don't own a 1581 floppy drive. I would like to own one, but collector's prices on the retro market are beyond what I am willing to spend.

#### Does this project only run on specific Arduinos? Why is that the best possible hardware for this kind of project?

While Robert has chosen an Atmega328 based Arduino Pro Mini (16Mhz, 5V), I can offer the alternative to use an Atmega32U4 based Arduino Pro Micro (16Mhz, 5V) instead. I have ported his sketch to the Pro Micro (haven't published this sourcecode yet). But the Pro Mini seems to be slightly cheaper anyway.

While learning more about micro controllers in 2019 and looking at other projects like [Fluxengine](http://cowlark.com/fluxengine/index.html) or [ADF-Copy](https://nickslabor.niteto.de/projekte/adf-copy/) I guess there is a big choice of microcontrollers that could do the job. Robert Smith has chosen a conveniently low-cost microcontroller that only runs on 16Mhz with a tiny bit of RAM and he was able to prove that it still can be a valid interface running just fast enough to do the proper job of reading and writing DD disks.

#### Why did you start this Python based project? Especially as a project like Fluxengine can do the same?

This little Python project started off as a proof of concept that the same hardware that Robert uses for handling Amiga Double Density floppy disks could also be used to read Commodore 1581 Double Density floppy disks. As an added benefit my Python based tool can also read Double Density DOS floppy disks because the sector structure and meta data is not different between Commodore 1581 and DOS disks (of course, there are other differences).

#### Can High Density (HD) floppy disks like FD2000 disks for Commodore computers be supported in the future?

I guess that it would make sense to do this with a different microcontroller.

## Credits
This tool relies on the work of many people (be it through other software components or providing documentation on the web) who all deserve a thank you. Additionally, I would particularly like to thank Robert Smith and David Given for their work on imaging floppy disks and publishing their work as open source projects.

## License

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
