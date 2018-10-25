#coding=utf-8
## @package maingui
#  Questo modulo contiene la classe per la finestra principale MyWindow e la sua implementazione 
import sys
from PyQt4 import QtGui, QtCore, uic
sys.path.insert(0, "..")
from FuzzySimulator import *
import copy
import random
import ConfigParser
import collections
import tempfile

from PyQt4 import QtTest


# matplotlib stuff
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import os

#import dialog class
from membership import *
from nodes import *
from condition import *
from rulesedit import *
from groups import *
#from progressSimulation import *
from aboutFumoso import *
from Model import *

#import plot MF e groups e rules
from plots import *


import pydot # import pydot or you're not going to get anywhere my friend :D



## La classe Setting è una Dialog che permette di specificare quali sono le preferenze dell'utente
class Settings(QtGui.QDialog):

    def __init__(self):
        super(Settings, self).__init__(flags=QtCore.Qt.WindowFlags(1))
        uic.loadUi('Settings.ui', self)
        self.main_ref = None
        self.layout().setSizeConstraint( QtGui.QLayout.SetFixedSize )
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        
## La classe MyWindow è una MainWindow che rappresenta il punto di ingresso del programma
# La MyWindow è composta in alto da una barra delle applicazioni per creare/salvare/rilanciare la simulazione
# A sinistra sono visualizzati gruppi e membership che si possono plottare
# Nei vari menù a tendina è possibile editare nuovi nodi/regole/ membership
class MyWindow(QtGui.QMainWindow):

	#creazione di un sengale che durante il lancio della simulazione verrà emesso per aggioranre la progress bar
    notifyProgress = QtCore.pyqtSignal(int)

    def __init__(self):
        super(MyWindow, self).__init__()
       
        uic.loadUi('maingui.ui', self)

        conditions.main_ref = self
    	rulesviewer.main_ref = self
    	nodeeditor.main_ref = self
    	membershipeditor.main_ref = self
    	settings.main_ref = self
    	groups.main_ref = self
    	rulesEdit.main_ref = self

    	self.conditions = conditions
        
        self.actionEdit_Rules.triggered.connect(self.openRulesEdit)
        self.action_View_Model.triggered.connect(self.openViewModel)

        #self.progressSimulation = ProgressSimulation()
        #self.progressSimulation.main_ref = self
        #self.notifyProgress.connect(self.progressSimulation.onProgress)
        
        self.currentFileFum = '../provaDoppio.fum'
        self.show()

        # initialize data
        self.CDS = None
        self.modelpath = None
        self.relations = {}
        self.document_path = ""

        self.subwindows_spawned = 0
        self.fuss_modified = False
        self.reopen_last_fuss = True
        self.save_on_exit = True

        self.last_output_directory = "./"
        
        self.windows_list = {}
        self.windows_list_MF = {}
        self.rel_group_window = {}
        self.rel_group_window_MF = {}

        self.list_of_rules = None
        self.rules_canvas = None

        self.list_last_fuss = collections.deque(maxlen=10)

        self.settings = QtCore.QSettings("BIMIB", "FUMOSO")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())
        self.restoreState(self.settings.value("windowState").toByteArray())
        
        self.load_configfile()

        print " * All systems nominal"


    ## Metodo che di recuperare gli ultimi file fum aperti
    # @param self puntatore all'oggetto
    # @return ritorna la lista degli ultimi fum aperti
    def get_last_fusses(self):
        for i in self.list_last_fuss:
            print i
        return self.list_last_fuss


    ## Metodo che ritorna la lista di tutti i gruppi che sono selezionati
    # @param self puntatore all'oggetto
    # @return ritorna la lista con i gruppi visualizzati
    def get_selected_groups(self):
        """ Returns the list of selected groups in the groups dock. """
        selected_groups = []
        for x in xrange(self.scrollAreaWidgetGroups.layout().count()):
            if self.scrollAreaWidgetGroups.layout().itemAt(x).widget().isChecked():
                selected_groups.append(str(self.scrollAreaWidgetGroups.layout().itemAt(x).widget().text()))
        return selected_groups

    ## Metodo che ritorna la lista di tutte le membership visualizzate
    # @param self puntatore all'oggetto
    # @return ritorna la lista con le variabili linguistiche visualizzate
    def get_selected_mfs(self):
        """ Returns the list of selected membership functions in the MFs dock. """
        selected_mfs = []
        for x in xrange(self.scrollAreaWidgetContents.layout().count()):
            if self.scrollAreaWidgetContents.layout().itemAt(x).widget().isChecked():
                selected_mfs.append(str(self.scrollAreaWidgetContents.layout().itemAt(x).widget().text()))
        return selected_mfs

    ## Metodo che ritorna la lista di tutti i gruppi presenti
    # @param self puntatore all'oggetto
    # @return ritorna la lista con i gruppi 
    def get_all_groups(self):
        """ Returns the whole list of groups in groups dock. """
        groups = []
        for x in xrange(self.scrollAreaWidgetGroups.layout().count()):
            groups.append(str(self.scrollAreaWidgetGroups.layout().itemAt(x).widget().text()))
        return groups

    
    ## Metodo che ritorna la lista di tutte le membership 
    # @param self puntatore all'oggetto
    # @return ritorna la lista con tutte le variabili linguistiche
    def get_all_MFs(self):
        """ Returns the whole list of membership functions in groups dock. """
        MFs = []
        for x in xrange(self.scrollAreaWidgetContents.layout().count()):
            MFs.append(str(self.scrollAreaWidgetContents.layout().itemAt(x).widget().text()))
        return MFs


    ## Metodo che permette di aggiornare la lista dei gruppi nella finestra principale
    # Aggiorna i gruppi in base alle variabili linguistiche presenti nel sistema
    # @param self puntatore all'oggetto
    def update_groups(self):
        """ Updates the list of groups in the main window, according to the relations dictionary. """

        selected_groups = self.get_selected_groups()
        previous_groups = self.get_all_groups()

        pointer = self.scrollAreaWidgetGroups.layout()
        for i in reversed(range(0,pointer.count())): 
            pointer.itemAt(i).widget().setParent(None)

        copylist = self.relations.items()
        copylist.sort(key=lambda x: x[0].upper())

        for groupname, list_elements  in copylist:
            nb = QtGui.QPushButton(groupname)
            nb.setCheckable(True)
            nb.setChecked(groupname in selected_groups)
            nb.setFlat(True)
            pointer.addWidget(nb)
            self.connect(nb, QtCore.SIGNAL("clicked()"), lambda who=groupname, what=nb: self.display_group(who, what))

        # create windows
        for (groupname, list_elements) in self.relations.items():
            if groupname not in previous_groups:
                self.add_subwindow(groupname=groupname, title="Group "+groupname, group=list_elements, hidden=True)


    ## Metodo che permette di visualizzare o nascondere il gruppo selezionato
    # @param self puntatore all'oggetto
    # @param groupanme gruppo che vogliamo visualizzare
    # @param nb valore booleano che permette di stabilire se vogliamo visualizzare(True) o nascondere(False)
    def display_group(self, groupname, nb):
        display_num = self.rel_group_window[groupname]
        if nb.isChecked():
            self.windows_list[display_num][0].show()        
            if self.CDS.whole_dynamics != None:
                self.force_plot(groupname)
        else:
            self.windows_list[display_num][0].hide()      

        self.mdiArea.tileSubWindows()   # mmh

    ## Metodo che permette di leggere il file di configurazione iniziale
    # @param self puntatore all'oggetto
    def load_configfile(self):
        """ Loads the config.ini and sets the user settings. """
        cp = ConfigParser.RawConfigParser()
        cp.read('config.ini')
        try:
            self.reopen_last_fuss = cp.getboolean('General', 'reopen_last_fuss')
            self.save_on_exit = cp.getboolean('General', 'save_on_exit')
            last_fuss = cp.get('General', 'last_fuss')
            if self.reopen_last_fuss==True:
                #self.progressSimulation.start()
                self.actualFUMLoad(last_fuss, True)
        except ConfigParser.NoSectionError:
            print "WARNING: config.ini seems to be broken or missing"
        except ConfigParser.NoOptionError:
            print "WARNING: config ini seems to be old"


