from PyQt4 import QtCore, QtGui
import numpy as np
from math import *

class fullImWidget(QtGui.QWidget) :

    newRect = QtCore.pyqtSignal(QtCore.QRect)
    
    def __init__(self, parent) :
        QtGui.QWidget.__init__(self, parent)
        self.loadImage = 0
        self.clicked = False
        self.boxRect = QtCore.QRect (0,0,500/10,400/10)
        self.dragBox = False
        self.pscale=5
        
        
    def setImage (self, qim) :
        self.qimage = qim
        self.loadImage = 1
        print 'image should be loaded'
        self.repaint()

    def mousePressEvent (self, event) :
        xloc = event.x()
        yloc = event.y()
        startPt = self.boxRect.topLeft()
        dist = sqrt(pow(xloc - startPt.x(),2.) + pow(yloc-startPt.y(),2.)) 
        if (dist < 20) :
            self.dragBox = True
            
    def mouseReleaseEvent (self, event) :
        if (self.dragBox) :
            self.dragBox = False ;

    def mouseMoveEvent (self,event) :
        if (self.dragBox) :
            mpos = event.pos()
            newx = mpos.x() + self.fullSize.width()/self.pscale
            newy = mpos.y() + self.fullSize.height()/self.pscale
            newpos = QtCore.QPoint(newx,newy)
            self.boxRect.setTopLeft (event.pos())
            self.boxRect.setBottomRight (newpos)
            print self.pscale
            print self.boxRect
            mpos *= self.pscale
            newpos *= self.pscale
            newRectArg = QtCore.QRect (mpos, newpos)
            self.newRect.emit (newRectArg)
            self.repaint()

    def setFullResSize (self, fsize) :
        self.fullSize = fsize 

    def paintEvent (self, event) :
        w = self.width()
        h = self.height()
        painter = QtGui.QPainter(self) 
        p = QtGui.QPen (QtGui.QColor (0,255,255))
        painter.setPen (p)
        painter.drawLine (0., 0, w-1, 0)
        painter.drawLine (w-1, 0, w-1, h-1)
        painter.drawLine (w-1, h-1, 0, h-1)
        painter.drawLine (0., h-1, 0, 0)
        print w, h
        if (self.loadImage==1) :
            print 'drawing'
            painter.drawImage (0, 0, self.qimage, 0.,0., w, h) 
            # draw box for fullres window
            p = QtGui.QPen (QtGui.QColor (0255,255,0))
            painter.setPen (p)
            painter.drawRect (self.boxRect)
            


    def writeQImage (self, fulldata) :
        self.xsize = self.width()
        self.ysize = self.height()
        self.fulldata = fulldata
        tempdata = self.fulldata
        tempdata[tempdata<0.]=0.5
        h,w = self.fulldata.shape
        self.min = np.min(tempdata)
        
        self.max = np.max (tempdata)
        self.scale = 255. / (self.max - self.min)
        print self.min, self.max
        print self.scale
        xscale = int(w / self.xsize)
        yscale = int(h / self.ysize)
        self.pscale = xscale
        if (yscale > self.pscale) :
            self.pscale = yscale
        
        
        uarr = (self.scale * (self.fulldata - self.min)).astype(np.uint8)
        
        print uarr.shape
        uarr = uarr[::self.pscale,::self.pscale]
        a = np.zeros((uarr.shape[0],uarr.shape[1],4),dtype=np.uint8)
        a[:,:,3]=255
        a[:,:,2]=uarr[:,:]
        a[:,:,1]=uarr[:,:]
        a[:,:,0]=uarr[:,:]
        
        self.qimage = QtGui.QImage (a.data,a.shape[1],a.shape[0], QtGui.QImage.Format_ARGB32) 
        self.qimage.ndarray = a
        self.loadImage = 1
        self.repaint()
