#coding=utf-
## @package aboutFumoso
#  Questo modulo permette di visualizzare le informazioni dell'applicazione Fumoso
import sys
from PyQt4 import QtGui, QtCore, uic
sys.path.insert(0, "..")

## La classe rappresenta una Dialog che contiene le informazioni e il logo dell'applicazione FUMOSO
class AboutFumoso(QtGui.QDialog):

    def __init__(self):
        super(AboutFumoso, self).__init__(None, QtCore.Qt.WindowStaysOnTopHint)
        uic.loadUi('about.ui', self)