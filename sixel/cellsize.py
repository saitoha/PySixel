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
import os
import termios
import select


class CellSizeDetector:

    def __set_raw(self):
        fd = sys.stdin.fileno()
        backup = termios.tcgetattr(fd)
        try:
            new = termios.tcgetattr(fd)
            new[0] = 0  # c_iflag = 0
            new[3] = 0  # c_lflag = 0
            new[3] = new[3] & ~(termios.ECHO | termios.ICANON)
            termios.tcsetattr(fd, termios.TCSANOW, new)
        except Exception:
            termios.tcsetattr(fd, termios.TCSANOW, backup)
        return backup

    def __reset_raw(self, old):
        fd = sys.stdin.fileno()
        termios.tcsetattr(fd, termios.TCSAFLUSH, old)

    def __get_report(self, query):
        result = ''
        fd = sys.stdin.fileno()
        rfds = [fd]
        wfds = []
        xfds = []

        sys.stdout.write(query)
        sys.stdout.flush()

        rfd, wfd, xfd = select.select(rfds, wfds, xfds, 0.5)
        if rfd:
            result = os.read(fd, 1024)
            return result[:-1].split(';')[1:]
        return None

    def get_size(self):

        backup_termios = self.__set_raw()
        try:
            height, width = self.__get_report("\x1b[14t")
            row, column = self.__get_report("\x1b[18t")

            char_width = int(width) / int(column)
            char_height = int(height) / int(row)
        finally:
            self.__reset_raw(backup_termios)
        return char_width, char_height
