# an attempt to refactor mainwindow, allow its resizing, and use less code.
# WIP
# GOAL should be to separate automatically generated from custom code.
# this file should probably not be edited any more.
# 1) cretae a new UI in designer.
# 2) put custom code in a separate file (i.e. not this one)
# 3) develop that separate file, and leave this one alone.

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIcon, QPixmap, QFont
import resources.svg_paths as svg_paths


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # testing code
        # rect_item = QtWidgets.QGraphicsRectItem(QtCore.QRectF(0, 0, 100, 100))
        # rect_item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        # self.scene.addItem(rect_item)

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

        self.setupUi()

    def setupUi(self):
        self.scene = QtWidgets.QGraphicsScene(self)
        self.view = QtWidgets.QGraphicsView(self.scene)
        # self.setCentralWidget(self.view)

        self.setObjectName("Main Window")
        self.resize(842, 575)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        # self.centralwidget.resize(300, 300)
        # self.setCentralWidget(self.centralwidget)


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

        self.ui_skip_to_start_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.ui_skip_to_start_pushButton.setGeometry(QtCore.QRect(365, 430, 30, 30))
        self.ui_skip_to_start_pushButton.setText("")
        icon = QIcon()
        icon.addPixmap(QPixmap(svg_paths.skip_to_begin), QIcon.Normal, QIcon.Off)
        self.ui_skip_to_start_pushButton.setIcon(icon)
        self.ui_skip_to_start_pushButton.setIconSize(QtCore.QSize(100, 42))
        self.ui_skip_to_start_pushButton.setObjectName("ui_skip_to_start_pushButton")
        self.ui_skip_back_one_step_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.ui_skip_back_one_step_pushButton.setGeometry(QtCore.QRect(405, 430, 30, 30))
        self.ui_skip_back_one_step_pushButton.setText("")
        icon1 = QIcon()
        icon1.addPixmap(QPixmap(svg_paths.step_backwards), QIcon.Normal, QIcon.Off)
        self.ui_skip_back_one_step_pushButton.setIcon(icon1)
        self.ui_skip_back_one_step_pushButton.setIconSize(QtCore.QSize(100, 25))
        self.ui_skip_back_one_step_pushButton.setObjectName("ui_skip_back_one_step_pushButton")
        self.ui_skip_forward_one_step_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.ui_skip_forward_one_step_pushButton.setGeometry(QtCore.QRect(445, 430, 30, 30))
        self.ui_skip_forward_one_step_pushButton.setText("")
        icon2 = QIcon()
        icon2.addPixmap(QPixmap(svg_paths.step_forwards), QIcon.Normal, QIcon.Off)
        self.ui_skip_forward_one_step_pushButton.setIcon(icon2)
        self.ui_skip_forward_one_step_pushButton.setIconSize(QtCore.QSize(100, 25))
        self.ui_skip_forward_one_step_pushButton.setObjectName("ui_skip_forward_one_step_pushButton")
        self.ui_skip_to_end_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.ui_skip_to_end_pushButton.setGeometry(QtCore.QRect(485, 430, 30, 30))
        self.ui_skip_to_end_pushButton.setText("")
        icon3 = QIcon()
        icon3.addPixmap(QPixmap(svg_paths.skip_to_end), QIcon.Normal, QIcon.Off)
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
        self.bold_font = QFont()
        self.bold_font.setBold(True)
        self.mw_current_line_lbl.setFont(self.bold_font)
        self.mw_current_line_lbl.show()

        # added in order to be below self.mw_current_line_lbl and show past strings
        self.mw_previous_line_lbl = QtWidgets.QLabel(self.centralwidget)
        self.mw_previous_line_lbl.setGeometry(QtCore.QRect(550, 455, 130, 100))
        self.mw_previous_line_lbl.setObjectName("mw_previous_line_lbl")
        self.strikethrough_font = QFont()
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
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.setCentralWidget(self.centralwidget)
        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

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

if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())