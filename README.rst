pyAccess1581
==============

This is a floppy disk image utility aimed at the Commodore retro computing community.

pyAccess1581 can create disk images of specific double density (DD) floppy disks by using a specific Arduino based hardware interface to communicate with a vintage 3.5" PC floppy drive. The focus is on the floppy disk format of Commodore 1581 disks - and as an added bonus, DOS floppy disks can also be read as long as they are DD. High density disks (HD) are not supported.

Warning: This software is in a highly experimental alpha state - potentially full of bugs and surprises. Don't use it with the intention to create reliable backups of your data. Always write-protect your floppy disks before using it with this tool!

Python code written by Henning Pingel, reusing hardware interface of `"Arduino Amiga Floppy Disk Reader/Writer" <http://amiga.robsmithdev.co.uk/>`_ by Robert Smith

Software requirements
---------------------

To run this tool on your PC/Notebook you need to have Python3 language installed. I personally tested it with Python 3.6.x and 3.7.x on Linux and Windows 10. It might run on MacOS (untested).

You need to install a number of Python modules: pyserial, bitstring...

Hardware and Arduino firmware requirements
------------------------------------------

This tool only works in conjunction with a specific hardware interface that bridges the gap between an ordinary modern PC/Notebook and a vintage 3.5" PC floppy drive. The hardware interface is based on an 16Mhz Arduino running a specific firmware. The modern PC communicates with the Arduino via a serial connection over a USB cable. A FTDI USB adapter is used for this USB tunnelling task. The Arduino communicates with the floppy drive using its GPIO pins.

This mandatory hardware interface and the firmware for the Arduino were already designed long before this Python based project came into existence: They were actually engineered for another open source project created by Robert Smith in 2017 and 2018: The `"Arduino Amiga Floppy Disk Reader/Writer" <http://amiga.robsmithdev.co.uk/`_. At this time, pyAccess1581 is simply reusing the set of commands that Robert has created to control the floppy drive via a serial connection.

The Arduino Pro Mini 16Mhz 5V that is recommended by Robert is running an ATmega 328. I was also able to make Robert's firmware run on an Arduino Pro Micro running an ATmega 32U4 - with modifications. The additional FTDI adapter is needed anyway.

For further information on the Amiga floppy reader/writer hardware please check `Robert's instructions <http://amiga.robsmithdev.co.uk/instructions>`_. You can find the source code of Robert's project `here <https://github.com/RobSmithDev/ArduinoFloppyDiskReader>`_ (including the firmware to be flashed on to the Arduino Pro Mini):

Usage
-----

Please call script to display help:

.. code-block:: sh
    $ python3 disk2image.py -h

Currently the following options are available (none of them are mandatory to use):
.. code-block:: sh
    -h, --help            show this help message and exit
    -d DISKTYPE, --disktype=DISKTYPE
                          type of DD disk in floppy drive: cbm1581 [default],
                          ibmdos
    -o OUTPUTIMAGE, --output=OUTPUTIMAGE
                          file path/name of image file to write to, default is
                          image_cbm1581.d81
    -s SERIALDEVICENAME, --serialdevice=SERIALDEVICENAME
                          device name of the serial device, for example
                          /dev/ttyUSB0
    -r RETRIES, --retries=RETRIES
                          number of retries to read disk track again after
                          invalid CRC check, default: 5 retries
FAQ
---

I tried to build it and it doesn't work! Who will help?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First of all, you need to own double density disks to test the reader. Ideally you already have an Amiga formatted DD disk with an adf image already correctly written to it. Then you can use Robert's Windows software called ArduinoFloppyReaderWin.exe and launch the excellent "Run diagnostics" menu item to let the software check if you have assembled the hardware correctly. Please don't bother Robert with problems originating from my Python code.

Are there any other projects that do the same stuff?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Yes, have a look at the very promising project `Fluxengine <http://cowlark.com/fluxengine/index.html>`_.

Is this a finished project?
^^^^^^^^^^^^^^^^^^^^^^^^^^^

No, when I find time I want to implement new features. Depending on the complexity of the feature, it will take me some time... Writing a d81 to disk might be possible but it will involve a lot of work.

How does it work?
^^^^^^^^^^^^^^^^^

