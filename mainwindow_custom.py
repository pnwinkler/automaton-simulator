# -*- coding: utf-8 -*-
# Form implementation generated from reading ui file 'mainwindow.ui'
# Created by: PyQt5 UI code generator 5.10.1
# DO NOT REPLACE THIS FILE!!! it contains custom code

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QFont
from GUI_custom_scene import clickable_qgraphicsscene
from GUI_custom_ellipseitem import *
from generate_strings_from_regex import *
import automaton_logic as automaton_logic
import regex_generator as regex_generator
import resources.svg_paths as svg_paths
from collections import OrderedDict


class Ui_MainWindow(object):
    def __init__(self):
        # set up variables related to automaton logic
        # user_string holds the string entered into self.mw_enter_string_to_test_lineedit
        # it's typically passed on to other functions for testing acceptance against the
        # onscreen automaton
        self.user_string = None

        # whereas the self.user_string remains unchanged throughout, this string will be
        # printed, and used to demonstrate the progress of the automaton (the strikethrough area...)
        # self.progress_string = None

        # an index of our position in the user's string. Incremented as we progress the automaton,
        # decremented as we regress. Used for keeping track of current character for input processing
        self.index_in_user_str = 0

        # we don't create the automaton yet, because it will be created only when there's stuff to populate it with
        # it also allows for easier coding, where we can just check if not self.automaton:...
        self.automaton = None

        # used by self.updateAutomatonFromAutomatonBoard() to see if changes have been made
        self.previous_board = None

        # the regex problem for the user to solve. Appears in the top left.
        self.regex_to_solve = None

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(840, 580)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # set up the label in the top left
        self.ui_problem_to_solve_tooltip_label = QtWidgets.QLabel(self.centralwidget)
        self.ui_problem_to_solve_tooltip_label.setGeometry(QtCore.QRect(0, 0, 300, 21))
        self.ui_problem_to_solve_tooltip_label.setObjectName("ui_problem_to_solve_tooltip_label")
        self.ui_problem_to_solve_tooltip_label.setFont(QFont("Arial", 12))

        # create a QGraphicsView in self.centralwidget, to house the QGraphicsScene below
        self.mw_central_graphics_area_graphicsView = QtWidgets.QGraphicsView(self.centralwidget)

        # I don't know to what value to set this, or why it should be that particular value
        self.mw_central_graphics_area_graphicsView.setSceneRect(QtCore.QRectF(0, 0, 838, 428))

        # defines the borders of the graphicsView area. It's within these borders that the scene goes
        # if the scene is smaller than the view's geometry, scroll bars appear
        self.mw_central_graphics_area_graphicsView.setGeometry(QtCore.QRect(0, 0, 840, 430))
        self.mw_central_graphics_area_graphicsView.setObjectName("mw_central_graphics_area_graphicsView")

        # use our own subclass for the graphics scene
        self.mw_central_graphicsScene = clickable_qgraphicsscene(self.mw_central_graphics_area_graphicsView)
        self.mw_central_graphics_area_graphicsView.setScene(self.mw_central_graphicsScene)

        # print(self.centralwidget.size())

        # A block of code to put an object on screen. Used in testing sometimes
        # (item size can be changed after being added to scene)
        # self.svgItem = QtSvg.QGraphicsSvgItem(svg_paths.state_initial)
        # self.svgItem = svgItem_mod(svg_paths.state_initial)
        # self.svgSize = self.svgItem.renderer().defaultSize()
        # print('self.svgSize', self.svgSize)
        # self.svgItem.setScale(0.09)
        # self.mw_central_graphicsScene.addItem(self.svgItem)
        # self.svgItem.setPos(100, 100)
        # self.svgItem.setProperty('state', 1)
        # self.svgItem.setProperty('initial', 1)
        # self.svgItem.setToolTip("Default state mainwindow_custom.")

        # testing code
        # self.el = custom_ellipse()
        # self.el.setRect(50,50,120,120)
        # self.mw_central_graphicsScene.addItem(self.el)
        # self.el2 = QtWidgets.QGraphicsEllipseItem()
        # self.el2.setRect(160,145,10,10)
        # self.mw_central_graphicsScene.addItem(self.el2)
        # # collision detection works excellently with ellipses
        # print("Debug: Do the two ellipses collide?", self.el2.collidesWithItem(self.el))

        # set background color of graphicsView
        # self.mw_central_graphics_area_graphicsView.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(245,245,255)))

        self.ui_skip_to_start_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.ui_skip_to_start_pushButton.setGeometry(QtCore.QRect(365, 430, 30, 30))
        self.ui_skip_to_start_pushButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(svg_paths.skip_to_begin), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui_skip_to_start_pushButton.setIcon(icon)
        self.ui_skip_to_start_pushButton.setIconSize(QtCore.QSize(100, 42))
        self.ui_skip_to_start_pushButton.setObjectName("ui_skip_to_start_pushButton")
        self.ui_skip_back_one_step_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.ui_skip_back_one_step_pushButton.setGeometry(QtCore.QRect(405, 430, 30, 30))
        self.ui_skip_back_one_step_pushButton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(svg_paths.step_backwards), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui_skip_back_one_step_pushButton.setIcon(icon1)
        self.ui_skip_back_one_step_pushButton.setIconSize(QtCore.QSize(100, 25))
        self.ui_skip_back_one_step_pushButton.setObjectName("ui_skip_back_one_step_pushButton")
        self.ui_skip_forward_one_step_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.ui_skip_forward_one_step_pushButton.setGeometry(QtCore.QRect(445, 430, 30, 30))
        self.ui_skip_forward_one_step_pushButton.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(svg_paths.step_forwards), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui_skip_forward_one_step_pushButton.setIcon(icon2)
        self.ui_skip_forward_one_step_pushButton.setIconSize(QtCore.QSize(100, 25))
        self.ui_skip_forward_one_step_pushButton.setObjectName("ui_skip_forward_one_step_pushButton")
        self.ui_skip_to_end_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.ui_skip_to_end_pushButton.setGeometry(QtCore.QRect(485, 430, 30, 30))
        self.ui_skip_to_end_pushButton.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(svg_paths.skip_to_end), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui_skip_to_end_pushButton.setIcon(icon3)
        self.ui_skip_to_end_pushButton.setIconSize(QtCore.QSize(100, 42))
        self.ui_skip_to_end_pushButton.setObjectName("ui_skip_to_end_pushButton")
        self.ui_take_string_to_test_lineedit = QtWidgets.QLineEdit(self.centralwidget)
        self.ui_take_string_to_test_lineedit.setGeometry(QtCore.QRect(365, 460, 150, 31))
        self.ui_take_string_to_test_lineedit.setToolTip("")
        self.ui_take_string_to_test_lineedit.setToolTipDuration(2)
        self.ui_take_string_to_test_lineedit.setObjectName("ui_take_string_to_test_textEdit")
        self.ui_live_input_proc_summary_label = QtWidgets.QLabel(self.centralwidget)
        self.ui_live_input_proc_summary_label.setGeometry(QtCore.QRect(375, 490, 130, 17))
        self.ui_live_input_proc_summary_label.setObjectName("ui_live_input_proc_summary_label")
        self.ui_input_accepted_or_rejected_label = QtWidgets.QLabel(self.centralwidget)
        self.ui_input_accepted_or_rejected_label.setGeometry(QtCore.QRect(410, 530, 130, 21))
        self.ui_input_accepted_or_rejected_label.setObjectName("ui_input_accepted_or_rejected_label")

        # added to display bolded text, for the currently processed string
        self.mw_current_line_lbl = QtWidgets.QLabel(self.centralwidget)
        self.mw_current_line_lbl.setGeometry(QtCore.QRect(550, 425, 120, 35))
        self.mw_current_line_lbl.setObjectName("mw_current_line_lbl")
        # self.mw_current_line_lbl.setText("TK: this will hold currently processed line (i.e. user string minus already done stuff")
        self.bold_font = QtGui.QFont()
        self.bold_font.setBold(True)
        self.mw_current_line_lbl.setFont(self.bold_font)
        self.mw_current_line_lbl.show()

        # added in order to be below self.mw_current_line_lbl and show past strings
        self.mw_previous_line_lbl = QtWidgets.QLabel(self.centralwidget)
        self.mw_previous_line_lbl.setGeometry(QtCore.QRect(550, 455, 130, 100))
        self.mw_previous_line_lbl.setObjectName("mw_previous_line_lbl")
        self.strikethrough_font = QtGui.QFont()
        self.strikethrough_font.setStrikeOut(True)
        self.mw_previous_line_lbl.setFont(self.strikethrough_font)
        self.mw_previous_line_lbl.show()

        self.ui_difficulty_easy_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.ui_difficulty_easy_pushButton.setGeometry(QtCore.QRect(0, 430, 110, 41))
        self.ui_difficulty_easy_pushButton.setObjectName("ui_difficulty_easy_pushButton")
        self.ui_difficulty_medium_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.ui_difficulty_medium_pushButton.setGeometry(QtCore.QRect(0, 470, 110, 41))
        self.ui_difficulty_medium_pushButton.setObjectName("ui_difficulty_medium_pushButton")
        self.ui_difficulty_hard_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.ui_difficulty_hard_pushButton.setGeometry(QtCore.QRect(0, 510, 110, 41))
        self.ui_difficulty_hard_pushButton.setObjectName("ui_difficulty_hard_pushButton")
        self.ui_update_automaton_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.ui_update_automaton_pushButton.setGeometry(QtCore.QRect(730, 510, 110, 41))
        self.ui_update_automaton_pushButton.setObjectName("ui_update_automaton_pushButton")
        self.ui_submit_solution_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.ui_submit_solution_pushButton.setGeometry(QtCore.QRect(730, 470, 110, 41))
        self.ui_submit_solution_pushButton.setObjectName("ui_submit_solution_pushButton")
        self.ui_request_hint_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.ui_request_hint_pushButton.setGeometry(QtCore.QRect(730, 430, 110, 41))
        self.ui_request_hint_pushButton.setObjectName("ui_request_hint_pushButton")
        self.mw_central_graphics_area_graphicsView.raise_()
        self.ui_problem_to_solve_tooltip_label.raise_()
        self.ui_skip_to_start_pushButton.raise_()
        self.ui_skip_back_one_step_pushButton.raise_()
        self.ui_skip_forward_one_step_pushButton.raise_()
        self.ui_skip_to_end_pushButton.raise_()
        self.ui_take_string_to_test_lineedit.raise_()
        self.ui_live_input_proc_summary_label.raise_()
        self.ui_input_accepted_or_rejected_label.raise_()
        self.ui_difficulty_easy_pushButton.raise_()
        self.ui_difficulty_medium_pushButton.raise_()
        self.ui_difficulty_hard_pushButton.raise_()
        self.ui_update_automaton_pushButton.raise_()
        self.ui_submit_solution_pushButton.raise_()
        self.ui_request_hint_pushButton.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.ui_problem_to_solve_tooltip_label.setText(_translate("MainWindow", "Problem to solve: "))
        self.ui_take_string_to_test_lineedit.setPlaceholderText(_translate("MainWindow", "Enter a string to test"))
        self.ui_live_input_proc_summary_label.setText(_translate("MainWindow", ""))
        self.ui_input_accepted_or_rejected_label.setText(_translate("MainWindow", ""))
        self.ui_difficulty_easy_pushButton.setText(_translate("MainWindow", "Easy"))
        self.ui_difficulty_medium_pushButton.setText(_translate("MainWindow", "Medium"))
        self.ui_difficulty_hard_pushButton.setText(_translate("MainWindow", "Hard"))
        self.ui_update_automaton_pushButton.setText(_translate("MainWindow", "Update auto."))
        self.ui_submit_solution_pushButton.setText(_translate("MainWindow", "Submit"))
        self.ui_request_hint_pushButton.setText(_translate("MainWindow", "Hint"))

    def renameGuiElements(self):
        # I want maximally descriptive names as items are being created, but shorter names
        # when I work with them
        # ui_ indicates items generated by Qt, and mw_ items that I'm modifying
        # so when I see a ui_ item elsewhere, I know not to modify it
        self.mw_problem_to_solve_lbl = self.ui_problem_to_solve_tooltip_label
        self.mw_user_string_accepted_or_rejected_lbl = self.ui_input_accepted_or_rejected_label
        self.mw_enter_string_to_test_lineedit = self.ui_take_string_to_test_lineedit
        self.mw_easy_pushbtn = self.ui_difficulty_easy_pushButton
        self.mw_med_pushbtn = self.ui_difficulty_medium_pushButton
        self.mw_hard_pushbtn = self.ui_difficulty_hard_pushButton
        self.mw_hint_pushbtn = self.ui_request_hint_pushButton
        self.mw_submit_pushbtn = self.ui_submit_solution_pushButton
        self.mw_update_automaton_pushbtn = self.ui_update_automaton_pushButton
        self.mw_skip_to_begin_pushbtn = self.ui_skip_to_start_pushButton
        self.mw_step_backwards_pushbtn = self.ui_skip_back_one_step_pushButton
        self.mw_step_forwards_pushbtn = self.ui_skip_forward_one_step_pushButton
        self.mw_skip_to_end_pushbtn = self.ui_skip_to_end_pushButton
        self.mw_live_summary_lbl = self.ui_live_input_proc_summary_label

    def linkButtonsWithFunctions(self):
        # generate a problem and write to the appropriate label
        self.mw_easy_pushbtn.clicked.connect(self.requestProblemEasy)
        self.mw_med_pushbtn.clicked.connect(self.requestProblemMedium)
        self.mw_hard_pushbtn.clicked.connect(self.requestProblemHard)

        # accepts a string to test. Reads the user's input, saves it,
        # other functions may use that string to test the automaton
        self.mw_enter_string_to_test_lineedit.editingFinished.connect(self.takeStringToTest)

        # when the automaton progresses, indicate whether the user's entered string is
        # accepted/accepting/rejected/rejecting, where the -ed prints indicate the final result
        # and the -ing prints indicate acceptance *at the current stage* of progression
        # self.mw_step_forwards_pushbtn.clicked.connect(self.stepForwards)

        # generate a problem to solve
        # self.mw_easy_pushbtn.clicked.connect(self.requestProblemEasy)
        self.mw_easy_pushbtn.clicked.connect(self.requestProblemEasy)
        self.mw_med_pushbtn.clicked.connect(self.requestProblemMedium)
        self.mw_hard_pushbtn.clicked.connect(self.requestProblemHard)

        # generate a hint
        self.mw_hint_pushbtn.clicked.connect(self.generateHint)

        # let user submit solution, then test it and do whatever else necessary
        self.mw_submit_pushbtn.clicked.connect(self.acceptSubmission)

        # toggle the solution
        self.mw_update_automaton_pushbtn.clicked.connect(self.updateAutomaton)

        # playback control
        self.mw_skip_to_begin_pushbtn.clicked.connect(self.skipToBegin)
        self.mw_step_backwards_pushbtn.clicked.connect(self.stepBackwards)
        self.mw_step_forwards_pushbtn.clicked.connect(self.stepForwards)
        self.mw_skip_to_end_pushbtn.clicked.connect(self.skipToEnd)

    def takeStringToTest(self):
        # called when user finishes editing self.mw_enter_string_to_test_lineedit
        # takes the user string, resets the automaton to start(?), then passes
        # the string on to automaton logic for processing
        self.user_string = self.mw_enter_string_to_test_lineedit.text()
        # self.progress_string = self.user_string
        self.mw_live_summary_lbl.setText("Entered:  " + self.user_string)
        # italics = QtGui.QFont()
        # italics.setItalic(True)
        # self.mw_live_summary_lbl.setFont(italics)
        print(f"User string \"{self.user_string}\" saved")

    def updateAutomatonFromAutomatonBoard(self):
        # looks to self.mw_central_graphicsScene.automaton_board to determine the
        # properties of the board that the user wishes to create
        # then interprets automaton_board in order to create the objects and transitions
        # in automaton_logic.py
        # when I have time, I might write a more efficient solution
        # given limited time, this is the fastest-to-write, least error-prone solution I could come up with

        # we use deepcopy because automaton_board is a dict and is therefore passed by reference
        # but we don't want to change it here
        self.automaton = automaton_logic.Automaton()
        # received_board = deepcopy(self.mw_central_graphicsScene.automaton_board)

        # we use an OrderedDict so that that our automaton nodes in node_lst will have their indexes match
        # those of states_to_add (in block below)
        received_board = OrderedDict(self.mw_central_graphicsScene.automaton_board)

        # print("received board", received_board)
        states_to_add = received_board.keys()

        # create a list of nodes, so that they are all created and useable as target states
        # for when we want to have them be target nodes for transitions
        node_lst = []
        for s in states_to_add:
            node_lst.append(self.automaton.addStateReturnID())

        # print("DEBUG: received board", received_board)

        # use an index to iterate through the newly-created nodes, as well as the values in
        # received_board, which as an OrderedDict, will retain order.
        for x in range(len(states_to_add)):
            # use this index for both list and dict
            # to create transitions
            # for values in the .get stuff
            originating_node = node_lst[x]

            # get is the value for each key in order, in received_board
            get = list(received_board.values())[x]
            # print("debug: get=", get)

            if not get:
                # there's no value registered for that state. i.e. no outbound to add
                continue

            # set properties, such as accepting or initial
            # and shorten get accordingly, removing 'a'/'i' this signals
            if get[0] == 'a':
                self.automaton.flipAcceptingOrRejecting(originating_node)
            elif get[1] == 'i':
                self.automaton.setInitialNode(originating_node)

            try:
                if get[1] == 'a':
                    self.automaton.flipAcceptingOrRejecting(originating_node)
                if get[1] == 'i':
                    self.automaton.setInitialNode(originating_node)
            except IndexError:
                pass

            if self.automaton.initial_node_obj == self.automaton.takeIDReturnNodeObject(originating_node):
                # we set it to be initial, so we remove a leading (which will be either a or i)
                get = get[1:]
            if self.automaton.takeIDReturnNodeObject(originating_node).accepting:
                # we set it to be initial, so we remove a leading letter (which will be either a or i)
                get = get[1:]

            # for the values at that key
            for c in get:
                if c == "Q" or c == 'i':
                    # don't add the state name to transitions
                    pass
                elif c.isdigit():
                    # it's the numeric portion of our target state's identifier (e.g. Q3)
                    # we save it in the N1__ format, just in case we need to find it in our automaton states
                    target_state = "N10" + c
                else:
                    # add the transition letter to transitions
                    self.automaton.addTransition(originating_node, target_state, c)
                    # print(f"info: adding transition {c}")
        # print("States and transitions added to automaton")
        print("Automaton updated")
        print("Nodes in automaton", [node.identifier for node in self.automaton.node_collection])
        for node in self.automaton.node_collection:
            print(f"\tNode {node.identifier}, with outbound transitions: {node.outbound_transitions}")

    def updateAutomatonBoard(self):
        # I don't think we need this automaton_board doesn't do anything within the program,
        # it's just for external use. If we need to change the appearance of its items, I think we can just
        # call them directly, or make a new function in GUI_..py and call that (for example to scale an item)
        pass

    def generateProblemToSolve(self, requested_difficulty):
        # called by the 3 functions below.
        # randomly generates a problem for the user to solve
        # then writes it to the label
        self.regex_to_solve = regex_generator.generateRegex(requested_difficulty)
        self.mw_problem_to_solve_lbl.setText("Problem to solve: " + self.regex_to_solve)
        self.mw_problem_to_solve_lbl.setFont(QFont("Arial", 12))

    def requestProblemEasy(self):
        self.generateProblemToSolve('easy')

    def requestProblemMedium(self):
        self.generateProblemToSolve('medium')

    def requestProblemHard(self):
        self.generateProblemToSolve('hard')

    # def acceptOrRejectUserString(self):
    #     # determines whether a user's string is accepted or rejected
    #     # probably needs the formula of the automaton on screen, in the user space
    #     return 'PLACEHOLDER string accepted'

    def generateHint(self):
        # we should test the current automaton (without using GUI elements), on a variety of strings
        # if it passes a string in the fail category, or fails one in the pass category, we write that
        # to the hint label

        if not self.regex_to_solve:
            print("No regex to solve")
            return
        if not self.automaton:
            print("No automaton created yet")
            return

        # returns 2 lists, first of pass strings, second of fail strings. Both sorted by shortest first
        pass_list, fail_list = generate_Strings_from_reg(self.regex_to_solve)

        # needs an input string. Returns True if the whole thing is accepted, False if it's rejected
        for p in pass_list:
            passed = self.automaton.determineWholeInputAcceptance(p)
            if not passed:
                print(p)
                self.mw_hint_pushbtn.setText(p)
                return False
        for f in fail_list:
            failed = self.automaton.determineWholeInputAcceptance(f)
            if not failed:
                print(f)
                self.mw_hint_pushbtn.setText(p)
                return False
        print("Automaton fully correct! No hint to give")
        return True

    def acceptSubmission(self):
        # this handles hints. If it returns true we say ACCEPTED, else REJECTED
        # this way we automatically generate hints for the user
        if not self.automaton:
            print("No automaton recognized yet. Please create one, and press \"Update Automaton\"")

        passed = self.generateHint()
        if passed:
            self.mw_submit_pushbtn.setText("ACCEPTED")
        else:
            self.mw_submit_pushbtn.setText("REJECTED")

    def updateAutomaton(self):
        # after a user submitted / gave up, this function
        # lets them switch between viewing their submission
        # and the generated solution
        self.updateAutomatonFromAutomatonBoard()
        # print('Updated automaton')
        # return 'PLACEHOLDER toggle()'

    def skipToBegin(self):
        # recreate the automaton or regressToStart(),
        # reset indexes,
        # clear the history and current lines
        # clear accepted / rejected label
        # reset hint button
        # reset submit button
        if not self.automaton:
            return

        self.automaton.regressToStart()
        self.index_in_user_str = 0
        self.mw_current_line_lbl.setText("")
        self.mw_previous_line_lbl.setText("")
        self.mw_user_string_accepted_or_rejected_lbl.setText("")
        self.mw_hint_pushbtn.setText("Hint")
        self.mw_submit_pushbtn.setText("Submit")

        print('skipped to beginning')
        return 'PLACEHOLDER skipToBegin()'

    def stepBackwards(self):
        # strictly speaking, this is inefficient, but it minimizes how many places need maintenance
        # as opposed to computing each step in reverse, then exactly undoing what each function did previously
        # it's also fast, so performance is not an issue
        len_contents_before = len(self.mw_current_line_lbl.text())

        self.skipToBegin()
        while len(self.mw_current_line_lbl.text()) != len_contents_before + 1:
            retval = self.stepForwards()
            if retval == -1:
                # otherwise we get "No valid automaton" spam
                break

    def stepForwards(self):
        # todo:
        #  consider implementing visual indications of changes (i.e. active node)
        #  if so:
        #   we probably need a way to translate between what self.automaton.active_node_obj is,
        #   and what the graphical element that we want to adjust / unadjust is. Or just scale
        if not self.automaton:
            print("No valid automaton. If you've created one, please click the Update Automaton button")
            return -1
        if not self.user_string:
            print("No user string provided. Please enter it into the text field in the middle, then press enter")
            return -1

        # print("DEBUG: self.user_string", self.user_string)
        try:
            # try block completes once, fails next time
            # print("DEBUG: index in try block:", self.index_in_user_str)
            # NOTE: the index is handled in the self.progressLiveFeed() function
            accepting = self.automaton.progressOneStep(self.user_string[self.index_in_user_str])
            # print("DEBUG: try block accepting?", accepting)
            # self.index_in_user_str += 1
            # print("DEBUG: happening")
        except IndexError:
            # string is exhausted. We test whether the current node is accepting or rejecting
            # print("DEBUG: index", self.index_in_user_str)
            # print("DEBUG: user_str", self.user_string)
            accepting = self.automaton.progressOneStep("")
            # print("DEBUG: except block accepting?", accepting)
            if accepting:
                self.mw_user_string_accepted_or_rejected_lbl.setText("ACCEPTED")

        if not accepting:
            self.mw_user_string_accepted_or_rejected_lbl.setText("REJECTED")
            return False
        else:
            self.mw_user_string_accepted_or_rejected_lbl.setText("accepting")
            self.progressLiveFeed()
            return True

    def skipToEnd(self):
        # the +1 is important! We use it to test whether the automaton accepts "" at the end of the string
        # i.e. is the final state accepting?
        if self.user_string is not None:
            for c in range(len(self.user_string) + 1):
                self.stepForwards()
        else:
            # I don't think we need to show this to the user within the GUI right?
            # actually, at some point it's worth doing so. Just create a short-lived label
            # that draws their attention, then disappears
            print("Cannot progress automaton. No user string provided to test against.")

    def progressLiveFeed(self):
        # updates the "live" processing area, below the box where the user entered the string.
        # this moves characters, bolds them, strikes them through, each run.

        if self.index_in_user_str == 0:
            # we are just starting
            curr_text = self.mw_live_summary_lbl.text()

            # get rid of initial tabs
            curr_text.replace("\t", "").replace("\t", "")

            # set topmost label, right of centre screen, on the bottom portion of the screen
            # to equal the newly-entered user string
            self.index_in_user_str += 1
            curr_text = self.user_string[self.index_in_user_str:]
            self.mw_current_line_lbl.setText('\n' + curr_text)

            # clear past history (there shoudn't be any anyway)
            self.mw_previous_line_lbl.setText("")
        else:
            if self.index_in_user_str == len(self.user_string) - 1:
                previous_content_of_current_line_lbl = self.mw_current_line_lbl.text()

                print("User string exhausted. No more input to process")
                self.mw_current_line_lbl.setText("ε")

                updated_history = previous_content_of_current_line_lbl + self.mw_previous_line_lbl.text()
                self.mw_previous_line_lbl.setText(updated_history)

                # prompts self.stepForwards() to continue, and process the empty string
                self.index_in_user_str += 1
                return

            # todo: resolve font issues in the top label
            # set self.mw_current_line_lbl to the remainder of string
            self.mw_current_line_lbl.setFont(QFont("Arial", 12))
            self.index_in_user_str += 1
            previous_content_of_current_line_lbl = self.mw_current_line_lbl.text()
            self.mw_current_line_lbl.setText("\n" + self.user_string[self.index_in_user_str:])
            print("info: remainder of user string:", self.user_string[self.index_in_user_str:])

            # we always prepend to mw_previous_line_lbl
            updated_history = previous_content_of_current_line_lbl + self.mw_previous_line_lbl.text()
            self.mw_previous_line_lbl.setText(updated_history)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()  # class object
    ui.setupUi(MainWindow)  # class function. basically an __init__

    # do whatever else setup, linking etc
    ui.renameGuiElements()
    ui.linkButtonsWithFunctions()

    MainWindow.show()

    # print('TEST:\n',
    #       '\n'.join([ui.generateProblemToSolve('easy'),
    #                  ui.acceptOrRejectUserString(),
    #                  ui.generateHint(),
    #                  ui.toggleSolution(),
    #                  ui.acceptSubmission(),
    #                  ui.skipToBegin(),
    #                  ui.stepBackwards(),
    #                  ui.stepForwards(),
    #                  ui.skipToEnd(),
    #                  ui.updateStringSummary()]))

    sys.exit(app.exec_())
