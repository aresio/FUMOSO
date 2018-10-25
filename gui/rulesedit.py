#coding=utf-8
## @package rulesedit
#  Questo modulo permette la visualizzazione di regole con la classe Rules e la creazione di regole sulle variabili linguistiche con la classe RulesEdit
import sys
from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from FuzzySimulator import *


## La classe RulesEdit è una Dialog che permette di creare nuove regole sulle variabili linguistiche create in precedenza
class RulesEdit(QtGui.QDialog):

    ## Metodo costruttore che permette di inizializzare i dati membro della classe
    # Collega segnali agli slot corrispondenti

    # @param self puntatore all'oggetto
    def __init__(self):
        super(RulesEdit, self).__init__(None, QtCore.Qt.WindowStaysOnTopHint)
        uic.loadUi('editRules.ui', self)
        
        ## Puntatore alla variabile di classe MyWindow del modulo maingui.py
        self.main_ref = None
        ## @var _main_ref

        ## Copia locale di tutte le variabili linguistiche
        self.listNodes = []
        ## @var _self.listNodes
        
        ## Nodo selezionato nella comboBox di variabile linguistica di OUT
        self.currentNode = ''
        ## @var _self.currentNode
        
        ## Variabile intera che stabilisce il numero di antecedenti nella regola
        self.numbers = 0
        ## @var _self.numbers

        ## Variabile intera che stabilisce in che posizione dovranno essere inseriti i nuovi widget
        self.index = 4
        ## @var _self.index

        ## Lista di stringhe che contiene la regola da aggiungere in forma di lista di stringhe
        self.arrayRule =['IF', 'nodo', 'IS', 'valore'] 
        ## @var _self.arrayRule
        
        ## Lista di stringhe che contiene la seconda parte della regola
        self.then = ['THEN','nodo', 'IS', 'valore'] 
        ## @var _self.then
        
        ## Dizionario che contiene, nel caso di regole con più di un antecedente, gli antecedenti dopo il primo
        self.dictComplessRule = {}
        ## @var _self.dictComplessRule
        
        self.btn_add.clicked.connect(self.addWidgets)
        self.cb_nodes.currentIndexChanged.connect(self.cbChange)
        #self.cb_node1.currentIndexChanged.connect(self.updateVariables)
        self.cb_node1.currentIndexChanged.connect(self.deleteAllPlusWidgets)
        
        self.cb_variable1.currentIndexChanged.connect(self.varChange)
        self.cb_varResult.currentIndexChanged.connect(self.varChange)
        self.btn_confirm.clicked.connect(self.addRule)
        

    ## Metodo costruttore che permette di visualizzare nella label la regola da inserire nel sistema
    # @param self puntatore all'oggetto
    def printRule(self):
        #compone la stringa e la visualizza nella label lbl_result
        string = ''
        c = 0
        for i in self.arrayRule:
            #se 
            if c < self.index:
                string = string + i + ' '
            c = c +1

        for i in self.then:
            string = string + i + ' '

        self.lbl_result.setText(string)

    ## Metodo che aggiorna il valore di antecedente e conseguente a seguito delle modifiche
    # @param self puntatore all'oggetto
    def varChange(self):
        self.arrayRule[3] = str(self.cb_variable1.currentText())
        self.then[1] = str(self.cb_nodes.currentText())
        self.then[3] = str(self.cb_varResult.currentText())
        self.printRule()
        

    ## Metodo che aggiorna la lista delle varaibili linguistiche disponibili
    # @param self puntatore all'oggetto
    # @param lista lista di variabili linguistiche da aggiungere alle comboBox
    def updateListNodes(self, lista):
        self.listNodes = lista[:]
        self.cb_node1.clear()
        self.cb_node1.addItems(lista[:])
        
        self.cb_variable1.clear()
        nodeToDelete = str(self.cb_node1.currentText())
        for key_lin, adjective in self.main_ref.CDS.fuzzySystem.variables[nodeToDelete].adjectives.items():
            self.cb_variable1.addItem(str(key_lin))
        
        #elimino nodo selezionato dalla lista
        lista.remove(nodeToDelete)
        self.cb_nodes.clear()
        self.cb_nodes.addItems(lista)
        self.cb_varResult.clear()

        nodename = str(self.cb_nodes.currentText())
        for key_lin, adjective in self.main_ref.CDS.fuzzySystem.variables[nodename].adjectives.items():
            self.cb_varResult.addItem(str(key_lin))
        
        #copio lista con nodo in meno
        
        self.currentNode = nodename        
        self.then[1] = self.currentNode
        self.then[3] = str(self.cb_varResult.currentText())

    ## Metodo che rimuove tutti widgets aggiunti, si riporta a situazione di unico antecedente
    # @param self puntatore all'oggetto
    def deleteAllPlusWidgets(self):
        if self.numbers > 0:
            indexDelete = self.index +1
        else:
            indexDelete = self.index
        for i in reversed(range(4,indexDelete)):
            self.h1.itemAt(i).widget().setParent(None)
            self.index = self.index -1
        self.numbers = 0
        self.index = 4

        self.updateVariables()

        
    ## Metodo che permette di aggiornare il valore di antecedente singolo e conseguente a seguito di modifiche
    ## Il metodo carica la lista degli aggettivi disponibili definiti sulla membership della varaibili linguistica definita come antecedente
    # @param self puntatore all'oggetto
    def updateVariables(self):
        nodename = str(self.cb_node1.currentText())
       
        if nodename != '':
            self.cb_variable1.clear()
            #carico 
            for key_lin, adjective in self.main_ref.CDS.fuzzySystem.variables[nodename].adjectives.items():
                self.cb_variable1.addItem(str(key_lin))

            self.cb_nodes.clear()
            copyList = self.listNodes[:]
            copyList.remove(nodename)
            self.cb_nodes.addItems(copyList)
            self.cb_varResult.clear()

            nodename = str(self.cb_nodes.currentText())
            for key_lin, adjective in self.main_ref.CDS.fuzzySystem.variables[nodename].adjectives.items():
                self.cb_varResult.addItem(str(key_lin))

            self.arrayRule[1] = str(self.cb_node1.currentText())
            self.arrayRule[3] = str(self.cb_variable1.currentText())
            self.then[1] = str(self.cb_nodes.currentText())
            self.then[3] = str(self.cb_varResult.currentText())
        
            self.printRule()

    ## Metodo che permette di recuperare la lista degli aggettivi disponibili definiti sulla membership della varaibili linguistica passata
    # @param self puntatore all'oggetto
    # @param nodename variabili linguistica
    # @return lista degli aggettivi disponibili nella membership del nodo passato
    def updateVariablesPlus(self, nodename):
        listAdj = []
        for key_lin, adjective in self.main_ref.CDS.fuzzySystem.variables[nodename].adjectives.items():
            listAdj.append(str(key_lin))
        return listAdj


    ## Metodo che aggiunge elementi grafici allo scopo di permettere l'inserimento di regole con più antecedenti
    # I nuovi elementi grafici vengono collegati
    # @param self puntatore all'oggetto
    def addWidgets(self):
    	
        #creazione label AND
        lbl_and = QtGui.QLabel("AND", self)
        
    	#creazione combo con lista di variabili linguistiche disponibili
    	combo2 = QtGui.QComboBox(self)
        copyList = self.listNodes[:]
        copyList.remove(str(self.cb_node1.currentText()))
        combo2.addItems(copyList)

        #creo un nome univoco
        combo2.setObjectName('comboNodes%d' % (self.numbers +1))
        
        #aggiunto al dizionario nome-valore corrente selezionato
        self.dictComplessRule[str(combo2.objectName())] = str(combo2.currentText())
        
        #creazione label IS
    	lbl = QtGui.QLabel("IS", self)
        
        #creazione combo con lista di aggettivi disponibili per la variabile correntemente selezionata
        combo3 = QtGui.QComboBox(self)
        combo3.addItems(self.updateVariablesPlus(str(combo2.currentText())))
        combo3.setObjectName('comboVariables%d' % (self.numbers +1))
        combo3.currentIndexChanged.connect(self.changeValue)

        #aggiunto al dizionario nome-valore corrente selezionato
        self.dictComplessRule[str(combo3.objectName())] = str(combo3.currentText())

        #Quando cambia l'indice corrente nella combo delle variabili linguistiche, bisogna aggiornare quella degli aggettivi
        combo2.currentIndexChanged.connect(lambda: self.cbChange2(combo2, combo3))

        #aggiunta al layout
        self.h1.insertWidget(self.index,lbl_and)
        self.index = self.index +1
        self.h1.insertWidget(self.index,combo2)
        self.index = self.index +1
        self.h1.insertWidget(self.index,lbl)
        self.index = self.index +1
        self.h1.insertWidget(self.index,combo3)
        self.index = self.index +1
        
        #aggiuta del bottone delete, solo se precedentemente non era stato già aggiunto
        if self.numbers == 0:
            btn = QtGui.QPushButton('', self)
            btn.setIcon(QIcon("minus.png"));
            btn.setIconSize(QSize(16,16));
            btn.clicked.connect(self.deleteLastAntecedent)
            self.h1.insertWidget(self.index,btn)
        
        #incremento del numero di antecedenti oltre il primo
        self.numbers = self.numbers +1
        
        #aggiroanmento lista di stringhe che contiene la regola completa
        self.arrayRule.append('AND')
        self.arrayRule.append(combo2.currentText())
        self.arrayRule.append('IS')
        self.arrayRule.append(combo3.currentText())
        
        #stampa la regola a schermo nella sua label
        self.printRule()

    ## Metodo che rimuove l'ultima clausola AND inserita
    # Rimuove gli elementi grafici e aggiorna la regola risultante a schermo
    # @param self puntatore all'oggetto
    def deleteLastAntecedent(self):
    	#eliminazione dell'elemento grafico
    	for i in reversed(range(self.index -4,self.index)):
    		self.h1.itemAt(i).widget().setParent(None)
    		self.index = self.index -1

        #se rimane solo il primo antecedente elimina anche bottone delete
    	if self.numbers == 1:
    		self.h1.itemAt(self.index).widget().setParent(None)
    	self.numbers = self.numbers -1

        self.printRule()
    	
    
    ## Metodo che permette di aggiornare la comboBox degli aggettivi in corrispondenza del nodo selezionato
    # @param self puntatore all'oggetto
    def cbChange(self):
        self.cb_varResult.clear()
        nodename = str(self.cb_nodes.currentText())
        if nodename != '':
            for key_lin, adjective in self.main_ref.CDS.fuzzySystem.variables[nodename].adjectives.items():
                self.cb_varResult.addItem(str(key_lin))

            self.currentNode = nodename
        self.varChange()

    ## Metodo che permette di aggiornare la comboBox degli aggettivi in corrispondenza del nodo selezionato 
    # @param self puntatore all'oggetto
    # @param comboNodes il nome della combo_box delle varaibili linguistiche che è stato modificata
    # @param comboAdj il nome della combo_box degli aggettivi che è da modificare 
    def cbChange2(self, comboNodes, comboAdj):
        nodename = str(comboNodes.currentText())
        comboAdj.clear()
        comboAdj.addItems(self.updateVariablesPlus(nodename))
        self.changeValue()

    ## Metodo che permette di aggiornare la variabile membro arrayRule con i dati correnti dal secondo antecedente in poi
    # @param self puntatore all'oggetto
    def changeValue(self):
        sending_button = self.sender()
        self.dictComplessRule[str(sending_button.objectName())] = str(sending_button.currentText())
        
        i = 4
        for k in range(1, self.numbers +1):
            self.arrayRule[i] = 'AND'
            i = i +1

            key = 'comboNodes' + str(k)
            self.arrayRule[i] = self.dictComplessRule[key]
            i= i + 1
            
            self.arrayRule[i] = 'IS'
            i= i + 1
            
            key = 'comboVariables' + str(k)
            self.arrayRule[i] = self.dictComplessRule[key]
            i= i + 1

        self.printRule()

    ## Metodo che permette di recuperare il numero successivo all'ultima regola definita per quella variabile linguistica
    # @param self puntatore all'oggetto
    # @return numero intero usabile per memorizzare la regola sulla variabile linguistica corrente
    def getRuleNumber(self):
        num = -1
        for r in self.main_ref.CDS.fuzzySystem.rules:
            if self.currentNode + '_rules.' in r:
                number =r.split(self.currentNode + '_rules.')[1]
                if num < int(number):
                    num = int(number)
        num = num +1
        return num

    ## Metodo che permette di aggiungere la regola al sistema, peremtte l'aggiunta di regole con uno o più antecedenti
    # @param self puntatore all'oggetto
    def addRule(self):
        
        #numero della regoa su quel nodo
        num = self.getRuleNumber()

        #una regola è una fuzzy.Rule.Rule(ad, op) ha due parametri:
        #adj ovvero l'aggettivo della varaibile linguistica selezionata come conseguente (OUT)
        #op è un operatore che può essere Input se regola semplice 
        #op è Compound se regola presenta più antecedenti
        
        if self.index == 4:
            #Regola con singolo antecedente
            adj= None
            op = None

            #estraggo Adj ovvero antecedente
            nodeInput = str(self.cb_node1.currentText())
            for value in self.main_ref.CDS.fuzzySystem.variables[nodeInput].adjectives.items():
                if value[0] == self.cb_variable1.currentText():
                    adj = value[1]

            #operator se singolo
            #<fuzzy.operator.Input.Input object at 0x7f32b2ed1610>
            #ha adjective

            #creazione dell'operatore
            op = fuzzy.operator.Input.Input(adj)

            #va cercato sull OUT altrimenti non va bene
            for value in self.main_ref.CDS.fuzzySystem.variables[str(self.currentNode+"OUT")].adjectives.items():
                if value[0] == self.cb_varResult.currentText():
                    ad = [value[1]]
        
            #Creazione regola
            a = fuzzy.Rule.Rule(ad, op)

            #Aggiunta al dizioanrio delle regole
            self.main_ref.CDS.fuzzySystem.rules[unicode(self.currentNode+"_rules."+str(num))] = a
        else:
            
            #se composto
            #<fuzzy.operator.Compound.Compound object at 0x7f32b2ed1a90>

            #recupero tutti i nodi antecedenti
            #recupero tutti i valori corrisponddenti dei nodi
            nodesInput = [str(self.cb_node1.currentText())]
            vareInput = [str(self.cb_variable1.currentText())]
            
            #dall'indice 5 in poi perchè ho elementi aggiunti a run time  
            k = 5
            for i in range(self.numbers, self.numbers +1):
                nodesInput.append(str(self.arrayRule[k*i]))
                vareInput.append(str(self.arrayRule[k*i +2]))

            #creo una lista di oggetti di tipo input, ogni oggetto input è creato da adjective selezionata 
            op = None
            norm = None
            inputs = []
            c = 0
            for node in nodesInput:
                for value in self.main_ref.CDS.fuzzySystem.variables[node].adjectives.items():
                    if value[0] == vareInput[c]:
                        inputs.append(fuzzy.operator.Input.Input(value[1]))
                        c = c + 1
                        break
                
            #lo vuole il simulatore, li crea in questo modo
            norm = fuzzy.norm.Min.Min()

            #creazione oggetto compound
            compound = fuzzy.operator.Compound.Compound(norm,None)
            compound.inputs = tuple(inputs)

            #va cercato sull OUT altrimenti non va bene
            for value in self.main_ref.CDS.fuzzySystem.variables[str(self.currentNode+"OUT")].adjectives.items():
                if value[0] == self.cb_varResult.currentText():
                    ad = [value[1]]

            #creazioen regola
            a = fuzzy.Rule.Rule(ad, compound)

            #aggiunta regola al dizionario
            self.main_ref.CDS.fuzzySystem.rules[unicode(self.currentNode+"_rules."+str(num))] = a
        
        #aggioranmento simulazione
        self.toReplot = self.main_ref.deplot()
        self.toReplotGroups = self.main_ref.deplotGroups()

        #self.main_ref.progressSimulation.start()
        self.main_ref.saveOnFile()
        self.main_ref.actualFUMLoad('prova')

        self.main_ref.replot(self.toReplot)
        self.main_ref.replotGroups(self.toReplotGroups)


