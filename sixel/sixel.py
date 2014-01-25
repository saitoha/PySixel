#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ***** BEGIN LICENSE BLOCK *****
# Copyright (C) 2012  Hayaki Saito <user@zuse.jp>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ***** END LICENSE BLOCK *****

import sys
import os
import logging
try:
    from sixel_cimpl import SixelConverter
except ImportError, e:
    logging.exception(e)
    from converter import SixelConverter

class SixelWriter:
    
    def __init__(self, f8bit = False):
        self.f8bit = f8bit
        if f8bit:  # 8bit mode
            self.CSI='\x9b'
        else:
            self.CSI='\x1b['

    def save_position(self, output):
        if os.isatty(output.fileno()):
            output.write('\x1b7')  # DECSC

    def restore_position(self, output):
        if os.isatty(output.fileno()):
            output.write('\x1b8')  # DECRC

    def move_x(self, n, fabsolute, output):
        output.write(self.CSI)
        if fabsolute:
            output.write('%d`' % n)
        elif n > 0:
            output.write('%dC' % n)
        elif n < 0:
            output.write('%dD' % -n)

    def move_y(self, n, fabsolute, output):
        output.write(self.CSI)
        if fabsolute:
            output.write('%dd' % n)
        elif n > 0:
            output.write('%dB' % n)
        elif n < 0:
            output.write('%dA' % n)

    def draw(self,
             filename,
             output=sys.stdout,
             absolute=False,
             x=None,
             y=None,
             w=None,
             h=None,
             ncolor=16,
             alphathreshold=0,
             chromakey=False):

        try:
            filename.seek(0)
        except AttributeError:
            pass
        self.save_position(output)

        try:
            if not x is None:
                self.move_x(x, absolute, output)

            if not y is None:
                self.move_y(y, absolute, output)

            sixel_converter = SixelConverter(filename,
                                             self.f8bit,
                                             w,
                                             h,
                                             ncolor,
                                             alphathreshold=alphathreshold,
                                             chromakey=chromakey)
            sixel_converter.write(output)

        finally:
            self.restore_position(output)
        

