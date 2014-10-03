import sys
from PyQt4 import QtCore, QtGui, uic


class testDialog (QtGui.QDialog) :

	def __init__(self) :
		QtGui.QDialog.__init__(self)
		self.ui = uic.loadUi("testDialog.ui", self)

		
