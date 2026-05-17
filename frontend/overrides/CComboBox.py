from PyQt5 import QtWidgets
from PyQt5 import QtCore


class CComboBox(QtWidgets.QComboBox):
    arrowClicked = QtCore.pyqtSignal()
    popupAboutToShow = QtCore.pyqtSignal()

    def showPopup(self):
        self.popupAboutToShow.emit()
        super().showPopup()
