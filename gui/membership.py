#coding=utf-8
## @package membership
#  Questo modulo permette la gestione delle membership delle varaibili linguistiche e composto da due Classi: Membership e EditMember
import sys
from PyQt4 import QtGui, QtCore, uic
sys.path.insert(0, "..")
from FuzzySimulator import *


# matplotlib stuff
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import os

## La classe Membership è una Dialog che permette di visualizzare e di editare le membership delle variabili linguistiche
# E' possibile  creare, modificare, eliminare una o più aggettivi delle variabili linguistiche
class Membership(QtGui.QDialog):

    ## Metodo costruttore che permette di inizializzare i dati membro della classe
    # @param self puntatore all'oggetto
    def __init__(self):
        super(Membership, self).__init__(None, QtCore.Qt.WindowStaysOnTopHint)
        uic.loadUi('membershipeditor.ui', self)
        
        #finestra MODALE
        self.setModal(True)

        ## Puntatore alla variabile di classe MyWindow del modulo maingui.py
        self.main_ref = None
        ## @var _main_ref
        
        ## Variabile booleana che stabilisce se è la prima apertura della dialog o meno
        self.firstOpen = True
        ## @var _firstOpen
        
        ## Variabile booleana che stabilisce se ci sono state modifica da salvare e rilanciare simulazione
        self.changeSomething = False
        ## @var _changeSomething 
        
        ##lista di dizionari, dove ogni dizionario corrisponde ad un singolo aggettivo della variabile linguistica
        self.nodeVariables = []
        ## @var _nodeVariables

        ##Lista di booleani usata per verificare che i campi dell' aggettivo corrente siano accettabili
        self.checkList = [False, False, False, False, False, False, False, False, False]
        ## @var _checkList
        
        ##contiene i valori dei campi temporanei dell'aggetivo corrente prima che venga cliccato add
        self.values = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        ## @var _values

        ##lista di plot di Membership che saranno da riplottare dopo aver chiuso la Dialog Membership
        self.toReplot = None
        ## @var _toReplo

        ##lista di plot di Gruppi che saranno da riplottare dopo aver chiuso la Dialog Membership
        self.toReplotGroups = None
        ## @var _toReplotGroups

        #settaggio default bottoni
        self.btnAdd.setEnabled(False)
        self.btnEdit.setEnabled(False)
        self.btnDelete.setEnabled(False)
        self.btn_load2.setEnabled(False)
        self.btn_load3.setEnabled(False)

        #collegamenti segnali slot
        self.btnDelete.clicked.connect(self.removeItem)
        self.cbType.currentIndexChanged.connect(self.cbChange)
        self.btnAdd.clicked.connect(self.addItem)
        self.btnEdit.clicked.connect(self.editItem)
        self.node_box.activated.connect(self.updateLingset)
        self.leName.textChanged.connect(self.checkName)
        self.leX1.textChanged.connect(self.checkX1)
        self.leY1.textChanged.connect(self.checkY1)
        self.leX2.textChanged.connect(self.checkX2)
        self.leY2.textChanged.connect(self.checkY2)
        self.leX3.textChanged.connect(self.checkX3)
        self.leY3.textChanged.connect(self.checkY3)
        self.leX4.textChanged.connect(self.checkX4)
        self.leY4.textChanged.connect(self.checkY4)
        self.listItem.currentRowChanged.connect(self.ableEditDelete)
        self.btnSet.clicked.connect(self.setMaxMinValue)
        self.finished.connect(self.close)
        self.btn_load2.clicked.connect(lambda: self.addSample(2))
        self.btn_load3.clicked.connect(lambda: self.addSample(3))


    ## Metodo che permette di aggiungere 2 o 3 variabili linguistiche di default in base al valore passato
    # @param self puntatore all'oggetto
    # @param n numero di aggettivi di esempio da caricare
    def addSample(self, n):
        print 'aggiungo esempi'
        self.btn_load2.setEnabled(False)
        self.btn_load3.setEnabled(False)
        if n == 2:
            dictSample = {'Low':[(0.0,0.0),(0.0,1.0),(1.0,0.0)], 'High':[(0.0,0.0),(1.0,1.0),(1.0,0.0)]}
        else:
            dictSample = {'Low':[(0.0,0.0),(0.0,1.0),(1.0,0.0)], 'Medium':[(0.0,0.0),(0.5,1.0),(1.0,0.0)], 'High':[(0.0,0.0),(1.0,1.0),(1.0,0.0)]}

        i = 0
        for name, coords in dictSample.items():
            self.nodeVariables.append({'name' : name, 'type' : 'triangle', 'P1': [coords[0][0], coords[0][1]] , 'P2': [coords[1][0], coords[1][1]],  'P3': [coords[2][0], coords[2][1]], 'valid': True})
            a = fuzzy.Adjective.Adjective(Polygon(coords))
            a.set.points = coords
            self.main_ref.CDS.fuzzySystem.variables[self.nodename].adjectives[name] = a
            if self.nodename+'OUT' in self.main_ref.CDS.fuzzySystem.variables:
                b =fuzzy.Adjective.Adjective(Polygon(coords))
                b.set.points = coords
                self.main_ref.CDS.fuzzySystem.variables[self.nodename+'OUT'].adjectives[name] = b

            self.nodeVariables[i]['valid']= self.checkMinMaxAfterChange(i)
            i = i + 1

        #aggiroanmento file
        self.main_ref.saveOnFile()

        #aggironamento lista
        self.refresh()
             
    ## Metodo che permette recuperare i plot(Gruppi e Membership) da riplottare successivamente 
    # @param self puntatore all'oggetto
    def toReplotFun(self):
        self.toReplot = self.main_ref.deplot()
        self.toReplotGroups = self.main_ref.deplotGroups()

    ## Metodo che prima di chiudere riplotta i plot memorizzati nelle variabili membro self.toReplot e self.toReplotGroups
    # Inoltre rilancia la simulazione
    # @param self puntatore all'oggetto
    def close(self):
        if self.changeSomething:
            #self.main_ref.progressSimulation.start()
            self.main_ref.saveOnFile()
            self.changeSomething = False
            self.firstOpen = True
            self.main_ref.actualFUMLoad('prova')
        self.main_ref.replot(self.toReplot)
        self.main_ref.replotGroups(self.toReplotGroups)
    
    ## Metodo che permette di recuperare le coordinate dell'i-esimo aggettivo della variabile linguistica corrente
    # @param self puntatore all'oggetto
    # @param i i indice intero che farà riferimento all'i-esimo aggettivo del nodo corrente
    # @return lista di liste, dove le liste interne sono delle coppie con le coordinate [x, y]
    def getCoords(self, i):
    	coord = []
    	p = []
    	row = self.nodeVariables[i]
    	p.append(row['P1'][0])
    	p.append(row['P1'][1])
    	coord.append(p)
    	p = []
    	p.append(row['P2'][0])
    	p.append(row['P2'][1])
    	coord.append(p)
    	p = []
    	p.append(row['P3'][0])
    	p.append(row['P3'][1])
    	coord.append(p)
    	p = []
    	if row['type'] == 'Trapeze':
    		p.append(row['P4'][0])
    		p.append(row['P4'][1])
    		coord.append(p)
    	
    	return coord
    
    ## Metodo che permette di caricare tutti gli aggettivi relativi al nodo selezionato 
    def updateLingset(self):
        print 'updateLingset'

        #svuota gli elementi precedenti
        self.clear()
        self.listItem.clear()
        self.nodeVariables  = []
        self.checkList = [False, False, False, False, False, False, False, False, False]
        self.firstOpen = False
        
        #recupero nodo corrente
        self.nodename = str(self.node_box.currentText())

        #recupero minimo e massimo delle x della variabile linguistica
        self.universMin = self.main_ref.CDS.fuzzySystem.variables[self.nodename].min 
        self.universMax = self.main_ref.CDS.fuzzySystem.variables[self.nodename].max
        
        self.isShowed = True
        self.spMin.setValue(self.universMin)
        self.spMax.setValue(self.universMax)
        self.isShowed = False
        
        #creazione della lista di dizionari di aggettivi e informazioni relative
        i = 0
        for  key_lin, adjective in self.main_ref.CDS.fuzzySystem.variables[self.nodename].adjectives.items():
            print 'variabile: ' + str(key_lin)
            if isinstance(adjective, fuzzy.Adjective.Adjective):
                dict = {'name' : key_lin}
                coords = self.main_ref.CDS.fuzzySystem.variables[self.nodename].adjectives[key_lin].set.points
                if len(coords) == 3:
                	dict['type'] = 'Triangle'
                	dict['P1'] = [coords[0][0], coords[0][1]]
                	dict['P2'] = [coords[1][0], coords[1][1]]
                	dict['P3'] = [coords[2][0], coords[2][1]]
                else:
                	dict['type'] = 'Trapeze'
                	dict['P1'] = [coords[0][0], coords[0][1]]
                	dict['P2'] = [coords[1][0], coords[1][1]]
                	dict['P3'] = [coords[2][0], coords[2][1]]
                	dict['P4'] = [coords[3][0], coords[3][1]]

                #aggiunta del dizioanario alla variabile membro
                self.nodeVariables.append(dict)

                self.listItem.addItem(self.dicToString(i))
                
                self.nodeVariables[i]['valid']= self.checkMinMaxAfterChange(i)
                self.item = self.listItem.item(i)
                if self.nodeVariables[i]['valid']:
                	self.item.setTextColor(QtGui.QColor("black"))
                else:
                	self.item.setTextColor(QtGui.QColor("red"))

                i = i + 1

        #visualizza plot 
        self.showVariables()

        #verifica se è possibile caricare 2 o 3 esempi 
        self.ableDisableBtnSample()
    
    ## Metodo che permette di creare un plot degli aggettivi della variabile linguistica corrente 
    # Il grafico viene aggiornato in tempo reale, quindi visualizza le modifiche apportate dall'utente
    def showVariables(self):
        
        if self.isShowed:
        	return 

        if self.h1.count() > 0:
            #elimino plot vecchio
    	    self.h1.itemAt(0).widget().setParent(None)
    	    del self.theplot
    	    del self.figure
    	    del self.widget
    	    
        #creo nuovo plot
    	self.widget = QtGui.QWidget()
        #aggiungo una figura
        self.figure = plt.figure(figsize=(7,3), dpi=100)

        self.widget = FigureCanvas(self.figure)

        #aggiunge un subplot dove metteremo le nostre linee
        self.theplot = self.figure.add_subplot(111)
        
        #per ogni aggettivo verifica se è valido lo stampa
        for i in range(len(self.nodeVariables)):
           if self.nodeVariables[i]['valid'] == True:
               x,y = self.getPoints(i)
               self.theplot.plot(x, y, label = self.nodeVariables[i]['name'])
        
        #stampa punti inseriti del nuovo aggettivo che sto inserendo
        xTemp = []
        yTemp = []
        complete = True
        selezionato = self.cbType.currentText()
        finish = 0
        if selezionato == 'Triangle':
        	finish = 7
        else:
        	finish = 9

        #solo se la coppia del punto (xi, yi) è valida viene plottata
        for i in range(1,finish,2):
        	if self.checkList[i] and self.checkList[i +1]:
        		xTemp.append(self.values[i])
        		yTemp.append(self.values[i+1])

        	complete = complete and self.checkList[i]
        
        #se completo aggiungo il primo punto in modo da visualizzare la figura completa
        if complete:
        	xTemp.append(self.values[1])
        	yTemp.append(self.values[2])
        
        #visualizza i punti
        if xTemp != []:
            self.theplot.plot(xTemp, yTemp, marker='o', color='red', label='Current Points')

        #aggiunta della legenda
        self.theplot.legend()

        #aggiunta del widget al layout
        self.h1.addWidget(self.widget)
    

    ## Metodo che permette di recuperare le liste delle x, e delle y dell'i-esimo aggettivo della variabile linguistica corrente
    # @param self puntatore all'oggetto
    # @param i indice intero che farà riferimento all' i-esimo aggettivo del nodo corrente
    # @return lista di due liste, dove le 2 liste interne sono tutte le coordinate di x e y della figura
    def getPoints(self, i):
    	x = []
    	y = []
    	row = self.nodeVariables[i]
    	x.append(row['P1'][0])
    	y.append(row['P1'][1])
    	x.append(row['P2'][0])
    	y.append(row['P2'][1])
    	x.append(row['P3'][0])
    	y.append(row['P3'][1])
    	if row['type'] == 'Trapeze':
    	    x.append(row['P4'][0])
    	    y.append(row['P4'][1])
    	x.append(row['P1'][0])
    	y.append(row['P1'][1])
    	return [x, y]

    
    
    ## Metodo che setta nuovi valori di max/min e se necessario richiama aggiornamento plot
    # @param self puntatore all'oggetto
    def setMaxMinValue(self):
        string = ''
        show = False
        # c contattore di aggettivi che non sono validi
        c = 0
        self.universMin = self.spMin.value()
        self.universMax = self.spMax.value()
        self.changeSomething = True

        for i in range(len(self.nodeVariables)):
            beforeValid = self.nodeVariables[i]['valid']
            currentValid = self.checkMinMaxAfterChange(i)
            self.nodeVariables[i]['valid'] = currentValid
            if currentValid == False and currentValid == (not beforeValid):
                c = c + 1
                string = string + self.nodeVariables[i]['name'] + os.linesep
                self.item = self.listItem.item(i)
                self.item.setTextColor(QtGui.QColor("red"))
                show = True
            elif currentValid == True and currentValid == (not beforeValid):
                self.item = self.listItem.item(i)
                self.item.setTextColor(QtGui.QColor("black"))
                show = True

        self.main_ref.CDS.fuzzySystem.variables[self.nodename].min = self.universMin
        self.main_ref.CDS.fuzzySystem.variables[self.nodename].max = self.universMax

        #se ci sono modifica da visualizzare 
        if show:
            self.showVariables()
            #se ci sono aggettivo non più validi
            if c > 0:
                msg = QtGui.QMessageBox()
                msg.setIcon(QtGui.QMessageBox.Information)
                msg.setIcon(QtGui.QMessageBox.Information)
                msg.setText("These variables are not feasable: " + os.linesep + string)
                msg.exec_()
			


    

    ## Metodo che verifica se l'aggettivo index-esimo ha delle cooridante valide per il valori di min/max
    # @param self puntatore all'oggetto
    # @param index indice dell'index-esimo aggettivo
    # @return valore booleano di validità
    def checkMinMaxAfterChange(self, index):
    	#print 'checkMinMaxAfterChange'
    	x = []
    	row = self.nodeVariables[index]
    	x.append(row['P1'][0])
    	x.append(row['P2'][0])
    	x.append(row['P3'][0])
    	if row['type'] == 'Trapeze':
    	    x.append(row['P4'][0])

        for value in x:
        	if not(value <= self.universMax and value >= self.universMin):
				return False
        return True
        
    
    ## Metodo che verifica se il nome del nuov aggettivo index-esimo è valido
    # @param self puntatore all'oggetto
    def checkName(self):
    	#print 'checkName'
    	name = self.leName.text()
    	bool = True

        for i in range(len(self.nodeVariables)):
            nameb = str(self.nodeVariables[i]['name']).upper()
            if name.toUpper() == nameb or name == '':
    		    bool = False
        
        self.checkList[0] = bool
        self.ableDisableBtnAdd()

    ## Metodo che abilita l'inserimento delle coordinate del punto P4 solo per il trapezio
    # @param self puntatore all'oggetto
    def cbChange(self):
    	#print 'cbChange'
        selezionato = self.cbType.currentText()
        if selezionato == 'Triangle':
            self.leX4.setEnabled(False) 
            self.leY4.setEnabled(False)
            rangeChecked = range(0,7)
        else:
            self.leX4.setEnabled(True) 
            self.leY4.setEnabled(True)
            rangeChecked = range(len(self.checkList))

        check = True  
        for i in rangeChecked:
        	check = check and self.checkList[i]

        self.btnAdd.setEnabled(check)  
    
    
    ## Metodo che verifica validità della i-esima coordianta x
    # @param self puntatore all'oggetto
    # @param i indice della x che vogliamo verificare
    def generalCheckX(self, text, i):
    	#print 'generalCheckX'
    	bool = False
    	value, ok = text.toDouble()
        if ok and value >= self.universMin and value <= self.universMax: 
    		bool = True
    		self.values[i] = value
    		
    	self.checkList[i] = bool
    	if bool and self.checkList[i +1]:
    	    self.showVariables()
    	self.ableDisableBtnAdd()
    
    ## Metodo che verifica validità della i-esima coordianta y
    # @param self puntatore all'oggetto
    # @param i indice della y che vogliamo verificare
    def generalCheckY(self, text, i):
    	#print 'generalCheckY'
    	bool = False
    	value, ok = text.toDouble()
        if ok and value >= 0 and value <= 1:
    		bool = True
    		self.values[i] = value	
    		
    	self.checkList[i] = bool
    	if bool and self.checkList[i -1]:
    	    self.showVariables()
    	self.ableDisableBtnAdd()
    
    ## Metodo che permette di abilitare/disabilitare il bottone di aggiunta di un aggettivo
    # @param self puntatore all'oggetto
    def ableDisableBtnAdd(self):
    	#print 'ableDisableBtnAdd'
    	selected = self.cbType.currentText()
        rangeChecked = 0
        if(selected == 'Triangle'):
            rangeChecked = range(0, 7)
        else:
            rangeChecked = range(len(self.checkList))
        
        check = True  
        for i in rangeChecked:
        	check = check and self.checkList[i]

        self.btnAdd.setEnabled(check)
    
    ## Metodo che permette di abilitare/disabilitare il bottone di aggiunta degli esempi
    # @param self puntatore all'oggetto
    def ableDisableBtnSample(self):
        if self.listItem.count() == 0:
            self.btn_load2.setEnabled(True)
            self.btn_load3.setEnabled(True)
        else:
            self.btn_load2.setEnabled(False)
            self.btn_load3.setEnabled(False)


    ## Metodo che permette di verificare la X1
    # @param self puntatore all'oggetto
    def checkX1(self):
    	x1 = self.leX1.text()
    	self.generalCheckX(x1, 1)
    
    ## Metodo che permette di verificare la Y1
    # @param self puntatore all'oggetto
    def checkY1(self):
    	y1 = self.leY1.text()
    	self.generalCheckY(y1, 2)
    
    ## Metodo che permette di verificare la X2
    # @param self puntatore all'oggetto        
    def checkX2(self):
    	x2 = self.leX2.text()
        self.generalCheckX(x2, 3)
    
    ## Metodo che permette di verificare la Y"
    # @param self puntatore all'oggetto
    def checkY2(self):
    	y2 = self.leY2.text()
        self.generalCheckY(y2, 4)

    ## Metodo che permette di verificare la X3
    # @param self puntatore all'oggetto
    def checkX3(self):
    	x3 = self.leX3.text()
    	self.generalCheckX(x3, 5)
    
    ## Metodo che permette di verificare la Y3
    # @param self puntatore all'oggetto
    def checkY3(self):
    	y3 = self.leY3.text()
    	self.generalCheckY(y3, 6)
    
    ## Metodo che permette di verificare la X4
    # @param self puntatore all'oggetto
    def checkX4(self):
    	x4 = self.leX4.text()
    	self.generalCheckX(x4, 7)

    ## Metodo che permette di verificare la Y4
    # @param self puntatore all'oggetto
    def checkY4(self):
    	y4 = self.leY4.text()
    	self.generalCheckY(y4, 8)
    
    
    ## Metodo che permette di aggiungere un aggettivo alla variabili linguistica corrente
    # @param self puntatore all'oggetto
    def addItem(self):
        #i dati sono già stati validati
    	name = str(self.leName.text())
        selected = self.cbType.currentText()
        if selected == 'Trapeze':
            self.nodeVariables.append({'name' : name, 'type' : selected, 'P1': [self.values[1], self.values[2]] , 'P2': [self.values[3], self.values[4]], 'P3': [self.values[5], self.values[6]], 'P4': [self.values[7], self.values[8]], 'valid': True})
            self.listItem.addItem(self.dicToString(len(self.nodeVariables) -1))
        elif selected == 'Triangle':
            self.nodeVariables.append({'name' : name, 'type' : selected, 'P1': [self.values[1], self.values[2]] , 'P2': [self.values[3], self.values[4]], 'P3': [self.values[5], self.values[6]], 'valid': True})
            self.listItem.addItem(self.dicToString(len(self.nodeVariables) -1))
        
        self.item = self.listItem.item(len(self.nodeVariables) -1)
        self.item.setTextColor(QtGui.QColor("black"))
        self.changeSomething = True
        
        #aggiunta della nuova adjective al nodo input
        c = 0
        for i in range (len(self.nodeVariables)):
            if self.nodeVariables[i]['name'] == name:
                c = i
        
        coords = self.getCoords(c)
        a = fuzzy.Adjective.Adjective(Polygon(coords))
        a.set.points = coords

        #aggiunta della nuova adjective al nodo output se presente
        self.main_ref.CDS.fuzzySystem.variables[self.nodename].adjectives[name] = a
        if self.nodename+'OUT' in self.main_ref.CDS.fuzzySystem.variables:
            #ne creo una diversa perchè devono essere memorizzati come oggetti diversi
            b = fuzzy.Adjective.Adjective(Polygon(coords))
            b.set.points = coords
            self.main_ref.CDS.fuzzySystem.variables[self.nodename+'OUT'].adjectives[name] = b
            print "anche out"
        
        #salvataggio su file
        self.main_ref.saveOnFile()
        self.clear()

        #visulizzazione su plot
        self.showVariables()
        self.ableDisableBtnSample()
    
    ## Metodo che permette di ripulire i campi per aggiungere il nuovo aggettivo
    # @param self puntatore all'oggetto
    def clear(self):
    	#print 'clear'
    	self.values = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.checkList = [False, False, False, False, False, False, False, False, False]
        self.leName.setText('')
        self.leX1.setText('')
        self.leX2.setText('') 
        self.leX3.setText('') 
        self.leX4.setText('')  
        self.leY1.setText('')
        self.leY2.setText('') 
        self.leY3.setText('') 
        self.leY4.setText('')
        self.cbType.setCurrentIndex(0)
        self.leX4.setEnabled(False) 
        self.leY4.setEnabled(False) 
    
    ## Metodo che permette di convertire un aggettivo in stringa, per visualizzarla nella lista degli aggettivi
    # @param self puntatore all'oggetto
    # @param i indice dell' i-esimo aggettivo che vogliamo trasformare
    # @return ritorna l'aggettivo i-esimo in forma di stringa
    def dicToString(self, i):
    	#print 'dicToString'
        itemRow = self.nodeVariables[i]
        string =  itemRow['name'] + ': ' + itemRow['type'] + ' ' + '(' + str(itemRow['P1'][0]) +',' + str(itemRow['P1'][1]) +') ' 
        string =  string  + '(' + str(itemRow['P2'][0]) +',' + str(itemRow['P2'][1]) +') ' 
        string =  string  + '(' + str(itemRow['P3'][0]) +',' + str(itemRow['P3'][1]) +') ' 
        if itemRow['type'] == 'Trapeze':
            string =  string  + '(' + str(itemRow['P4'][0]) +',' + str(itemRow['P4'][1]) +') ' 
    	return string

    ## Metodo che permette di abilitare/disabilitare i bottoni delete e Edit
    # I bottono saranno abilitati solo nel caso in cui ci sia un elemento selezionato
    # @param self puntatore all'oggetto
    def ableEditDelete(self):
    	#print 'ableEditDelete'
    	if self.listItem.currentRow() >= 0:
            self.btnEdit.setEnabled(True)
            self.btnDelete.setEnabled(True)
        else:
        	self.btnEdit.setEnabled(False)
        	self.btnDelete.setEnabled(False)
    
    ## Metodo che permette di cancellare un aggettivo dalla lista e dalle variabili
    # @param self puntatore all'oggetto
    #funzione che rimuove elemento dalla lista delle variabili    
    def removeItem(self):
    	#elimino elemento in posizione corrente
        itemRow = self.listItem.currentRow()
        self.item = self.listItem.takeItem(itemRow)

        #rimozione adjective dalle regole sia come conseguente che antecedente
        stringToCheck = self.nodename +'OUT' + ' IS ' + self.nodeVariables[itemRow]['name']
        stringToCheckAnt = self.nodename + ' IS ' + self.nodeVariables[itemRow]['name']

        #rimozione di elemento dalle regole
        lr = self.main_ref.CDS.get_list_rules()
        ruleToDelete = []
        ruleToDelete2 = []
        for group, rules in  lr.items():
            for r in rules:
                if stringToCheck in self.main_ref.CDS.rule_to_string(r):
                    ruleToDelete.append(r[0])
                if stringToCheckAnt in self.main_ref.CDS.rule_to_string(r):
                    ruleToDelete2.append(r[0])
        
        #eliminazione concreta regola individuata
        for value in ruleToDelete2:
            del self.main_ref.CDS.fuzzySystem.rules[value]

        #eliminazione concreta individuata
        for value in ruleToDelete:
            del self.main_ref.CDS.fuzzySystem.rules[value]
                
        item = None

        
        name = self.nodeVariables[itemRow]['name']

        #eliminazione aggettivo dalla variabile del simulatore
        del self.main_ref.CDS.fuzzySystem.variables[self.nodename].adjectives[name]
        if self.nodename+'OUT' in self.main_ref.CDS.fuzzySystem.variables:
            #elimino anche da nodo di OUT se esiste
            del self.main_ref.CDS.fuzzySystem.variables[self.nodename+'OUT'].adjectives[name]
        
        #rimozione da variabile locale
        del self.nodeVariables[itemRow] 
        
        #salvataggio cambiamenti e visualizzazione
        self.changeSomething = True
        self.ableDisableBtnSample()
        self.main_ref.saveOnFile()
        self.showVariables()

    ## Metodo che permette di aprire una dialog di classe EditMember per la modifica di un aggettivo
    # @param self puntatore all'oggetto
    def editItem(self):
    	
        #recupero aggettivo corrente da editare
        itemRow = self.listItem.currentRow()
        #creo oggetto di classe EditMember passando i parametri
        self.editMember = EditMember(itemRow, self.nodeVariables, [self.universMin, self.universMax], self.nodename)
        self.editMember.finished.connect(self.refresh)
        self.editMember.main_ref = self.main_ref
        self.editMember.member = self
        self.editMember.exec_()

    ## Metodo che permette di aggiornare la lista delle variabili e il plot dopo le modifiche
    # @param self puntatore all'oggetto   
    def refresh(self):
    	#print 'refresh'
    	self.listItem.clear()
        for i in range(len(self.nodeVariables)):
        	self.listItem.addItem(self.dicToString(i))
        	self.item = self.listItem.item(i)
        	if self.nodeVariables[i]['valid']:
        	    self.item.setTextColor(QtGui.QColor("black"))
        	else:
        		self.item.setTextColor(QtGui.QColor("red"))
        self.changeSomething = True
        self.showVariables()

