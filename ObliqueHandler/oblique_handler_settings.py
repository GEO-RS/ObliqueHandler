
# -*- coding: utf-8 -*-
import os

from PyQt4 import QtGui, uic
from qgissettingmanager import SettingManager, SettingDialog
from qgissettingmanager.types import String
from qgissettingmanager.setting import Scope

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), 'oblique_handler_settings.ui')
)

class ObliqueHandlerSettings(SettingManager):
    def __init__(self):
        SettingManager.__init__(self, 'ObliqueHandler')
        self.add_setting(String('KFuser', Scope.Global, ''))
        self.add_setting(String('KFpass', Scope.Global, ''))


class ObliqueHandlerSettingsDialog(QtGui.QDialog, FORM_CLASS, SettingDialog):
    def __init__(self, settings):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        SettingDialog.__init__(self, settings)