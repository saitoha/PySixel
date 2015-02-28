#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ***** BEGIN LICENSE BLOCK *****
# Copyright (C) 2012-2014  Hayaki Saito <user@zuse.jp>
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
if sys.version_info[0] == 3:
    xrange = range
del sys


class SixelConverter:

    def __init__(self, file,
                 f8bit=False,
                 w=None,
                 h=None,
                 ncolor=256,
                 alphathreshold=0,
                 chromakey=False,
                 fast=True):

        self.__alphathreshold = alphathreshold
        self.__chromakey = chromakey
        self._slots = [0] * 257
        self._fast = fast

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
            from PIL import Image  # PIL
        except ImportError:
            import imageloader as Image

        image = Image.open(file)
        image = image.convert("RGB").convert("P",
                                             palette=Image.ADAPTIVE,
                                             colors=ncolor)
        if w or h:
            width, height = image.size
            if not w:
                w = width
            if not h:
                h = height
            image = image.resize((w, h))

        self.palette = image.getpalette()
        self.data = image.getdata()
        self.width, self.height = image.size

        if alphathreshold > 0:
            self.rawdata = Image.open(file).convert("RGBA").getdata()

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
        template = '%d;%d;%dq"1;1;%d;%d'
        args = (aspect_ratio, background_option, dpi, self.width, self.height)
        output.write(template % args)

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
        for n in xrange(0, self._ncolor):
            palette = self.palette
            r = palette[n * 3 + 0] * 100 / 256
            g = palette[n * 3 + 1] * 100 / 256
            b = palette[n * 3 + 2] * 100 / 256
            output.write('#%d;2;%d;%d;%d\n' % (n, r, g, b))
        height = self.height
        width = self.width
        for y in xrange(0, height, 6):
            if height - y <= 5:
                band = height - y
            else:
                band = 6
            buf = []
            set_ = set()

            def add_node(n, s):
                node = []
                cache = 0
                count = 0
                if s:
                    node.append((0, s))
                for x in xrange(s, width):
                    count += 1
                    p = y * width + x
                    six = 0
                    for i in xrange(0, band):
                        d = data[p + width * i]
                        if d == n:
                            six |= 1 << i
                        elif not d in set_:
                            set_.add(d)
                            add_node(d, x)
                    if six != cache:
                        node.append([cache, count])
                        count = 0
                        cache = six
                if cache != 0:
                    node.append([cache, count])
                buf.append((n, node))

            add_node(data[y * width], 0)

            for n, node in buf:
                output.write("#%d\n" % n)
                for six, count in node:
                    if count < 4:
                        output.write(chr(0x3f + six) * count)
                    else:
                        output.write('!%d%c' % (count, 0x3f + six))
                output.write("$\n")
            output.write("-\n")

    def __write_body_without_alphathreshold_fast(self, output, data, keycolor):
        height = self.height
        width = self.width
        n = 1
        for y in xrange(0, height):
            p = y * width
            cached_no = data[p]
            count = 1
            c = -1
            for x in xrange(0, width):
                color_no = data[p + x]
                if color_no == cached_no:  # and count < 255:
                    count += 1
                else:
                    if cached_no == keycolor:
                        c = 0x3f
                    else:
                        c = 0x3f + n
                        if self._slots[cached_no] == 0:
                            palette = self.palette
                            r = palette[cached_no * 3 + 0] * 100 / 256
                            g = palette[cached_no * 3 + 1] * 100 / 256
                            b = palette[cached_no * 3 + 2] * 100 / 256
                            self._slots[cached_no] = 1
                            output.write('#%d;2;%d;%d;%d' % (cached_no, r, g, b))
                        output.write('#%d' % cached_no)
                    if count < 3:
                        output.write(chr(c) * count)
                    else:
                        output.write('!%d%c' % (count, c))
                    count = 1
                    cached_no = color_no
            if c != -1 and count > 1:
                if cached_no == keycolor:
                    c = 0x3f
                else:
                    if self._slots[cached_no] == 0:
                        palette = self.palette
                        r = palette[cached_no * 3 + 0] * 100 / 256
                        g = palette[cached_no * 3 + 1] * 100 / 256
                        b = palette[cached_no * 3 + 2] * 100 / 256
                        self._slots[cached_no] = 1
                        output.write('#%d;2;%d;%d;%d' % (cached_no, r, g, b))
                    output.write('#%d' % cached_no)
                if count < 3:
                    output.write(chr(c) * count)
                else:
                    output.write('!%d%c' % (count, c))
            if n == 32:
                n = 1
                output.write('-')  # write sixel line separator
            else:
                n <<= 1
                output.write('$')  # write line terminator

    def __write_body_with_alphathreshold(self, output, data, keycolor):
        rawdata = self.rawdata
        height = self.height
        width = self.width
        max_runlength = 255
        n = 1
        for y in xrange(0, height):
            p = y * width
            cached_no = data[p]
            cached_alpha = rawdata[p][3]
            count = 1
            c = -1
            for x in xrange(0, width):
                color_no = data[p + x]
                alpha = rawdata[p + x][3]
                if color_no == cached_no:
                    if alpha == cached_alpha:
                        if count < max_runlength:
                            count += 1
                            continue
                if cached_no == keycolor:
                    c = 0x3f
                elif cached_alpha < self.__alphathreshold:
                    c = 0x3f
                else:
                    c = n + 0x3f
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
            if c != -1:
                if cached_no == keycolor:
                    c = 0x3f
                if count == 1:
                    output.write('#%d%c' % (cached_no, c))
                elif count == 2:
                    output.write('#%d%c%c' % (cached_no, c, c))
                else:
                    output.write('#%d!%d%c' % (cached_no, count, c))
            output.write('$')  # write line terminator
            if n == 32:
                n = 1
                output.write('-')  # write sixel line separator
            else:
                n <<= 1

    def __write_body_section(self, output):
        data = self.data
        if self.__chromakey:
            keycolor = data[0]
        else:
            keycolor = -1
        if self.__alphathreshold == 0:
            if self._fast:
                self.__write_body_without_alphathreshold_fast(output, data, keycolor)
            else:
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

    def write(self, output, bodyonly=False):
        if not bodyonly:
            self.__write_header(output)
        self.__write_body_section(output)
        if not bodyonly:
            self.__write_terminator(output)
