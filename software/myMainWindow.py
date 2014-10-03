import sys
import pdb
from PyQt4 import QtCore, QtGui, uic
from myImage import *
from fullImWidget import *
from fullResImWidget import *
from testDialog import *
import time

class myMainWindow (QtGui.QMainWindow) :
    

    def __init__(self) :
        QtGui.QMainWindow.__init__(self)
        self.ui = uic.loadUi("uiMainWindow.ui", self)
        self.ui.actionInput_Image.triggered.connect (self.blippy)
        self.ui.actionDEM_File.triggered.connect (self.defDEM)
        self.ui.actionSet_Working_Directory.triggered.connect (self.setWorkdir)
        self.ui.plotDEMCB.stateChanged.connect (self.demPlotChanged)
        self.startCoords = QtCore.QPoint (0., 0.)
        
          
        self.ui.fullimWidget.newRect.connect(self.newFullResBox)
        self.ui.fullResWidget.fullResSize.connect (self.geomSize)
        self.ui.fullResWidget.profileDefined.connect (self.defineProfile)
        frsize = self.ui.fullResWidget.size()
        self.ui.fullimWidget.setFullResSize(frsize)
        self.ui.rawProfCB.currentIndexChanged[int].connect(self.profTypeCBIndex)
        self.ui.outBrowseButton.clicked.connect(self.browseOut)
        self.ui.saveFileButton.clicked.connect(self.writeOut)
        self.ui.radprofButton.clicked.connect (self.radprof)
        self.ui.outPrefixLE.setText ('/data/gridhost/harold/zeph0/results_full/test0')
        self.workdir = '/data/gridhost/harold/zeph0/results_full'
        self.cellsize = 1.
        self.plotDEMFlag = True ;
        
        
        #tDlg = testDialog(self)
        #tDlg.show()

    def setWorkdir (self) :
        self.workdir = QtGui.QFileDialog.getExistingDirectory (self, 'Working Directory')
                                                               
    def demPlotChanged (self):
        self.plotDEMFlag = self.plotDEMCB.isChecked()
        self.ui.plotWidget.demToggle (self.plotDEMFlag) 
 
    def defDEM (self) :
        self.demfile = QtGui.QFileDialog.getOpenFileName (self,'Open DEM') 
        self.myDEM = myImage (self.demfile)
        self.fullresDEM = self.myDEM.getFullRes(0,0,500,600)

    def browseOut(self) :
        ofile = QtGui.QFileDialog.getSaveFileName (self, 'Output Prefix Name', self.workdir)
        self.ui.outPrefixLE.setText (ofile)
        
    def profTypeCBIndex (self, val) :
        self.plotData (val) 
        
            
    def plotData (self, val) :
        if (val==0) :
            self.ui.plotWidget.setMyDataDEM (self.profArr, self.profArrDEM)
            self.ui.plotWidget.setLabels ("Pixel", "DN")
        elif (val ==1) :
            self.ui.plotWidget.setMyDataFFTDEM (self.fftFreq, self.magProf, self.magProfDEM)
            self.ui.plotWidget.setLabels ("Frequency", "Magnitude")
        else :
            self.ui.plotWidget.setMyDataDEM (self.profArrAuto, self.profDEMAuto)
            self.ui.plotWidget.setLabels ("Lag", "Correlation")

    

        
    def blippy (self):
        print 'blippy'
        self.imfile = QtGui.QFileDialog.getOpenFileName(self, 'Open image', self.workdir)
        print self.imfile
        self.myim = myImage (self.imfile)
        self.fullres = self.myim.getFullRes(0,0, 500,600)
        self.ui.fullimWidget.writeQImage(self.myim.fulldata)
        self.ui.fullResWidget.writeQImage (self.fullres)

    def loadImage (self,imfile):
        self.myim = myImage (imfile)
        self.fullres = self.myim.getFullRes(0,0, 500,600)
        self.ui.fullimWidget.writeQImage(self.myim.fulldata)
        self.ui.fullResWidget.writeQImage (self.fullres)

    def loadDEM (self,demfile):
        self.myDEM = myImage (demfile)
        self.fullresDEM = self.myDEM.getFullRes(0,0,500,600)
    

    def newFullResBox (self, newbox) :
        self.fullres = self.myim.getFullResRect (newbox)
        self.ui.fullResWidget.writeQImage (self.fullres)
        self.startCoords = newbox.topLeft()
    
    def geomSize (self, size) :
        print 'resize'
        print size
        self.ui.fullimWidget.setFullResSize(size)

    def defineProfile (self, startPt, stopPt) :
        startPt += self.startCoords
        stopPt += self.startCoords
        #self.xystart.append (startPt)
        #self.xystop.append (stopPt)
        self.dist = sqrt(pow(startPt.x() - stopPt.x(),2) + pow(startPt.y() - stopPt.y(),2))
        print 'Profile distance is : ', self.dist
        self.angle = atan2 (float(stopPt.x() - startPt.x()),float(startPt.y() - stopPt.y()))*180./pi
        print 'Profile orientation is :', self.angle
        self.profArr = self.myim.getProfile (startPt, stopPt)
        self.profArrDEM = self.myDEM.getProfile (startPt, stopPt)
        self.nptsProf = len (self.profArr)
        
            
        #for i in range (10):
        #   print profArr[i]
        #self.ui.plotWidget.setMyData(profArr)
        
        #self.ui.plotWidget.setMyDataDEM (self.profArr, self.profArrDEM)
        self.fftProfiles()
        self.autoCorr () 
        self.plotData (self.ui.rawProfCB.currentIndex())
        outstring = "Start Point (x y) : %d %d\r\n"%(self.myim.locations[0,0], self.myim.locations[0,1])
        tstring = outstring
        print self.nptsProf
        outstring = "Stop Point (x y) : %d %d\r\n"%(self.myim.locations[self.nptsProf-1,0], self.myim.locations[self.nptsProf-1,1])
        tstring += outstring
        outstring = "Profile orientation (azimuth degrees) : %f\r\n"%(self.angle)
        tstring += outstring
        outstring = "Profile length (pixels) : %f\r\n"%(self.dist)
        tstring += outstring
        self.ui.resultsWindowText.clear()
        self.ui.resultsWindowText.setText (tstring)

    def fftProfiles (self):
        # zero mean the profile
        npts = len(self.profArr)
        xvals = np.arange(npts)
        # get the third order poly fit
        p0 = np.polyfit (xvals, self.profArr, 3)
        yf = np.polyval (p0, xvals)
        temp = self.profArr - yf
        self.magProf = np.abs(np.fft.fft (temp))/ npts
        self.fftFreq = np.zeros (npts)
        for i in range(npts) :
            self.fftFreq[i]=float(i)/float(npts * self.cellsize)

        
        # get the third order poly fit
        p0DEM = np.polyfit (xvals, self.profArrDEM, 3)
        yf = np.polyval (p0DEM, xvals)
        temp = self.profArrDEM - yf
        self.magProfDEM = np.abs(np.fft.fft (temp))

    def autoCorr (self) :
        a0 = self.profArr - self.profArr.mean()
        
        self.profArrAuto = self.autoCorrArray(self.profArr)
        self.profDEMAuto = self.autoCorrArray(self.profArrDEM)
        
    def autoCorrArray (self, arr) :
        arr0 = arr-arr.mean()
        temp = np.correlate (arr0, arr0, mode='full')
        temp = temp[temp.size/2:]/temp[temp.size/2]
        return temp


    def writeOut (self) :
        self.outFilePrefix = self.outPrefixLE.text()
        if (len(self.outFilePrefix) < 2) :
            self.outFile = QtGui.QFileDialog.getOpenFileName (self, "Output Prefix", self.workdir)
        outfile = self.outFilePrefix+'_prof.txt'
        print 'writing to ', outfile
        npts = len(self.profArr)
        nptsFFT = len (self.magProfDEM)
        f = open (outfile, 'w')

        outstring = "X Y DN Elev Corr(DN) Corr(Elev) Freq FFT-Mag FFT-Mag-DEM\r\n"
        f.write (outstring)
        for i in range(npts) :
            if (i <= nptsFFT) :
                outstring = "%d %d %f %f %f %f %f %f %f\r\n"%(self.myim.locations[i,0],self.myim.locations[i,1],
                    self.profArr[i], self.profArrDEM[i], self.profArrAuto[i], self.profDEMAuto[i], self.fftFreq[i], self.magProf[i], self.magProfDEM[i])
            else :
                outstring = "%d %d %f %f %f %f\r\n"%(self.myim.locations[i,0],self.myim.locations[i,1],
                    self.profArr[i], self.profArrDEM[i], self.profArrAuto[i], self.profDEMAuto[i])
            f.write (outstring)
        f.close()

        
        outfile = self.outFilePrefix+'_params.txt'
        outfileJpg = self.outFilePrefix+'_fullimg.jpg'
        outfilePlot = self.outFilePrefix+'_raw_Profplot.jpg'
        print 'writing to ', outfile
        try :
            f0 = open (outfile, 'w')
            outstring = "Start Point (x y) : %d %d\r\n"%(self.myim.locations[0,0], self.myim.locations[0,1])
            tstring = outstring
            print outstring
            f0.write (outstring)
            print self.nptsProf
            outstring = "Stop Point (x y) : %d %d\r\n"%(self.myim.locations[self.nptsProf-1,0], self.myim.locations[self.nptsProf-1,1])
            tstring += outstring
            print outstring
            f0.write (outstring)
            outstring = "Profile orientation (azimuth degrees) : %f\r\n"%(self.angle)
            tstring += outstring
            print outstring
            f0.write (outstring)
            outstring = "Profile length (pixels) : %f\r\n"%(self.dist)
            tstring += outstring
            print outstring
            f0.write (outstring)
            f0.close ()
            self.ui.resultsWindowText.clear()
            self.ui.resultsWindowText.setText (tstring)
            mypixmap = QtGui.QPixmap.grabWidget (self.ui.fullResWidget)
            
            print 'writing to file', outfilePlot
            mypixmap.save (outfileJpg)
            self.plotData(0)
            time.sleep(2)
            myPlotPixmap = QtGui.QPixmap.grabWidget (self.ui.plotWidget)
            myPlotPixmap.save (outfilePlot)
            self.plotData(1)
            time.sleep(2)
            outfilePlot = self.outFilePrefix+'_fft_Profplot.jpg'
            myPlotPixmap = QtGui.QPixmap.grabWidget (self.ui.plotWidget)
            myPlotPixmap.save (outfilePlot)
            self.plotData(2)
            time.sleep(2)
            outfilePlot = self.outFilePrefix+'_acorr_Profplot.jpg'
            myPlotPixmap = QtGui.QPixmap.grabWidget (self.ui.plotWidget)
            myPlotPixmap.save (outfilePlot)
            
            
            print 'done'
            #self.ui.plotWidget.grab().save(outfilePlot)
            #self.ui.fullResWidget.grab().save(outfileJpg) 
            print tstring
            
        except IOError :
            print 'problem with file write'


    def radprof (self) :
        xcent = 1062
        ycent = 4650
        dist = 100
        i = 0
        xang = np.zeros (90, dtype=float)
        xcorr = np.zeros (90, dtype=float)
        for iang in range (0, 120,2) :
            radprof = self.ui.myim.getProfileAngle (xcent, ycent, iang, dist)
            acorr = self.autoCorrArray (radprof)
            maxloc = np.max (acorr[14:])
            xang [i] = iang
            xcorr [i] = maxloc
            #print iang, maxloc
            i = i+1
        self.ui.plotWidget.setMyData (xcorr)
        
            
app = QtGui.QApplication(sys.argv)
mainWindow = myMainWindow()
mainWindow.show()
print sys.argv[0]
if (len(sys.argv) >2) :
    infile = sys.argv[1]
    demfile = sys.argv[2]

    mainWindow.loadImage (infile)
    mainWindow.loadDEM (demfile)
sys.exit(app.exec_()) 


