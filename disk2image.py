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

import sys, time
from access1581.cli_launcher import *

def main():
    try:
        starttime = time.time()
        launcher()
        duration = int((time.time() - starttime)*100)/100
        print  ("Estimated total duration            : " + str(duration) + " seconds")
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

if __name__ == '__main__':
    main()
