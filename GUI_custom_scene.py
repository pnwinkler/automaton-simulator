# contains the custom scene. Orchestrates custom items, allowing for custom
# control scheme

from PyQt5.QtWidgets import QGraphicsScene, QGraphicsTextItem, QLineEdit, QPushButton
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QTransform
from simulator.GUI_custom_svgitem import svgItem_mod
import simulator.resources.svg_paths as svg_paths


# TODO: resolve bug where connecting an arrow to a state slightly to the left, but far below the originating state
#  results in an arrow being placed on the state's left, instead of its bot

# todo:
#  allow for diagonal arrows
#  allow for curved arrows
#  make curved arrows correctly point to distant states
#  make arrows touch states (repositioning not necessary). Optional because user can delete and replace state themselves
#   get states to spawn in fixed, arrow-length distances from each other

class clickable_qgraphicsview(QGraphicsScene):
    def __init__(self, parent):
        QGraphicsScene.__init__(self, parent)
        # the text which appears when a state is moused over. The "XXX" will be replaced
        # on state creation, as well as when the user requests it (once we implement state renaming)
        # note that the first sentence must remain in the same format!
        self.default_state_tooltip = "State XXX. \nClick centre to change properties\nClick edge to add transition\nRight click to delete, change size, or move"

        # simply provides an incrementing count for each created state,
        # so that states get unique names
        self.state_name_count = 0

        # offsets required to have spawned states centre on cursor
        # should be replaced by smarter code sometime
        # this is for circular graphics
        self.state_x_offset = -33
        self.state_y_offset = -33
        self.state_scale = 0.09

        # offsets for straight lines
        self.straight_arrows_x_offset = -65
        self.straight_arrows_y_offset = -10
        self.straight_arrows_scale = .2

        # multiplier of state height and width to ensure that new states
        # may be spaced appropriately from the old
        self.multiplier_acceptable_distance_from_existing_state = 1.7

        # signals mousePressEvent() not to create an object
        self.dont_create = 'dontcreate'

        # signals the naming function whether to overrule its default behavior
        # we need this so that when we change a state's property (specifically accepting, initial)
        # we don't rename the state
        # the first value indicates whether special action is required by the tooltip setting function
        # the second is the tooltip which we would set, in that scenario
        self.force_name = [False, None]

        # complete guess. Used by the state placement function to place states at appropriate distances
        # from each other (i.e. arrow length distances)
        # edit as needed
        self.arrow_length = 150

        # a variable to represent the state of the automaton at any given point
        # used to present the simulation to outside files,
        # and may be updated internally according to outside requests
        # those requests will then have to update their understanding based on this var
        self.automaton_board = dict()

    # todo: rename this
    # it doesn't at all explain that it captures mouse press events, for example
    def _helperChooseAndReturnSvgitemPath(self, event):
        # based on the position that the user clicks, we determine the appropriate
        # SVG graphic and return its path, so that another function may create it
        # the other function can then create it and set its scale, properties, etc
        # note that, at the moment this function has a lot of responsibilities.
        # (such as transition editing)
        # it should probably be split into smaller functions

        x = event.scenePos().x()
        y = event.scenePos().y()

        state_count = 0

        # QTransform() doesn't seem to do anything but is mandatory
        item_at_click_loc = self.itemAt(x, y, QTransform())

        if not isinstance(item_at_click_loc, QGraphicsTextItem):
            # Determine where (relative to on-screen icons) a user clicked
            # so that we can take action if necessary
            # note that an object's coords refer to its top left corner, not its centre
            # so if the user clicks in the centre of an on-screen item, the coords would not match up
            # by default, so usually we tweak them as necessary
            user_clicked_state_centre = False
            user_clicked_state_edge = False
            user_clicked_empty_space = False

            self.items_copy = self.items()

            if len(self.items_copy) == 0:
                user_clicked_empty_space = True

            for c in self.items_copy:
                # c may be a Qt.Svg.QGraphicsSvgItem, or another type like a label
                # we look to the object's properties to determine which
                item_centre = None
                is_state = c.toGraphicsObject().property('state')
                is_arrow = c.toGraphicsObject().property('arrow')
                clicked_obj = c

                if is_state:
                    state_size = c.sceneBoundingRect().size()
                    state_width = state_size.width()
                    state_height = state_size.height()
                    item_centre = ((c.pos().x() + 0.4 * state_width),
                                   (c.pos().y() + 0.4 * state_height))

                elif is_arrow:
                    arrow_size = c.sceneBoundingRect().size()
                    arrow_height = arrow_size.height()
                    arrow_width = arrow_size.width()
                    item_centre = ((c.pos().x() + 0.4 * arrow_width),
                                   (c.pos().y() + 0.4 * arrow_height))

                # we determine where (relative to each item in self.items) the user clicked
                # so we can set execute appropriate behaviour later
                if is_state:
                    # reset user_clicked_empty_space. We only want it tracking the last c
                    user_clicked_empty_space = False

                    if abs(x - item_centre[0]) < 0.35 * state_width \
                            and abs(y - item_centre[1]) < 0.35 * state_height:
                        user_clicked_state_centre = True
                        break

                    # note that "empty space" may not be empty, it's just distant from c
                    elif abs(x - item_centre[0]) > 0.7 * state_width \
                            or abs(y - item_centre[1]) > 0.7 * state_height:
                        user_clicked_empty_space = True

                    # anything else is considered the edge (currently between 0.35 and 0.7)
                    else:
                        user_clicked_state_edge = True
                        break

            # provide connection options to other states
            if user_clicked_state_edge:
                connection_options = []
                for i in self.items_copy:
                    if i.property('state'):
                        state_count += 1
                        if i == clicked_obj:
                            pass
                        else:
                            connection_options.append(i)

                # we want min 2 states if we are to provide a transition arrow
                if state_count < 2:
                    print('state_count', state_count)
                    print('No two states to connect! Please add a state by clicking in empty space')
                else:
                    # todo: turn into factory
                    # the number of states here determines how many states we can connect to
                    # could be replaced by a factory, following the suggestion at:
                    # https://stackoverflow.com/questions/6784084/how-to-pass-arguments-to-functions-by-the-click-of-button-in-pyqt
                    # it's kinda fucked if there are more than 6 user states
                    op1 = QPushButton(self.parent())
                    op2 = QPushButton(self.parent())
                    op3 = QPushButton(self.parent())
                    op4 = QPushButton(self.parent())
                    op5 = QPushButton(self.parent())
                    op6 = QPushButton(self.parent())
                    op7 = QPushButton(self.parent())

                    # this is the limit of what can fit on screen, roughly.
                    available_ops = [op1, op2, op3, op4, op5, op6, op7]

                    # tmpcount is an index, used to set the correct state names, and adjust y offset
                    # so that the QPushButtons below do not stack over each other
                    tmpcount = 0
                    state_names = []
                    for co in connection_options:
                        # expects a '.' after the state
                        # state names will be like "State 1" or "State Q1"
                        state_names.append(co.toolTip().split('.')[0])
                        # print('info: state_name=', state_names)

                        # set properties of each option
                        # there's a limit of 9 states right now
                        available_ops[tmpcount].setGeometry(300, 200 + 30 * tmpcount, 200, 30)
                        available_ops[tmpcount].setText("Connect to: " + state_names[tmpcount])

                        item_at_click_loc = self.itemAt(x, y, QTransform())

                        # if state_names[tmpcount] == item_at_click_loc:
                        #     available_ops[tmpcount].setText("Connect to: " + state_names[tmpcount] + "(self)")

                        # we need this hacky solution to a fringe error
                        # namely when the user creates 2 states, then clicks NEAR but not on one
                        # item_at_click_loc is set to None and the connectTwoStates function throws an error
                        # note that the 130 is guesswork and this whole block should be replaced
                        # by something more sensible
                        if not item_at_click_loc:
                            # find closest item to click location
                            for i in self.items():
                                if i.property('state'):
                                    if abs(i.pos().x() - x) < 130:
                                        item_at_click_loc = i
                                        break
                                    # print("DEBUG ", abs(i.pos().x() - x))

                        # clumsy, but this self._args is setup so the _connectTwoStates() function can access its vars
                        # now that we have a closure, this could be made into params
                        # PROBLEM: we create two states, then click on empty space to connect
                        # and this then causes problems with nonetypes
                        self._args = (item_at_click_loc, available_ops)

                        # should be avoided by the hacky block above
                        if not item_at_click_loc:
                            raise ValueError("NO ITEM AT CLICK LOC")

                        # we pass this text (which mentions the state name) to _connectTwoStates()
                        # so it can find itself the correct target state, as it receives the text
                        # of the clicked QPushButton passed in
                        text_to_attach = available_ops[tmpcount].text()
                        available_ops[tmpcount].clicked.connect(self._closureconnectTwoStates(text_to_attach))

                        available_ops[tmpcount].show()
                        tmpcount += 1
                    op_cancel = QPushButton(self.parent())
                    available_ops.append(op_cancel)
                    op_cancel.setGeometry(300, 200 + 30 * tmpcount, 200, 30)
                    op_cancel.clicked.connect(self._closeOptions)
                    op_cancel.setText("Cancel")
                    op_cancel.show()

                return self.dont_create

            if user_clicked_state_centre:
                # each time the user clicks the state centre, it switches between
                # regular, accepting, initial properties (& appearance)
                # in practise, this means deleting the clicked-on state
                # and putting a state of different appearance but near-identical
                # properties in its place

                # this has never happened, but I keep it in case I modify the code above
                # at some point, so I can catch errors early.
                if not item_at_click_loc.property('state'):
                    raise ValueError(
                        'This should not happen. user_clicked_state_centre is True, but item_at_click_loc is not a state')

                # delete the clicked item (if it's a state), so we can replace it
                placement_x = item_at_click_loc.pos().x()
                placement_y = item_at_click_loc.pos().y()
                deleted_state_tooltip = item_at_click_loc.toolTip()
                self.removeItem(item_at_click_loc)

                # print('info: item(s) at click location', self.itemAt(x, y, QTransform()))
                # print('state at location accepting?:', item_at_click_loc.property('accepting'))
                # print('state at location initial?:', item_at_click_loc.property('initial'))

                # accepting -> initial + accepting -> state -> accepting -> initial
                # self.force_name gets reset every time a new tooltip is created
                self.force_name = [True, deleted_state_tooltip]

                # we replace the state with another object of the same name, but different graphic
                # we set the properties accordingly. Because we force the same state name, we do
                # not need to wipe & redo its entry in self.automaton_board, instead we just update it
                if item_at_click_loc.property('accepting') and not item_at_click_loc.property('initial'):
                    self._addStatePropertyToAutomatonBoard(item_at_click_loc, 'i')
                    return svg_paths.state_accepting_initial_colour, (placement_x, placement_y)

                elif item_at_click_loc.property('initial') and item_at_click_loc.property('accepting'):
                    self._removeStatePropertyFromAutomatonBoard(item_at_click_loc, 'ai')
                    return svg_paths.state, (placement_x, placement_y)

                elif not item_at_click_loc.property('initial') and not item_at_click_loc.property('accepting'):
                    self._addStatePropertyToAutomatonBoard(item_at_click_loc, 'a')
                    return svg_paths.state_accepting_colour, (placement_x, placement_y)

                elif item_at_click_loc.property('accepting'):
                    self._removeStatePropertyFromAutomatonBoard(item_at_click_loc, 'a')
                    self._addStatePropertyToAutomatonBoard(item_at_click_loc, 'i')
                    return svg_paths.state_initial, (placement_x, placement_y)

                elif item_at_click_loc.property('initial') and not item_at_click_loc.property('accepting'):
                    self._removeStatePropertyFromAutomatonBoard(item_at_click_loc, 'i')
                    self._addStatePropertyToAutomatonBoard(item_at_click_loc, 'a')
                    return svg_paths.state_accepting_colour, (placement_x, placement_y)

                # then mousePressEvent function will set further properties, such as 'state'
                # we don't currently use those properties for logging, but they're used by other functions
                raise Exception('ERROR: item_to_create incorrectly set')

            if user_clicked_empty_space:
                print('info: user clicked on empty space')
                return svg_paths.state

            # doesn't seem to ever happen
            print('ERROR: user click was not assigned to any category')
            return svg_paths.skip_to_begin

        # item_at_loc is a QGraphicsTextItem
        else:
            # we create a temporary text box for user to enter a new transition into
            # once the user presses return/enter, takeNewTransitionString() is called, and this text box disappears
            # and a new textitem appears in its place, displaying the new transition
            tmp_coords = (item_at_click_loc.x(), item_at_click_loc.y())
            self.removeItem(item_at_click_loc)
            tmp_lineedit = QLineEdit(self.parent())
            tmp_lineedit.setGeometry(QRect(int(tmp_coords[0]), int(tmp_coords[1]), 450, 31))
            tmp_lineedit.setPlaceholderText("a,b  [TO REMOVE TRANSITION, LEAVE EMPTY, PRESS ENTER]")

            self._givenTextitemAddOutboundRules(tmp_lineedit)
            # print(self.automaton_board)
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
            if i.property('state'):
                state_lst.append(i)

        min_dist = None
        closest_state = None
        for s in state_lst:
            # for whatever reason *0.4 gives us almost exactly the centre
            state_size = s.boundingRect().size() * self.state_scale * 0.4
            state_width = state_size.width()
            state_height = state_size.height()
            state_centre = (s.pos().x() + state_width, s.pos().y() + state_height)
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
        # print(f"DEBUG: determined originating_state={self._getNameFromState(originating_state)}, target_state={self._getNameFromState(target_state)}")
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
        #     f"info: origin_state name= {self._getNameFromState(origin_state)}, target_state= {self._getNameFromState(target_state)}, transition= {transition}")
        self._addOutboundTransitionToStateInAutomatonBoard(origin_state, target_state, transition)

    def mousePressEvent(self, event):
        # todo: flesh this out.
        #  and make the rest of the program respond appropriately
        #  add behavior for movement
        # check if any items want to be deleted or moved
        for i in self.items():
            if i.property('state'):
                if i.wants_to_be_deleted:
                    # remove transitions and remove item itself
                    name_to_remove = self._getNameFromState(i)
                    self._removeStateFromAutomatonBoard(name_to_remove)
                    print("info: state removed")
                    i.deleteLater()
                    print(self.automaton_board)
                    return
            if i.property('arrow'):
                # todo: fill this in
                pass

        # mouse X, mouse Y
        x = event.scenePos().x()
        y = event.scenePos().y()

        # create objects
        if event.button() == Qt.LeftButton:
            # retrieve svg item path, and (if given), state placement coordinates
            # these coordinates can be used to place states
            svgPath = self._helperChooseAndReturnSvgitemPath(event)
            if isinstance(svgPath, tuple):
                received_placement_coords = svgPath[1]
                svgPath = svgPath[0]

            if svgPath == self.dont_create:
                # don't create anything.
                # this can be desirable when the line edit item is waiting on input
                # or when the _helper function finds that the new item would overlap an old item
                return

            if svgPath != None:
                self.svgItem = svgItem_mod(svgPath)

            else:
                raise ValueError('Helper function returned no path for mousePressEvent() to use')

            if 'state' in svgPath:
                if 'accepting' in svgPath:
                    self.svgItem.setProperty('accepting', 1)
                if 'initial' in svgPath:
                    self.svgItem.setProperty('initial', 1)
                try:
                    # set coords only for states that are being replaced / having properties modified
                    self.svgItem.setPos(received_placement_coords[0], received_placement_coords[1])
                except:
                    # this will set coords for all new states
                    # placement_coords = self._setStateCoords(x, y)
                    # print(
                    #     'no placement coords received. Not necessarily a problem. Using _setStateCoords values instead')
                    self.svgItem.setPos(x + self.state_x_offset, y + self.state_y_offset)
                self.svgItem.setProperty('state', 1)
                self.svgItem.setScale(self.state_scale)
                self.svgItem.setToolTip(self._helperReturnStateTooltip())

            self.addItem(self.svgItem)

            # self.force_name indicates that we're renaming a state or changing its properties
            # we're not adding it, so if self.force_name, we don't add to self.automaton_board
            # same thing with received_placement_coords
            # NOTE: this has to be called after _helperReturnStateToolTip because that increments state count
            # or something like that
            try:
                if received_placement_coords:
                    # print("debug: not adding state to board")
                    pass
                elif self.force_name:
                    # print("debug: not adding state to board")
                    pass
            except:
                self._addStateToAutomatonBoard()

        pass

    # long-ass function factory
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
        state_to_change = self._getNameFromState(state_to_change)
        print(f"info: state property added to automaton board. Before: {self.automaton_board.get(state_to_change)}",
              end=' ')
        if property != 'a' and property != 'i' and property != 'ai':
            raise ValueError(
                '_addStatePropertyToAutomatonBoard received unwelcome format for "property" param. If adding accepting and initial, add as \'ai\' not \'ia\'')
        if state_to_change not in self.automaton_board.keys():
            print(f"Did not find \"{state_to_change}\" in automaton board \"{self.automaton_board}\"")
            raise ValueError('No state found with that name in self.automaton_board. Cannot add properties to it')

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
        state_to_change = self._getNameFromState(state_to_change)

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
                state_to_change = self._getNameFromState(state_to_change)
            except:
                raise ValueError('state_to_change not found in self.automaton_board')
        if target_state not in self.automaton_board.keys():
            try:
                target_state = self._getNameFromState(target_state)
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

    def _getNameFromState(self, state_to_change):
        # receives tooltip in form like:
        # "State Q1. \nClick centre to change properties\nClick edge to add transition\nRight click to delete"
        # print(f"info: state_to_change.toolTip()={state_to_change.toolTip()}")
        return "Q" + state_to_change.toolTip().split('.')[0].replace("State ", "")

    def _closeOptions(self):
        available_ops = self._args[1]
        for i in available_ops:
            i.deleteLater()

    def _closureconnectTwoStates(self, target_state_tooltip):
        def _connectTwoStates():
            # connects origin state and target state with an arrow via their closest corners
            # will (soon) provide curved arrows in cases where there's a state between orig.. and target
            # also controls the orientation of arrows
            # and provides curved arrows when needed
            # and sets the textbox over arrows to the appropriate spot when arrows are scaled

            # the state from which our arrow emerges
            # print(f"info: self_args = {self._args}")
            originatingState = self._args[0]

            # the set of QPushButtons, one of which was pressed, to bring the user here.
            # deleted below
            available_ops = self._args[1]

            # grab the tooltip so we can identify the target state by its tooltip
            target_state_name = target_state_tooltip.replace("Connect to: ", "").replace("Connect to:", "")
            # print(f"info: target_state_name: '{target_state_name}'")
            for x in self.items():
                # print("item in self.items()...", x)
                if isinstance(x, svgItem_mod):
                    if x.property('state'):
                        # print('info: is state, with text:', x.toolTip())
                        if target_state_name in x.toolTip():
                            target_state = x
            if not target_state:
                print(f'Failed to find: "{target_state_name}"')
                raise ValueError('Target state not found')  # programming error. Should never happen. Has yet to happen.

            # the user has clicked one of the QPushButtons, so we delete all buttons in the group
            for i in available_ops:
                i.deleteLater()

            # determine the size, width, height of the origin and target states
            # so that we can determine corners correctly, and therefore place arrows correctly
            origin_size = originatingState.boundingRect().size() * self.state_scale * 0.4
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
