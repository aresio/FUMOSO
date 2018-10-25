#coding=utf-8
## @package groups
#  Questo modulo permette la gestione di gruppi di variabili linguistiche per la visualizzazione dei grafici.
import sys
from PyQt4 import QtGui, QtCore, uic
sys.path.insert(0, "..")
from FuzzySimulator import *

## La classe Groups è una Dialog che permette di creare/rimuovere/modificare gruppi di variabili linguistiche.
class Groups(QtGui.QDialog):

    ## Metodo costruttore che permette di inizializzare i dati membro della classe
    # Collega segnali agli slot corrispondenti

    # @param self puntatore all'oggetto
    def __init__(self):
        super(Groups, self).__init__()
        uic.loadUi('Groups.ui', self)
        self.ref_model = None
         ## Puntatore alla variabile di classe MyWindow del modulo maingui.py
        self.main_ref = None
        ## @var _main_ref
        self.btn_remove.setEnabled(False)
        self.btn_rename.setEnabled(False)
        self.btn_selAll.setEnabled(False)
        self.btn_selNone.setEnabled(False)
        self.btn_selNone.clicked.connect(self.selectNoneRelations)
        self.btn_new.clicked.connect(self.addNewGroup)
        self.btn_remove.clicked.connect(self.removeGroup)
        self.btn_rename.clicked.connect(self.renameGroup)
        self.btn_selAll.clicked.connect(self.selectAllRelations)
        self.btn_selNone.clicked.connect(self.selectNoneRelations)
        self.listGroups.itemSelectionChanged.connect(self.updateGroupSublist)
        self.elementsListGroups.itemClicked.connect(self.updateRelations)
    
    ## Metodo per creare/aggiornare la lista dei gruppi memorizzata nella variabile relations del modulo maingui.py
    # @param self puntatore all'oggetto
    def populate_groups(self):
        self.listGroups.clear()
        for groupname in self.main_ref.relations.keys():
            self.listGroups.addItem(groupname)
        self.listGroups.sortItems()

    ## Metodo che crea la lista di checkbox di variabili aggiungibili ai vari gruppi
    # @param self puntatore all'oggetto
    def populate_groups_manager(self):
        self.elementsListGroups.clear()
        for n, v in enumerate(self.main_ref.CDS.get_list_input_variables()):
            checkBox = QtGui.QListWidgetItem()
            checkBox.setText(v)
            checkBox.setCheckState(QtCore.Qt.Unchecked)
            self.elementsListGroups.addItem(checkBox)
        self.elementsListGroups.sortItems()

    ## Metodo che disabilita bottoni di rimozione, rinomina, seleziona tutti e nessuno
    # @param self puntatore all'oggetto
    def setConfiguration(self):
        self.btn_remove.setEnabled(False)
        self.btn_rename.setEnabled(False)
        self.btn_selAll.setEnabled(False)
        self.btn_selNone.setEnabled(False)
        self.elementsListGroups.setEnabled(False)

    ## Metodo che permette di selezionare tutte le variabili linguistiche presenti nella lista d checbox
    # @param self puntatore all'oggetto
    def selectAllRelations(self):
        for x in xrange(self.elementsListGroups.count()):
            self.elementsListGroups.item(x).setCheckState(QtCore.Qt.Checked)
        self.updateRelations()

    ## Metodo che permette di deselezionare tutte le variabili linguistiche presenti nella lista d checbox
    # @param self puntatore all'oggetto
    def selectNoneRelations(self):
        for x in xrange(self.elementsListGroups.count()):
            self.elementsListGroups.item(x).setCheckState(QtCore.Qt.Unchecked)
        self.updateRelations()


    ## Metodo che permette di creare un nuovo gruppo
    # @param self puntatore all'oggetto
    def addNewGroup(self):
        groupname, ok = QtGui.QInputDialog.getText(self, 'Group name', 'Enter the name of the group:')    
        if ok:            
            if groupname != '' and groupname not in self.main_ref.relations.keys() :
                self.listGroups.addItem(str(groupname))
                self.main_ref.relations[str(groupname)]=[]
                self.listGroups.sortItems()
                currentIndex = 0
                for i in range(len(self.listGroups)):
                    if self.listGroups.item(i).text() == groupname:
                        currentIndex = i
                        break 
                self.listGroups.setCurrentRow(currentIndex)
                self.main_ref.update_groups()
                self.main_ref.saveOnFile()
            else:
                print "ERROR: group name already exists"

    ## Metodo che permette di eliminare un gruppo selezionato
    # @param self puntatore all'oggetto
    def removeGroup(self):
        groupname = str(self.listGroups.currentItem().text())
        
        row = self.listGroups.currentRow()
        self.listGroups.takeItem(row)
        if self.main_ref.scrollAreaWidgetGroups.layout().itemAt(row).widget().isChecked():
            self.main_ref.scrollAreaWidgetGroups.layout().itemAt(row).widget().setChecked(False)
            self.main_ref.display_group(groupname,self.main_ref.scrollAreaWidgetGroups.layout().itemAt(row).widget())

        
        del self.main_ref.relations[groupname]
        
        if self.listGroups.count() == 0:
            self.setConfiguration()
        self.main_ref.update_groups()
        self.main_ref.saveOnFile()


    ## Metodo che permette di rinominare un gruppo selezionato
    # @param self puntatore all'oggetto
    def renameGroup(self):
        oldgroupname =  str(self.listGroups.currentItem().text())
        index = self.listGroups.currentRow()
        newgroupname, ok = QtGui.QInputDialog.getText(self, 'Group name', 'Enter the new name of the group' + oldgroupname +':') 
        refresh = False   
        if ok:            
            if newgroupname != '' and newgroupname not in self.main_ref.relations.keys() :
                #aggiorno relations
                if self.main_ref.scrollAreaWidgetGroups.layout().itemAt(index).widget().isChecked():
                    refresh = True
                    self.main_ref.scrollAreaWidgetGroups.layout().itemAt(index).widget().setChecked(False)
                    self.main_ref.display_group(oldgroupname,self.main_ref.scrollAreaWidgetGroups.layout().itemAt(index).widget())
                
                copy = self.main_ref.relations[oldgroupname]
                self.main_ref.relations[str(newgroupname)] = copy
                del self.main_ref.relations[oldgroupname]
                
                #aggiorno listGroups
                self.listGroups.takeItem(index)
                self.listGroups.addItem(str(newgroupname))

                self.listGroups.sortItems()
                currentIndex = 0
                for i in range(len(self.listGroups)):
                    if self.listGroups.item(i).text() == str(newgroupname):
                        currentIndex = i
                        break 
                self.listGroups.setCurrentRow(currentIndex)
                self.main_ref.update_groups()
                self.main_ref.saveOnFile()
                
                if refresh:
                    self.main_ref.scrollAreaWidgetGroups.layout().itemAt(currentIndex).widget().setChecked(True)
                    self.main_ref.display_group(str(newgroupname),self.main_ref.scrollAreaWidgetGroups.layout().itemAt(currentIndex).widget())
                #self.main_ref.force_plot(str(newgroupname))
                
            else:
                print "ERROR: group name already exists"

    ## Metodo che permette di aggiornare la lista dei gruppi
    # @param self puntatore all'oggetto
    def updateGroupSublist(self):
        self.btn_remove.setEnabled(True)
        self.btn_rename.setEnabled(True)
        self.btn_selAll.setEnabled(True)
        self.btn_selNone.setEnabled(True)
        self.elementsListGroups.setEnabled(True)
        
        groupname =  str(self.listGroups.currentItem().text())
        for x in xrange(self.elementsListGroups.count()):
            self.elementsListGroups.item(x).setCheckState(QtCore.Qt.Unchecked)

        for element in self.main_ref.relations[groupname]:
            for item in self.elementsListGroups.findItems(element, QtCore.Qt.MatchExactly):
                item.setCheckState(QtCore.Qt.Checked)
        
    ## Metodo che permette di aggiornare la lista delle variabili linguistiche che possono essere aggiunte
    # @param self puntatore all'oggetto
    def updateRelations(self):
        groupname = str(self.listGroups.currentItem().text())
        self.main_ref.relations[groupname] = []
        for x in xrange(self.elementsListGroups.count()):
            element = str(self.elementsListGroups.item(x).text())
            if self.elementsListGroups.item(x).checkState()==QtCore.Qt.Checked:
                self.main_ref.relations[groupname].append(element)
        print " * Relations updated"
        self.main_ref.force_plot(groupname)
        self.main_ref.saveOnFile()

    ## Metodo che permette di chiudere la dialog
    # @param self puntatore all'oggetto
    def closeEvent(self, event):
        self.main_ref.update_groups()
        self.main_ref.saveOnFile()


    