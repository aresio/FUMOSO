#coding=utf-8
## @package maingui
#  Questo modulo contiene le classi per la creazioni di plot riguardanti Gruppi, Membership, Regole 
import sys
from PyQt4 import QtGui, QtCore, uic
sys.path.insert(0, "..")
from FuzzySimulator import *
import copy
import random
import ConfigParser
import collections
import tempfile


# matplotlib stuff
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import os

class PlotWindow(QtGui.QMdiSubWindow):
 
    def __init__(self, parent = None):
        QtGui.QMdiSubWindow.__init__(self, parent)
        self.main_frame = QtGui.QWidget()
        vbox = QtGui.QVBoxLayout()
        self.canvas = GraphCanvas()
        vbox.addWidget(self.canvas)
        self.main_frame.setLayout(vbox)
        self.setWidget(self.main_frame)

        self._want_to_close = False

    def closeEvent(self, evnt):
        if self._want_to_close:
            super(MyDialog, self).closeEvent(evnt)
        else:
            evnt.ignore()
            self.setWindowState(QtCore.Qt.WindowMinimized)



class PlotWindowMF(QtGui.QMdiSubWindow):
 
    def __init__(self, parent = None, MFname=""):
        QtGui.QMdiSubWindow.__init__(self, parent)
        self.main_frame = QtGui.QWidget()
        vbox = QtGui.QVBoxLayout()
        self.canvas = GraphCanvasMF()
        vbox.addWidget(self.canvas)
        self.main_frame.setLayout(vbox)
        self.setWidget(self.main_frame)

        self._want_to_close = False
        self.main_app_ref = parent
        self.MF = MFname

        self.main_frame.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.main_frame.customContextMenuRequested.connect(self.popup)

    def popup(self, pos):
        menu = QtGui.QMenu()
        quitAction = menu.addAction("&Save figure...")
        
        action = menu.exec_(self.mapToGlobal(pos))
        if action == quitAction:
            outputfile = QtGui.QFileDialog.getSaveFileName(self, "Please choose a destination file", "", "Portable Network Graphics (*.png)")
            outputfile = str(outputfile)
            if outputfile != None:
                self.main_app_ref.save_figure_MF(self.MF)
        


    def closeEvent(self, evnt):
        if self._want_to_close:
            super(MyDialog, self).closeEvent(evnt)
        else:
            evnt.ignore()
            self.setWindowState(QtCore.Qt.WindowMinimized)


""" Main output simulation """
class GraphCanvas(FigureCanvas):

    def __init__(self, parent=None, dpi=100):

        self.fig = Figure(dpi=dpi)                
        self.axes = self.fig.add_subplot(111)        
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.init_variables()


    def init_variables(self):
        self.markers=[]
        for m in Line2D.markers:
            try:
                if len(m) == 1 and m != ' ':
                    self.markers.append(m)
            except TypeError:
                pass
        self.group=[]
        self.title=""
        self.data={}
        self.mtime = 0
        self.iters = 0

    def drawGraph(self, group=[], title="", data={}, mtime=1.0, iters=10, 
        ctime=0.0, dict_markers={}, dict_colors={}):
        
        self.group = group
        self.title = title
        self.data  = data
        self.mtime = mtime
        self.iters = iters

        # print " * Plotting ", self.group

        self.axes.cla()
        if data ==[]:
            self.axes.plot([],[],label='No nodes for this group ')
            self.draw()
            return


        values = range(len(group))
        jet = cm = plt.get_cmap('jet') 
        cNorm  = Normalize(vmin=0, vmax=values[-1])
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)

        xax = linspace(0, mtime, iters)
    
        for numtest, variabile in enumerate(group):
            #colorVal = scalarMap.to_rgba(values[numtest])            
            # markerVal = self.markers[numtest%len(self.markers)]                
            try:
                colorVal = dict_colors[variabile]
                #self.axes.plot(xax, data[variabile], "o-", label=variabile, color= colorVal, marker=markerVal, markersize=4)
                self.axes.plot(xax, data[variabile], "o-", label=variabile, color= colorVal, marker=dict_markers[variabile], markersize=4)
                #self.axes.plot(xax, data[variabile], "o-", label=variabile, color= colorVal, markersize=4)
            except:
                print "WARNING: cannot find data for", variabile,"(maybe the species does not belong to the model any longer?)"
                #self.axes.plot(xax, data[variabile], "o-", label=variabile, color= colorVal, marker=dict_markers[variabile], markersize=4)

        self.axes.legend(prop={'size': 6.5}, loc='best' )
        self.axes.set_ylabel("Level [a.u.]")
        self.axes.set_xlabel("Time [a.u.]")
        self.fig.canvas.mpl_connect('motion_notify_event', self.onMove)


        # self.fig.tight_layout()
        self.axes.set_title(title)
        self.axes.set_ylim(0, 1)
        self.axes.set_xlim(0, self.mtime)

        self.axes.plot([ctime, ctime], [0,self.mtime], "--", lw=1, color="gray")
        
        self.draw()
        self.background = self.fig.canvas.copy_from_bbox(self.axes.bbox)


    """ Detect mouse movement """
    def onMove(self, event):
        return

        # cursor moves on the canvas
        if event.inaxes:

            # restore the clean background
            self.fig.canvas.restore_region(self.background)
            ymin, ymax = self.axes.get_ylim()
            x = event.xdata - 1

            # draw each vertical line
            for line in self.verticalLines:
                line.set_xdata((x,))
                line.set_ydata((ymin, ymax))
                self.axes.draw_artist(line)
                x += 1

            self.fig.canvas.blit(self.axes.bbox)



