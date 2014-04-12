#/*##########################################################################
# Copyright (C) 2004-2013 European Synchrotron Radiation Facility
#
# This file is part of the PyMca X-ray Fluorescence Toolkit developed at
# the ESRF by the Software group.
#
# This toolkit is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# PyMca is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# PyMca; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# PyMca follows the dual licensing model of Riverbank's PyQt and cannot be
# used as a free plugin for a non-free program.
#
# Please contact the ESRF industrial unit (industry@esrf.fr) if this license
# is a problem for you.
#############################################################################*/
import sys
from PyMca5.PyMcaGui import PyMcaQt as qt
QTVERSION = qt.qVersion()
DEBUG = 0

try:
    import PyMca5.Object3D
    OBJECT3D = True
except:
    OBJECT3D = False

class SpecFileCntTable(qt.QTableWidget):
    def __init__(self, parent=None):
        qt.QTableWidget.__init__(self, parent)
        self.cntList      = []
        self.mcaList      = []
        self.xSelection   = []
        self.ySelection   = []
        self.monSelection = []
        self.__is3DEnabled = False
        self.__is2DEnabled = False
        labels = ['Counter', 'X    ', 'Y    ', 'Mon']
        self.setColumnCount(len(labels))
        for i in range(len(labels)):
            item = self.horizontalHeaderItem(i)
            if item is None:
                item = qt.QTableWidgetItem(labels[i],
                                           qt.QTableWidgetItem.Type)
            item.setText(labels[i])
            self.setHorizontalHeaderItem(i,item)
        """
        #the cell is not the same as the check box
        #but I wonder about the checkboxes being destroyed
        qt.QObject.connect(self,
                     qt.SIGNAL("cellClicked(int, int)"),
                     self._mySlot)
        """

    def build(self, cntlist, nmca=None):
        if not OBJECT3D:
            nmca = 0
        nmca = 0
        if nmca is None:
            nmca = 0 
        self.cntList = cntlist
        self.mcaList = []
        n = len(cntlist)
        self.setRowCount(n)
        if n > 0:
            self.setRowCount(n + nmca)
            rheight = self.horizontalHeader().sizeHint().height()
            for i in range(n):
                self.setRowHeight(i, rheight)
                self.__addLine(i, cntlist[i])
                for j in range(1, 4, 1):
                    widget = self.cellWidget(i, j)
                    widget.setEnabled(True)
            for j in range(nmca):
                row = n+j
                self.setRowHeight(n+j, rheight)
                mca = "Mca %d" % (j+1)
                self.mcaList.append(mca)
                self.__addLine(n+j, self.mcaList[j])
                #the x checkbox
                widget = self.cellWidget(row, 1)
                widget.setChecked(False)
                widget.setEnabled(False)
                #the y checkbox
                widget = self.cellWidget(row, 2)
                widget.setChecked(False)
                widget.setEnabled(True)
                #the Monitor checkbox
                widget = self.cellWidget(row, 3)
                widget.setChecked(False)
                widget.setEnabled(False)
        else:
            self.setRowCount(0)

        self.resizeColumnToContents(1)
        self.resizeColumnToContents(2)
        self.resizeColumnToContents(3)
        
    def __addLine(self, i, cntlabel):
        #the counter name
        item = self.item(i, 0)
        if item is None:
            item = qt.QTableWidgetItem(cntlabel,
                                       qt.QTableWidgetItem.Type)
            item.setTextAlignment(qt.Qt.AlignHCenter | qt.Qt.AlignVCenter)
            self.setItem(i, 0, item)
        else:
            item.setText(cntlabel)
        #item is just enabled (not selectable)
        item.setFlags(qt.Qt.ItemIsEnabled)

        #the checkboxes
        for j in range(1, 4, 1):
            widget = self.cellWidget(i, j)
            if widget is None:
                widget = CheckBoxItem(self, i, j)
                self.setCellWidget(i, j, widget)
                qt.QObject.connect(widget,
                                   qt.SIGNAL('CheckBoxItemSignal'),
                                   self._mySlot)
            else:
                pass

    def set3DEnabled(self, value):
        self.__is2DEnabled = False
        if value:
            self.__is3DEnabled = True
            if len(self.xSelection) > 3:
                self.xSelection = self.xSelection[-3:]
        else:
            self.__is3DEnabled = False
            if len(self.xSelection) > 1:
                self.xSelection = [1 * self.xSelection[0]]                    
        self._update()

    def set2DEnabled(self, value):
        self.__is3DEnabled = False
        if value:
            self.__is2DEnabled = True
            if len(self.xSelection) > 2:
                self.xSelection = self.xSelection[-2:]
        else:
            self.__is2DEnabled = False
            if len(self.xSelection) > 1:
                self.xSelection = [1 * self.xSelection[0]]                    
        self._update()

    def _mySlot(self, ddict):
        row = ddict["row"]
        col = ddict["col"]
        if col == 1:
            if ddict["state"]:
                if row not in self.xSelection:
                    self.xSelection.append(row)
            else:
                if row in self.xSelection:
                    del self.xSelection[self.xSelection.index(row)]
            if (not OBJECT3D) or (not self.__is3DEnabled):
                if len(self.xSelection) > 2:
                    #that is to support mesh plots
                    self.xSelection = self.xSelection[-2:]
                if not self.__is2DEnabled:
                    if len(self.xSelection) > 1:
                        self.xSelection = self.xSelection[-1:]
            elif len(self.xSelection) > 3:
                self.xSelection = self.xSelection[-3:]

        if col == 2:
            if ddict["state"]:
                if row not in self.ySelection:
                    self.ySelection.append(row)
            else:
                if row in self.ySelection:
                    del self.ySelection[self.ySelection.index(row)]
        if col == 3:
            if ddict["state"]:
                if row not in self.monSelection:
                    self.monSelection.append(row)
            else:
                if row in self.monSelection:
                    del self.monSelection[self.monSelection.index(row)]
            if len(self.monSelection) > 1:
                self.monSelection = self.monSelection[-1:]
        self._update()

    def _update(self):
        for i in range(self.rowCount()):
            j = 1
            widget = self.cellWidget(i, j)
            if i in self.xSelection:
                if not widget.isChecked():
                    widget.setChecked(True)
            else:
                if widget.isChecked():
                    widget.setChecked(False)
            j = 2
            widget = self.cellWidget(i, j)
            if i in self.ySelection:
                if not widget.isChecked():
                    widget.setChecked(True)
            else:
                if widget.isChecked():
                    widget.setChecked(False)
            j = 3
            widget = self.cellWidget(i, j)
            if i in self.monSelection:
                if not widget.isChecked():
                    widget.setChecked(True)
            else:
                if widget.isChecked():
                    widget.setChecked(False)
        ddict = {}
        ddict["event"] = "updated"
        self.emit(qt.SIGNAL('SpecCntTableSignal'), ddict)        
        

    def getCounterSelection(self):
        ddict = {}
        ddict['cntlist'] = self.cntList * 1
        ddict['mcalist'] = self.mcaList * 1
        ddict['x']       = self.xSelection * 1
        ddict['y']       = self.ySelection * 1
        ddict['m'] = self.monSelection * 1        
        return ddict

    def setCounterSelection(self, ddict):
        keys = ddict.keys()
        if 'cntlist' in keys: cntlist = ddict['cntlist']
        else: cntlist = self.cntList * 1

        if 'x' in keys: x = ddict['x']
        else: x = []

        if 'y' in keys: y = ddict['y']
        else: y = []

        if 'm' in keys: monitor = ddict['m']
        else: monitor = []

        self.xSelection = []
        for item in x:
            if item < len(cntlist):
                counter = cntlist[item]
                if 0:
                    if counter in self.cntList:
                        self.xSelection.append(self.cntList.index(counter))
                else:
                    self.xSelection.append(item)

        self.ySelection = []
        for item in y:
            if item < len(cntlist):
                counter = cntlist[item]
                if counter in self.cntList:
                    self.ySelection.append(self.cntList.index(counter))
        self.monSelection = []
        for item in monitor:
            if item < len(cntlist):
                counter = cntlist[item]
                if counter in self.cntList:
                    self.monSelection.append(self.cntList.index(counter))
        self._update()
        

class CheckBoxItem(qt.QCheckBox):
    def __init__(self, parent, row, col):
        qt.QCheckBox.__init__(self, parent)
        self.__row = row
        self.__col = col
        qt.QObject.connect(self, qt.SIGNAL("clicked(bool)"), self._mySignal)

    def _mySignal(self, value):
        ddict = {}
        ddict["event"] = "clicked"
        ddict["state"] = value
        ddict["row"] = self.__row * 1
        ddict["col"] = self.__col * 1
        self.emit(qt.SIGNAL('CheckBoxItemSignal'), ddict)

def main():
    app = qt.QApplication([])
    tab = SpecFileCntTable()
    tab.build(["Cnt1", "Cnt2", "Cnt3"])
    tab.setCounterSelection({'x':[1, 2], 'y':[4], 'cntlist':["dummy", "Cnt0", "Cnt1", "Cnt2", "Cnt3"]})
    tab.show()
    app.exec_()

if __name__ == "__main__":
    main()
    
