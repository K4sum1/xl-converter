from PySide2.QtGui import QWheelEvent
from PySide2.QtWidgets import QSpinBox, QDoubleSpinBox

class SpinBox(QSpinBox):
    def wheelEvent(self, e: QWheelEvent) -> None:
        e.ignore()

class DoubleSpinBox(QDoubleSpinBox):
    def wheelEvent(self, e: QWheelEvent) -> None:
        e.ignore()