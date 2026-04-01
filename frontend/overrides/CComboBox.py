from pyqtgraph.Qt import QtWidgets
from pyqtgraph.Qt import QtCore


class CComboBox(QtWidgets.QComboBox):
    arrowClicked = QtCore.Signal()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        opt = QtWidgets.QStyleOptionComboBox()
        self.initStyleOption(opt)
        sub_control = self.style().hitTestComplexControl(
            QtWidgets.QStyle.CC_ComboBox, opt, event.pos(), self
        )
        if sub_control == QtWidgets.QStyle.SC_ComboBoxArrow:
            self.arrowClicked.emit()