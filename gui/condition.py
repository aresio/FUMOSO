#coding=utf-8
## @package condition
#  Questo modulo permette la gestione delle condizioni iniziali delle variabili linguistiche
import sys
from PyQt4 import QtGui, QtCore, uic
sys.path.insert(0, "..")
from FuzzySimulator import *

## La classe Conditions è una Dialog che permette di visualizzare in forma tabellare e modificare le condizioni iniziali delle varaibili linguistiche
# E' possibile anche specificare una funzione che la varaibile linguistica deve seguire
class Conditions(QtGui.QDialog):


    ## Metodo costruttore che permette di inizializzare i dati membro della classe
    # @param self puntatore all'oggetto
    def __init__(self):
        super(Conditions, self).__init__(None, QtCore.Qt.WindowStaysOnTopHint)
        uic.loadUi('Conditions.ui', self)
        
        ## Puntatore alla variabile di classe MyWindow del modulo maingui.py
        self.main_ref = None
        ## @var _main_ref
        
        ## Lista che contiene le informazioni da visualizzare nella tabella.
        #E' una lista di liste formata da 4 elementi:
        #nome della variabile linguistica
        #valore iniziale
        #funzione custom
        #parametri per la funzione
        self.data_states = []
        ## @var _data_states

    ## Metodo che permette di salvare le modifiche che vengono effettuate nella tabella sulla variabile data_states
    # @param self puntatore all'oggetto
    def saveItemChanged(self):
        toReplot = self.main_ref.deplot()
        toReplotGroups = self.main_ref.deplotGroups()
    	model = self.tableView.model()
    	for row in range(len(self.data_states)):
    	    index = model.index(row,0)                                                            
            value = model.data(index).toString()
            self.data_states[row][1] = str(value)
            
            index = model.index(row,1)                                                            
            value = model.data(index).toString()
            self.data_states[row][2] = str(value)

            index = model.index(row,2)                                                            
            value = model.data(index).toString()
            self.data_states[row][3] = str(value)

        #fa partire la progressBar per vedere progressi simulazione
        self.main_ref.progressSimulation.start()
        self.main_ref.saveOnFile()
        self.main_ref.actualFUMLoad('prova')
        self.main_ref.replot(toReplot)
        self.main_ref.replotGroups(toReplotGroups)


    ## Metodo che dalla tabella riempita riesce a recuperare lo stato iniziale per la simulazione
    # @param self puntatore all'oggetto
    def generate_state(self):
        
        #recupera tabella
        model = self.tableView.model()  
        test = self.tableView.verticalHeader()
        
        #per ogni variabile nella tabella recupera il nome
        variables = []
        for row in xrange(model.rowCount()):
            variables.append(str(test.model().headerData(row, QtCore.Qt.Vertical).toString()))

        #svuota la varaibile state
        self.main_ref.CDS.state = {}

        #per ogni variabile nella tabella aggiunge al dizionario la coppia nodo-valoreIniziale

        for x in xrange(model.rowCount()):                      # x-esima riga del modello            
            index = model.index(x,0)                            # index = puntatore alla x-ma riga
            name = variables[x]                                 # name preso da get_list_input_variables
            value = float(model.data(index).toString())
            self.main_ref.CDS.state[name] = value            

        print " * State generated:", self.main_ref.CDS.state



    ## Metodo che permette di creare e o aggiornare la struttura della tabella e includere i dati presenti 
    # @param self puntatore all'oggetto
    def updateInitialCondition(self):
        print 'updateInitialCondition'
        data_length = len(self.data_states)
        self.data_states.sort(key=lambda x: x[0].upper())
        #print self.data_states

        model = QtGui.QStandardItemModel(data_length,2)        
        model.setHorizontalHeaderItem(0, QtGui.QStandardItem("Initial condition"))
        model.setHorizontalHeaderItem(1, QtGui.QStandardItem("Custom update function"))
        model.setHorizontalHeaderItem(2, QtGui.QStandardItem("Time intervals for custom update function"))
        
        self.tableView.setModel(model)
        #print self.data_states
        for i in range(data_length):
            model.setVerticalHeaderItem(i, QtGui.QStandardItem(self.data_states[i][0]))
            model.setItem(i,0, QtGui.QStandardItem(self.data_states[i][1]))
            model.setItem(i,1, QtGui.QStandardItem(self.data_states[i][2]))
            model.setItem(i,2, QtGui.QStandardItem(self.data_states[i][3]))

        self.tableView.resizeColumnsToContents()

    ## Metodo che permette di aggiungere alla variabile membro data_states l'item passato 
    # @param self puntatore all'oggetto
    # @param item lista da aggiungere alla lista data_states
    def addNodeStates(self, item):
    	self.data_states.append(item)

    ## Metodo che permette di rmuove dalla variabile membro data_states l'item passato 
    # @param self puntatore all'oggetto
    # @param item lista da rimuovere dalla lista data_states
    def removeNodeStates(self, item):
    	print 'removeNodeStates'
    	for i in range(len(self.data_states)):
            if item == self.data_states[i][0]:
                del self.data_states[i]
                break


    ## Metodo che ritorna la lunghezza della variabile data_states
    # @param self puntatore all'oggetto
    # @return la lunghezza della variabile data_states
    def lenListStateNodes(self):
    	return len(self.data_states)

    ## Metodo che permette di modificare il nome di una variabile linguistica
    # @param self puntatore all'oggetto
    # @param nodeName indica il vecchio nome della varaibile linguistica
    # @param newName indica il nuovo nome della varaibile linguistica
    def editNodeStates(self, nodeName, newName):
    	print 'editNodeStates'
    	for i in range(len(self.data_states)):
            if nodeName == self.data_states[i][0]:
            	self.data_states[i][0] = newName
            	break

    ## Metodo che svuota la lista membro data_states
    # @param self puntatore all'oggetto
    def clear(self):
    	self.data_states = []

    ## Metodo che permette di recuperare l'i-esimo elelemento della lista data_states
    # @param self puntatore all'oggetto
    # @param i indice intero per accedere all'i-esimo elemento
    # @return l'i-esimo elelemento della lista data_states
    def getItem(self, i):
    	return self.data_states[i]