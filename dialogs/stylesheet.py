#    Copyright (C) 2009 Jeremy S. Sanders
#    Email: Jeremy Sanders <jeremy@jeremysanders.net>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
###############################################################################

# $Id: $

import os.path

import veusz.utils as utils
import veusz.qtall as qt4
import veusz.document as document
from veusz.windows.treeeditwindow import TabbedFormatting, PropertyList

class StylesheetDialog(qt4.QDialog):
    """This is a dialog box to edit stylesheets.
    Most of the work is done elsewhere, so this doesn't do a great deal
    """

    def __init__(self, parent, document):
        qt4.QDialog.__init__(self, parent)
        qt4.loadUi(os.path.join(utils.veuszDirectory, 'dialogs',
                                'stylesheet.ui'),
                   self)
        self.document = document
        self.stylesheet = document.basewidget.settings.StyleSheet

        self.stylesListWidget.setMinimumWidth(100)

        # initial properties widget
        self.tabformat = None
        self.properties = None

        self.fillStyleList()

        self.connect(self.stylesListWidget,
                     qt4.SIGNAL(
                'currentItemChanged(QListWidgetItem *,QListWidgetItem *)'),
                     self.slotStyleItemChanged)

        self.stylesListWidget.setCurrentRow(0)

        close = self.buttonBox.button(qt4.QDialogButtonBox.Close)
        close.setDefault(False)
        close.setAutoDefault(False)

        exportButton = qt4.QPushButton("Export...")
        exportButton.setDefault(False)
        exportButton.setAutoDefault(False)
        self.buttonBox.addButton(exportButton, qt4.QDialogButtonBox.ActionRole)
        self.connect(exportButton, qt4.SIGNAL('clicked()'),
                     self.slotExportStyleSheet)

        importButton = qt4.QPushButton("Import...")
        importButton.setDefault(False)
        importButton.setAutoDefault(False)
        self.buttonBox.addButton(importButton, qt4.QDialogButtonBox.ActionRole)
        self.connect(importButton, qt4.SIGNAL('clicked()'),
                     self.slotImportStyleSheet)

    def fillStyleList(self):
        """Fill list of styles."""
        for stns in self.stylesheet.getSettingsList():
            item = qt4.QListWidgetItem(utils.getIcon(stns.pixmap),
                                       stns.usertext)
            item.VZsettings = stns
            self.stylesListWidget.addItem(item)

    def slotStyleItemChanged(self, current, previous):
        """Item changed in list of styles."""
        if current is None:
            return

        if self.tabformat:
            self.tabformat.deleteLater()
        if self.properties:
            self.properties.deleteLater()

        style = str(current.text())
        settings = current.VZsettings

        # update formatting properties
        self.tabformat = TabbedFormatting(self.document, settings)
        self.formattingGroup.layout().addWidget(self.tabformat)

        # update properties
        self.properties = PropertyList(self.document, showsubsettings=False)
        self.properties.updateProperties(settings, showformatting=False)
        self.propertiesScrollArea.setWidget(self.properties)

    def slotExportStyleSheet(self):
        """Export stylesheet as a file."""
    
        filename = self.parent()._fileSaveDialog(
            'vst', 'Veusz stylesheet', 'Export stylesheet')
        if filename:
            try:
                f = open(filename, 'w')
            except IOError:
                qt4.QMessageBox("Veusz",
                                "Cannot export stylesheet as '%s'" % filename,
                                qt4.QMessageBox.Critical,
                                qt4.QMessageBox.Ok | qt4.QMessageBox.Default,
                                qt4.QMessageBox.NoButton,
                                qt4.QMessageBox.NoButton,
                                self).exec_()
                return
            
            self.document.exportStyleSheet(f)
            
    def slotImportStyleSheet(self):
        """Import a style sheet."""
        filename = self.parent()._fileOpenDialog(
            'vst', 'Veusz stylesheet', 'Import stylesheet')
        if filename:
            self.document.applyOperation(
                document.OperationImportStyleSheet(filename) )