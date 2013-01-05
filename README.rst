pysixel
=======

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

Command line tool::

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

Code Example
------------

::

    import sixel
    writer = sixel.SixelWriter()
    writer.draw('test.png') 

Dependency
----------
 - Python Imaging Library (PIL)
   http://www.pythonware.com/products/pil/ 

Reference
---------
 - Chris_F_Chiesa, 1990 : All About SIXELs
   ftp://ftp.cs.utk.edu/pub/shuford/terminal/all_about_sixels.txt

 - Netpbm http://netpbm.sourceforge.net/

   It includes ppmtosixel command
   http://netpbm.sourceforge.net/doc/ppmtosixel.html

 - vt100.net http://vt100.net/

