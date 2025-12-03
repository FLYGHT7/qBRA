from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.core import QgsApplication
from qgis.utils import iface

import os

class QbraIlsLlzPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.plugin_dir = os.path.dirname(__file__)

    def tr(self, message):
        return QCoreApplication.translate('QbraIlsLlzPlugin', message)

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, 'resources', 'icon.png')
        self.action = QAction(QIcon(icon_path), self.tr('ILS LLZ (Single Freq)'), self.iface.mainWindow())
        self.action.setToolTip(self.tr('Ejecutar cálculo ILS LLZ'))
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(self.tr('qBRA'), self.action)

    def unload(self):
        if self.action:
            self.iface.removeToolBarIcon(self.action)
            self.iface.removePluginMenu(self.tr('qBRA'), self.action)

    def run(self):
        try:
            # Lógica stub: llamar al módulo del plugin (buenas prácticas)
            from .module.run_ils_llz import run_ils_llz_single_frequency
            count = run_ils_llz_single_frequency()
            QMessageBox.information(self.iface.mainWindow(), self.tr('Resultado'), self.tr(f'Ejecución completada. Salidas: {count}'))
        except Exception as e:
            QMessageBox.critical(self.iface.mainWindow(), self.tr('Error'), str(e))
