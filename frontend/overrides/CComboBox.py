from PyQt5 import QtWidgets
from PyQt5 import QtCore


class CComboBox(QtWidgets.QComboBox):
    arrowClicked = QtCore.pyqtSignal()
    popupAboutToShow = QtCore.pyqtSignal()

    def showPopup(self):
        self.popupAboutToShow.emit()
        super().showPopup()
    #     QtCore.QTimer.singleShot(0, self.popup_proxy)
    #
    # def popup_proxy(self):
    #     view = self.view()
    #     view.setTextElideMode(QtCore.Qt.TextElideMode.ElideRight)
    #     popup_widget = view.window()
    #     popup_proxy = popup_widget.graphicsProxyWidget()
    #     popup_proxy.setFlag(
    #         QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations,
    #         True,
    #     )
    #     popup_widget.update()
