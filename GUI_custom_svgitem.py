# contains the code for custom SVG objects (states and arrows)
# includes code for boundary setting etc
# SUBCLASS FURTHER? can name them differently too?
# could allow us to get rid of the property tags which we're using
# factory?
# review this later. For now, there are simplier things that need improving

from PyQt5 import QtSvg
from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QMenu

class svgItem_mod(QtSvg.QGraphicsSvgItem):
    def __init__(self, parent):
        QtSvg.QGraphicsSvgItem.__init__(self, parent)
        self.wants_to_be_deleted = False

    # could add a function like setStateProperties or setArrowProperties
    # so that the distinction can be chosen by the scene
    # also need custom hitboxes

    def contextMenuEvent(self, event):
        # turns out svgitem doesn't have a to global coords function
        # todo: consider a 'click again for new position' option
        # (or right click to cancel)
        # click again for new position is tricky, because only scene can capture it?
        menu = QMenu(self.parent())
        delete_action = menu.addAction("Delete object")
        increase_scale_action = menu.addAction("Increase scale")
        decrease_scale_action = menu.addAction("Decrease scale")
        move_actionl5 = menu.addAction("Move state left 5 pixels")
        move_actionr5 = menu.addAction("Move state right 5 pixels")
        move_actionu5 = menu.addAction("Move state up 5 pixels")
        move_actiond5 = menu.addAction("Move state down 5 pixels")
        move_actionl25 = menu.addAction("Move state left 25 pixels")
        move_actionr25 = menu.addAction("Move state right 25 pixels")
        move_actionu25 = menu.addAction("Move state up 25 pixels")
        move_actiond25 = menu.addAction("Move state down 25 pixels")
        cancel_action = menu.addAction("Cancel")

        # these coords place the menu that you get when right-clicking a state
        # these coords should be softcoded
        # ideally, they'll appear in a sensible position near the state?
        # should be global screen coordinates?, softcoded
        self_x = self.pos().x()
        self_y = self.pos().y()
        action = menu.exec(QPoint(self_x + 50, self_y + 50))

        if action == increase_scale_action:
            print(f"From scale {self.scale()} to scale", end=' ')
            self.setScale(1.09 * self.scale())
            print(self.scale())

        if action == decrease_scale_action:
            print(f"From scale {self.scale()} to scale", end=' ')
            self.setScale(self.scale() * 0.91)
            print(self.scale())

        # I can't figure out how to make a delete here trigger an adjustment
        # to automaton_board, so I've had to program a delay.
        # todo: make deletions happen immediately
        # action = menu.exec_(event.pos())
        if action == delete_action:
            print('this item will be deleted next mouse click')
            self.wants_to_be_deleted = True

        if action == move_actionl5:
            self.setPos(self.pos().x() - 5, self.pos().y())

        if action == move_actionr5:
            self.setPos(self.pos().x() + 5, self.pos().y())

        if action == move_actionu5:
            self.setPos(self.pos().x(), self.pos().y() - 5)

        if action == move_actiond5:
            self.setPos(self.pos().x() + 5, self.pos().y() + 5)

        if action == move_actionl25:
            self.setPos(self.pos().x() - 25, self.pos().y())

        if action == move_actionr25:
            self.setPos(self.pos().x() + 25, self.pos().y())

        if action == move_actionu25:
            self.setPos(self.pos().x(), self.pos().y() - 25)

        if action == move_actiond25:
            self.setPos(self.pos().x(), self.pos().y() + 25)

        # I couldn't get user entered coordinate setting to work (i.e. with keyoard)
        # I will revisit this system when I have time

        if action == cancel_action:
            pass