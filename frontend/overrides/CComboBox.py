from PyQt5 import QtCore, QtWidgets


class CComboBox(QtWidgets.QComboBox):
    popupAboutToShow = QtCore.pyqtSignal()

    def showPopup(self):
        self.popupAboutToShow.emit()
        super().showPopup()
