from PyQt4 import QtCore, QtGui
import numpy as np
from scipy import ndimage


class fullResImWidget(QtGui.QWidget) :

    fullResSize = QtCore.pyqtSignal(QtCore.QSize)
    profileDefined = QtCore.pyqtSignal(QtCore.QPoint, QtCore.QPoint)
    
    def __init__(self, parent) :
        QtGui.QWidget.__init__(self, parent)
        self.loadImage = 0
        self.fullResSize.emit(self.size())
        self.profDefined = False
        self.numPtsClick = 0
        self.xystart = list() ;
        self.xystop = list() ;
        
        

    def setImage (self, qim) :
        self.qimage = qim
        self.loadImage = 1
        print 'image should be loaded'
        self.repaint()


    def paintEvent (self, event) :
        nprofiles = len (self.xystart) - 1
        print 'number of profiles ', nprofiles
        self.fullResSize.emit(self.size())  
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
            p = QtGui.QPen (QtGui.QColor (255, 0,0))
            painter.setPen (p)
            print 'drawing'
            painter.drawImage (0, 0, self.qimage, 0.,0., w, h)
            for i in range (nprofiles) :
                print self.xystart[i]
                painter.drawLine (self.xystart[i], self.xystop[i]) 
            if (self.numPtsClick==1) :
                p = QtGui.QPen (QtGui.QColor (255,255,0))
                painter.setPen (p)
                painter.drawLine (self.startPoint, self.endPoint)
            if (self.profDefined==1) :
                p = QtGui.QPen (QtGui.QColor (0,255,0))
                painter.setPen (p)
                painter.drawLine (self.startPoint, self.endPoint)
            

    def resizeEvent (self, event) :
        sz = event.size()
        self.fullResSize.emit(sz) 
            
    def mousePressEvent (self, event) :
        if (self.numPtsClick ==0) :
            self.startPoint = event.pos()
            self.endPoint = event.pos()
            self.numPtsClick = 1
            self.profDefined = False
            
        print 'xy location clicked :', event.pos()

    def mouseMoveEvent (self, event) :
        if (self.numPtsClick ==1) :
            self.endPoint = event.pos()
            self.repaint()

    def mouseReleaseEvent (self,event) :
        if (self.numPtsClick ==1) :
            self.endPoint = event.pos()
            self.numPtsClick = 0
            self.profDefined = True
            self.profileDefined.emit (self.startPoint, self.endPoint)
            self.xystart.append (self.startPoint)
            self.xystop.append (self.endPoint)
            self.repaint() 

    def writeQImage (self, fulldata) :
        self.xstart = list()  
        self.ystart = list()
        self.xsize = self.width()
        self.ysize = self.height()
        wt = np.zeros ((5,5))+1./25.
        smooth = ndimage.convolve (fulldata, wt)
        self.fulldata = 1.5 * fulldata - smooth 
        tempdata = self.fulldata
        tempdata [tempdata<0.]=0.5
        h,w = self.fulldata.shape
        print 'fulldata shape is ',self.fulldata.shape
        self.min = np.min(tempdata)
        #self.min = 0. 
        self.max = np.max (tempdata)
        self.scale = 255. / (self.max - self.min)

        xscale = int(w / self.xsize)
        yscale = int(h / self.ysize)
        self.pscale = xscale
        if (yscale > self.pscale) :
            self.pscale = yscale
        self.pscale=1
        
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
