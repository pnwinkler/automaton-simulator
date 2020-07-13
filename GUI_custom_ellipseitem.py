# custom ellipse class to work as a state within the automaton
# uses parent (ellipse's) drawing and collision detection
# its only additions are state specific behavior and context options

from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QGraphicsEllipseItem, QAction
from PyQt5.QtWidgets import QMenu
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication
from PyQt5.QtGui import QIcon
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class custom_ellipse(QGraphicsEllipseItem):
    def __init__(self, *args, **kwargs):
        QGraphicsEllipseItem.__init__(self, *args, **kwargs)
        logger.debug("CUSTOM ELLIPSE ITEM CREATED")
        self.accepting = False
        self.initial = False

    def toggleInitial(self):
        self.initial = not self.initial
        
    def toggleAccepting(self):
        self.accepting = not self.accepting

    # def mouseReleaseEvent(self, event):
    #     # Do your stuff here.
    #     return QtGui.QGraphicsEllipseItem.mouseReleaseEvent(self, event)
    #
    # def hoverMoveEvent(self, event):
    #     # Do your stuff here.
    #     pass

    def contextMenuEvent(self, event):
        # add right click behavior (if relevant)
        # menu = QMenu(QGraphicsEllipseItem)
        menu = QMenu()
        '''
        # removing the parameter lets it spawn, but far away in the top left.
        # I need to determine: does the menu need to be child to the ellipse?
        # or just appear in the right place?
        # making it a child would allow for easier references to its parent
        # Docs say: 
            Although a popup menu is always a top-level widget, 
            if a parent is passed the popup menu will be deleted when
            that parent is destroyed (as with any other QObject).
        
        TypeError: arguments did not match any overloaded call:
        QMenu(parent: QWidget = None): argument 1 has unexpected type 'sip.wrappertype'
        QMenu(str, parent: QWidget = None): argument 1 has unexpected type 'sip.wrappertype'
        '''
        # note that actions can have icons and shortcuts. That might be nice.
        # delete_action = menu.addAction("Delete object")
        # delete_action.setStatusTip("Exit the program")
        # menu.addAction(delete_action)
        # move_action = menu.addAction("TK: Placeholder: Move state")
        # cancel_action = menu.addAction("Cancel")
        # # delete_action.triggered.connect(quit())
        # # needs a very specific format. Specifically a function (lambda or declared elsewhere). self.hide() by itself autotriggers.
        # # PLACEHOLDER
        # # idea is that I'll get the scene to handle deletion, given that it will involve deleting related items
        # # like transitions too
        # delete_action.triggered.connect(lambda x: self.parentWidget().delete_ellipse(self))
        #
        #
        # action = menu.exec(QPoint(self.pos().x(), self.pos().y()))

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
