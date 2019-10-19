# custom ellipse class to work as a state within the automaton
# uses parent (ellipse's) drawing and collision detection
# its only additions are state specific behavior and context options
import typing

from PyQt5.QtWidgets import QGraphicsEllipseItem
from PyQt5.QtWidgets import QMenu

class custom_ellipse(QGraphicsEllipseItem):
    def __init__(self, *args, **kwargs):
        QGraphicsEllipseItem.__init__(self, *args, **kwargs)
        # self.setup_initial_graphic(coords_tpl)
        print("CUSTOM ELLIPSE ITEM CREATED")
        # self.bounding = coords_tpl
        self.accepting = False
        self.initial = False

    def contextMenuEvent(self, event):
        # add right click behavior (if relevant)
        menu = QMenu(QGraphicsEllipseItem)
        delete_action = menu.addAction("Delete object")
        move_actionl = menu.addAction("TK: Placeholder: Move state")
        cancel_action = menu.addAction("Cancel")

        action = menu.exec(QPoint(self.pos().x(), self.pos().y()))

    # todo: code methods to toggle accepting, initial states
    # and represent them, too (logically)
    