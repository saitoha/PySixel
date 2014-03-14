pysixel
=======

What is SIXEL?
--------------

.. image:: http://zuse.jp/misc/sixel_gnuplot.png
   :width: 640

SIXEL is one of image formats for terminal imaging introduced by DEC VT series.
SIXEL image data scheme is represented as a terminal-friendly escape sequence.
So if you want to show a SIXEL image file, all you have to do is "cat" it to your terminal. 

.. image:: http://zuse.jp/misc/sixel_hikari.png
   :width: 640

I heard SIXEL was supported by some old terminal applications, such as SAS, WordPerfect.

Nowadays netpbm and Gnuplot support this.

.. image:: http://zuse.jp/misc/sixel_ls.png
   :width: 640


Requirements
------------

If you want to view a SIXEL image, you have to get a terminal
which support sixel graphics.

Now SIXEL feature is supported by the following terminals.

- RLogin (Japanese terminal emulator)

  http://nanno.dip.jp/softlib/man/rlogin/

- tanasinn (Works with firefox)

  http://zuse.jp/tanasinn/

- mlterm

  Works on each of X, win32/cygwin, framebuffer version.
  http://mlterm.sourceforge.net/

- XTerm (compiled with --enable-sixel option)
  You should launch xterm with "-ti 340" option.
  the SIXEL palette is limited to a maximum of 16 colors.
  http://invisible-island.net/xterm/

- DECterm

- Kermit

- WRQ Reflection

- ZSTEM


Install
-------

via github ::

    $ git clone https://github.com/saitoha/PySixel.git
    $ cd pysixel 
    $ python setup.py install

or via pip ::

    $ pip install PySixel 


Usage
-----

PySixel provides a Command line tool::

    $ sixelconv [options] filename

or ::

    $ cat filename | sixelconv [options]


* Options::

  -h, --help                                            show this help message and exit
  -8, --8bit-mode                                       Generate a sixel image for 8bit terminal or printer
  -7, --7bit-mode                                       Generate a sixel image for 7bit terminal or printer
  -r, --relative-position                               Treat specified position as relative one
  -a, --absolute-position                               Treat specified position as absolute one
  -x LEFT, --left=LEFT                                  Left position in cell size, or pixel size with unit 'px'
  -y TOP, --top=TOP                                     Top position in cell size, or pixel size with unit 'px'
  -w WIDTH, --width=WIDTH                               Width in cell size, or pixel size with unit 'px'
  -e HEIGHT, --height=HEIGHT                            Height in cell size, or pixel size with unit 'px'
  -t ALPHATHRESHOLD, --alpha-threshold=ALPHATHRESHOLD   Alpha threshold for PNG-to-SIXEL image conversion
  -c, --chromakey                                       Enable auto chroma key processing
  -n NCOLOR, --ncolor=NCOLOR                            Specify number of colors
  -b, --body-only                                       Output sixel without header and DCS envelope
  -f, --fast                                            The speed priority mode (default)
  -s, --size                                            The size priority mode


Example
-------

View an image file::

    $ sixelconv test.png

Generate sixel file from an image file::

    $ sixelconv < test.png > test.six

View generated sixel file::

    $ cat test.six

Show sixel in xterm ::

	$ curl ftp://invisible-island.net/xterm/xterm-301.tgz | tar xz
	$ cd xterm-301
	$ ./configure --enable-wide-chars --enable-sixel-graphics --enable-256-color
	$ make
	# make install
	$ xterm -ti vt340 -e 'sixelconv -n16 ~/testdir/test.jpg'


Code Example
------------

::

    import sixel
    writer = sixel.SixelWriter()
    writer.draw('test.png') 

Dependency
----------
 - Pillow
   https://github.com/python-imaging/Pillow

 - Python imageloader module 
   https://pypi.python.org/pypi/imageloader

Reference
---------
 - Chris_F_Chiesa, 1990 : All About SIXELs
   ftp://ftp.cs.utk.edu/pub/shuford/terminal/all_about_sixels.txt

 - Netpbm http://netpbm.sourceforge.net/

   It includes ppmtosixel command
   http://netpbm.sourceforge.net/doc/ppmtosixel.html

 - vt100.net http://vt100.net/

