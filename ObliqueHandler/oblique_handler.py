# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ObliqueHandler
                                 A QGIS plugin
 Oblique Handler lets you work with Oblique images
                              -------------------
        begin                : 2018-01-28
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Danish National Mapping Authority (sdfe.dk)
        email                : anfla@sdfe.dk
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import urllib2

# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from oblique_handler_dialog import ObliqueHandlerDialog
import os.path
from qgis.gui import QgsMapToolEmitPoint
from oblique_handler_settings import ObliqueHandlerSettings, ObliqueHandlerSettingsDialog
import webbrowser


class ObliqueHandler:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'ObliqueHandler_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Oblique Handler')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'ObliqueHandler')
        self.toolbar.setObjectName(u'ObliqueHandler')

        #set mapclicktool
        self.canvas = self.iface.mapCanvas()
        self.clickTool = QgsMapToolEmitPoint(self.canvas)
        QObject.connect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.open_oblique_web)

        # Settings dialog etc.
        self.settings = ObliqueHandlerSettings()
        self.settings_dlg = ObliqueHandlerSettingsDialog(self.settings)
        #self.add_setting(String('user', Scope.Global, 'fotoflyvning'))
        #self.add_setting(String('pass', Scope.Global, 'Paeren42!'))

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('ObliqueHandler', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = ObliqueHandlerDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)



        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        # icon_path = ':/plugins/ObliqueHandler/icon.png'
        # self.add_action(
        #     icon_path,
        #     text=self.tr(u'ObliqueHandler'),
        #     callback=self.run,
        #     parent=self.iface.mainWindow())

        icon_path = ':/plugins/ObliqueHandler/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Find obliques'),
            callback=self.coo_measure,
            parent=self.iface.mainWindow())

        self.add_action(
            None,
            text=self.tr(u'Settings'),
            add_to_toolbar=False,
            callback=self.open_settings,
            parent=self.iface.mainWindow()
        )

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Oblique Handler'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def open_settings(self):
        self.settings_dlg.show()

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def coo_measure(self):

        self.canvas.setMapTool(self.clickTool)

        pass

    def getCadaster(self,x,y):
        #QMessageBox.information(None, "geometritype", str(x)+str(y))

        matURL = "https://services.kortforsyningen.dk?servicename=RestGeokeys_v2&method=matrikelnr&geop={matrx},{matry}&geometry=true&login={user}&password={passw}".format(
            matrx=x,
            matry=y,
            #user='fotoflyvning',
            #passw='Paeren42!'
            user=self.settings.value('KFuser'),
            passw=self.settings.value('KFpass')
        )

        ejrKode = ''
        matNr = ''
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        respone = opener.open(matURL)
        svar = respone.read()
        #QMessageBox.information(None, "geometritype",svar)

        ffe = svar.split('\n')
        for i in ffe:
            u = i.lstrip().strip(",").split(' ')

            if (u[0] == '"ejerlav_kode":'):
                ejrKode = u[1]
            if (u[0] == '"matnr":'):
                matNr = u[1].strip("\"")

        return (ejrKode, matNr)

    def open_oblique_web(self,point):
        #self.canvas.setMapTool(QgsMapToolPan(self.canvas))
        x=point.x()
        y=point.y()

        matt = self.getCadaster(x,y)
        ejrKode = matt[0]
        matNr = matt[1]
        #QMessageBox.information(None, "geometritype", 'x:'+ str(x)+'y='+str(y))
        #URL = 'http://www.idansoft.com/oblivisionJS/index.aspx?project=nakskov&x='+str(x)+'&y='+str(y)
        #URL = 'http://load195.kmsext.dk/oblivisionjs/index.aspx?project=denmark&background=1&x='+str(x)+'&y='+str(y)
        URL = 'https://skraafoto.kortforsyningen.dk/oblivisionjs/index.aspx?project=Denmark&x='+str(x)+'&y='+str(y)+'&parcels='+ejrKode+'-'+matNr
        webbrowser.open_new(URL)