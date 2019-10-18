# replace SVG stuff with subclassed QGraphicsItem + QPainterPath
# the latter will handle collision detection
# the former we choose because it's the best fit (we're not using SVGs any more)
import typing

from PyQt5.QtWidgets import QGraphicsItem, QGraphicsEllipseItem, QStyleOptionGraphicsItem, QWidget
from PyQt5.QtCore import QRect, QRectF
from PyQt5.QtGui import QPainter, QPainterPath

class state_graphic(QGraphicsItem):
    def __init__(self, *args, **kwargs):
        QGraphicsItem.__init__(self, *args, **kwargs)
        # self.setup_initial_graphic(coords_tpl)
        print("CUSTOM GRAPHICSITEM CREATED")
        # self.bounding = coords_tpl

    # CURRENTLY UNUSED
    def setup_initial_graphic(self, coords_tpl):
        # create an ellipse item, or set properties
        # is this confused? Should state_graphic class be the graphic?
        # and this stuff below is a new, separate creation?
        self.ellipse = QGraphicsEllipseItem()
        self.ellipse.setRect(coords_tpl)
        # self.state = QGraphicsItem.

    def boundingRect(self) -> QRectF:
        # PLACEHOLDER! REPLACE!!
        # until this is replaced with proper values,
        # collision detection will be fucked
        self.zxc = QGraphicsEllipseItem()
        # the reason why this is registering as collision is because
        # it's in the same place as our new object (class) here
        # I think
        self.zxc.setRect(50,50,120,120)
        return self.zxc.boundingRect()
        return QRectF(50,50,100,100)


    def paint(self, painter: QPainter, option: 'QStyleOptionGraphicsItem', widget: typing.Optional[QWidget] = ...) -> None:
        # PLACEHOLDER! REPLACE!!
        painter.drawEllipse(50,50,120,120)

    def contextMenuEvent(self, event):
        # add right click behavior (if relevant)
        pass