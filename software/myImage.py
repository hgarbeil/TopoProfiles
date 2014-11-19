
from PyQt4 import QtCore, QtGui
import numpy as np
import re
import struct
from math import *

class myImage :
    def __init__(self, filename):
        self.hdrfile = filename+'.hdr'
        self.infile = filename
        
        
        self.dtype = 0
        self.readHeader ()
        self.readData()
        #self.writeQImage()

    def readHeader (self):
        f = open (self.hdrfile, 'r')
        for line in f :
            if re.search("samp",line) :
                numstr = re.split ('=', line)
                print 'samples:',numstr[1]
                self.ns = int(numstr[1])
            if re.search("lines",line) :
                numstr = re.split ('=', line)
                print 'lines :',numstr[1]
                self.nl = int(numstr[1])
            if re.search("bands",line) :
                numstr = re.split ('=', line)
                print 'bands :',numstr[1]
                self.nb = int(numstr[1])
            if re.search("data type",line) :
                numstr = re.split ('=', line)
                print 'data type :',numstr[1]
                self.dtype = int(numstr[1])
            

            
    def readData (self) :
        f = open (self.infile, 'r')
        if self.dtype == 1 :
            self.fulldata = np.fromfile (f, dtype=np.uint8).reshape(self.nl, self.ns)
            self.type = np.uint8
        if self.dtype == 2 :
            self.type= np.int16
            self.fulldata = np.fromfile (f, dtype=np.int16).reshape(self.nl, self.ns)
        if self.dtype == 4 :
            self.type = np.float32
            self.fulldata = np.fromfile (f, dtype=np.float32).reshape(self.nl, self.ns)
        

    def getProfile (self, startPt, stopPt):
        startx = startPt.x()
        starty = startPt.y()
        stopx = stopPt.x()
        stopy = stopPt.y()
        totalPts = int(sqrt (pow(startx-stopx,2)+ pow(starty-stopy,2))+1.)
        print totalPts,' in profile'
        profile = np.zeros (totalPts)
        self.locations = np.zeros((totalPts,2),dtype=np.float32)
        xinc = (stopx - startx) / float(totalPts)
        yinc = (stopy - starty) / float (totalPts)
        for i in range(totalPts) :
            xloc = int(startx + i * xinc + 0.5)
            yloc = int(starty + i * yinc + 0.5)
            self.locations[i,:]=xloc, yloc
            profile[i] = self.fulldata[yloc,xloc]
        
        return profile
            

    def writeQImage (self, fulldata) :
        h,w = self.fulldata.shape
        tempdata = self.fulldata
        tempdata [tempdata<0.] = 0.5
        self.min = np.min(self.tempdata)
        self.min = 0. 
        self.max = np.max (self.tempdata)
        self.scale = 255. / (self.max - self.min)
        
        uarr = (self.scale * (self.fulldata - self.min)).astype(np.uint8)
        print uarr.shape
        uarr = uarr[::4,::4]
        a = np.zeros((uarr.shape[0],uarr.shape[1],4),dtype=np.uint8)
        a[:,:,3]=255
        a[:,:,2]=uarr[:,:]
        a[:,:,1]=uarr[:,:]
        a[:,:,0]=uarr[:,:]
        
        self.qim = QtGui.QImage (a.data,a.shape[1],a.shape[0], QtGui.QImage.Format_ARGB32) 
        self.qim.ndarray = a


    def getFullRes (self, ss, sl, ns, nl):
        self.fullRes = np.zeros ((ns, nl), dtype=self.type)
        self.fullRes = self.fulldata [sl:sl+nl, ss:ss+ns]
        return self.fullRes

    def getFullResRect (self, newrect):
        tl = newrect.topLeft()
        br = newrect.bottomRight()
        
        ss = tl.x()
        es = br.x()
        sl = tl.y()
        el = br.y()
        self.fullRes = self.fulldata [sl:el, ss:es]
        return self.fullRes
        

    def getProfileAngle (self, cent_x, cent_y, angle, distance) :
        dist2 = distance / 2.
        idist = (int (distance))
        angrad = angle * pi / 180.
        
        startx = cent_x + sin (angrad) * dist2
        endx = cent_x - sin (angrad) * dist2
        starty = cent_y + cos(angrad) * dist2
        endy = cent_y - cos (angrad) * dist2

        
        xinc = (endx - startx) / distance
        yinc = (endy - starty) / distance
        print angrad, xinc, yinc
        profile = np.zeros (idist)

        for i in range (idist) :
            xloc = (int) (startx + xinc * i)
            yloc = (int) (starty + yinc * i)
            profile[i] = self.fulldata[yloc, xloc]
            #print xloc,yloc

        return profile 

        
        
