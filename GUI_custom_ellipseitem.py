# custom ellipse class to work as a state within the automaton
# uses parent (ellipse's) drawing and collision detection
# its only additions are state specific behavior and context options

from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QGraphicsEllipseItem
from PyQt5.QtWidgets import QMenu

class custom_ellipse(QGraphicsEllipseItem):
    def __init__(self, *args, **kwargs):
        QGraphicsEllipseItem.__init__(self, *args, **kwargs)
        print("CUSTOM ELLIPSE ITEM CREATED")
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
    def toggleAccepting(self):
        # looks to self.accepting to determine whether to enable or disable
        # changes the onscreen graphic, then updates the self.accepting property

        # if not accepting, add an ellipse inside the current ellipse
        # and disable its collision detection (if possible / feasible)
        # maybe group the two? Idk - look into it
        x_pos = self.boundingRect().x()
        y_pos = self.boundingRect().y()
        w = self.boundingRect().size().width()
        h = self.boundingRect().size().height()

        # UNFINISHED and UNTESTED
        # Idea is that we create an inner ellipse, then group the two objects
        # or redraw or whatever
        # placeholder values
        self.NEW = QGraphicsEllipseItem(1.1* x_pos, 1.1* y_pos, 0.5 * w, 0.5* h)

        pass

    def toggleInitial(self):
        pass

    def getCentre(self):
        # returns the x,y coords of this item's centre as a tuple
        # might not be exact, but it's close.
        br = self.boundingRect()
        x_centre = br.x() + 0.5 * br.width()
        y_centre = br.y() + 0.5 * br.height()
        return (x_centre,y_centre)
