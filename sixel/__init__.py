#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

__author__  = "Hayaki Saito (user@zuse.jp)"
__version__ = "0.0.6"
__license__ = "GPL v3"

import os, sys, optparse, select
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

from sixel import SixelWriter, SixelConverter

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
                      default=False,
                      action="store_false",
                      dest="fabsolute",
                      help="Treat specified position as relative one")
  
    parser.add_option("-a", "--absolute-position",
                      action="store_true",
                      dest="fabsolute",
                      help="Treat specified position as absolute one")
     
    parser.add_option("-x", "--left",
                      dest="left",
                      help="Left position in cell size, or pixel size with unit 'px'")

    parser.add_option("-y", "--top",
                      dest="top",
                      help="Top position in cell size, or pixel size with unit 'px'")
     
    parser.add_option("-w", "--width",
                      dest="width",
                      help="Width in cell size, or pixel size with unit 'px'")
     
    parser.add_option("-e", "--height",
                      dest="height",
                      help="Height in cell size, or pixel size with unit 'px'")

    parser.add_option("-t", "--alpha-threshold",
                      dest="alphathreshold",
                      default="0",
                      help="Alpha threthold for PNG-to-SIXEL image conversion")

    parser.add_option("-c", "--chromakey",
                      dest="chromakey",
                      default=False,
                      action="store_true",
                      help="Enable auto chroma key processing")

    options, args = parser.parse_args()

    import cellsize

    if os.isatty(sys.stdin.fileno()):
        try:
            char_width, char_height = cellsize.CellSizeDetector().get_size()
        except:
            char_width, char_height = (10, 20)
    else:
        char_width, char_height = (10, 20)

    left = options.left
    if not left is None:
        pos = left.find("px")
        if pos > 0:
            left = int(left[:pos]) / char_width 
        else:
            left = int(left) 

    top = options.top
    if not top is None:
        pos = top.find("px")
        if pos > 0:
            top = int(top[:pos]) / char_width 
        else:
            top = int(top) 
 
    width = options.width
    if not width is None:
        pos = width.find("px")
        if pos > 0:
            width = int(width[:pos]) 
        else:
            width = int(width) * char_width
 
    height = options.height
    if not height is None:
        pos = height.find("px")
        if pos > 0:
            height = int(height[:pos]) 
        else:
            height = int(height) * char_height
               
    writer = sixel.SixelWriter(f8bit=options.f8bit)

    if select.select([sys.stdin, ], [], [], 0.0)[0]:
        imagefile = StringIO(sys.stdin.read())
    else:
        if len(args) == 0 or args[0] == '-':
            imagefile = StringIO(sys.stdin.read())
        else:
            imagefile = args[0]

    alphathreshold = int(options.alphathreshold)

    writer.draw(imagefile,
                absolute=options.fabsolute,
                x=left,
                y=top,
                w=width,
                h=height,
                alphathreshold=alphathreshold,
                chromakey=options.chromakey) 
if __name__ == '__main__':
    main()