class GraphCanvasMF(FigureCanvas):

    def __init__(self, parent=None, dpi=100):

        self.fig = Figure(dpi=dpi)        
        self.axes = self.fig.add_subplot(111)        
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.init_variables()


    def init_variables(self):
        self.markers=[]
        for m in Line2D.markers:
            try:
                if len(m) == 1 and m != ' ':
                    self.markers.append(m)
            except TypeError:
                pass
        self.group=[]
        self.title=""
        self.data={}
        self.mtime = 0
        self.iters = 0


    def drawGraph(self, attribute=None, title="", CDS=None, iteration=1):

        if CDS==None or attribute==None:
            print "WARNING: cannot plot membership without a fuzzy system"
            return
        self.title = title
        self.attribute = attribute

        self.axes.cla()        
        # CDS.plot_all_membership(self.attribute, ax=self.axes)
        CDS.plot_precalculated_membership(self.attribute, ax=self.axes, iteration=iteration)
        self.draw()
        self.background = self.fig.canvas.copy_from_bbox(self.axes.bbox)


    """ Detect mouse movement """
    def onMove(self, event):
        return

        # cursor moves on the canvas
        if event.inaxes:

            # restore the clean background
            self.fig.canvas.restore_region(self.background)
            ymin, ymax = self.axes.get_ylim()
            x = event.xdata - 1

            # draw each vertical line
            for line in self.verticalLines:
                line.set_xdata((x,))
                line.set_ydata((ymin, ymax))
                self.axes.draw_artist(line)
                x += 1

            self.fig.canvas.blit(self.axes.bbox)


