#!/usr/bin/env python2
#vim:fileencoding=utf8
import matplotlib
matplotlib.rcParams["backend"]="Agg"
import pylab as pl
import numpy as np
from cStringIO import StringIO
import sixel

def sixelfig():
    buf = StringIO()
    pl.savefig(buf)
    buf.seek(0)
    writer = sixel.SixelWriter()
    writer.draw(buf)

def main():
    pl.figure(figsize=(4,3))
    x = np.linspace(0,1,100)
    y = x**2
    pl.plot(x,y)
    sixelfig()
    pass

if __name__=="__main__":
    main()

