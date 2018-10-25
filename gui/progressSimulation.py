#coding=utf-8
## @package progressSimulation
#  Questo modulo permette la creazione di una ProgressBar che si aggiorna in base ai progressi della simulazione
import sys
from PyQt4 import QtGui, QtCore, uic
sys.path.insert(0, "..")
from FuzzySimulator import *
from PyQt4 import QtTest
## La classe ProgressSimulation è una Dialog che permette di visualizzare lo stato della simulazione in forma di progress Bar
class ProgressSimulation(QtGui.QDialog):

    ## Metodo costruttore che permette di inizializzare i dati membro della classe
    # @param self puntatore all'oggetto
    def __init__(self):
        super(ProgressSimulation, self).__init__(None, QtCore.Qt.WindowStaysOnTopHint)
        uic.loadUi('ProgressSimulation.ui', self)
        self.setModal(True)
        
        ## Puntatore alla variabile di classe MyWindow del modulo maingui.py
        self.main_ref = None
        ## @var _main_ref
        
        ## Variabile booleana che stabilisce se è possibile chiudere la Dialog con la Progress Bar
        self.canClose = False
        ## @var _canClose

        ## Variabile intera che memorizza il valore attuale del progresso della simulazione
        self.currentValue = 0
        ## @var _canClose

        self.pb_simulation.setValue(0)
        self.label.setText('Simulation Progress')
        

    ## Metodo che permette di modificare il valore corrente della progress Bar
    # @param self puntatore all'oggetto
    # @param value valore da settare come valore corrente
    def onProgress(self, value):
    	self.currentValue = value
    	self.pb_simulation.setValue(self.currentValue)
    	if value == 100:
    		self.stop()

    ## Metodo che permette di far partire la progress Bar
    # @param self puntatore all'oggetto
    def start(self):
    	self.currentValue = 0
    	self.label.setText('Simulation Progress')
    	self.pb_simulation.setValue(self.currentValue)
    	self.show()
        #serve per dare tempo a PyQT di creare la dialog con successo
    	QtTest.QTest.qWait(200)
   	
    # Metodo che permette bloccare l'esecuzione della progress Bar
    # @param self puntatore all'oggetto
    def stop(self):
    	self.canClose = True
    	self.done(0)

    # Metodo della dialog a cui viene fatto override per permettere la chiusura della Dialog con la Progress Bar solo quando la simulazione è completata 
    # @param self puntatore all'oggetto
    # @param event evento chiusura

    def closeEvent(self, event):
        if self.canClose:
        	super(ProgressSimulation, self).closeEvent(event)
        	self.canClose = False
        	self.label.setText('Simulation Progress')
        	self.currentValue = 0
        else:
        	event.ignore()