While Robert Smith focussed on Amiga disk images he still had to come up with a floppy disk reader/writer that is able to decode and encode data stored using Modified Frequency Modulation (MFM). The MFM encoding is commonly used by most of other 3.5" floppy disk formats. As a prerequisite of his Amiga project he had to write an MFM reader/writer/encoder/decoder on which this project relies.

Do you own a 1581 floppy drive to make sure the tool can really do what it claims?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

No, I don't own a 1581 floppy drive. I would like to own one, but collector's prices on the retro market are beyond what I am willing to spend.

Where did you get authentic floppy media from if you don't own a 1581 floppy drive yourself?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

With the VC1581 it's a bit of a chicken and egg problem. Commercial software was never published in the 1581 format back in the days - the 1541 disk drive was the lowest common denominator that had the biggest market share. So the 1581 was always used in conjunction with empty disks that were formatted and filled at home. The lack of commercial releases on 3.5" disk for Commodore 64/128 also means that there were hardly any copy protections in place and as a consequence there was no raw image format needed next to d81 (that only contains the data chunks of the sectors) that would reflect irregularities of floppy track content caused by any kind of copy protection.

Where was I? Ahh... As I didn't own any 3.5" DD floppy disks (except for my HP printer DOS driver disk from 1995 that I found the other day) I recently bought a few boxes of used Amiga disks and then used an ancient PC I discovered in the cellar of my parents. That PC from 2002 included a 3.5" floppy drive. Using Linux, I was able to configure the disk drive in a way that is acknowledged to be feasable to write valid disks for the 1581 disk drive.

To enforce the 1581 format on my Linux OS I used ``fdutils`` and had do the following:

.. code-block:: sh
    mknod /dev/fd0cbm1581 b 2 124
    setfdprm /dev/fd0cbm1581 DD DS sect=10 cyl=80 swapsides
    floppycontrol /dev/fd0 -A 31,7,8,4,25,28,22,21

Information regarding the parameters may also be found inside of the sourcecode of fdutils (in  file `mediaprm <https://github.com/Distrotech/fdutils/blob/master/src/mediaprm>`_). A quote from there:

.. code-block:: sh
    #Commodore 1581 (the 3 1/2 drive of the Commodore 128)
    "CBM1581":
    DS DD sect=10 cyl=80 ssize=512 fmt_gap=35 gap=12 swapsides

Afterwards I was able to format the DD disk like this:
.. code-block:: sh
    fdformat /dev/fd0cbm1581

Finally I used ``dd`` to put a d81 image on the real disk.

Does this project only run on specific Arduinos? Why is that the best possible hardware for this kind of project?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

While Robert has chosen an Atmega328 based Arduino Pro Mini (16Mhz, 5V), I can offer the alternative to use an Atmega32U4 based Arduino Pro Micro (16Mhz, 5V) instead. I have ported his sketch to the Pro Micro (haven't published this sourcecode yet). But the Pro Mini seems to be slightly cheaper anyway.

While learning more about micro controllers in 2019 and looking at other projects like `Fluxengine <http://cowlark.com/fluxengine/index.html>`_ or `ADF-Copy<https://nickslabor.niteto.de/projekte/adf-copy/>`_ I guess there is a big choice of microcontrollers that could do the job. Robert Smith has chosen a conveniently low-cost microcontroller that only runs on 16Mhz with a tiny bit of RAM and he was able to prove that it still can be a valid interface running just fast enough to do the proper job of reading and writing DD disks.

Why did you start this Python based project? Especially as a project like Fluxengine can do the same?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This little Python project started off as a proof of concept that the same hardware that Robert uses for handling Amiga Double Density floppy disks could also be used to read Commodore 1581 Double Density floppy disks. As an added benefit my Python based tool can also read Double Density DOS floppy disks because the sector structure and meta data is not different between Commodore 1581 and DOS disks (of course, there are other differences).

Can High Density (HD) floppy disks like FD2000 disks for Commodore computers be supported in the future?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

I guess that it would make sense to do this with a different microcontroller that is faster than 16 Mhz. It looks like Fluxengine can be used for that already: Please have a look at `my little report about this format <https://github.com/davidgiven/fluxengine/issues/107>`_

Credits
-------
This tool relies on the work of many people (be it through other software components or providing documentation on the web) who all deserve a thank you. Additionally, I would particularly like to thank Robert Smith and David Given for their work on imaging floppy disks and publishing their work as open source projects.

License
-------
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