## La classe EditMember è una Dialog modale che permette la modifica dei parametri di un aggettivo
# E' possibile  rinominare, modificare punti e tipo dell'aggettivo
class EditMember(QtGui.QDialog):
    
    ## Metodo costruttore che permette di inizializzare i dati membro della classe
    # @param self puntatore all'oggetto   
    # @param i indice dell'i-esimo aggettivo che vogliamo editare 
    # @param variables la lista di dizionari  
    # @param limits una lista formata da minimo e massimo della variabile linguistica
    # @param nodename la variabile linguistica corrente

    def __init__(self, i, variables, limits, nodename):
        super(EditMember, self).__init__(None, QtCore.Qt.WindowStaysOnTopHint)
        uic.loadUi('memberEdit.ui', self)
        self.setModal(True)

        ## Puntatore alla variabile di classe MyWindow del modulo maingui.py
        self.main_ref = None
        ## @var _main_ref

        ##Lista di dizionari, dove ogni dizionario corrisponde ad un singolo aggettivo della variabile linguistica
        self.nodeVariables = variables
        ## @var _nodeVariables

        ##Lista di booleani usata per verificare che i campi dell' aggettivo corrente siano accettabili
        self.checkList = [False, False, False, False, False, False, False, False, False]
        ## @var _checkList

        ## Nome del nodo di cui stiamo modificando l'aggettivo
        self.nodename = nodename
        ## @var _nodename

        ## Lista che contiene i valori dei campi temporanei dell'aggetivo corrente 
        self.values = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        ## @var _values
        
        ## Puntatore alla variabile di classe Membership del modulo membership.py
        self.member = None 
        ## @var _member
        
        #variabile che contiene il valore minimo che una coordinata x di un punto può avere
        self.min = limits[0]
        ## @var _min

        #variabile che contiene il valore massimo che una coordinata x di un punto può avere
        self.max = limits[1]
        ## @var _max

        #collegamenti segnali slot
        self.cbType.currentIndexChanged.connect(self.cbChange)
        self.leName.textChanged.connect(self.checkName)
        self.leX1.textChanged.connect(self.checkX1)
        self.leY1.textChanged.connect(self.checkY1)
        self.leX2.textChanged.connect(self.checkX2)
        self.leY2.textChanged.connect(self.checkY2)
        self.leX3.textChanged.connect(self.checkX3)
        self.leY3.textChanged.connect(self.checkY3)
        self.leX4.textChanged.connect(self.checkX4)
        self.leY4.textChanged.connect(self.checkY4)
        self.btnCancel.clicked.connect(self.cancel)
        self.btnAdd.clicked.connect(self.updateAdj)

        #inserimento dati nelle lineEdit
        variable = self.nodeVariables[i]
        self.index = i
        self.leName.setText(variable['name'])
        self.leX1.setText(str(variable['P1'][0]))
        self.leY1.setText(str(variable['P1'][1]))
        self.leX2.setText(str(variable['P2'][0]))
        self.leY2.setText(str(variable['P2'][1]))
        self.leX3.setText(str(variable['P3'][0]))
        self.leY3.setText(str(variable['P3'][1]))
        
        if variable['type'] == 'Trapeze':
            self.cbType.setCurrentIndex(1)
            self.leX4.setText(str(variable['P4'][0]))
            self.leY4.setText(str(variable['P4'][1]))

    
    ## Metodo che permette di chiudere la finestra
    # @param self puntatore all'oggetto 
    def cancel(self):
    	self.done(0)

    ## Metodo che permette di terminare di modificare l'aggettivo corrente, se i campi sono accettabili
    # @param self puntatore all'oggetto
    def updateAdj(self):

        #vecchio aggettivo, mi memorizzo l' oggetto, perchè all'oggetto potrebbero essere legate delle regole!
        oldName = self.nodeVariables[self.index]['name']
        old = self.main_ref.CDS.fuzzySystem.variables[self.nodename].adjectives[oldName]

        #nuovo nome dell'aggetivo
        name = str(self.leName.text())
        
        #tipo dell'aggettivo
        selected = self.cbType.currentText()

        #aggioranemnto dizionario dell'aggettivo vecchio
        if selected == 'Trapeze' :
            self.nodeVariables[self.index] = {'name' : name, 'type' : selected, 'P1': [self.values[1], self.values[2]] , 'P2': [self.values[3], self.values[4]], 'P3': [self.values[5], self.values[6]], 'P4': [self.values[7], self.values[8]], 'valid': True}
        else:
            self.nodeVariables[self.index] = {'name' : name, 'type' : selected, 'P1': [self.values[1], self.values[2]] , 'P2': [self.values[3], self.values[4]], 'P3': [self.values[5], self.values[6]], 'valid': True}
        
        #eliminazione vecchio aggettivo
        del self.main_ref.CDS.fuzzySystem.variables[self.nodename].adjectives[oldName]
        
        #creazione nuove coordinate
        coords = self.member.getCoords(self.index)
        
        #utilizzo vecchio oggetto, in cui modifico solo le coordinate
        old.set = fuzzy.Adjective.Adjective(Polygon(coords))
        old.set.points = coords

        #aggioranemto dell'aggettivo sulla variabile 'globale'
        self.main_ref.CDS.fuzzySystem.variables[self.nodename].adjectives[name] = old
        
        #se c'è anche nodo di OUT faccio stesse operazioni
        if self.nodename+'OUT' in self.main_ref.CDS.fuzzySystem.variables:
            oldOUT = self.main_ref.CDS.fuzzySystem.variables[self.nodename +'OUT'].adjectives[oldName]
            del self.main_ref.CDS.fuzzySystem.variables[self.nodename + 'OUT'].adjectives[oldName]
            oldOUT.set = fuzzy.Adjective.Adjective(Polygon(coords))
            oldOUT.set.points = coords
            self.main_ref.CDS.fuzzySystem.variables[self.nodename + 'OUT'].adjectives[name] = oldOUT

        #print self.main_ref.CDS.fuzzySystem.variables[self.nodename].adjectives

        #salvataggio su file
        self.main_ref.saveOnFile()

        #chiusura finestra
        self.done(1)


    ## Metodo che verifica se il nuovo nome dell' aggettivo è valido
    # @param self puntatore all'oggetto
    def checkName(self):
    	name = self.leName.text()
    	bool = True
        #verifica che non ci siano doppioni nello stesso membership set
        for i in range(len(self.nodeVariables)):
        	if i != self.index:
                 nameb = str(self.nodeVariables[i]['name']).upper()
                 if name.toUpper() == nameb or name == '' :
    		        bool = False
        
        self.checkList[0] = bool
        self.ableDisableBtnAdd()
    
    ## Metodo che verifica se la coordinata dell'i-esima x è valida
    # @param self puntatore all'oggetto
    # @param text testo che viene inserito nella lineEdit corrispondente
    # @param i i-esimo punto 
    def generalCheckX(self, text, i):
    	bool = False
    	value, ok = text.toDouble()

        #verifica che sia un double e che stia nei limiti 
        if ok and value >= self.min and value <= self.max: 
    		bool = True
    		self.values[i] = value
    	self.checkList[i] = bool
    	self.ableDisableBtnAdd()
    
    ## Metodo che verifica se la coordinata dell'i-esima y è valida
    # @param self puntatore all'oggetto
    # @param text testo che viene inserito nella lineEdit corrispondente
    # @param i i-esimo punto 
    def generalCheckY(self, text, i):
    	bool = False
    	value, ok = text.toDouble()
        if ok and value >= 0 and value <= 1:
    		bool = True
    		self.values[i] = value
    	self.checkList[i] = bool
    	self.ableDisableBtnAdd()

    ## Metodo che abilita il bottone per la conferma della modifica solo se i dati sono corretti
    # @param self puntatore all'oggetto
    def ableDisableBtnAdd(self):
    	selected = self.cbType.currentText()
        rangeChecked = 0
        if(selected == 'Triangle'):
            rangeChecked = range(0, 7)
        else:
            rangeChecked = range(len(self.checkList))
        check = True  
        for i in rangeChecked:
        	check = check and self.checkList[i]
        self.btnAdd.setEnabled(check)

    ## Metodo che permette di verificare la X1
    # @param self puntatore all'oggetto
    def checkX1(self):
    	x1 = self.leX1.text()
    	self.generalCheckX(x1, 1)
    
    ## Metodo che permette di verificare la Y1
    # @param self puntatore all'oggetto
    def checkY1(self):
    	y1 = self.leY1.text()
    	self.generalCheckY(y1, 2)
    
    ## Metodo che permette di verificare la X2
    # @param self puntatore all'oggetto
    def checkX2(self):
    	x2 = self.leX2.text()
        self.generalCheckX(x2, 3)
    
    ## Metodo che permette di verificare la Y2
    # @param self puntatore all'oggetto
    def checkY2(self):
    	y2 = self.leY2.text()
        self.generalCheckY(y2, 4)

    ## Metodo che permette di verificare la X3
    # @param self puntatore all'oggetto
    def checkX3(self):
    	x3 = self.leX3.text()
    	self.generalCheckX(x3, 5)
    
    ## Metodo che permette di verificare la Y3
    # @param self puntatore all'oggetto
    def checkY3(self):
    	y3 = self.leY3.text()
    	self.generalCheckY(y3, 6)
    
    ## Metodo che permette di verificare la X4
    # @param self puntatore all'oggetto   
    def checkX4(self):
    	x4 = self.leX4.text()
    	self.generalCheckX(x4, 7)

    ## Metodo che permette di verificare la Y4
    # @param self puntatore all'oggetto
    def checkY4(self):
    	y4 = self.leY4.text()
    	self.generalCheckY(y4, 8)
    
    ## Metodo che abilita/disabilita le lineEdit del punto P4 in base al tipo di figura selezionata
    # @param self puntatore all'oggetto
    def cbChange(self):
        selezionato = self.cbType.currentText()
        if selezionato == 'Triangle':
            self.leX4.setEnabled(False) 
            self.leY4.setEnabled(False)
            rangeChecked = range(0,7)
        else:
            self.leX4.setEnabled(True) 
            self.leY4.setEnabled(True)
            rangeChecked = range(len(self.checkList))

        check = True  
        for i in rangeChecked:
        	check = check and self.checkList[i]

        self.btnAdd.setEnabled(check) 