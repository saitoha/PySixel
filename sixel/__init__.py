#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

__author__ = "Hayaki Saito (user@zuse.jp)"
__version__ = "0.1.11"
__license__ = "GPL v3"

import os
import sys
import optparse
import select
import logging

from .cellsize import CellSizeDetector
from .sixel import SixelWriter

license_text = """
Copyright (C) 2012-2014  Hayaki Saito <user@zuse.jp>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


def _filenize(f):
    import stat

    mode = os.fstat(f.fileno()).st_mode
    if stat.S_ISFIFO(mode) or os.isatty(f.fileno()):
        try:
            from cStringIO import StringIO
        except ImportError:
            from StringIO import StringIO
        return StringIO(f.read())
    return f


def main():

    parser = optparse.OptionParser()

    parser.add_option("-8", "--8bit-mode",
                      action="store_true",
                      dest="f8bit",
                      help="Generate a sixel image for 8bit terminal or printer")

    parser.add_option("-7", "--7bit-mode",
                      action="store_false",
                      dest="f8bit",
                      help="Generate a sixel image for 7bit terminal or printer")

    parser.add_option("-r", "--relative-position",
                      action="store_false",
                      default=False,
                      dest="fabsolute",
                      help="Treat specified position as relative one")

    parser.add_option("-a", "--absolute-position",
                      action="store_true",
                      dest="fabsolute",
                      help="Treat specified position as absolute one")

    parser.add_option("-x", "--left",
                      action="store",
                      dest="left",
                      help="Left position in cell size, or pixel size with unit 'px'")

    parser.add_option("-y", "--top",
                      action="store",
                      dest="top",
                      help="Top position in cell size, or pixel size with unit 'px'")

    parser.add_option("-w", "--width",
                      action="store",
                      dest="width",
                      help="Width in cell size, or pixel size with unit 'px'")

    parser.add_option("-e", "--height",
                      action="store",
                      dest="height",
                      help="Height in cell size, or pixel size with unit 'px'")

    parser.add_option("-t", "--alpha-threshold",
                      action="store",
                      type="int",
                      dest="alphathreshold",
                      default="0",
                      help="Alpha threthold for PNG-to-SIXEL image conversion")

    parser.add_option("-c", "--chromakey",
                      dest="chromakey",
                      default=False,
                      action="store_true",
                      help="Enable auto chroma key processing")

    parser.add_option("-n", "--ncolor",
                      action="store",
                      type="int",
                      dest="ncolor",
                      default=256,
                      help="Specify number of colors")

    parser.add_option("-b", "--body-only",
                      action="store_true",
                      dest="bodyonly",
                      default=False,
                      help="Output sixel without header and DCS envelope")

    parser.add_option("-f", "--fast",
                      action="store_true",
                      dest="fast",
                      default=True,
                      help="The speed priority mode (default)")

    parser.add_option("-s", "--size",
                      action="store_false",
                      dest="fast",
                      default=True,
                      help="The size priority mode")

    parser.add_option("-v", "--version",
                      action="store_true",
                      dest="version",
                      default=False,
                      help="Show version")

    options, args = parser.parse_args()

    if options.version:
        print(license_text)
        sys.exit(0)

    rcdir = os.path.join(os.getenv("HOME"), ".pysixel")
    logdir = os.path.join(rcdir, "log")
    if not os.path.exists(logdir):
        os.makedirs(logdir)

    logfile = os.path.join(logdir, "log.txt")
    logging.basicConfig(filename=logfile, filemode="w")

    stdin, stdout = sys.stdin, sys.stdout
    left = options.left
    top = options.top
    width = options.width
    height = options.height

    if (left, top, width, height) != (None, None, None, None):
        if os.isatty(stdout.fileno()) and os.isatty(stdin.fileno()):
            try:
                char_width, char_height = CellSizeDetector().get_size()
            except Exception:
                char_width, char_height = (10, 20)
        else:
            char_width, char_height = (10, 20)

        if not left is None:
            pos = left.find("px")
            if pos > 0:
                left = int(left[:pos]) / char_width
            else:
                left = int(left)

        if not top is None:
            pos = top.find("px")
            if pos > 0:
                top = int(top[:pos]) / char_width
            else:
                top = int(top)

        if not width is None:
            pos = width.find("px")
            if pos > 0:
                width = int(width[:pos])
            else:
                width = int(width) * char_width

        if not height is None:
            pos = height.find("px")
            if pos > 0:
                height = int(height[:pos])
            else:
                height = int(height) * char_height

    writer = SixelWriter(f8bit=options.f8bit,
                         bodyonly=options.bodyonly)

    try:
        if select.select([stdin, ], [], [], 0.0)[0]:
            imagefile = _filenize(stdin)
        elif len(args) == 0 or args[0] == '-':
            imagefile = _filenize(stdin)
        else:
            imagefile = args[0]

        writer.draw(imagefile,
                    output=sys.stdout,
                    absolute=options.fabsolute,
                    x=left,
                    y=top,
                    w=width,
                    h=height,
                    ncolor=int(options.ncolor),
                    alphathreshold=options.alphathreshold,
                    chromakey=options.chromakey,
                    fast=options.fast)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
