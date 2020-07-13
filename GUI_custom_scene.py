# contains the custom scene.
# responsible for creating and placing items, representing a board state,
# updating item properties, handling all left-click behavior etc.

from PyQt5 import QtCore, QtWidgets
import PyQt5.QtGui
from PyQt5.QtCore import QTimer, QLineF
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QGraphicsLineItem, QGraphicsEllipseItem
from PyQt5.QtGui import QIcon, QPixmap, QFont

from PyQt5.QtWidgets import QGraphicsScene, QGraphicsTextItem, QLineEdit, QPushButton
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QTransform
from GUI_custom_ellipseitem import custom_ellipse
import resources.svg_paths as svg_paths
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class clickable_qgraphicsscene(QGraphicsScene):
    def __init__(self, parent):
        QGraphicsScene.__init__(self, parent)
        # Placeholder tooltip. Overwritten on state creation, as well as upon user request
        # (once we implement state renaming)
        # note that the first sentence must remain in the same format!!
        # this is because some functions depend on reading this format
        # namely _getQNameFromState and unrelated subfuction connection_options
        # todo: reimplement with setters, so the user knows what they can do.
        # self.default_state_tooltip = "State XXX. \nClick centre to change properties\nClick edge to add transition\nRight click to delete, change size, or move"

        # an incrementing count for each created state,
        # so that states get unique IDs
        self.state_count = 0

        # used to set ellipse height and width upon creation
        self.state_default_width = 50
        self.state_default_height = 50

        # offsets for straight lines
        # self.straight_arrows_x_offset = -65
        # self.straight_arrows_y_offset = -10
        # self.straight_arrows_scale = .2

        # a variable to represent the state of the automaton at any given point
        # used to present the simulation to outside files,
        # and may be updated internally according to outside requests
        # those requests will then have to update their understanding based on this var
        self.automaton_board = dict()

    def mousePressEvent(self, event):
        # should be put into a behaviours file imo. Makes this file more legible.
        # be wary of import problems / problems accessing "self" or whatever

        # todo: update description below, once stuff is implemented.
        # depending on where the user clicks, we trigger a different behavior
        # BEHAVIOR SCHEME:
        # 1) left click on empty space -> create state
        # 2) left click on state -> change its properties
        # 3) left drag on state -> move state & associated transitions
        # 4) right click on state -> bring up options menu. Idk where this is best implemented. Probably here? Consistent?
        # 5) left click on arrow -> we change its transition character.
        # ...

        # click location is only meaningfully measured in terms of scenePos(). pos() just gives 0,0
        x = event.scenePos().x()
        y = event.scenePos().y()

        state_count = 0

        # QTransform() is mandatory
        # todo: is this the best approach? Do we not want to find the closest item centre to the click?
        #   but would that cause bugs in closely-placed states? Where clicking on a state's edge would
        #   register as clicking on the transition's centre (as it's closer)?
        #   but there's no need to click on or near a state edge in our current control scheme
        item_at_click_loc = self.itemAt(x, y, QTransform())

        # TODO: REDO ALL THIS STUFF (behavior) below
        # then move into its own file, probably
        if not item_at_click_loc:
            # Behavior 1) create ellipse
            print('info: user clicked on empty space. Creating ellipse')
            self.el = custom_ellipse(name="State " + str(self.state_count), ID_num=self.state_count)
            self.state_count += 1
            self.el.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
            # spawn on mouse click location
            # Concerns:
            # 1) although the event scenePos seems always correct,
            # the ellipse's scenePos and pos are always (-25.5, -25.5)
            # 2) the ellipses have no parents, be they Item, Object or Widget
            # !!! HOWEVER, we still have access to useful coords via: !!!
            # print(self.el.mapToScene(self.el.boundingRect().center()))
            # I think that nullifies the 2 problems above, but I still want them to be noted.
            # print(f'DEBUG XYZZ_1: event scenePos({event.scenePos().x()},{event.scenePos().y()})')

            # set size
            self.el.setRect(event.scenePos().x(),
                            event.scenePos().y(),
                            self.state_default_width,
                            self.state_default_height)
            # centre ellipse on mouse click
            self.el.setPos(self.el.pos().x() - 0.5 * self.el.boundingRect().width(),
                           self.el.pos().y() - 0.5 * self.el.boundingRect().height())
            self.el.mapToScene(event.scenePos().x(), event.scenePos().y())
            self.addItem(self.el)
            # I'm not setting properties automatically. I'll leave that up to the user for now.
            return

        if isinstance(item_at_click_loc, custom_ellipse):
            # TODO: code for dragging behavior
            # see https://qt.developpez.com/doc/4.6/dnd/
            # ctrl-f
            # "For widgets that need to distinguish between mouse clicks and drags"
            if event.button() == Qt.LeftButton:
                # Behavior 2) change state properties
                print('info: user clicked state. Changing state properties')
                clicked_state = item_at_click_loc

                # accepting.initial. -> a. -> i. -> neither -> accepting.initial. -> ...
                if clicked_state.accepting and clicked_state.initial:
                    # ai -> a
                    self._removeStatePropertyFromAutomatonBoard(clicked_state, 'i')
                    clicked_state.toggleInitial()
                elif clicked_state.accepting and not clicked_state.initial:
                    # a -> i
                    self._removeStatePropertyFromAutomatonBoard('i')
                    self._addStatePropertyToAutomatonBoard('a')
                    clicked_state.toggleAccepting()
                    clicked_state.toggleInitial()
                elif not clicked_state.accepting and clicked_state.initial:
                    # i -> neither
                    clicked_state.toggleInitial()
                    self._removeStatePropertyFromAutomatonBoard(clicked_state, 'i')
                elif not clicked_state.accepting and not clicked_state.initial:
                    # neither -> ai
                    self._addStatePropertyToAutomatonBoard(clicked_state, 'ai')
                    clicked_state.toggleAccepting()
                    clicked_state.toggleInitial()
                return
            elif event.button() == Qt.RightButton:
                # Behavior 4) spawn menu
                # todo: spawn menu and stuff
                # provide connection options to other states
                connection_options = []
                for i in self.items():
                    if isinstance(i, custom_ellipse):
                        state_count += 1
                        if i == item_at_click_loc:
                            pass
                        else:
                            # adds a reference to that object to connection_options
                            connection_options.append(i)

                # we want min 2 states if we are to provide a transition arrow
                if state_count < 2:
                    print('state_count', state_count)
                    # consider giving the user this info on-screen
                    print('No two states to connect! Please add a state by clicking in empty space')
                    return
                else:
                    self.available_ops = []
                    for state in range(state_count):
                        # each QPushButton is a connection option, targeting another state
                        self.available_ops.append(QPushButton(self.parent()))

                    # option_count reflects the number of connection options
                    # it's used as an index, to set the correct state names
                    # and adjust y offsets, so that the QPushButtons below do not stack
                    option_count = 0
                    state_names = []
                    for co in connection_options:
                        # examines the tooltip of each object in connection_options
                        # to determine its name - how its name will be represented
                        # to the user.
                        # expects a '.' after the state
                        state_names.append(co.toolTip().split('.')[0])

                        # todo: set the size and text of each menu option

                        # item_at_click_loc = self.itemAt(x, y, QTransform())

                        # these 2 vars are used by other functions:
                        # closeOptionsMenu and _closureconnectTwoStates
                        # self.item_at_click_loc_COPY = item_at_click_loc
                        # self.available_ops_COPY = available_ops

                        # we need this hacky solution to a fringe error
                        # namely when the user creates 2 states, then clicks NEAR but not on one
                        # item_at_click_loc is set to None and the connectTwoStates function throws an error
                        # note that the 130 is guesswork and this whole block should be replaced
                        # by something more sensible
                        # if not item_at_click_loc:
                        #     raise ValueError(
                        #         'No item at click_loc. Might need to reimplement the lines below this. Or just review stuff generally')

                        # we pass this text (which mentions the state name) to _connectTwoStates()
                        # so it can find itself the correct target state, as it receives the text
                        # of the clicked QPushButton passed in
                        text_to_attach = self.available_ops[option_count].text()
                        self.available_ops[option_count].clicked.connect(self._closureconnectTwoStates(item_at_click_loc, co))
                        self.available_ops[option_count].setGeometry(300, 200 + 30 * option_count, 200, 30)
                        self.available_ops[option_count].setText("Connect to: " + co.name)


                        self.available_ops[option_count].show()
                        option_count += 1

                    op_cancel = QPushButton(self.parent())
                    self.available_ops.append(op_cancel)
                    op_cancel.setGeometry(300, 200 + 30 * option_count, 200, 30)
                    op_cancel.clicked.connect(self._closeOptionsMenu)
                    op_cancel.setText("Cancel")
                    op_cancel.show()
            else:
                # neither left nor right click on state
                return


        # if not isinstance(item_at_click_loc, QGraphicsTextItem):
        #     # Determine where (relative to on-screen icons) a user clicked
        #     # so that we can repond appropriately
        #     user_clicked_state_centre = False
        #     user_clicked_state_edge = False
        #     user_clicked_empty_space = False
        #
        #     self.items_copy = self.items()
        #
        #     if len(self.items_copy) == 0:
        #         user_clicked_empty_space = True
        #
        #     for c in self.items_copy:
        #         # c may be any object on screen: a state, an arrow, a textbox...
        #         # note that textboxes may soon be abolished
        #         is_state = self._isState(c)
        #         clicked_obj = c
        #
        #         # note that QRectF has methods like bottomLeft() and center() !!
        #         width = c.boundingRect().width()
        #         height = c.boundingRect().height()
        #         item_centre = (c.boundingRect().center().x(), c.boundingRect().center().y())
        #
        #         # we determine where (relative to each item in self.items) the user clicked
        #         # so we can set execute appropriate behaviour later
        #         if is_state:
        #             # reset user_clicked_empty_space. We only want it tracking the last c
        #             user_clicked_empty_space = False
        #
        #             # why is every custom ellipse seemingly  at -25.5, -25.5?
        #             # this happens even though the ellipses APPEAR to be far from each other
        #             # look to where ellipses are defined and created, for clues
        #             # c.setPos(50,50)
        #             print("info: user clicked on state")
        #             print("DEBUG: c.pos().x(), c.pos().y(), event.pos().x(), event.pos().y()", end='\n\t')
        #             print(c.pos().x(), c.pos().y(), event.pos().x(), event.pos().y())
        #
        #             # user clicked the central third
        #             if abs(x - item_centre[0]) < 0.33 * width \
        #                     and abs(y - item_centre[1]) < 0.33 * height:
        #                 user_clicked_state_centre = True
        #
        #             # todo: determine why this isn't giving expected value
        #             elif c.contains(event.scenePos()):
        #                 user_clicked_state_edge = True
        #
        #             else:
        #                 user_clicked_empty_space = True
        #                 print('DEV: item at click loc? : ', self.items_copy)
        #                 print(f'DEV: click location in terms of scenePos {event.scenePos().x()}{event.scenePos().y()}')
        #                 print(f'DEV: click location in terms of pos {event.pos().x()}{event.pos().y()}')
        #                 print(f'DEV: nearby item(s)')
        #                 for c in self.items_copy:
        #                     print(
        #                         f'item scenePos({c.scenePos().x()}, {c.scenePos().y()}), item pos({c.pos().x()}, {c.pos().y()})')
        #         else:
        #             print(
        #                 "_respondToMouseEvents / mousePressEvent does not yet have behavior coded here for non-state objects")
        #             print('todo: decide what to do if the user clicks on an object that is not a state')
            # take action according to where a user clicked (relative to the state)
            # if user_clicked_state_edge:
                # provide connection options to other states
                # connection_options = []
                # for i in self.items_copy:
                #     if isinstance(i, custom_ellipse):
                #         state_count += 1
                #         if i == clicked_obj:
                #             pass
                #         else:
                #             # adds a reference to that object to connection_options
                #             connection_options.append(i)
                #
                # # we want min 2 states if we are to provide a transition arrow
                # if state_count < 2:
                #     print('state_count', state_count)
                #     print('No two states to connect! Please add a state by clicking in empty space')
                # else:
                #     # make this shared file-wide, so other functions can access it
                #     # e.g. closeOptionsMenu and _closureconnectTwoStates
                #     self.available_ops = []
                #     for state in range(state_count):
                #         # each QPushButton is a connection option, targeting another state
                #         self.available_ops.append(QPushButton(self.parent()))
                #
                #     # option_count reflects the number of connection options
                #     # it's used as an index, to set the correct state names
                #     # and adjust y offsets, so that the QPushButtons below do not stack
                #     option_count = 0
                #     state_names = []
                #     for co in connection_options:
                #         # examines the tooltip of each object in connection_options
                #         # to determine its name - how its name will be represented
                #         # to the user
                #         # expects a '.' after the state
                #         state_names.append(co.toolTip().split('.')[0])
                #
                #         # sets the size and text of each menu option
                #         # available_ops[option_count].setGeometry(300, 200 + 30 * option_count, 200, 30)
                #         # available_ops[option_count].setText("Connect to: " + state_names[option_count])
                #         self.available_ops[option_count].setGeometry(300, 200 + 30 * option_count, 200, 30)
                #         self.available_ops[option_count].setText("Connect to: " + state_names[option_count])
                #
                #         # item_at_click_loc = self.itemAt(x, y, QTransform())
                #         self.item_at_click_loc = self.itemAt(x, y, QTransform())
                #         # these 2 vars are used by other functions:
                #         # closeOptionsMenu and _closureconnectTwoStates
                #         # self.item_at_click_loc_COPY = item_at_click_loc
                #         # self.available_ops_COPY = available_ops
                #
                #         ## we need this hacky solution to a fringe error
                #         ## namely when the user creates 2 states, then clicks NEAR but not on one
                #         ## item_at_click_loc is set to None and the connectTwoStates function throws an error
                #         ## note that the 130 is guesswork and this whole block should be replaced
                #         ## by something more sensible
                #         if not item_at_click_loc:
                #             raise ValueError(
                #                 'No item at click_loc. Might need to reimplement the lines below this. Or just review stuff generally')
                #
                #         # we pass this text (which mentions the state name) to _connectTwoStates()
                #         # so it can find itself the correct target state, as it receives the text
                #         # of the clicked QPushButton passed in
                #         text_to_attach = self.available_ops[option_count].text()
                #         self.available_ops[option_count].clicked.connect(self._closureconnectTwoStates(text_to_attach))
                #
                #         self.available_ops[option_count].show()
                #         option_count += 1
                #
                #     op_cancel = QPushButton(self.parent())
                #     self.available_ops.append(op_cancel)
                #     op_cancel.setGeometry(300, 200 + 30 * option_count, 200, 30)
                #     op_cancel.clicked.connect(self._closeOptionsMenu)
                #     op_cancel.setText("Cancel")
                #     op_cancel.show()
                # return

            # if user_clicked_state_centre:
            #     # toggle state properties (accepting, initial)
            #     # each time the user clicks a state centre
            #     # this affects state appearance too
            #     # the clicked-on object is modified in place. It's not replaced
            #     state_at_click_loc = item_at_click_loc
            #
            #     # accepting.initial. -> a. -> i. -> neither -> a.i. -> ...
            #     if state_at_click_loc.accepting and state_at_click_loc.initial:
            #         # ai -> a
            #         self._removeStatePropertyFromAutomatonBoard(item_at_click_loc, 'i')
            #         item_at_click_loc.toggleInitial()
            #     elif state_at_click_loc.accepting and not state_at_click_loc.initial:
            #         # a -> i
            #         self._removeStatePropertyFromAutomatonBoard('i')
            #         self._addStatePropertyToAutomatonBoard('a')
            #         item_at_click_loc.toggleAccepting()
            #         item_at_click_loc.toggleInitial()
            #     elif not state_at_click_loc.accepting and state_at_click_loc.initial:
            #         # i -> neither
            #         item_at_click_loc.toggleInitial()
            #         self._removeStatePropertyFromAutomatonBoard(item_at_click_loc, 'i')
            #     elif not state_at_click_loc.accepting and not state_at_click_loc.initial:
            #         # neither -> ai
            #         self._addStatePropertyToAutomatonBoard(item_at_click_loc, 'ai')
            #         item_at_click_loc.toggleAccepting()
            #         item_at_click_loc.toggleInitial()
            #     return

            # if user_clicked_empty_space:
            #     print('info: user clicked on empty space. Creating ellipse')
            #     self.el = custom_ellipse()
            #     # self.el.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
            #     # spawn on mouse click location
            #     # Concerns:
            #     # 1) although the event scenePos seems always correct,
            #     # the ellipse's scenePos and pos are always (-25.5, -25.5)
            #     # 2) the ellipses have no parents, be they Item, Object or Widget
            #     # !!! HOWEVER, we still have access to useful coords via: !!!
            #     # print(self.el.mapToScene(self.el.boundingRect().center()))
            #     # I think that nullifies the 2 problems above, but I still want them to be noted.
            #     print(f'DEBUG XYZZ_1: event scenePos({event.scenePos().x()},{event.scenePos().y()})')
            #
            #     # set size
            #     self.el.setRect(event.scenePos().x(),
            #                     event.scenePos().y(),
            #                     self.state_default_width,
            #                     self.state_default_height)
            #     # centre ellipse on mouse click
            #     self.el.setPos(self.el.pos().x() - 0.5 * self.el.boundingRect().width(),
            #                    self.el.pos().y() - 0.5 * self.el.boundingRect().height())
            #     self.el.mapToScene(event.scenePos().x(), event.scenePos().y())
            #     self.addItem(self.el)
            #     return

        # item_at_loc is a QGraphicsTextItem
        # todo: review if we still need separate QGraphicsTextItem objects
        #  or if we can just group them with arrows or something
        # NOTE! this must match the type of the object visually indicating transitions between states
        # TODO: review this logic. It's flawed. How can you create a line item if you need to first click on one to create it?
        # on 2nd thoughts, that's fine. But the user does need to be prompted to give a transition letter
        # and be allowed to change it/them when they please.
        # so for now this is defunct.
        # also, there needs to be an easy way to change transitions. To click on a LineItem is to pixel hunt
        elif isinstance(item_at_click_loc, QGraphicsLineItem):
            # create an outbound transition
            # we create a temporary text box for user to enter a new transition into
            # once the user presses return/enter, takeNewTransitionString() is called, and this text box disappears
            # and a new textitem appears in its place, displaying the new transition
            tmp_coords = (item_at_click_loc.x(), item_at_click_loc.y())
            self.removeItem(item_at_click_loc)
            tmp_lineedit = QLineEdit(self.parent())
            tmp_lineedit.setGeometry(QRect(int(tmp_coords[0]), int(tmp_coords[1]), 450, 31))
            tmp_lineedit.setPlaceholderText("a,b  [TO REMOVE TRANSITION, LEAVE EMPTY, PRESS ENTER]")

            self._givenTextitemAddOutboundRules(tmp_lineedit)
            tmp_lineedit.setToolTipDuration(2)
            tmp_lineedit.show()

            # When editing is finished, either because the line edit lost focus or
            # Return/Enter is pressed the editingFinished() signal is emitted
            def _takeNewTransitionString():
                # parts of this should at some point be made into its own function.
                # We have duplicated code.
                self.entered_string = tmp_lineedit.text()

                # create the new text item
                text_placement_coords = (tmp_lineedit.pos().x(), tmp_lineedit.pos().y())
                textitem_x_coord = text_placement_coords[0]
                arrow_textitem = QGraphicsTextItem(self.entered_string)
                textitem_y_coord = text_placement_coords[1]
                arrow_textitem.setPos(textitem_x_coord, textitem_y_coord)
                arrow_textitem.setToolTip("Click here to change this arrow's transition")

                # these should mirror the settings below
                # until both blocks are consolidated into 1 function
                arrow_textitem.setScale(1.3)
                arrow_textitem.setProperty('textitem', 1)
                self.addItem(arrow_textitem)

                tmp_lineedit.deleteLater()

                # these passed in coords are real fucky. We want the closest arrow, but in a pinch
                # we'll make do with the closest textitem coords
                self._givenTextitemAddOutboundRules(arrow_textitem)
                return

            tmp_lineedit.editingFinished.connect(_takeNewTransitionString)
            return self.dont_create

    def _findClosestArrowToGivenCoords(self, coords_tpl):
        # returns the arrow closest to the coordinates given by coords_tpl
        coords_x = coords_tpl[0]
        coords_y = coords_tpl[1]
        arrow_lst = []
        for i in self.items():
            if i.property('arrow'):
                arrow_lst.append(i)

        min_dist = None
        closest_arrow = None
        for s in arrow_lst:
            dist_from_coords = abs(s.pos().x() - coords_x) + abs(s.pos().y() - coords_y)
            if not min_dist:
                min_dist = dist_from_coords
                closest_arrow = s
            else:
                if dist_from_coords < min_dist:
                    min_dist = dist_from_coords
                    closest_arrow = s
        return closest_arrow

    def _findClosestStateToGivenCoords(self, coords_tpl):
        # return the state closest to the coordinates given by coords_tpl
        # usually called twice:
        # first for originating state (arrow base),
        # then for target state (arrow tip)
        coords_x = coords_tpl[0]
        coords_y = coords_tpl[1]
        state_lst = []
        for i in self.items():
            if self._isState(i):
                state_lst.append(i)

        min_dist = None
        closest_state = None
        for s in state_lst:
            # for whatever reason *0.4 gives us almost exactly the centre
            state_size = s.boundingRect().size() * self.state_scale * 0.4
            state_width = state_size.width()
            state_height = state_size.height()
            # state_centre = (s.pos().x() + state_width, s.pos().y() + state_height)
            # QGraphicsEllipseItem has no center() method, so we use our own
            state_centre = s.getCentre()

            # these 3 lines demonstrate where the calculated centre is
            # self.tmpitem = QLineEdit(self.parent())
            # self.tmpitem.setGeometry(state_centre[0], state_centre[1], 20, 20)
            # self.tmpitem.show()

            dist_from_coords = abs(state_centre[0] - coords_x) + abs(state_centre[1] - coords_y)
            if not min_dist:
                min_dist = dist_from_coords
                closest_state = s
            else:
                if dist_from_coords < min_dist:
                    min_dist = dist_from_coords
                    closest_state = s
        return closest_state

    def _givenArrowReturnOriginAndTargetStates(self, arrow):
        # the 'arrow' param is the arrow around which we're searching
        # this function returns the state closest to the tip of the arrow
        # i.e. the target state
        # as well as the state at the other end of the arrow
        # i.e. the originating state

        # we can ignore the height. Even if an arrow is rotated, what looks like height
        # should just be width (probably)
        arrow_size = arrow.boundingRect().size() * self.straight_arrows_scale
        arrow_width = arrow_size.width()
        # we need arrow rotation so that we know in which direction the arrow extends
        # and therefore where its tip is
        arrow_rotation = arrow.rotation()

        # note that arrow_tip can be at the x,y origin of the arrow, or the opposite end
        # it is based on the where the arrowhead of the arrow is,
        # and NOT simply the position of the arrow
        # same deal with arrow_base_coords, except it refers to the other end (visually) of the arrow
        # print("DEBUG: arrow's original position", arrow.pos().x(), arrow.pos().y(), end='. ')
        if arrow_rotation == 0:
            # arrow goes from left to right
            arrow_tip_coords = (arrow.pos().x() + arrow_width, arrow.pos().y())
            arrow_base_coords = (arrow.pos().x(), arrow.pos().y())
        elif arrow_rotation == 90:
            # arrow points downwards. Again, trial and error offset numbers
            arrow_tip_coords = (arrow.pos().x() - 15, arrow.pos().y() + arrow_width)
            arrow_base_coords = (arrow.pos().x() - 15, arrow.pos().y())
        elif arrow_rotation == 180:
            # arrow goes right to left. Arrow's anchor, i.e. its .pos() is now its top right hand corner
            arrow_tip_coords = (arrow.pos().x() - arrow_width, arrow.pos().y() - 15)
            arrow_base_coords = (arrow.pos().x(), arrow.pos().y() - 15)
        elif arrow_rotation == 270:
            # arrow points upwards
            arrow_tip_coords = (arrow.pos().x(), arrow.pos().y() - arrow_width)
            arrow_base_coords = (arrow.pos().x(), arrow.pos().y())
            self.tmpitem = QLineEdit(self.parent())
        else:
            raise ValueError('Arrow has unexpected degree of rotation')

        # print(f"Ascertained arrow_tip at {arrow_tip_coords}, arrow_base at {arrow_base_coords}")

        if not isinstance(arrow_tip_coords, tuple):
            print(arrow_tip_coords)
            raise ValueError("arrow_tip_coords not a tuple")
        if not isinstance(arrow_base_coords, tuple):
            print(arrow_base_coords)
            raise ValueError("arrow_base_coords not a tuple")
        # print("\nDEBUG: calling for originating state (i.e. arrow_base_coords)")
        originating_state = self._findClosestStateToGivenCoords(arrow_base_coords)
        # print("\nDEBUG: calling for target state (i.e. arrow_tip_coords)")
        target_state = self._findClosestStateToGivenCoords(arrow_tip_coords)
        # print(f"DEBUG: determined originating_state={self._getQNameFromState(originating_state)}, target_state={self._getQNameFromState(target_state)}")
        return originating_state, target_state

    def _givenTextitemAddOutboundRules(self, textitem):
        # given a textitem, calls other functions to:
        #  find its closest arrow
        #  find that arrow's target and originating states (affected by to arrow rotation)
        # it then manipulates that textitem.text()
        # and combines it with the target and originating state info
        # in order to create a self.automaton_board friendly transition
        # which is then added to self.automaton_board

        textitem_coords_tuple = (textitem.pos().x(), textitem.pos().y())
        # todo resolve why we have QGraphicsTextitem and the line thingy
        # print(type(textitem))
        try:
            textitem_string = textitem.text()
        except:
            textitem_string = textitem.toPlainText()

        closest_arrow = self._findClosestArrowToGivenCoords(textitem_coords_tuple)
        origin_state, target_state = self._givenArrowReturnOriginAndTargetStates(closest_arrow)

        # manipulate the textitem_string and combine the 3 variables,
        # to create a valid transition rule
        transition = textitem_string.replace(',', '')

        # finally, add that rule to self.automaton_board
        # print(
        #     f"info: origin_state name= {self._getQNameFromState(origin_state)}, target_state= {self._getQNameFromState(target_state)}, transition= {transition}")
        self._addOutboundTransitionToStateInAutomatonBoard(origin_state, target_state, transition)

    def _addStateToAutomatonBoard(self):
        # add a state to self.automaton_board
        # we just add the latest state (i.e. the highest count)
        print(f"info: state Q{str(self.state_name_count)} added to automaton board")
        state_name = "Q" + str(self.state_name_count)
        self.automaton_board[state_name] = ''

    def _removeStateFromAutomatonBoard(self, state_name):
        # removes a state from self.automaton_board
        print("info: state removed from automaton board")
        del self.automaton_board[state_name]

    def _addStatePropertyToAutomatonBoard(self, state_to_change, property):
        # adds a property to a state on self.automaton_board
        # property is 'a' like accepting or 'i' like initial
        state_to_change = self._getQNameFromState(state_to_change)
        if property != 'a' and property != 'i' and property != 'ai':
            raise ValueError(
                '_addStatePropertyToAutomatonBoard received unwelcome format for "property" param. If adding accepting and initial, add as \'ai\' not \'ia\'')
        if state_to_change not in self.automaton_board.keys():
            print(f"Did not find \"{state_to_change}\" in automaton board \"{self.automaton_board}\"")
            raise ValueError('No state found with that name in self.automaton_board. Cannot add properties to it')

        print(f"info: state property added to automaton board. Before: {self.automaton_board.get(state_to_change)}",
              end=' ')

        val_before = self.automaton_board.get(state_to_change)
        if val_before:
            # prepend 'a' or 'i' to the value of the state
            # for example {'Q1': 'Q2ab'} -> {'Q1': 'aQ2ab'} or {'Q1': 'aiQ2ab'}
            if not property in val_before:
                if property == 'i':
                    # add after the a
                    val_after = val_before + property
                elif property == 'a':
                    # add before the 'i'
                    val_after = property + val_before
                self.automaton_board[state_to_change] = val_after
        else:
            # add the first value to that key
            self.automaton_board[state_to_change] = property
        print(f"after: {self.automaton_board.get(state_to_change)}")

    def _removeStatePropertyFromAutomatonBoard(self, state_to_change, property):
        state_to_change = self._getQNameFromState(state_to_change)

        if state_to_change not in self.automaton_board.keys():
            print(f"Did not find {state_to_change} in automaton board {self.automaton_board}")
            raise ValueError('No state found with that name. Cannot remove properties from it')

        # removes a property from a state on self.automaton_board
        val_before = self.automaton_board.get(state_to_change)
        print(f"info: state property removed from automaton board. Before: {val_before}", end=' ')
        if val_before:
            # add a value error or whatever if property was never there
            # prepend 'a' or 'i' to the value of the state
            # for example {'Q1': 'Q2ab'} -> {'Q1': 'aQ2ab'} or {'Q1': 'aiQ2ab'}
            if len(property) == 2:
                if property not in val_before:
                    raise ValueError(
                        f"State_to_change did not find property {property} in state_to_change {state_to_change} values in automaton_board{self.automaton_board}")
                val_after = val_before.replace(property, '', 1)
                self.automaton_board[state_to_change] = val_after
            else:
                if val_before[0] == property or val_before[1] == property:
                    # max 1 replace, so we don't remove 'a' from outbound transitions for example
                    val_after = val_before.replace(property, '', 1)
                    self.automaton_board[state_to_change] = val_after
                else:
                    print(
                        f"info: tried to remove property \"{property}\" from key \"{state_to_change}\" in self.automaton_board{self.automaton_board}")
                    raise ValueError(
                        'State_to_change property not found in expected place. Format may be incorrect, or property was not there, and therefore cannot be removed')
        else:
            raise ValueError("Tried to remove properties from a state which had none to begin with")
        print(f"AFTER: {val_after}")

    def _addOutboundTransitionToStateInAutomatonBoard(self, state_to_change, target_state, transition):
        # transition is in format: 'ab' or 'b'
        # adds an outbound transition to one state in automaton board
        # we don't need to add transitions to automaton board if it's an empty arrow
        # print("info: outbound transition added to state in automaton board")

        # just in case it's incorrectly passed in
        transition = transition.replace(",", "")

        if state_to_change not in self.automaton_board.keys():
            try:
                state_to_change = self._getQNameFromState(state_to_change)
            except:
                raise ValueError('state_to_change not found in self.automaton_board')
        if target_state not in self.automaton_board.keys():
            try:
                target_state = self._getQNameFromState(target_state)
            except:
                raise ValueError('target_state not found in self.automaton_board')

        # if the state exists but has no outbounds...
        if not self.automaton_board.get(state_to_change):
            # print("info: the originating state is in self.automaton_board but has no outbounds")
            self.automaton_board[state_to_change] = target_state + transition
            return

        # if there's an existing entry, but it's not ours
        if target_state not in self.automaton_board[state_to_change] and self.automaton_board.get(state_to_change):
            # print("info: there's an existing entry but it's not ours")
            # print("now the board looks like:", self.automaton_board)
            self.automaton_board[state_to_change] = self.automaton_board[state_to_change] + target_state
            print("Updated automaton board:", self.automaton_board)
            return

        # find the string starting with our state and ending with ',' or another state
        our_addition = target_state + ''.join([c for c in (set(transition))])
        try:
            # if this passes, we already have our target state in the outbounds
            our_q_index = self.automaton_board[state_to_change].index(target_state)
            is_our_target_in_outbounds = True
            # print("info: our target is in outbounds")
        except ValueError:
            # our  target state is not in the outbounds
            # we simply append our addition and finish
            # print("info: our target state is not in outbounds")
            # print("now the board looks like:", self.automaton_board)
            self.automaton_board[state_to_change] = our_addition
            # print("Updated automaton board:", self.automaton_board)
            return
        try:
            # our target state is already there. There is another q block after it?
            # if so, replace our q block, using its start index, and stopping just short
            # of the next block
            next_q_index = self.automaton_board[state_to_change][our_q_index + 1:].index("Q")
            # print("info: our target state is in outbounds, and there is another qblock after it")
            # print("now the board looks like:", self.automaton_board)
            current_target_qblock = self.automaton_board[state_to_change][our_q_index:next_q_index]
            self.automaton_board[state_to_change].replace(current_target_qblock, our_addition)
            # print("Updated automaton board:", self.automaton_board)
            return
        except ValueError:
            if self.automaton_board[state_to_change].count("Q") == 1:
                # our state is the only one
                # print("info: our target state is the only qblock")
                self.automaton_board[state_to_change] = our_addition
                # print("Updated automaton board:", self.automaton_board)
                return
            # our target state is the last state
            # so we replace our_q_index until end of string with our_addition
            # print("info: our target state is the last qblock")
            current_target_qblock = self.automaton_board[state_to_change][our_q_index:]
            self.automaton_board[state_to_change] = self.automaton_board[state_to_change].replace(current_target_qblock,
                                                                                                  our_addition)
            print("Updated automaton board:", self.automaton_board)
            return

    def _modOneStateInAutomatonBoardRemoveOutboundsToTargetState(self, state_to_change, target_state):
        # in automaton board, from state_to_change, we remove all outbound transitions...
        # targeting target_state
        print("info: outbounds removed from one state in automaton board")

        if state_to_change not in self.automaton_board.keys():
            raise ValueError('state_to_change not found in self.automaton_board')

        if target_state not in self.automaton_board[state_to_change]:
            print(
                "target_state not found in state_to_change. Therefore, removing no transition from self.automaton_board")
            return

        if target_state[0] != 'Q' or state_to_change[0] != 'Q':
            raise ValueError('incorrect format for state received')

        val_before = self.automaton_board[state_to_change]
        # there are multiple states mentioned in state_to_change 's outbounds
        if val_before.count(',') > 0:
            splits = val_before.split('.')
            val_after = [','.join(s for s in splits if target_state not in s)]

        # only target_state is mentioned in state_to_change 's outbounds
        else:
            val_after = ''
        self.automaton_board[state_to_change] = val_after

    def _getQNameFromState(self, state_to_change):
        # receives tooltip parameter. Returns string in Q format,
        # like Q1 or Q2 etc
        # tooltips are formatted like this:
        #   "State Q1. \nClick centre to change properties\nClick edge to add transition\nRight click to delete"
        return "Q" + state_to_change.toolTip().split('.')[0].replace("State ", "")

    def _closeOptionsMenu(self):
        available_ops = self.available_ops_COPY
        for i in available_ops:
            i.deleteLater()

    def _return_target_state(self, target_name):
        # idk why we're using names instead of IDs
        # todo: determine which and why
        # takes string parameter, the identifier of a state
        target_state = None
        for x in self.items():
            if self._isState(x):
                if x.name == target_name:
                    target_state = x
                    break
        if not target_state:
            raise ValueError(f'Target state, name="{target_name}" not found')  # programming error. Should never happen. Has yet to happen.

    def _closureconnectTwoStates(self, origin_state, target_state):
        # takes 2 custom_ellipseitem objects and returns a function to connect them
        # cannot connect them directly because menu, or QButton objects, need to be connected to functions
        # for our purposes, these functions must be unique (i.e. no identical origin target pair)
        # therefore, we must create however many unique functions
        def _connectTwoStates():
            # todo: get arrow to spawn from edge not centre.
            # todo: replace line with arrow (our SVG thing?)
            start = origin_state.mapToScene(origin_state.boundingRect().center())
            end = target_state.mapToScene(target_state.boundingRect().center())
            l = QGraphicsLineItem(QLineF(start, end))

            # target_state_name = target_state.tooltip.replace("Connect to: ", "").replace("Connect to:", "")
            self.addItem(l)
            l.show()

            # this function is only called when the user has clicked to request a connection between states
            # therefore, we can delete all of the QPushButtons in the group
            for i in self.available_ops:
                i.deleteLater()

            # todo: fill in
            # this will be the code which will make arrows spawn from the cardinal directions of a state
            # rather than its centre
            origin_corners = None
            target_corner = None

            # todo: complete this function
            return

            # todo: replace with something more elegant. Like using boundingRect
            origin_size = origin_state.boundingRect().size() * self.state_scale * 0.4
            origin_width = origin_size.width()
            origin_height = origin_size.height()
            target_size = target_state.boundingRect().size() * self.state_scale * 0.4
            target_width = target_size.width()
            target_height = target_size.height()

            # find the centre and 'corners' (so to say) of the origin state
            # target_centre is used below as the x,y coordinates which these corners compare themselves to
            # many of the numbers below are trial and error, to most closely approximate that 'corner'
            # for current setup, these nearly perfectly 'find' the corners, as far as concerns placing the arrows
            # (see below)
            origin_centre = ((originatingState.pos().x() + 0.4 * origin_width),
                             (originatingState.pos().y() + 0.4 * origin_height))
            target_centre = ((target_state.pos().x() + 0.4 * target_width),
                             (target_state.pos().y() + 0.4 * target_height))
            o_top_centre = (int(origin_centre[0] + 0.49 * origin_width), int(origin_centre[1] - 0.2 * origin_height))
            o_bot_centre = (int(origin_centre[0]) + 1.2 * origin_width, int(origin_centre[1] + 2 * origin_height))
            o_mid_left = (int(origin_centre[0] - 0.42 * origin_width), int(origin_centre[1]) + 1 * origin_height)
            o_mid_right = (int(origin_centre[0] + 1.96 * origin_width), int(origin_centre[1]) + 0.69 * origin_height)
            o_corners = [o_top_centre, o_bot_centre, o_mid_left, o_mid_right]

            # find the closest target corner to connect to
            t_top_centre = (int(target_centre[0] + 0.49 * origin_width), int(target_centre[1] - 0.2 * origin_height))
            t_bot_centre = (int(target_centre[0]) + 1.2 * origin_width, int(target_centre[1] + 2 * origin_height))
            t_mid_left = (int(target_centre[0] - 0.42 * origin_width), int(target_centre[1]) + 1 * origin_height)
            t_mid_right = (int(target_centre[0] + 1.96 * origin_width), int(target_centre[1]) + 0.69 * origin_height)
            t_corners = [t_top_centre, t_bot_centre, t_mid_left, t_mid_right]

            min_dist = None
            closest_o_corner = None
            # print("o", o_corners)
            # print("t", t_corners)
            for t in t_corners:
                # 16 computations, but at least it's simple arithmetic
                # iterate through both t and o corners to find the pair with the shortest distance difference
                # if we don't do this, we end up with inconsistent arrow placement (i.e. sometimes they spawn
                # on the wrong side of a state, like right instead of top)
                for o in o_corners:
                    if not min_dist:
                        min_dist = abs(t[0] - o[0]) + abs(t[1] - o[1])
                        closest_o_corner = o
                    else:
                        curr_dist = abs(t[0] - o[0]) + abs(t[1] - o[1])
                        if curr_dist < min_dist:
                            min_dist = curr_dist
                            closest_o_corner = o
            closest_corner_to_target = closest_o_corner

            # print('info: _connectTwoStates corners:', corners)

            # determine the closest corner of the origin state to the target state
            # note that each of the "c"  corners is affected by a guesstimated modifier
            dist_from_each = [abs(target_centre[0] - c[0]) + abs(target_centre[1] - c[1]) for c in o_corners]
            # print('info: _connectTwoStates dist_from_each', dist_from_each)
            # closest_corner_to_target = o_corners[dist_from_each.index(min(dist_from_each))]
            # print('info: _connectTwoStates closest_corner_to_target', closest_corner_to_target)

            # place arrow on the closest corner
            # if circular, don't forget this line...
            #     self.svgItem.setProperty('arrow_circular', 1)
            self.svgItem = svgItem_mod(svg_paths.arrow_outwards)
            self.svgItem.setProperty('arrow', 1)
            self.svgItem.setScale(self.straight_arrows_scale)
            self.svgItem.setPos(closest_corner_to_target[0], closest_corner_to_target[1])
            self.svgItem.setProperty('arrow_outwards', 1)
            self.addItem(self.svgItem)
            self.svgItem.show()

            # set arrow rotation, so that it faces the target state
            # note that we're only dealing in 90 degree increments now
            # default angle is horizontal, arrowhead pointing from left to right
            # we also reposition textitem to prevent overlap with other graphical objects
            # after an arrow rotates
            # and we set an offset for the arrows, so that states aligned in a plane
            # with mutually connecting arrows, do not spawn those arrows on top of each other
            ind = o_corners.index(closest_corner_to_target)
            if ind == 0:
                # top centre, so we go straight up
                self.svgItem.setRotation(270)
                self.svgItem.setPos(self.svgItem.pos().x() + 10, self.svgItem.pos().y())
                textitem_x_offset = 20
                textitem_y_offset = -40
            elif ind == 1:
                # bot centre
                self.svgItem.setRotation(90)
                self.svgItem.setPos(self.svgItem.pos().x() - 10, self.svgItem.pos().y())
                # place the textitem to the left of the arrow
                textitem_x_offset = -47
                textitem_y_offset = 35
            elif ind == 2:
                # mid left
                self.svgItem.setRotation(180)
                self.svgItem.setPos(self.svgItem.pos().x(), self.svgItem.pos().y() - 10)
                # place textitem below
                textitem_x_offset = -65
                textitem_y_offset = -40
            elif ind == 3:
                # mid right
                # self.svgItem.setRotation(90)
                self.svgItem.setPos(self.svgItem.pos().x(), self.svgItem.pos().y() + 10)
                textitem_y_offset = 5
                textitem_x_offset = 35
                pass

            # add a text item to display an arrow's accepted transitions
            # and to allow the user to modify those transitions
            arrow_textitem = QGraphicsTextItem("Please enter a transition")

            # calculate the centre of the arrow, so that we can place the textitem accordingly
            arrow_size = self.svgItem.boundingRect().size() * self.straight_arrows_scale
            arrow_width = arrow_size.width()
            arrow_height = arrow_size.height()
            arrow_centre = ((self.svgItem.pos().x() + 0.0 * arrow_width),
                            (self.svgItem.pos().y() + 0.0 * arrow_height))

            textitem_x_coord = arrow_centre[0] + textitem_x_offset
            textitem_y_coord = arrow_centre[1] + textitem_y_offset
            arrow_textitem.setPos(textitem_x_coord, textitem_y_coord)
            arrow_textitem.setToolTip("Click to change this arrow's transition")

            # setting the scale is an easy way to adjust font size.
            # note that the multiplier in textitem_y_coord should be adjusted in tandem
            # as adjusting the scale affects textitem's height
            arrow_textitem.setScale(1.3)
            arrow_textitem.setProperty('textitem', 1)
            self.addItem(arrow_textitem)

        # long-ass function factory
        return _connectTwoStates

    def _helperReturnStateTooltip(self):
        # self.force_name is a list of length 2. [0] is True or False,
        #  indicating whether we want to force a name to stay the same,
        #  and [1] is the original tooltip that we want
        if self.force_name[0]:
            self.force_name[0] = False
            return self.force_name[1]
        else:
            self.state_name_count += 1
            return self.default_state_tooltip.replace("XXX", str(self.state_name_count))

    def _isState(self, c):
        return isinstance(c, custom_ellipse)
    # def _helperIsClosestGrapicalItemTooClose(self, onscreen_items, user_click_coords, x_threshold, y_threshold):
    # as of yet unused
    # returns True if user requests a new state too close to one already existing, else returns False
    # looks to the threshold params to determine what's an acceptable distance
    # may be used by the other helper to prevent new graphical items from being added
    # looks to x_threshold and y_threshold to determine if anything is too close
    # for c in onscreen_items:
    #     dist = (abs(user_click_coords[0] - c.pos().x()), abs(user_click_coords[1] - c.pos().y()))
    #     if (dist[0] < x_threshold) or (dist[1] < y_threshold):
    #         return True
