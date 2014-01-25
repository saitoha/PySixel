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

class SixelConverter:

    def __init__(self, file,
                 f8bit=False,
                 w=None,
                 h=None,
                 ncolor=16,
                 alphathreshold=0,
                 chromakey=False):

        self.__alphathreshold = alphathreshold
        self.__chromakey = chromakey

        if ncolor >= 256:
            ncolor = 256

        self._ncolor = ncolor

        if f8bit:  # 8bit mode
            self.DCS = '\x90'
            self.ST = '\x9c'
        else:
            self.DCS = '\x1bP'
            self.ST = '\x1b\\'

        try:
            import Image  # PIL
        except ImportError:
            import imageloader as Image

        image = Image.open(file)
        image = image.convert("RGB").convert("P",
                                             palette=Image.ADAPTIVE,
                                             colors=ncolor)
        if not (w is None and h is None):
            width, height = image.size
            if w is None:
                w = width
            if h is None:
                h = height
            image = image.resize((w, h))

        if alphathreshold > 0:
            self.rawdata = image.convert("RGBA").getdata()

        self.palette = image.getpalette()
        self.data = image.getdata()
        self.width, self.height = image.size

    def __write_header(self, output):
        # start Device Control String (DCS)
        output.write(self.DCS)

        # write header
        aspect_ratio = 7  # means 1:1
        if self.__chromakey:
            background_option = 2
        else:
            background_option = 1
        dpi = 75  # dummy value
        output.write('%d;%d;%dq"1;1' % (aspect_ratio, background_option, dpi))

    def __write_palette_section(self, output):

        palette = self.palette

        # write palette section
        for i in xrange(0, self._ncolor * 3, 3):
            no = i / 3
            r = palette[i + 0] * 100 / 256
            g = palette[i + 1] * 100 / 256
            b = palette[i + 2] * 100 / 256
            output.write('#%d;2;%d;%d;%d' % (no, r, g, b))

    def __write_body_without_alphathreshold(self, output, data, keycolor):
        height = self.height
        width = self.width
        for y in xrange(0, height):
            cached_no = data[y * width]
            count = 1
            c = None
            for x in xrange(0, width):
                color_no = data[y * width + x]
                if color_no == cached_no and count < 255:
                    count += 1
                    continue
                if cached_no == keycolor:
                    c = '?'
                else:
                    c = chr(pow(2, y % 6) + 63)
                if count == 1:
                    output.write('#%d%c' % (cached_no, c))
                elif count == 2:
                    output.write('#%d%c%c' % (cached_no, c, c))
                    count = 1
                else:
                    output.write('#%d!%d%c' % (cached_no, count, c))
                    count = 1
                cached_no = color_no
            if c is not None:
                if cached_no == keycolor:
                    c = '?'
                if count == 1:
                    output.write('#%d%c' % (cached_no, c))
                elif count == 2:
                    output.write('#%d%c%c' % (cached_no, c, c))
                else:
                    output.write('#%d!%d%c' % (cached_no, count, c))
            output.write('$')  # write line terminator
            if y % 6 == 5:
                output.write('-')  # write sixel line separator

    def __write_body_with_alphathreshold(self, output, data, keycolor):
        rawdata = self.rawdata
        height = self.height
        width = self.width
        max_runlength = 255
        for y in xrange(0, height):
            cached_no = data[y * width]
            cached_alpha = rawdata[y * width][3]
            count = 1
            c = None
            for x in xrange(0, width):
                color_no = data[y * width + x]
                alpha = rawdata[y * width + x][3]
                if color_no == cached_no:
                    if alpha == cached_alpha:
                        if count < max_runlength:
                            count += 1
                            continue
                if cached_no == keycolor:
                    c = '?'
                elif cached_alpha < self.__alphathreshold:
                    c = '?'
                else:
                    c = chr(pow(2, y % 6) + 63)
                if count == 1:
                    output.write('#%d%c' % (cached_no, c))
                elif count == 2:
                    output.write('#%d%c%c' % (cached_no, c, c))
                    count = 1
                else:
                    output.write('#%d!%d%c' % (cached_no, count, c))
                    count = 1
                cached_no = color_no
                cached_alpha = alpha
            if c is not None:
                if cached_no == keycolor:
                    c = '?'
                if count == 1:
                    output.write('#%d%c' % (cached_no, c))
                elif count == 2:
                    output.write('#%d%c%c' % (cached_no, c, c))
                else:
                    output.write('#%d!%d%c' % (cached_no, count, c))
            output.write('$')  # write line terminator
            if y % 6 == 5:
                output.write('-')  # write sixel line separator

    def __write_body_section(self, output):
        data = self.data
        if self.__chromakey:
            keycolor = data[0]
        else:
            keycolor = -1
        if self.__alphathreshold == 0:
            self.__write_body_without_alphathreshold(output, data, keycolor)
        else:
            self.__write_body_with_alphathreshold(output, data, keycolor)

    def __write_terminator(self, output):
        # write ST
        output.write(self.ST)  # terminate Device Control String

    def getvalue(self):

        try:
            from cStringIO import StringIO
        except ImportError:
            from StringIO import StringIO
        output = StringIO()

        try:
            self.write(output)
            value = output.getvalue()

        finally:
            output.close()

        return value

    def write(self, output):
        self.__write_header(output)
        self.__write_palette_section(output)
        self.__write_body_section(output)
        self.__write_terminator(output)

