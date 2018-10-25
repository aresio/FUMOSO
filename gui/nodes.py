#coding=utf-8
## @package nodes
#  Questo modulo permette la gestione delle variabili linguistiche in FUMOSO.

import sys
from PyQt4 import QtGui, QtCore, uic
sys.path.insert(0, "..")
from FuzzySimulator import *


## La classe Nodes è una Dialog che permette di creare/rimuovere/modificare variabili linguistiche.

class Nodes(QtGui.QDialog):
    

    ## Metodo costruttore che permette di inizializzare i dati membro della classe
    # Collega segnali agli slot corrispondenti

    # @param self puntatore all'oggetto
    def __init__(self):
        
        super(Nodes, self).__init__(None, QtCore.Qt.WindowStaysOnTopHint)
        uic.loadUi('nodeeditor.ui', self)

        ## Puntatore alla variabile di classe MyWindow del modulo maingui.py
        self.main_ref = None
        ## @var _main_ref
        
        self.btnEdit.setEnabled(False)
        self.btnRemove.setEnabled(False)
        self.btnSetMember.setEnabled(False)
        
        self.btnAdd.clicked.connect(self.addNode)
        self.btnEdit.clicked.connect(self.editNode)
        self.btnRemove.clicked.connect(self.removeNode)
        self.btnSetMember.clicked.connect(self.goToMembershipEditor)
        self.btnClear.clicked.connect(self.clearSelection)
        self.btnSelectAll.clicked.connect(self.selectAllNodes)
        self.listNodes.itemClicked.connect(self.ableButtons)

    ## Metodo per impostare non attivi i bottoni di modifica, rimozione, e membership
    # @param self puntatore all'oggetto
    def setConfiguration(self):
        self.btnEdit.setEnabled(False)
        self.btnRemove.setEnabled(False)
        self.btnSetMember.setEnabled(False)

    ## Metodo che permette di selezionare tutte le variabili linguistiche presenti nella lista
    # @param self puntatore all'oggetto
    def selectAllNodes(self):
        for x in xrange(self.listNodes.count()):
            self.listNodes.setItemSelected(self.listNodes.item(x), True)
        self.ableButtons()

    ## Metodo che permette di deselezionare tutte le variabili linguistiche presenti nella lista
    # @param self puntatore all'oggetto
    def clearSelection(self):
    	for x in xrange(self.listNodes.count()):
            self.listNodes.setItemSelected(self.listNodes.item(x), False)
        self.ableButtons()

    ## Metodo che permette di aggiornare la lista delle variabili linguistiche
    # @param self puntatore all'oggetto
    def refreshList(self):
        self.listNodes.clear()
        for key, variable in self.main_ref.CDS.fuzzySystem.variables.items():
                if isinstance(variable, fuzzy.InputVariable.InputVariable):
                    self.listNodes.addItem(key)
        self.listNodes.sortItems()

    ## Metodo che permette di selezionare la variabile linguistica, passata come parametro
    # @param nodename, variabile linguistica da selezionare
    def selectItem(self, nodename):
        index = 0
        for i in range(len(self.listNodes)):
            if self.listNodes.item(i).text() == nodename:
                index = i
                break 
        self.listNodes.setCurrentRow(index)

    ## Metodo che permette di stabilire se i bottoni debbano essere abilitati o meno
    # @param self puntatore all'oggetto
    def ableButtons(self):
    	
    	num = self.nodeSelected()
    	if num  == 1:
            self.btnEdit.setEnabled(True)
            self.btnRemove.setEnabled(True)
            self.btnSetMember.setEnabled(True)
        else:
        	self.btnEdit.setEnabled(False)
        	self.btnSetMember.setEnabled(False)
        	if num > 1:
        		self.btnRemove.setEnabled(True)
        	else:
        		self.btnRemove.setEnabled(False)

    ## Metodo che permette di recuperare una lista delle varibili linguistiche selezionate
    # @param self puntatore all'oggetto
    # @return lista delle variabili linguistiche selezionate
    def nodeSelected(self):
    	selectedIndex = [] 
    	for i in range(self.listNodes.count()):
    		if self.listNodes.isItemSelected(self.listNodes.item(i)):
    			selectedIndex.append(i)
    	return len(selectedIndex)

    ## Metodo che permette di raggiungere la Dialog MembershipEditor della variabile linguistica selezioanta 
    # @param self puntatore all'oggetto
    def goToMembershipEditor(self):
        nodename = self.listNodes.currentItem().text()
    	self.main_ref.openMembership_functions(nodename)

    
    ## Metodo che permette di aggiungere una variabile linguistica alla lista
    # @param self puntatore all'oggetto
    def addNode(self):
        nodename, ok = QtGui.QInputDialog.getText(self, 'New node', 'Enter the name of the node:')
        nodename = str(nodename)
        if ok:             
            if nodename not in self.main_ref.CDS.fuzzySystem.variables:
                #recupero plot da riplottare
                toReplot = self.main_ref.deplot()
                toReplotGroups = self.main_ref.deplotGroups()
                
                #creo variabile INPUT e variabile OUTPUT
                self.main_ref.CDS.fuzzySystem.variables[nodename] = fuzzy.InputVariable.InputVariable()
                self.main_ref.CDS.fuzzySystem.variables[nodename+'OUT'] = fuzzy.OutputVariable.OutputVariable()
                self.main_ref.CDS.fuzzySystem.variables[nodename].min = 0.0
                self.main_ref.CDS.fuzzySystem.variables[nodename].max = 1.0
                print "Node",nodename,"added"
                
                #aggiunta al gruppo all
                if 'All' in self.main_ref.relations.keys():
                    self.main_ref.relations['All'].append(nodename)

                #aggiunta initial condition default
                self.main_ref.conditions.addNodeStates([nodename, '1.0','',''])

                #aggiornamento lista elementi
                self.refreshList()

                #update initialcondition table
                self.main_ref.conditions.updateInitialCondition() 

                #seleziono il nondo appena inserito
                self.selectItem(nodename)

                
                #salvataggio su file
                #self.main_ref.progressSimulation.start()
                self.main_ref.saveOnFile()
                self.main_ref.actualFUMLoad('prova')

                self.ableButtons()
                self.main_ref.replot(toReplot)
                self.main_ref.replotGroups(toReplotGroups)

            else:
                #Messaggio di errore
                msg = QtGui.QMessageBox()
                msg.setIcon(QtGui.QMessageBox.Information)
                msg.setText('Node name ' + nodename + ' already exists!')
                msg.exec_()
                print "ERROR: node name already exists"

    #mio
    ## Metodo che permette di rimuovere il nodo selezionato
    # @param self puntatore all'oggetto
    def removeNode(self):
		
        #recupero plot da riplottare successivamente
        toReplot = self.main_ref.deplot()
        toReplotGroups = self.main_ref.deplotGroups()

        #per ogni nodo selezionato
        for SelectedItem in self.listNodes.selectedItems():
            nodename = str(SelectedItem.text())
            
            #rimozione delle regole che riguardano il nodo
            self.removeNodeInRules(nodename)

            #rimozione del nodo dalla lista delle variabili di input
            del self.main_ref.CDS.fuzzySystem.variables[nodename]
            print "Node",nodename,"removed"

            #rimozione del nodo dalla lista delle variabili di output se presente
            if nodename+'OUT' in self.main_ref.CDS.fuzzySystem.variables:
                del self.main_ref.CDS.fuzzySystem.variables[nodename +'OUT']
                print 'Node ',nodename+'OUT ','removed'


            #eliminare nodo da gruppi
            for x in self.main_ref.relations.keys():
                if nodename in self.main_ref.relations[x]:
                    index = self.main_ref.relations[x].index(nodename)
                    print 'elimino da gruppo: ',self.main_ref.relations[x][index]
                    del self.main_ref.relations[x][index]

            
            #elimino nodo da initial cond
            self.main_ref.conditions.removeNodeStates(nodename)
        

        #aggiornamento tabella dialog initial condition
        self.main_ref.conditions.updateInitialCondition()
        
        #aggiornamento lista dopo eliminazione nodi
        self.refreshList()
        self.ableButtons()
        
        #self.main_ref.progressSimulation.start()
        #salvataggio su file
        self.main_ref.saveOnFile()

        #rilancio lettura file, per aggiornamento plot
        
        self.main_ref.actualFUMLoad('prova')
        self.main_ref.replot(toReplot)
        self.main_ref.replotGroups(toReplotGroups)


    ## Metodo che permette di eliminare il nodo passato come parametro dalle regole in cui appare come antecedente o cosneguente
    # @param self puntatore all'oggetto
    # @param nodename variabile linguistica che vogliamo eliminare
    def removeNodeInRules(self, nodename):

        #elimina da regole del nodo(es: Attach_rules.0,Attach_rules.1 ...)
        self.main_ref.CDS.deleteRulesNode(nodename)

        #elimino regole dove il nodo è un antecedente
        # es: nodename = Attach, elimina regole in cui c'è if Attach is ..
        lr = self.main_ref.CDS.get_list_rules()
        for group, rules in  lr.items():
            toRemove = []
            lun = len(rules)
            for indice in range(lun):
                ant = self.main_ref.CDS.unpack_antecedents(rules[indice][1].operator)
                ant2 = []
                if isinstance(ant, list):
                    for i in ant:
                        if isinstance(i, list):
                            for k in i:
                                value = k.split(' IS')
                                ant2.append(value[0])
                        else:
                            value = i.split(' IS')
                            ant2.append(value[0])
                else:
                    value = ant.split(' IS')
                    ant2.append(value[0])

                if nodename in ant2:
                    print rules[indice],'da removed'
                    toRemove.append(rules[indice])

            self.main_ref.CDS.deleteRulesAntecedent(toRemove)

    ## Metodo che permette di modificare la variabile linguistica selezionata
    # @param self puntatore all'oggetto
    def editNode(self):
        nodename = str(self.listNodes.currentItem().text())
        newname, ok = QtGui.QInputDialog.getText(self, 'Edit node name', 'Enter a new name for '+nodename)
        newname = str(newname)
        if ok:            
            if newname not in self.main_ref.CDS.fuzzySystem.variables:
                
                #deplot dei vari plot aperti
                toReplot = self.main_ref.deplot()
                toReplotGroups = self.main_ref.deplotGroups()
                if nodename in toReplot:
                    toReplot.append(newname)

                old = self.main_ref.CDS.fuzzySystem.variables[nodename]
                self.main_ref.CDS.fuzzySystem.variables[newname] = old
                del self.main_ref.CDS.fuzzySystem.variables[nodename]

                if nodename+'OUT' in self.main_ref.CDS.fuzzySystem.variables:
                    oldOUT = self.main_ref.CDS.fuzzySystem.variables[nodename +'OUT']
                    self.main_ref.CDS.fuzzySystem.variables[newname +'OUT'] = oldOUT
                    del self.main_ref.CDS.fuzzySystem.variables[nodename +'OUT']

                #aggiornamento nomi nelle regole
                self.changeRule(nodename, newname)

                #aggiornemnto gruppi
                for x in self.main_ref.relations.keys():
                    if nodename in self.main_ref.relations[x]:
                        index = self.main_ref.relations[x].index(nodename)
                        print 'Modifico Gruppo: ',self.main_ref.relations[x][index]
                        self.main_ref.relations[x][index] = newname

                #aggiornamento initial condition
                self.main_ref.conditions.editNodeStates(nodename, newname)      
                    
                #aggiornamento lista nodi
                self.refreshList()

                self.main_ref.conditions.updateInitialCondition()
                
                #seleziono il nondo appena aggiornato
                self.selectItem(newname)
                
                #self.main_ref.progressSimulation.start()
                #salvataggio su file
                self.main_ref.saveOnFile()
                
                #rilancio lettura file, per aggiornamento plot
                self.main_ref.actualFUMLoad('prova')
                self.main_ref.replot(toReplot)
                self.main_ref.replotGroups(toReplotGroups)
                self.ableButtons()
         
            else:   
                msg = QtGui.QMessageBox()
                msg.setIcon(QtGui.QMessageBox.Information)
                msg.setText('Node name ' + newname +' already exists!')
                msg.exec_()
                print "ERROR:",newname,"node already exists"

    ## Metodo che permette di eliminare il nodo passato come parametro dalle regole in cui appare come antecedente o cosneguente
    # @param self puntatore all'oggetto
    # @param nodename variabile linguistica a cui vogliamo cambiare nome 
    # @param newname nuovo nome per la variabile linguistica 
    def changeRule(self, nodename, newname):
        #cambio dizionario regole
        toChange = []
        toChangeRule = []
        for r, value in self.main_ref.CDS.fuzzySystem.rules.items():
            if nodename + '_rules.' in r:
                valueSplit = r.split(nodename)
                newRule = newname + valueSplit[1]
                toChange.append(newRule)
                toChangeRule.append(value)
                del self.main_ref.CDS.fuzzySystem.rules[r]
                
        i = 0
        for x in toChange:
            self.main_ref.CDS.fuzzySystem.rules[x] = toChangeRule[i]
            i = i + 1
                
                