#################################################################################
#    SUBWINDOWS MANAGEMENT                                                      #
#################################################################################
    
    ## Metodo che permette di aggiungere un plot di una variabile lingusitica
    # @param self puntatore all'oggetto
    # @param title stringa da visualizzare
    # @param MFname nome della varaibili linguistica di cui creiamo il plot
    # @param hidden specificato a False per nasconderlo
    def add_subwindow_MF(self, title="Membership function", MFname="", hidden=True):
        """ Create and add a new subwindow for the membership function of attribute 'MFname'. """
        sb, tot, canvas, title = self.create_subwindow_MF(title=title, hidden=hidden, MFname=MFname)
        self.windows_list_MF[tot] = (sb, canvas, title)
        self.rel_group_window_MF[MFname] = tot
        #print " * Subwindow", title, "created"


    """
        Create a new subplot of dynamics.
    """

    ## Metodo che permette di creare un plot di una variabile lingusitica
    # @param self puntatore all'oggetto
    # @param title stringa da visualizzare
    # @param MFname nome della varaibili linguistica di cui creiamo il plot
    # @param hidden specificato a False per nasconderlo
    def create_subwindow_MF(self, title="", hidden=True, MFname=""):        
        sb = PlotWindowMF(parent=self, MFname=MFname)
        sb.setWindowTitle(title)        
        self.mdiArea.addSubWindow(sb)
        # mw = sb.canvas
        mw = sb.canvas
        if not hidden: sb.show()
        
        self.subwindows_spawned +=1
        return sb, self.subwindows_spawned, mw, title


    """ 
        Create and add a new subwindow for a plot.
    """
    ## Metodo che permette di aggiungere un plot di un gruppo
    # @param self puntatore all'oggetto
    # @param title stringa da visualizzare
    # @param lista degli elementi del gruppo
    # @param groupname nome del gruppo di cui creiamo il plot
    # @param hidden specificato a False per nasconderlo
    def add_subwindow(self, title="Groups dynamics plot", group=[], groupname="", hidden=True):
        sb, tot, canvas, title = self.create_subwindow(title=title, group=group, hidden=True)
        self.windows_list[tot] = (sb, canvas, title)
        self.rel_group_window[groupname] = tot
        # print " * Subwindow", title, "created"


    """
        Create a new subplot of dynamics.
    """

    ## Metodo che permette di creare un plot di un gruppo
    # @param self puntatore all'oggetto
    # @param title stringa da visualizzare
    # @param lista degli elementi del gruppo
    # @param hidden specificato a False per nasconderlo
    def create_subwindow(self, title="", group=[], hidden=True):        
        sb = PlotWindow(parent=self)
        sb.setWindowTitle(title)        
        self.mdiArea.addSubWindow(sb)
        # mw = sb.canvas
        mw = sb.canvas
        if not hidden: sb.show()
        
        self.subwindows_spawned +=1
        return sb, self.subwindows_spawned, mw, title

    
    ## Metodo che una volta che il sistema ha caricato i dati è in grado di creare e visualizzare l'area delle membership nella finestra principale
    # @param self puntatore all'oggetto
    def populate_members_dock(self):

        if self.scrollAreaWidgetContents.layout() != None:
            self.update_member_dock()
        else:
            print 'populate_members_dock'
            self.layout = QtGui.QVBoxLayout()        
            lista = self.CDS.get_list_input_variables()
            lista.sort(key=lambda x: x.upper())
            for v in lista:         
                checkBox = QtGui.QCheckBox()
                checkBox.setText(v)
                checkBox.setChecked(QtCore.Qt.Unchecked)
                self.connect(checkBox, QtCore.SIGNAL("clicked()"), lambda who=v, what=checkBox: self.toggleMF(who, what))
                self.layout.addWidget(checkBox)
                self.add_subwindow_MF(hidden=True, MFname=v, title="MF "+v)
            self.scrollAreaWidgetContents.setLayout(self.layout)

    
    ## Metodo che aggiorna la lista delle checkbox delle varaibili linguistiche
    # @param self puntatore all'oggetto
    def update_member_dock(self):

    	#distruggo widget
        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().setParent(None)

        #recupero lista
        lista = self.CDS.get_list_input_variables()
        lista.sort(key=lambda x: x.upper())
        
        #creo lista di checkbox per le mebership
        for v in lista:         
            checkBox = QtGui.QCheckBox()
            checkBox.setText(v)
            checkBox.setChecked(QtCore.Qt.Unchecked)
            self.connect(checkBox, QtCore.SIGNAL("clicked()"), lambda who=v, what=checkBox: self.toggleMF(who, what))
            self.layout.addWidget(checkBox)
            self.add_subwindow_MF(hidden=True, MFname=v, title="MF "+v)

    
    ## Metodo che rimuove i plot delle membership aperti
    # @param self puntatore all'oggetto
    # @return ritorna la lista dei plot delle variabili linguistiche che sono state chiuse
    def deplot(self):
        listRemove = []
        for i in reversed(range(self.layout.count())):
            if self.layout.itemAt(i).widget().isChecked():
                listRemove .append(str(self.layout.itemAt(i).widget().text()))
                self.layout.itemAt(i).widget().setChecked(False)
                self.toggleMF(str(self.layout.itemAt(i).widget().text()),self.layout.itemAt(i).widget())

        return listRemove

    ## Metodo che permette di plottare una lista di varaibili linguistiche passate come paraemtro
    # @param self puntatore all'oggetto
    # @param listToPlot lista di variabile linguistiche che vogliamo visualizzare
    def replot(self, listToPlot):
        for i in reversed(range(self.layout.count())):
            if str(self.layout.itemAt(i).widget().text()) in listToPlot:
                self.layout.itemAt(i).widget().setChecked(True)
                self.toggleMF(str(self.layout.itemAt(i).widget().text()),self.layout.itemAt(i).widget())


    ## Metodo che rimuove i plot dei gruppi aperti
    #@param self puntatore all'oggetto
    # @return ritorna la lista dei plot dei gruppi che sono stati chiusi
    def deplotGroups(self):
        listSelected = self.get_selected_groups()
        currentIndex = 0
        for x in xrange(self.scrollAreaWidgetGroups.layout().count()):
            if self.scrollAreaWidgetGroups.layout().itemAt(x).widget().text() in listSelected:
                self.scrollAreaWidgetGroups.layout().itemAt(x).widget().setChecked(False)
                self.display_group(str(self.scrollAreaWidgetGroups.layout().itemAt(x).widget().text()),self.scrollAreaWidgetGroups.layout().itemAt(currentIndex).widget())
            currentIndex = currentIndex + 1
        return listSelected

    ## Metodo che permette di plottare una lista di gruppi passati come parametro
    # @param self puntatore all'oggetto
    # @param listToPlot lista di gruppi che vogliamo visualizzare
    def replotGroups(self, listToPlot):
        currentIndex = 0
        for x in xrange(self.scrollAreaWidgetGroups.layout().count()):
            if self.scrollAreaWidgetGroups.layout().itemAt(x).widget().text() in listToPlot:
                self.scrollAreaWidgetGroups.layout().itemAt(x).widget().setChecked(True)
                self.display_group(str(self.scrollAreaWidgetGroups.layout().itemAt(x).widget().text()),self.scrollAreaWidgetGroups.layout().itemAt(currentIndex).widget())
            currentIndex = currentIndex + 1

    
    ## Metodo che permette di plottare una singola membership
    # @param self puntatore all'oggetto
    # @param n variabile lingusitica plottata
    # @param cb checkbox per verificare se è True o False
    def toggleMF(self,n, cb):
        print "Toggling", n
        v = self.rel_group_window_MF[n]
        print v
        self.windows_list_MF[v][1].drawGraph(attribute=n, CDS=self.CDS, iteration=self.get_current_iteration())
        if cb.checkState()==QtCore.Qt.Checked:
            self.windows_list_MF[v][0].show()
        else:
            self.windows_list_MF[v][0].hide()
            
        self.mdiArea.tileSubWindows()

    
    ## Metodo che permette di leggere un file FCL e creare grazie al simulatore le variabili del sistema
    # @param self puntatore all'oggetto
    # @param filename nome del file da leggere
    # @param widget_update per sapere se sono da aggiornare i widget 
    def actualFCLLoad(self, filename, widget_update=True):
        groups.main_ref = self
        QtGui.QCursor(QtCore.Qt.WaitCursor)    

        print " * Widget update:", widget_update
        self.CDS = FuzzySystem(input_file=filename, dump=False, max_time=1.0)
        print self.CDS
        self.modelpath = filename                                    

        if self.modelpath!=None:
            if widget_update:
                self.populate_members_dock()
                self.notifyProgress.emit(25)  
                groups.populate_groups_manager()          

            #self.statusBar().showMessage("Using FCL model from "+self.modelpath)            
            print " * Name of the model:", self.CDS.fuzzySystem.description
            self.menuRun_simulation.setEnabled(True)
            self.scrollAreaGroups.setEnabled(True)
            self.fuss_modified = True
            self.menu_Model.setEnabled(True)
            # self.CDS.simulate()
        else:
            print "Unable to enable simulations"
            self.menuRun_simulation.setEnabled(False)
            self.scrollAreaGroups.setEnabled(False)
            self.menu_Model.setEnabled(False)

        
        # self.save_FCL();


        QtGui.QCursor(QtCore.Qt.ArrowCursor)



    ## Metodo che permette di salvare l'immagine delle regole
    # @param self puntatore all'oggetto
    def save_figure_rule(self, path):
        rulesviewer.ruleDisplay.layout().itemAt(0).widget().fig.savefig(path, dpi=300)
        print " * Rule saved as", path

    ## Metodo che permette di aggiornare la progressBar
    # @param self puntatore all'oggetto
    # @param value valore da settare
    def updatepb(self, value):
        self.pb.setValue(value)
        

    def autonomous_display_rule(self):
        index = rulesviewer.treeView.selectionModel().currentIndex()
        selectedText = str(index.data().toString())

        hierarchyLevel = 1
        seekRoot = index
        while not seekRoot.parent() == QtCore.QModelIndex():
            seekRoot = seekRoot.parent()
            hierarchyLevel += 1
    
        if hierarchyLevel == 2:
            self.plot_rule(self.list_of_rules[selectedText], selectedText, self.rules_canvas)


    def display_rule(self, selected, deselected, lr):
        self.list_of_rules = lr
        self.autonomous_display_rule()


    def plot_rule(self, rules, title, canvas):
        canvas.drawGraph(title=title, rules=rules, CDS=self.CDS, iteration=self.get_current_iteration())
        

    """ Load an input fuzzy logic control file. """
    ## Metodo che permette di aprire un file FCL (non più utile? dato che usiamo FUM)
    # @param self puntatore all'oggetto
    def openFCL(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open FCL file', '', "FCL Files (*.fcl)")
        if filename:
            if self.modelpath!=None:
                print " * Model already loaded in", self.modelpath
                self.actualFCLLoad(filename, widget_update=False)
            else:
                print " * First loading of model"
                self.actualFCLLoad(filename)
        
       
    """
        Selects all checkboxes related to membership functions.
    """
    ## Metodo che permette di selezioanre tutte le checbox delle membership
    # @param self puntatore all'oggetto
    def selectAll(self):
        for item in xrange(self.scrollAreaWidgetContents.layout().count()):
            self.scrollAreaWidgetContents.layout().itemAt(item).widget().setChecked(QtCore.Qt.Checked)

        self.update_all_displayed_plots()

    """
        Selects all checkboxes related to membership functions.
    """
    ## Metodo che permette di deselezioanre tutte le checbox delle membership
    # @param self puntatore all'oggetto
    def deselectAll(self):
        for item in xrange(self.scrollAreaWidgetContents.layout().count()):
            self.scrollAreaWidgetContents.layout().itemAt(item).widget().setChecked(QtCore.Qt.Unchecked)
            mfname = str(self.scrollAreaWidgetContents.layout().itemAt(item).widget().text())
            number = self.rel_group_window_MF[mfname]
            self.windows_list_MF[number][0].hide()

        self.update_all_displayed_plots()

    ## Metodo che permette di modificare il massimo valore e rilancia la simulazione
    # @param self puntatore all'oggetto
    # @param v valore da settare
    def changeMaxLED(self, v):
        # print " * New maximum:", v
        self.horizontalSlider.setMaximum (v)
        self.forceRunSimulation()
    
    ## Metodo che in seguito ad una modifica rilancia la simulazione
    # @param self puntatore all'oggetto
    # @param v valore da settare
    def changeLED(self, s):
        # print " * New maximum:", v
        # self.horizontalSlider.setMaximum (v)
        self.forceRunSimulation()

    ## Metodo che forza il plot di un gruppo
    # @param self puntatore all'oggetto
    # @param groupname gruppo da plottare
    # @param hidden settato a false perchè visualizzato
    def force_plot(self, groupname, hidden=False):
        """ Actually plots the selected group. """
        print 'force_plot: ', groupname
        number = self.rel_group_window[groupname]
        if self.relations[groupname] == []:
            self.windows_list[number][1].drawGraph(data=[], group=self.relations[groupname], iters= self.get_iterations(), mtime=self.get_timemax(), ctime=self.get_current_time(), dict_markers=self.CDS.dict_markers, dict_colors=self.CDS.dict_colors )

        else:
            self.windows_list[number][1].drawGraph(data=self.CDS.whole_dynamics, group=self.relations[groupname], iters= self.get_iterations(), mtime=self.get_timemax(), ctime=self.get_current_time(), dict_markers=self.CDS.dict_markers, dict_colors=self.CDS.dict_colors )
            if not hidden: self.windows_list[number][1].show()

    ## Metodo che forza il plot di una membership
    # @param self puntatore all'oggetto
    # @param mfname nome della membership da plottare
    # @param hidden settato a false perchè visualizzato
    def force_plot_mf(self, mfname, hidden=False):
        """ Actually plots the selected membership function. """
        number = self.rel_group_window_MF[mfname]
        # def drawGraph(self, attribute=None, title="", CDS=None, iteration=1):
        self.windows_list_MF[number][1].drawGraph(CDS=self.CDS, attribute=mfname, iteration=self.get_current_iteration() )
        if not hidden: self.windows_list_MF[number][0].show()
        # print " * MF", mfname, "plotted"


    """
        Start simulation.
    """
    ## Metodo che forza l'avvio della simulazione
    # @param self puntatore all'oggetto
    def forceRunSimulation(self):        
        conditions.generate_state()
        self.notifyProgress.emit(72)
        self.generate_and_set_state_updaters()
        self.notifyProgress.emit(85)
        self.CDS.maximum_time = self.get_timemax()
        self.CDS.simulation_time = 0.0
        if self.CDS.simulate(iterations=self.get_iterations(), store_everything=True, Sugeno=True):
            self.scrollArea.setEnabled(True)
            self.selectAllButton.setEnabled(True)
            self.deselectAllButton.setEnabled(True)
            print " * Simulation completed"
            self.update_all_displayed_plots()
            self.notifyProgress.emit(92)
            self.generate_rules()
            self.notifyProgress.emit(100)
        else:
            print " * Simulation crashed"

  


    """ 
        Generates the state updaters according to the 
        conditions form. Then binds them to the fuzzy system.
    """
    ## Metodo che aggiorna lo stato della simulazione
    # @param self puntatore all'oggetto
    def generate_and_set_state_updaters(self, verbose=True):
        model = conditions.tableView.model()

        variables = []
        for x in xrange(conditions.tableView.verticalHeader().count()):
            variables.append(str(conditions.tableView.verticalHeader().model().headerData(x,  QtCore.Qt.Vertical).toString()))
        # variables = self.CDS.get_list_input_variables()

        st_ups = []
        for x in xrange(model.rowCount()):
            index = model.index(x,1)
            intex_third_column = model.index(x,2)
            interval = model.data(intex_third_column).toString()
            if model.data(index).toString()!="":
                newfun = eval("lambda time: "+str(model.data(index).toString()) )
                if len(str(interval))>0:
                    newlist = eval(str(interval))
                else:
                    newlist = []
                st_ups.append( (variables[x], newfun, newlist) )
        self.CDS.set_state_updaters(st_ups)

        conditions.updateInitialCondition()
        conditions.tableView.resizeColumnsToContents()


        if verbose:
            print " * State updaters:", st_ups
            #exit()




    """ Reads the simulation time from form. """

    ## Metodo che ritorna il tempo massimo della simulazione
    # @param self puntatore all'oggetto
    # @return tempo massimo della simulazione
    def get_timemax(self):
        return float(self.simulationTime.text())

    """ Reads the number of iterations from form. """
    
    ## Metodo che ritorna il numero di iterazioni
    # @param self puntatore all'oggetto
    # @return il numero di iterazioni
    def get_iterations(self):
        return int(self.totalIterations.value())

    """ Reads the current iteration from LCD. """
    ## Metodo che ritorna l'iterazione corrente
    # @param self puntatore all'oggetto
    # @return l'iterazione corrente
    def get_current_iteration(self):
        return self.lcdNumber.intValue()-1

    """ Determines the current time of simulation. """
    ## Metodo che ritorna il tempo corrente della simulazione
    # @param self puntatore all'oggetto
    # @return tempo corrente della simulazione
    def get_current_time(self):
        return self.get_current_iteration()*(self.get_timemax()/(self.get_iterations()-1))

    
    """ Move 'through time' in the simulation """
    ## Metodo che aggiorna la status bar dell'applicazione
    # @param self puntatore all'oggetto
    def updateFromSlider(self):
        self.update_all_displayed_plots()
        if rulesviewer.isVisible():
            self.autonomous_display_rule()
            
            self.statusBar().showMessage("Time: "+str(self.get_current_time()))            
            rulesviewer.statusBar().showMessage("Time: "+str(self.get_current_time()))            

    
    ## Metodo che aggiorna tutti i gruppi selezionati e tutte le mebership selezionate
    # @param self puntatore all'oggetto
    def update_all_displayed_plots(self):
        selected_groups = self.get_selected_groups()
        for groupname in selected_groups:
            self.force_plot(groupname)

        selected_mfs = self.get_selected_mfs()
        for mf in selected_mfs:
            self.force_plot_mf(mf)

    ## Metodo che aggiorna tutti i gruppi selezionati
    # @param self puntatore all'oggetto
    def update_all_dynamics(self, hidden=False):
        selected_groups = self.get_all_groups()
        for groupname in selected_groups:
            self.force_plot(groupname, hidden=hidden)

    ## Metodo che aggiorna tutte le membership visualizzate
    # @param self puntatore all'oggetto
    def update_all_MFs(self, hidden=False):
        selected_mfs = self.get_all_MFs()
        for mf in selected_mfs:
            self.force_plot_mf(mf, hidden=hidden)

    ## Metodo che aggiorna tutte le membership visualizzate e i gruppi (doppione???)
    # @param self puntatore all'oggetto
    def update_all_plots(self, hidden=False):
        self.update_all_dynamics(hidden=hidden)        
        self.update_MFs(hidden=hidden)        


    ## Metodo che permette di salvare su un file .fum diverso dal file correnti i dati della simulazione 
    # (Al momento sia salva che salva come sono collegati a questo slot)
    # @param self puntatore all'oggetto
    def saveSimulationData(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save FUM file',"", "Fum Files (*.fum)")  
        filename = str(filename)
        if not filename == '':
            if not '.fum' in filename:
                filename = filename + '.fum'

            print 'file su cui scrivere: ',filename
            self.saveOnFile(filename)
            self.actualFUMLoad(filename, True)

    
    ## Metodo che permette di leggere un file.fum e di creare i della simulazione
    # @param self puntatore all'oggetto
    # @param filename nome del file da aprire
    # @param new booleano da specificare True se il file non è quello corrente
    def actualFUMLoad(self, filename, new=None):

        #se true, nuovo file letto
        if new:
            self.currentFileFum = filename
        else:
            filename = self.currentFileFum

        self.statusBar().showMessage("Using Fum file "+self.currentFileFum) 
            
        self.notifyProgress.emit(13)
        if filename!=None and filename!="":
            file = None
            try:
            	print " * Automatically opening file", filename
            	file = open(filename, 'r')
            except:
            	self.notifyProgress.emit(100)
            	self.CDS = FuzzySystem("../celde13.fcl")
            	self.openNewFum("new")
            	return
            	
            fussThings = False
            fclThings = True
            #creo file temporanei per fuss e fcl
            f_fuss = tempfile.NamedTemporaryFile(mode='w+t', delete=False)
            f_fcl = tempfile.NamedTemporaryFile(mode='w+t', delete=False)
            #print file.read()
            for line in file:
                if fclThings:
                    f_fcl.write(line)
                    if 'END_FUNCTION_BLOCK' in line:
                        fussThings = True
                        fclThings = False
                    continue;
                if fussThings:
                    f_fuss.write(line)
            file.close()		
            f_fuss.seek(0)
            f_fcl.seek(0)
            

            fileFuss= f_fuss.name	
            section = 0
            model = None
            n=0

            self.setWindowTitle("FUMOSO - "+filename)
            self.notifyProgress.emit(22)

            self.relations = {}
            conditions.clear()
            minMax = {}
            with open(fileFuss) as fi:
                for line in fi:
                    #print line
                    line = line.strip("\n")
                    if not line.startswith("#"):
               
                        # flc file
                        if section==1:
                            self.actualFCLLoad(f_fcl.name)
                            self.notifyProgress.emit(30)

                        # groups observed
                        elif section==2:        
                            line = line.split("\t")                    
                            self.relations[line[0]] = eval(line[1])

                        # initial states
                        elif section==3:
                            data = line.split("\t")
                            if len(data)==2: 
                                print 'data',data
                                data.append('')
                            
                            minMax[data[0]] = data[4:]
                            #data = map(lambda x: QtGui.QStandardItem(x), data)
                            #model.appendRow(data[1:])
                            #model.setVerticalHeaderItem(n, QtGui.QStandardItem(data[0]))
                            conditions.addNodeStates(data[0:4])
                            self.notifyProgress.emit(35)
                            n+=1

                        # simulation data
                        elif section==4:
                            print "section:", section
                            line = line.split()
                            print "line", line
                            if line != []:
                            	self.maximum_time = float(line[1])      
                                self.iterations = int(line[3])
                                self.simulationTime.setText(str(self.maximum_time))
                                self.totalIterations.setValue(int(self.iterations))                      
                        
                    else:
                        section +=1
            
            self.notifyProgress.emit(45)
            self.setMaxMin(minMax)

            conditions.updateInitialCondition()
            self.notifyProgress.emit(57)
            self.update_groups()
            self.notifyProgress.emit(63)

            print " * FUSS file correctly opened"
            self.document_path = filename
            self.list_last_fuss.append(str(filename))
            #self.CDS.simulate()
            self.forceRunSimulation()

 
        else:
            print "Please select a valid FUSS file"

    ## Metodo che permette di settare ad ogni variabile linguistica il suo valore di minimo e massimo
    # @param self puntatore all'oggetto
    # @param dictMinMax dizionario che contiene per ogni variabile linguistica il suo valore di min e max
    def setMaxMin(self, dictMinMax):
        print 'dictMinMax', dictMinMax
        for node, listMinMax in dictMinMax.items():
            if listMinMax != []:
                self.CDS.fuzzySystem.variables[node].min = float(listMinMax[0])
                self.CDS.fuzzySystem.variables[node].max = float(listMinMax[1])


    
    ## Metodo che permette di creare le regole nella finestra di visualizzazione delle regole
    # @param self puntatore all'oggetto
    def generate_rules(self):

        lr = self.CDS.get_list_rules()
        #self.dict_rules = lr

        treemodel = QtGui.QStandardItemModel()
        treemodel.setHorizontalHeaderLabels(['List of rules', 'Rule'])        
        rulesviewer.treeView.setModel(treemodel)
        root = QtGui.QStandardItem("Fuzzy System")

        # we append the rules of each group in the FCL file
        for group, rules in  lr.items():
            child = QtGui.QStandardItem(group)
            root.appendRow(child)            
            
            # if there is not a specific updater for this node, add its rules
            if len(filter(lambda x: x[0]==group, self.CDS.updaters))==0:
                rules.sort(key=lambda x: int(x[0][x[0].find(".")+1:]) )            
                for r in rules:
                    subchild = QtGui.QStandardItem(r[0])
                    subchild_2 = QtGui.QStandardItem(self.CDS.rule_to_string(r))
                    child.appendRow([subchild, subchild_2])
            else:
                if len(rules)==0:
                    child.setForeground(QtGui.QColor(150,150,150))
                else:
                    child.setForeground(QtGui.QColor(150,150,50))

        # model was correctly loaded: append it to the root
        treemodel.appendRow(root)


        # what follows is the second phase: we must connect a signal to the list, 
        # so that we can show the antecedents and consequents of the selected rule      

        self.connect(rulesviewer.treeView.selectionModel(), 
                QtCore.SIGNAL("selectionChanged(QItemSelection, QItemSelection)"), 
                lambda x,y: self.display_rule(x,y,lr))

        vbox = rulesviewer.ruleDisplay.layout()
        for i in reversed(range(vbox.count())): 
            vbox.itemAt(i).widget().setParent(None)

        # canvas for rules display
        self.rules_canvas = GraphCanvasRules(statusbar_ref=rulesviewer.pb)
        vbox.addWidget(self.rules_canvas)

        # matplotlib navigation toolbar for the rules display
        toolbar = NavigationToolbar(self.rules_canvas, self)
        vbox.addWidget(toolbar)


    
    ## Metodo che permette di visualizzare la dialog per la gestione delle preferenze
    # @param self puntatore all'oggetto
    def showPreferences(self):
        # settings.show()
        settings.exec_()

    ## Metodo che permette di salvare tutte le immagini relative ai gruppi
    # @param self puntatore all'oggetto
    # @param groupname nome del gruppo da salvare
    # @param folder cartella di output
    # @param extension estensione dell'immagine
    def save_figure_dynamics(self, groupname, folder, extension="png"):
        number = self.rel_group_window[groupname]
        output_path = str(folder+"/"+groupname+"_group."+extension)
        print " * Saving file", output_path
        oldsizex, oldsizey = self.windows_list[number][1].fig.get_size_inches()
        self.windows_list[number][1].fig.set_size_inches(8.0, 6.0)
        self.windows_list[number][1].fig.savefig(output_path, dpi=300)
        self.windows_list[number][1].fig.set_size_inches(oldsizex, oldsizey) 


    ## Metodo che permette di salvare tutte le immagini relative alle membership
    # @param self puntatore all'oggetto
    # @param groupname nome della membership da salvare
    # @param folder cartella di output
    # @param extension estensione dell'immagine
    def save_figure_MF(self, MF, folder=".", extension="png"):
        number = self.rel_group_window_MF[MF]
        output_path = str(folder+"/"+MF+"_MF."+extension)
        print " * Saving file", output_path
        oldsizex, oldsizey = self.windows_list_MF[number][1].fig.get_size_inches()
        self.windows_list_MF[number][1].fig.set_size_inches(8.0, 6.0)
        self.windows_list_MF[number][1].fig.savefig(output_path, dpi=300)
        self.windows_list_MF[number][1].fig.set_size_inches(oldsizex, oldsizey)

    
    ## Metodo che permette di salvare tutte le immagini
    # @param self puntatore all'oggetto
    def exportFigures(self):
        directory = QtGui.QFileDialog.getExistingDirectory(self, 'Select output directory', self.last_output_directory)
        if directory:
            self.update_all_dynamics(hidden=True)
            for groupname in self.get_all_groups():
                self.save_figure_dynamics(groupname, directory)            

            print " * All dynamics saved in", directory
            self.update_all_dynamics()
            self.last_output_directory = directory
        else:
            print "WARNING: please specify a valid output folder"

    
    ## Metodo che permette di esportare file TSV (AL momento non abilitato)
    # @param self puntatore all'oggetto
    def exportTSVfile(self):
        outputfile = QtGui.QFileDialog.getSaveFileName(self, "Please choose a destination file", "", "Tab-separated file (*.tsv)")
        outputfile = str(outputfile)
        if outputfile != None:
            self.CDS.write_observed_to_file(outputfile)

   
    ## Metodo che permette di chiudere il programma FUMOSO
    # @param self puntatore all'oggetto
    # @param event evento chiusura programma
    def closeEvent(self, event):

        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())

        if self.fuss_modified:
            if not self.save_on_exit:
                quit_msg = "You have unsaved settings. Are you sure you want to exit the program?"
                reply = QtGui.QMessageBox.question(self, 'Confirm exit', 
                                 quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

                if reply == QtGui.QMessageBox.Yes:
                    self.saveAndExit()
                    event.accept()
                else:
                    event.ignore()
            else:
                print " * Saving automatically"
                self.saveAndExit()

    ## Metodo che permette di salvare tutte le variabili priam della chiusura
    # @param self puntatore all'oggetto   
    def saveAndExit(self):    
        cp = ConfigParser.RawConfigParser()
        cp.add_section('General') 
        cp.set('General', 'last_fuss', self.document_path)
        cp.set('General', 'save_on_exit', self.save_on_exit)
        cp.set('General', 'reopen_last_fuss', self.reopen_last_fuss)
        cp.set('General', 'lastfuss', self.list_last_fuss)
        with open("config.ini", "wb") as configfile:
            cp.write(configfile)
        print " * Configuration saved in config.ini"
        conditions.hide()
        rulesviewer.hide()
        groups.hide()

        #salva file
        self.saveOnFile()


    ## Metodo che permette di ricaricare la simulazione (AL momento inutile perche ogni volta viene salvato e rilanciata la simulazione)
    # @param self puntatore all'oggetto
    def reloadDocument(self):
    	self.deplot()
    	self.deplotGroups()
        #self.progressSimulation.start()
        self.actualFUMLoad('prova')
        self.forceRunSimulation()


    ## Metodo che visualizza a dialog che permette di aprire un file .fum
    # @param self puntatore all'oggetto
    def openSimulationFile(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open FUM file', '', "Fum Files (*.fum)")        
        filename = str(filename)
        QtTest.QTest.qWait(200)
        if not filename == '':
            try:
                self.deplot()
            except:
                print "WARNING: nothing to unplot, FUMOSO will continue..."
            self.deplotGroups()
            #self.progressSimulation.start()
            self.actualFUMLoad(filename, True)

    ## Metodo che permette di aprire una dialog per la creazioni di nuovi gruppi
    # @param self puntatore all'oggetto
    def openDialogManageGroups(self):
        groups.main_ref = self    
        groups.populate_groups()
        groups.populate_groups_manager() 
        groups.setConfiguration()
        groups.show()

    ## Metodo che permette di aprire una dialog per il settaggio delle condizioni iniziali
    # @param self puntatore all'oggetto
    def openDialogManageInitialConditions(self): 
        conditions.tableView.model().itemChanged.connect(conditions.saveItemChanged)
        conditions.show()

    ## Metodo che permette di aprire una dialog per la creazione di regole
    # @param self puntatore all'oggetto
    def openRulesEdit(self):
        listNodes = []
        for key, variable in self.CDS.fuzzySystem.variables.items():
            if isinstance(variable, fuzzy.InputVariable.InputVariable):
                if self.CDS.fuzzySystem.variables[key].adjectives.items() != []:
                    listNodes.append(key)
                else:
                    print 'nodo senza adj', key
        
        listNodes.sort(key=lambda x: x.upper())

        print " * %d variables were detected", len(listNodes)

        if len(listNodes) <2:
            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Information)
            msg.setText("No variables were defined. Please create variables before editing rules.")
            msg.exec_()
        else:
            rulesEdit.updateListNodes(listNodes[:])
            rulesEdit.show()


    ## Metodo che permette di aprire una dialog per la visualizzazione delle regole
    # @param self puntatore all'oggetto
    def openRules(self):
        self.generate_rules()
        rulesviewer.show()

    ## Metodo che permette di aprire una dialog per la creazioni di variabili linguistiche
    # @param self puntatore all'oggetto
    def openNodes(self):
    	print " * Opening nodes list"
        nodeeditor.setConfiguration()
        nodeeditor.listNodes.clear()
        for key, variable in self.CDS.fuzzySystem.variables.items():
            if isinstance(variable, fuzzy.InputVariable.InputVariable):
                nome = nodeeditor.listNodes.addItem(key)
        nodeeditor.listNodes.sortItems()
        nodeeditor.show()
        

    ## Metodo che permette di aprire una dialog per il settaggio delle mebership
    # @param self puntatore all'oggetto
    # @param specific intero  che se passato permette di selezioanre una specifica variabile linguistica
    def openMembership_functions(self, specific = None):
        print " * Opening membership functions editor"
        membershipeditor.node_box.clear()
        listNodes = []
        for key, variable in self.CDS.fuzzySystem.variables.items():
            if isinstance(variable, fuzzy.InputVariable.InputVariable):
                listNodes.append(key)
        
        listNodes.sort(key=lambda x: x.upper())
        membershipeditor.node_box.addItems(listNodes)
        if specific != None:
        	index = 0
        	for i in range(len(listNodes)):
        		if listNodes[i] == specific:
        			index = i 
        	membershipeditor.node_box.setCurrentIndex(index)
        
        if len(listNodes) == 0:
        	msg = QtGui.QMessageBox()
        	msg.setIcon(QtGui.QMessageBox.Information)
        	msg.setText("There are not nodes, first create nodes!")
        	msg.exec_()

        else:
        	membershipeditor.updateLingset()
        	membershipeditor.toReplotFun()
        	membershipeditor.show()

    def openViewModel(self):
    	dict_model = {}
    	dict_numb = {}
        for key, variable in self.CDS.fuzzySystem.variables.items():
            if isinstance(variable, fuzzy.InputVariable.InputVariable):
                dict_model[key]=[]
                dict_numb[key]= 0
        lr = self.CDS.get_list_rules()
        for group, rules in  lr.items():
            toRemove = []
            lun = len(rules)
            for indice in range(lun):
                ant = self.CDS.unpack_antecedents(rules[indice][1].operator)
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
                for a in ant2:
                    if group not in dict_model[a]:
                    	dict_model[a].append(group)
                dict_numb[group] = dict_numb[group] +1

        orderList = sorted(dict_numb.items(), key=lambda x: x[1])
        graph = pydot.Dot(graph_type='digraph',rankdir='LR')

        for elem in orderList:
        	ant = elem[0]
        	con = dict_model[ant]
        	if dict_numb[ant] == 0:
	        	graph.add_node(pydot.Node(ant, color = 'black', style= 'filled', fillcolor = '#D3D3D3', shape = 'ellipse'))
	        elif con == []:
	        	graph.add_node(pydot.Node(ant, color = 'black', style= 'filled', fillcolor = '#ADD8E6', shape = 'hexagon'))
	        else:
	        	graph.add_node(pydot.Node(ant, color = 'black', shape = 'polygon'))

	        for c in con:
		        edge = pydot.Edge(ant, c)
		        graph.add_edge(edge)
        graph.write_png('model2.png')
        viewModel.loadImage()
        viewModel.show()


    ## Metodo che permette di aprire una dialog per con le informazioni del programma FUMOSO
    # @param self puntatore all'oggetto
    def openAboutFumoso(self):
        print'openAboutFumoso'
        aboutFumoso.show()


    ## Metodo che permette di aprire una dialog per creare un nuovo file .fum
    # @param self puntatore all'oggetto
    def openNewFum(self,a=None):
        print 'openNewFum'
        if a== None:
        	self.deplot()
        	self.deplotGroups()
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Create FUM file',"", "Fum Files (*.fum)")  
        filename = str(filename)

        print filename
        if not filename == '':
            if not '.fum' in filename:
                filename = filename + '.fum'
            
            self.currentFileFum = filename
            self.statusBar().showMessage("Using Fum file "+ self.currentFileFum) 
            self.setWindowTitle("FUMOSO - "+filename)

            self.currentFileFum = filename
            self.document_path = filename



            self.CDS.fuzzySystem.variables = {}
            self.relations = {}
            conditions.data_states = []
            self.CDS.fuzzySystem.rules = {}
            if a != None:
            	self.populate_members_dock()
            self.update_groups()
            conditions.updateInitialCondition()
            self.update_member_dock()
            self.generate_rules()
            self.saveOnFile()
            self.list_last_fuss.append(str(filename))
            print self.list_last_fuss
            




    ## Metodo che permette di salvare su file i dati delle variabili linguistiche, e dei gruppi
    # @param self puntatore all'oggetto
    # @param file_name se specificato salva su quel file altrimenti sul corrente
    def saveOnFile(self, file_name = None):

    	FUNCTION_BLOCK = 'FUNCTION_BLOCK deathcell'
    	END_FUNCTION_BLOCK = 'END_FUNCTION_BLOCK' + os.linesep
    	VAR_INPUT = 'VAR_INPUT'
    	VAR_OUTPUT = 'VAR_OUTPUT'
    	END_VAR = 'END_VAR'
    	FUZZIFY = 'FUZZIFY '
    	TERM = 'TERM '
    	DEFUZZIFY = 'DEFUZZIFY '
    	END_ = 'END_'
    	ACCU = 'ACCU : MAX;'
    	METHOD = 'METHOD : COGS;'
    	DEFAULT = 'DEFAULT := 1.0;'
    	RULEBLOCK = 'RULEBLOCK '
    	RULE = 'RULE '
    	_rules = '_rules'
    	tab = '\t'

        if file_name == None:
    	   fileName = self.currentFileFum
        else:
            fileName = file_name


    	file = open(fileName,'w')
    	varsIn = ''
    	varsOut = ''
    	fuzzyfy = ''
    	defuzzyfy = ''
    	ruleBlock = ''
    	file.write(FUNCTION_BLOCK + os.linesep*2)

        listVariables = self.CDS.fuzzySystem.variables.items()
        listVariables.sort(key=lambda x: x[0].upper())
    	for key, variable in listVariables:
            if isinstance(variable, fuzzy.OutputVariable.OutputVariable):
                varsOut = varsOut + tab + VAR_OUTPUT + os.linesep + (tab)*2 + key +  ':\tREAL;' + os.linesep + tab + END_VAR + (os.linesep*2)
            if isinstance(variable, fuzzy.InputVariable.InputVariable):
                varsIn = varsIn + tab + VAR_INPUT + os.linesep + (tab)*2 + key +  ':\tREAL;' + os.linesep + tab + END_VAR + (os.linesep*2)
            terms= ''
            terms2= ''
    	
            for key_lin, adjective in self.CDS.fuzzySystem.variables[key].adjectives.items():
                if isinstance(variable, fuzzy.InputVariable.InputVariable):
                    terms = terms + (tab*2) + TERM + key_lin + ' :=' + self.getTuple(self.CDS.fuzzySystem.variables[key].adjectives[key_lin].set.points) +' ;' + os.linesep
                if isinstance(variable, fuzzy.OutputVariable.OutputVariable):
                    terms2 = terms2 + (tab*2) + TERM + key_lin + ' :=' + self.getMax(self.CDS.fuzzySystem.variables[key].adjectives[key_lin].set.points) +' ;' + os.linesep
            
            if isinstance(variable, fuzzy.InputVariable.InputVariable):
                fuzzyfy = fuzzyfy + tab + FUZZIFY + key + os.linesep + terms + tab + END_ + FUZZIFY + (os.linesep*2)
            if isinstance(variable, fuzzy.OutputVariable.OutputVariable):
                defuzzyfy = defuzzyfy + tab + DEFUZZIFY + key  + os.linesep + terms2 + (tab*2) + ACCU + os.linesep + (tab*2) + METHOD + os.linesep + (tab*2) + DEFAULT + os.linesep + tab + END_ + DEFUZZIFY + (os.linesep*2) 
    			
    	
    	lr = self.CDS.get_list_rules()
        for group, rules in  lr.items():
            #print 'groupppp:', group
            i = 0
            rulesToWrite = ''
            for r in rules:
                #print 'regola:', r
                rulesToWrite = rulesToWrite + (tab*2) + RULE + str(i) + ': '  + self.CDS.rule_to_string(r) +';'  + os.linesep
                i = i +1
            if rulesToWrite != '':
                ruleBlock = ruleBlock + tab + RULEBLOCK + group + _rules + os.linesep  + rulesToWrite + tab + END_ + RULEBLOCK + (os.linesep)*2
    		
    	
    	file.write(varsIn)
    	file.write(varsOut)
    	file.write(fuzzyfy)
    	file.write(defuzzyfy)
    	file.write(ruleBlock)
    	file.write(END_FUNCTION_BLOCK)

    	
    	#file fuss
    	inizio = '# FCL file' + os.linesep + '../celde13.fcl' + os.linesep
    	groups = '# groups observed' + os.linesep
    	initialState = '# initial states' + os.linesep

    	simulationData= '# simulation data' + os.linesep + 'timemax	1.0	iterations	100'

    	for x in self.relations.keys():
            self.relations[x].sort(key=lambda x: x.upper())
            groups = groups + str(x) + tab + str(self.relations[x]) + os.linesep


    	for i in range(conditions.lenListStateNodes()):
            row = conditions.getItem(i)
            min = str(self.CDS.fuzzySystem.variables[row[0]].min)
            max = str(self.CDS.fuzzySystem.variables[row[0]].max)
            initialState = initialState + row[0] + tab + row[1] + tab + row[2] + tab + row[3] + tab + min + tab + max + os.linesep 

        file.write(inizio)
    	file.write(groups)
    	file.write(initialState)
    	file.write(simulationData)
    	
    
    ## Metodo che crea secondo la sintassi fcl i valori dei termini
    # @param self puntatore all'oggetto
    # @param coords lista di coordinate
    def getTuple(self, coords):
        tupla = ''
        for i in range(len(coords)):
        	tupla = tupla + ' (' + str(coords[i][0]) + ', ' + str(coords[i][1]) + ')'
        return tupla
    
    ## Metodo che ritorna il valore di default per un aggettivo secondo specifiche fcl
    # @param self puntatore all'oggetto
    # @param coords lista di coordinate
    def getMax(self, coords):
    	k = 0
    	if len(coords) == 3:
    		for i in range(len(coords)):
    			if coords[i][1] > coords[k][1]:
    				k = i
    		return str(coords[k][0])
    	else:
    		return str((coords[1][0] + coords[2][0])/2)             


if __name__ == '__main__':

    matplotlib.rcParams.update({'font.size': 8})

    app = QtGui.QApplication(sys.argv)
    
    # create dialogs
    groups =        Groups()
    conditions =    Conditions()
    settings =      Settings()    
    rulesviewer =   Rules() 
    nodeeditor =    Nodes()
    membershipeditor = Membership()   
    rulesEdit = RulesEdit()
    aboutFumoso = AboutFumoso()
    viewModel = ViewModel()

    window =        MyWindow()
    
    conditions.main_ref = window
    rulesviewer.main_ref = window
    nodeeditor.main_ref = window
    membershipeditor.main_ref = window
    settings.main_ref = window
    groups.main_ref = window
    rulesEdit.main_ref = window
    viewModel.main_ref = window
    
    
    #window.show()
    sys.exit(app.exec_())
