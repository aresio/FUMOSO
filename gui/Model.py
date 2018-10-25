#coding=utf-8
## @package groups
#  Questo modulo permette la visione del modello in forma di grafo.
import sys
from PyQt4 import QtGui, QtCore, uic
sys.path.insert(0, "..")
from FuzzySimulator import *

## La classe Groups è una Dialog che permette di creare/rimuovere/modificare gruppi di variabili linguistiche.
class ViewModel(QtGui.QDialog):

    ## Metodo costruttore che permette di inizializzare i dati membro della classe
    # Collega segnali agli slot corrispondenti

    # @param self puntatore all'oggetto
    def __init__(self):
        super(ViewModel, self).__init__()
        uic.loadUi('model.ui', self)
         ## Puntatore alla variabile di classe MyWindow del modulo maingui.py
        self.main_ref = None
        self.lb_image.setScaledContents(True)
    
    def loadImage(self):
    	pixmap = QtGui.QPixmap('model2.png')
        pixmap2 = pixmap.scaled(self.width(),self.height())
        self.lb_image.setPixmap(pixmap)
        self.lb_image.show()