class GraphCanvasRules(FigureCanvas):

    def __init__(self, parent=None, dpi=100, statusbar_ref=None, figsize=None):

        self.fig = Figure(dpi=dpi, figsize=figsize)
        FigureCanvas.__init__(self, self.fig)
        # self.notifyProgress = QtCore.pyqtSignal(float)
        self.statusbar=statusbar_ref
        self.dpi = dpi


    def drawGraph(self, title="", rules=None, CDS=None, iteration=1):

        if CDS==None:
            print "WARNING: cannot plot membership without a fuzzy system"
            return

        if rules==[]:
            self.fig.clf()        
            ax = self.fig.add_subplot(1,1,1)
            ax.text(0.1,0.5,"No rules for this node")
            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)
            self.draw()
            return

        if len(filter(lambda x: x[0]==title, CDS.updaters))!=0:
            self.fig.clf()        
            ax = self.fig.add_subplot(1,1,1)
            ax.text(0.1,0.5,"Custom function defined for this node")
            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)
            self.draw()
            return

        # self.fig = Figure(dpi=self.dpi, figsize=(len(rules)*2,len(rules)))


        self.statusbar.show()

        ROWS = len(rules)+1

        antecedents = set()
        consequents = set()

        # I calculate the WHOLE sets of antecedents and consequents
        for r in rules:
            CDS.get_set_antecedents(antecedents, r[1].operator)
            CDS.get_set_consequents(consequents, r[1].adjective)

        filtered_antecedents = set()
        for x in antecedents:
            if not x==None:
                nome = x.adjective.getName(CDS.fuzzySystem)[1]
                filtered_antecedents.add(nome)

        seq_antecedents = {}
        list_ordered_antecedents = list(filtered_antecedents)
        for n,x in enumerate(list_ordered_antecedents):
            # seq_antecedents[x]=n
            seq_antecedents[n]=x
        
        
        filtered_consequents = set()
        for x in consequents:
            if not x==None:
                nome = x.getName(CDS.fuzzySystem)[1]
                filtered_consequents.add(nome)

        seq_consequents = {}
        list_ordered_consequents = list(filtered_consequents)
        for n,x in enumerate(list_ordered_consequents):
            seq_consequents[x]=n

        # print "seq cons", seq_consequents
    

        TYPES_ANT = len(filtered_antecedents)     
        TYPES_CON = len(filtered_consequents)
        COLUMNS = TYPES_ANT+TYPES_CON

        print " * Number or rows in the figure:", ROWS
        print " * Number or columns in the figure:", COLUMNS
        print " * Creating rules plot"

        self.fig.clf()        
        self.fig.suptitle(title, fontsize=12)

        for r in xrange(1,ROWS+1):

            cont = 0
            cont2 = 0
            best = sys.float_info.max
            la = []
            if r<ROWS: CDS.get_list_antecedents(la, rules[r-1][1].operator)

            lc = []
            if r<ROWS: CDS.get_list_consequents(lc, rules[r-1][1].adjective)

            allowed_ants = []
            for a in la:
                name = CDS.get_adj_name_from_antecedent(a)
                p = list_ordered_antecedents.index(name)
                allowed_ants.append(p)


            allowed_cons = []
            for c in lc:
                name = CDS.get_adj_name_from_consequent(c)
                p = list_ordered_consequents.index(name)
                allowed_cons.append(p)

            list2ant = {}
            for a in la:
                name = CDS.get_adj_name_from_antecedent(a)
                list2ant[name]=a

            list2con = {}
            for c in lc:
                name = CDS.get_adj_name_from_consequent(c)
                list2con[name]=c


            # print antecedents
            for colonna in xrange(TYPES_ANT):
                
                n = (r-1)*COLUMNS+(colonna)+1                    
                ax = self.fig.add_subplot(ROWS, COLUMNS, n)
                
                # remove subplots unused by rules
                if not colonna in allowed_ants:
                    ax.get_xaxis().set_visible(False)
                    ax.get_yaxis().set_visible(False)
                    ax.axis('off')
                else:                    
                    # temp = la[cont].adjective.getName(CDS.fuzzySystem)
                    temp = list2ant[seq_antecedents[colonna]].adjective.getName(CDS.fuzzySystem)
                    attribute = temp[1]
                    adjective = temp[0]
                    value = CDS.whole_memberships[attribute][iteration][adjective]
                    if value<best: best = value
                    CDS.plot_single_precalculated_membership(attribute=attribute, adjective=adjective, value=value, ax=ax)
                    cont+=1
                
                # print headers
                if r==1:
                    ax.text(0,1.1,seq_antecedents[colonna],fontsize=8)

            # print consequents
            for colonna in xrange(TYPES_CON):
                n = (r-1)*COLUMNS+(colonna+TYPES_ANT)+1                    
                ax = self.fig.add_subplot(ROWS, COLUMNS, n)

                if r<ROWS:
                    ax.set_xlim(0,1)
                    value = lc[cont2].set.getCOG()
                    CDS.plot_defuzzified_value_sugeno(value, best, ax)
                    cont2 +=1
                else:
                    ax = self.fig.add_subplot(ROWS, COLUMNS, n)
                    ax.set_xlim(0,1)
                    CDS.plot_actual_value(CDS.whole_dynamics[title][iteration], ax)                    
                    
            percentage = 100*float(r-1)/(ROWS)
            if self.statusbar!=None: self.statusbar.setValue(percentage)                    

            continue
            
        self.fig.tight_layout()
        self.fig.subplots_adjust(top=0.9, left=None, right=None, bottom=None, wspace=0.2, hspace=0.2)
        self.draw()
        

        self.statusbar.setValue(100)        
        print  " * Finished plotting rules"
        self.statusbar.hide()

    """ Detect mouse movement """
    def onMove(self, event):
        return

        # cursor moves on the canvas
        if event.inaxes:

            # restore the clean background
            self.fig.canvas.restore_region(self.background)
            ymin, ymax = self.axes.get_ylim()
            x = event.xdata - 1

            # draw each vertical line
            for line in self.verticalLines:
                line.set_xdata((x,))
                line.set_ydata((ymin, ymax))
                self.axes.draw_artist(line)
                x += 1

            self.fig.canvas.blit(self.axes.bbox)
