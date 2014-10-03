from PyQt4 import QtCore, QtGui
import PyQt4.Qwt5 as qwt
import numpy as np


class myProfilePlot (qwt.QwtPlot):

    def __init__(self, *args) :
        qwt.QwtPlot.__init__(self, *args)
        self.setCanvasBackground(QtGui.QColor("white"))
        self.plotLayout().setMargin(20)
        self.plotLayout().setCanvasMargin(0)
        self.enableAxis(qwt.QwtPlot.yRight, True)
        #self.setTitle("helllo")
        #self.yRight.setTitle("Elevation(m)")
        
        self.curve = qwt.QwtPlotCurve ("Selected Profile")
        self.curveDEM = qwt.QwtPlotCurve("Selected DEM Profile")
        self.curveDEM.setYAxis (qwt.QwtPlot.yRight)
        self.curve.attach(self)
        self.curveDEM.attach (self)
        self.curveDEM.setPen (QtGui.QPen (QtGui.QColor("red")))
        self.picker = qwt.QwtPlotPicker(qwt.QwtPlot.xBottom, qwt.QwtPlot.yLeft,
            qwt.QwtPicker.PointSelection, qwt.QwtPlotPicker.CrossRubberBand,
            qwt.QwtPicker.AlwaysOn, self.canvas())

        self.demFlag = True 
        self.updateLayout()
        self.replot()

    def setLabels (self, xlabel, ylabel):
        self.setAxisTitle (qwt.QwtPlot.xBottom, xlabel)
        self.setAxisTitle (qwt.QwtPlot.yLeft, ylabel)
        
    def demToggle (self, dFlag):
        if (dFlag == False) :
            self.demFlag = False
            self.curveDEM.detach()
        if (dFlag == True) :
            self.demFlag = True
            self.curveDEM.attach (self)
        self.replot()

    def setMyData (self, indata):
        npts = indata.shape[0]
        x = np.arange (npts)
        self.curve.setData (x, indata)
        self.replot()
         

    def setMyDataFFTDEM (self, xdata, indata, indataDEM) :
        npts = indata.shape[0]/2
        x = np.arange (npts)
        self.curve.setData (xdata[0:npts], indata[0:npts])
        self.curveDEM.setData (xdata[0:npts], indataDEM[0:npts])
        self.updateLayout()
        self.replot()

    def setMyDataDEM (self, indata, indataDEM) :
        npts = indata.shape[0]
        x = np.arange (npts)
        self.curve.setData (x, indata)
        self.curveDEM.setData (x, indataDEM)
        self.updateLayout()
        self.replot()

    def mousePressEvent (self, event):
	
	xloc = self.invTransform (qwt.QwtPlot.xBottom, event.pos().x())
	yloc = self.invTransform (qwt.QwtPlot.yLeft, event.y())
	print xloc, yloc
        
