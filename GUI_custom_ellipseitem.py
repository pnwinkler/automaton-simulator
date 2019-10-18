# replace SVG stuff with subclassed Ellipse item
import typing

from PyQt5.QtWidgets import QGraphicsEllipseItem, QStyleOptionGraphicsItem, QWidget
from PyQt5.QtCore import QRect, QRectF
from PyQt5.QtGui import QPainter, QPainterPath

class custom_ellipse(QGraphicsEllipseItem):
    def __init__(self, *args, **kwargs):
        QGraphicsEllipseItem.__init__(self, *args, **kwargs)
        # self.setup_initial_graphic(coords_tpl)
        print("CUSTOM ELLIPSEITEM CREATED")
        # self.bounding = coords_tpl

    # CURRENTLY UNUSED
    def setup_initial_graphic(self, coords_tpl):
        # create an ellipse item, or set properties
        # is this confused? Should state_graphic class be the graphic?
        # and this stuff below is a new, separate creation?
        self.ellipse = QGraphicsEllipseItem()
        self.ellipse.setRect(coords_tpl)
        # self.state = QGraphicsItem.

    # def boundingRect(self) -> QRectF:
    #     # PLACEHOLDER! REPLACE!!
    #     # in this class, no matter the value, this doesn't seem to do anything
    #     return QRectF(50,50,190,190)
    #     return QGraphicsEllipseItem.boundingRect(self)

    def contextMenuEvent(self, event):
        # add right click behavior (if relevant)
        pass