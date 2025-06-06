import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QPushButton,
                             QAction, QMenu)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
import PyQt5.QtCore.QObject



class App(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 menu - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 400
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        editMenu = mainMenu.addMenu('Edit')
        viewMenu = mainMenu.addMenu('View')
        searchMenu = mainMenu.addMenu('Search')
        toolsMenu = mainMenu.addMenu('Tools')
        helpMenu = mainMenu.addMenu('Help')
        
        exitButton = QAction(QIcon('exit24.png'), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close)
        fileMenu.addAction(exitButton)
        self.createActions()

        self.show()
        PyQt5.QtCore.QObject
    
    def contextMenuEvent(self, event):
        print("Clicked ")
        popUpMenu = QMenu()
        popUpMenu.addAction(self.my_act)

        popUpMenu.exec_(event.globalPos())

    def createActions(self):   
        self.my_act = QAction("&Display Image", self,
            shortcut=self.tr("Ctrl+D"),
            statusTip="Display current selected image", 
            triggered=self.my_slot)

    def my_slot(self):
        print("my_slot ") 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