## La classe Rules è una Dialog che permette di visualizzare le regole presenti nel sistema
class Rules(QtGui.QMainWindow):

    ## Metodo costruttore che permette di inizializzare i dati membro della classe
    def __init__(self):
        super(Rules, self).__init__(None, QtCore.Qt.WindowStaysOnTopHint)

        #carica il corrispondente ui
        uic.loadUi('Rules.ui', self)

        ## Puntatore alla variabile di classe MyWindow del modulo maingui.py
        self.main_ref = None
        ## @var _main_ref

        ## Progress bar per indicare lo stato di creazione dei grafici
        self.pb = QtGui.QProgressBar()
         ## @var _pb

        #aggiunta al layout
        self.statusBar().addWidget(self.pb)
        self.pb.setValue(0)
        self.pb.hide()


        # context menu for rule picture saving
        self.ruleDisplay.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ruleDisplay.customContextMenuRequested.connect(self.popup_save_rule)

        # create canvas for rule display
        # rulesviewer -> ruleDisplay -> vbox -> rules_canvas
        vbox = QtGui.QVBoxLayout()        
        self.ruleDisplay.setLayout(vbox)
      
    ## Metodo che crea il popup per salvare le immagini delle regole
    def popup_save_rule(self, pos):
        menu = QtGui.QMenu()
        quitAction = menu.addAction("&Save figure...")
        
        # action = menu.exec_(self.mapToGlobal(QtGui.QCursor.pos()))
        action = menu.exec_(QtGui.QCursor.pos())
        if action == quitAction:
            outputfile = QtGui.QFileDialog.getSaveFileName(self, "Please choose a destination file", "", "Portable Network Graphics (*.png)")
            outputfile = str(outputfile)
            if outputfile != None:
                self.save_figure_rule(outputfile)

    