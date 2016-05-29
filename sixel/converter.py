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
                 ncolor=255,
                 alphathreshold=0,
                 chromakey=False,
                 fast=True):

        self.__alphathreshold = alphathreshold
        self.__chromakey = chromakey

        if ncolor >= 255:
            ncolor = 255

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

    def __write_body_without_alphathreshold(self, output, data, keycolor):
        height = self.height
        width = self.width
        nc = self._ncolor
        for n in xrange(0, nc):
            palette = self.palette
            r = palette[n * 3 + 0] * 100 / 256
            g = palette[n * 3 + 1] * 100 / 256
            b = palette[n * 3 + 2] * 100 / 256
            output.write('#%d;2;%d;%d;%d' % (n, r, g, b))
        buf = bytearray(width * nc)
        cset = bytearray(nc)
        ch0 = 0x6d
        for z in xrange(0, int((height + 5) / 6)):
            # DECGNL (-): Graphics Next Line
            if z > 0:
                output.write('-')
            for p in xrange(0, 6):
                y = z * 6 + p
                for x in xrange(0, width):
                    idx = data[y * width + x]
                    cset[idx] = 0
                    buf[width * idx + x] |= 1 << p
            for n in xrange(0, nc):
                if cset[n] == 0:
                    cset[n] = 1
                    # DECGCR ($): Graphics Carriage Return
                    if ch0 == 0x64:
                        output.write('$')
                    # select color (#%d)
                    output.write('#%d' % n)
                    cnt = 0
                    for x in xrange(0, width):
                        # make sixel character from 6 pixels
                        ch = buf[width * n + x]
                        buf[width * n + x] = 0
                        if ch0 < 0x40 and ch != ch0:
                            # output sixel character
                            s = 63 + ch0
                            while cnt > 255:
                                cnt -= 255
                                # DECGRI (!): - Graphics Repeat Introducer
                                output.write('!255%c' % s)
                            if cnt < 3:
                                output.write(chr(s) * cnt)
                            else:
                                # DECGRI (!): - Graphics Repeat Introducer
                                output.write('!%d%c' % (cnt, s))
                            cnt = 0
                        ch0 = ch
                        cnt += 1
                    if ch0 != 0:
                        # output sixel character
                        s = 63 + ch0
                        while cnt > 255:
                            cnt -= 255
                            # DECGRI (!): - Graphics Repeat Introducer
                            output.write('!255%c' % s)
                        if cnt < 3:
                            output.write(chr(s) * cnt)
                        else:
                            # DECGRI (!): - Graphics Repeat Introducer
                            output.write('!%d%c' % (cnt, s))
                    ch0 = 0x64

    def __write_body_with_alphathreshold(self, output, data, keycolor):
        alphathreshold = self.__alphathreshold
        rawdata = self.rawdata
        height = self.height
        width = self.width
        nc = self._ncolor
        for n in xrange(0, nc):
            palette = self.palette
            r = palette[n * 3 + 0] * 100 / 256
            g = palette[n * 3 + 1] * 100 / 256
            b = palette[n * 3 + 2] * 100 / 256
            output.write('#%d;2;%d;%d;%d' % (n + 1, r, g, b))
        buf = bytearray(width * (nc + 1))
        cset = bytearray(nc + 1)
        ch0 = 0x6d
        for z in xrange(0, int((height + 5) / 6)):
            # DECGNL (-): Graphics Next Line
            if z > 0:
                output.write('-')
            for p in xrange(0, 6):
                y = z * 6 + p
                for x in xrange(0, width):
                    alpha = rawdata[y * width + x][3]
                    if alpha > alphathreshold:
                        idx = data[y * width + x] + 1
                        cset[idx] = 0
                    else:
                        idx = 0
                    buf[width * idx + x] |= 1 << p
            for n in xrange(1, nc):
                if cset[n] == 0:
                    cset[n] = 1
                    # DECGCR ($): Graphics Carriage Return
                    if ch0 == 0x64:
                        output.write('$')
                    # select color (#%d)
                    output.write('#%d' % n)
                    cnt = 0
                    for x in xrange(0, width):
                        # make sixel character from 6 pixels
                        ch = buf[width * n + x]
                        buf[width * n + x] = 0
                        if ch0 < 0x40 and ch != ch0:
                            # output sixel character
                            s = 63 + ch0
                            while cnt > 255:
                                cnt -= 255
                                # DECGRI (!): - Graphics Repeat Introducer
                                output.write('!255%c' % s)
                            if cnt < 3:
                                output.write(chr(s) * cnt)
                            else:
                                # DECGRI (!): - Graphics Repeat Introducer
                                output.write('!%d%c' % (cnt, s))
                            cnt = 0
                        ch0 = ch
                        cnt += 1
                    if ch0 != 0:
                        # output sixel character
                        s = 63 + ch0
                        while cnt > 255:
                            cnt -= 255
                            # DECGRI (!): - Graphics Repeat Introducer
                            output.write('!255%c' % s)
                        if cnt < 3:
                            output.write(chr(s) * cnt)
                        else:
                            # DECGRI (!): - Graphics Repeat Introducer
                            output.write('!%d%c' % (cnt, s))
                    ch0 = 0x64

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
            from io import StringIO
        except:
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
