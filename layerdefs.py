"""
A plugin for loading and saving QGIS Layer Definitions.  Layer Definitions are a new feature
found in upcoming QGIS 2.4 but this plugin brings the feature to the older 2.x releases.
"""
import os

from qgis.core import QgsVectorLayer, QgsRasterLayer, QgsMapLayerRegistry

from PyQt4.uic import loadUi
from PyQt4.QtCore import QDir
from PyQt4.QtGui import QAction, QFileDialog
from PyQt4.QtXml import QDomDocument

class LayerDefinitions(object):
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        # Create action that will start plugin configuration
        self.loadaction = QAction(u"Add from Layer Definition File...", self.iface.mainWindow())
        self.saveaction = QAction(u"Save as Layer Definition File...", self.iface.mainWindow())
        self.about = QAction(u"About", self.iface.mainWindow())
        # connect the action to the run method
        self.loadaction.triggered.connect(self.loadqlr)
        self.saveaction.triggered.connect(self.saveqlr)
        self.about.triggered.connect(self.showabout)

        self.iface.addPluginToMenu("Layer Definitions", self.saveaction)
        self.iface.addPluginToMenu("Layer Definitions", self.loadaction)
        self.iface.addPluginToMenu("Layer Definitions", self.about)

    def showabout(self):
        curpath = os.path.dirname(os.path.realpath(__file__))
        ui = loadUi(os.path.join(curpath, "ui_about.ui"))
        ui.exec_()

    def loadqlr(self):
        path = QFileDialog.getOpenFileName(self.iface.mainWindow(), "Add QGIS Layer Definition", QDir.home().path(), "*.qlr")
        if not path:
            return

        with open(path, 'r') as f:
            content = f.read()

        doc = QDomDocument()
        doc.setContent(content)
        layernode = doc.elementsByTagName('maplayer').at(0)
        layerelm = layernode.toElement()

        layertype = layerelm.attribute("type")
        layer = None
        if layertype == "vector":
            layer = QgsVectorLayer()
        elif layertype == 'raster':
            layer = QgsRasterLayer()

        ok = layer.readLayerXML(layerelm)
        if ok:
            QgsMapLayerRegistry.instance().addMapLayer(layer)

    def saveqlr(self):
        layer = self.iface.activeLayer()
        if not layer:
            return

        path = QFileDialog.getSaveFileName(self.iface.mainWindow(), "Save as QGIS Layer Definition", QDir.home().path(), "*.qlr")

        if not path:
            return

        doc = QDomDocument("qgis-layer-definition")
        mapnode = doc.createElement("maplayer")
        layer.writeLayerXML(mapnode, doc)
        mapnode.removeChild(mapnode.firstChildElement("id"))
        doc.appendChild(mapnode)

        with open(path, "w") as f:
            f.write(doc.toString())

    def unload(self):
        self.iface.removePluginMenu("Layer Definitions", self.saveaction)
        self.iface.removePluginMenu("Layer Definitions", self.loadaction)
