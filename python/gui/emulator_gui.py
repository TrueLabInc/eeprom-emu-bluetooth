#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'emulator.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

import os
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
from subprocess import Popen, PIPE
from emulator_2 import Emulator_2
from PyQt4.QtCore import QThread
import sys, time
from file_monitor import FileMonitor

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class IndicatorBlinkThread(QThread):
    status_signal = QtCore.pyqtSignal(object)
    def __init__(self, indicator, duration):
        QThread.__init__(self)
        self.indicator = indicator
        self.duration = duration

    def _blink(self, duration):
        self.status_signal.emit("active")
        time.sleep(duration)
        self.status_signal.emit("inactive")

    def blink(self, duration):
        if duration > 0:
            self._blink(duration)
        elif duration < 0:
            duration =duration * -1
            while 1:
                self._blink(duration)
                time.sleep(duration)

    def kill(self):
        self.indicator.set_inactive_clr()
        self.terminate()

    def run(self):
        self.blink(self.duration)

class PeriodicThread(QThread):
    periodic_signal = QtCore.pyqtSignal(object)
    def __init__(self, period=1):
        QThread.__init__(self)
        self.stop = False
        self.period = period

    def kill(self):
        self.stop = True

    def run(self):
         while not self.stop:
             self.periodic_signal.emit("")
             time.sleep(self.period)

class Indicator(object):
    def __init__(self, x, y, label='', parent = None):
        self.indicator = self._indicator(x, y, label, parent)
        self.active_color = "rgb(149,255,10)"
        self.nok_active_color = "rgb(179,7,10)"
        self.inactive_color = "rgb(179,173,171)"
        self.blink_thr = IndicatorBlinkThread(self, 1)
        self.blink_thr.status_signal.connect(self.change_active_state)
        self.blink_ok = True
        self.blink_status = 'ok'
        self.light_effect = QtGui.QGraphicsDropShadowEffect(self.indicator)
        self.light_effect.setOffset(0, 0)
        self.light_effect.setBlurRadius(0)
        self.indicator.setGraphicsEffect(self.light_effect)
        self.set_inactive_clr()

    def blink(self, duration, status='ok'):
        self.blink_status = status
        self.blink_thr.duration = duration
        self.blink_thr.start()

    def stop_blink(self):
        self.blink_thr.kill()

    def set_active_clr(self):
        _qcolor = [int(i) for i in self.active_color.replace("rgb", '').replace("(",'').replace(")",'').split(",")]
        _qcolor.append(255)
        self.light_effect.setColor(QColor(*_qcolor))
        self.light_effect.setBlurRadius(15)
        self.indicator.setStyleSheet("QFrame {{ background-color: {} }}".format(self.active_color))

    def set_inactive_clr(self):
        self.indicator.setStyleSheet("QFrame {{ background-color: {} }}".format(self.inactive_color))
        self.light_effect.setBlurRadius(0)

    def set_clr(self, clr):
        _qcolor = [int(i) for i in clr.replace("rgb", '').replace("(",'').replace(")",'').split(",")]
        _qcolor.append(255)
        self.light_effect.setColor(QColor(*_qcolor))
        self.light_effect.setBlurRadius(15)
        self.indicator.setStyleSheet("QFrame {{ background-color: {} }}".format(clr))

    def change_active_state(self, state):
        if self.blink_status == 'ok':
            if state == 'active':
                #self.indicator.setStyleSheet("QFrame {{ background-color: {} }}".format(self.active_color))
                self.set_active_clr()
            elif state == 'inactive':
                #self.indicator.setStyleSheet("QFrame {{ background-color: {} }}".format(self.inactive_color))
                self.set_inactive_clr()
        elif self.blink_status == 'nok':
            if state == 'active':
                self.set_clr(self.nok_active_color)
            elif state == 'inactive':
                self.set_inactive_clr()

    def _indicator(self, x, y, label, parent = None):
        indicator = QtGui.QFrame(parent)
        indicator.setGeometry(QtCore.QRect(x, y, 15, 10))
        indicator.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
        indicator.setLineWidth(1)
        indicator.setObjectName(_fromUtf8("frame"))
        #indicator.setStyleSheet("QFrame { background-color: rgb(100,140,100) }")
        if label:
            indicatorLabel = QLabel(parent)
            indicatorLabel.setText(label)
            indicatorLabel.setGeometry(x+20,y,60,20)
        effect = QtGui.QGraphicsBlurEffect(indicator)
        effect.setBlurRadius(2)
        indicator.setGraphicsEffect(effect)
        return indicator

class Ui_MainWindow(object):
    def __init__(self):
        self.threads = []

    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(410, 490)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))

        self.emulationFrame = self._frame(5, 105, 400, 160, "emulation", self.centralwidget)
        self.emulationFrame.setEnabled(False)
        self.fileInUse = QtGui.QLineEdit(self.emulationFrame)
        self.fileInUse.setObjectName(_fromUtf8("file in use"))
        self.fileInUse.setGeometry(65, 30, 250, 25)
        self.edit_btn = self._button(230, 60, 45, 25, "edit", self.emulationFrame)
        self.browse_btn = self._button(275, 60, 45, 25, "...", self.emulationFrame)
        self.auto_open_checkbox = QtGui.QCheckBox("auto open file", self.emulationFrame)
        self.auto_open_checkbox.setGeometry(62, 60, 20, 20)
        self.auto_open_label = QLabel(self.emulationFrame)
        self.auto_open_label.move(85, 62)
        self.auto_open_label.setText("auto open file")
        self.fileInUse.setFrame(1)
        self.fileInUse.setStyleSheet("background-color: rgb(245,255,255)")
        self.fileInUseLabel = QLabel(self.emulationFrame)
        self.fileInUseLabel.setText("File in use")
        self.fileInUseLabel.setGeometry(5,32,55,20)
        self.read_sram_btn = self._button(20, 100, 70, 20, "read sram", self.emulationFrame)
        self.read_flash_btn = self._button(90, 100, 70, 20, "read flash", self.emulationFrame)
        self.emulation_btn = self._button(160, 100, 70, 20, "EMULATE", self.emulationFrame)
        self.write_flash_btn = self._button(230, 100, 110, 20, "STORE TO FLASH", self.emulationFrame)
        #self.load_flash_btn = self._button(300, 100, 70, 20, "load flash", self.emulationFrame)
        self.emulation_frame_blur_effect = QtGui.QGraphicsBlurEffect(self.emulationFrame)
        self.emulation_frame_blur_effect.setBlurRadius(2)
        self.emulationFrame.setGraphicsEffect(self.emulation_frame_blur_effect)
        self.progressBar = QtGui.QProgressBar(self.emulationFrame)
        self.progressBar.setGeometry(QtCore.QRect(20, 120, 370, 40))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.controlFrame = self._frame(5, 5, 200, 100, "control", self.centralwidget)
        self.connect_btn = self._button(10, 30, 70, 20, "connect", self.controlFrame)

        self.ping_btn = self._button(10, 50, 70, 20, "ping", self.controlFrame)
        QtCore.QObject.connect(self.ping_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), MainWindow.ping_button_slot)

        self.flashBankFrame = self._frame(205, 5, 200, 100, "flash bank in use", self.centralwidget)
        self.flash_bank1_radio_btn = QtGui.QRadioButton("bank1", self.flashBankFrame)
        self.flash_bank1_radio_btn.move(10,32)
        self.flash_bank2_radio_btn = QtGui.QRadioButton("bank2", self.flashBankFrame)
        self.flash_bank2_radio_btn.move(10, 52)
        self.flash_bank3_radio_btn = QtGui.QRadioButton("bank3", self.flashBankFrame)
        self.flash_bank3_radio_btn.move(10, 72)
        self.lcd_flash_wear1 = QtGui.QLCDNumber(self.flashBankFrame)
        self.lcd_flash_wear1.setGeometry(75,30,80,22)
        #self.lcd_flash_wear1.display("10000")
        self.lcd_flash_wear2 = QtGui.QLCDNumber(self.flashBankFrame)
        self.lcd_flash_wear2.setGeometry(75,52,80,22)
        #self.lcd_flash_wear2.display("10000")
        self.lcd_flash_wear3 = QtGui.QLCDNumber(self.flashBankFrame)
        self.lcd_flash_wear3.setGeometry(75,74,80,22)
        #self.lcd_flash_wear3.display("10000")
        self.connect_ind = Indicator(85, 36, '', self.controlFrame)
        self.connect_ind.active_color = "rgb(75, 252, 72)"
        self.ping_ind = Indicator(85, 56, '', self.controlFrame)
        self.ping_ind.active_color = "rgb(75, 252, 72)"
        self.rw_ind = Indicator(110, 36, '', self.controlFrame)
        self.rw_ind.active_color = "rgb(252, 255, 21)"

        self.widget = QtGui.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(610, 480, 131, 61))
        self.widget.setObjectName(_fromUtf8("widget"))

        self.gridLayout = QtGui.QGridLayout(self.widget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))

        self.output = self._frame(5, 275, 400, 200, "console", self.centralwidget)

        self.main_output = QtGui.QTextBrowser(self.output)
        self.main_output.setObjectName(_fromUtf8("main_output"))
        self.main_output.setGeometry(5, 25, 390, 130)
        self.main_output.setStyleSheet("background-color: rgb(247,255,255)")
        self.main_output.setFontPointSize(8)

        self.cmdLine = QtGui.QLineEdit(self.output)
        self.cmdLine.setObjectName(_fromUtf8("cmd_line"))
        self.cmdLine.setGeometry(50, 160, 340, 25)
        self.cmdLine.setFrame(1)
        self.cmdLine.setStyleSheet("background-color: rgb(220,255,255)")
        self.cmdLabel = QLabel(self.output)
        self.cmdLabel.setText("CMD")
        self.cmdLabel.setGeometry(10,163,30,20)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 556, 29))
        self.menubar.setObjectName(_fromUtf8("menubar"))

        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        #MainWindow.setStyleSheet("background-color: rgb(229,255,215)")

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.connect_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), MainWindow.connect_button_slot)
        QtCore.QObject.connect(self.read_sram_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), MainWindow.read_sram_btn_slot)
        QtCore.QObject.connect(self.read_flash_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), MainWindow.read_flash_btn_slot)
        QtCore.QObject.connect(self.write_flash_btn, QtCore.SIGNAL(_fromUtf8("clicked()")),MainWindow.write_flash_btn_slot)
        QtCore.QObject.connect(self.emulation_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), MainWindow.emulation_btn_slot)
        QtCore.QObject.connect(self.browse_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), MainWindow.browse_button_slot)
        QtCore.QObject.connect(self.edit_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), MainWindow.edit_button_slot)
        #QtCore.QObject.connect(self.load_flash_btn, QtCore.SIGNAL(_fromUtf8("clicked()")), MainWindow.emulation_btn_slot)
        QtCore.QObject.connect(self.flash_bank1_radio_btn, QtCore.SIGNAL(_fromUtf8("clicked()")),
                               MainWindow.flash_bank_radio_btn_slot1)
        QtCore.QObject.connect(self.flash_bank2_radio_btn, QtCore.SIGNAL(_fromUtf8("clicked()")),
                               MainWindow.flash_bank_radio_btn_slot2)
        QtCore.QObject.connect(self.flash_bank3_radio_btn, QtCore.SIGNAL(_fromUtf8("clicked()")),
                               MainWindow.flash_bank_radio_btn_slot3)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.connect_btn, self.main_output)

    def _button(self, x, y, x_siz, y_siz, name, parent):
        button = QtGui.QPushButton(parent)
        button.setGeometry(QtCore.QRect(x, y, x_siz, y_siz))
        button.setObjectName(_fromUtf8(name))
        button.setText(name)
        return button

    def _frame(self, x, y, x_siz, y_siz, name, parent):
        #group frame
        frame = QtGui.QGroupBox(parent)
        frame.setTitle(name)
        frame.setGeometry(QtCore.QRect(x, y, x_siz, y_siz))
        frame.setObjectName(_fromUtf8(name))
        frame.setFlat(0)
        hLine = QtGui.QFrame(frame)
        #hLine.setFrameStyle(QFrame.HLine)
        hLine.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
        hLine.setGeometry(5, 22, x_siz-10, 2)
        frame.setStyleSheet("background-color: rgb(239,240,241)")
        return frame

    def _indicator(self, x, y, label, parent = None):
        indicator = QtGui.QFrame(parent)
        indicator.setGeometry(QtCore.QRect(x, y, 15, 15))
        indicator.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)
        indicator.setLineWidth(1)
        indicator.setObjectName(_fromUtf8("frame"))
        indicator.setStyleSheet("QFrame { background-color: rgb(100,140,100) }")
        if label:
            indicatorLabel = QLabel(parent)
            indicatorLabel.setText(label)
            indicatorLabel.setGeometry(x+20,y,60,20)
        effect = QtGui.QGraphicsBlurEffect(indicator)
        effect.setBlurRadius(2)
        indicator.setGraphicsEffect(effect)
        return indicator

    def chg_clr(self):
        self.threads.append('connected_status')
        self.clr_thrd.start()

    def change_status_clr(self, s):
        if s=='green':
            self.connect_ind.setStyleSheet("QFrame { background-color: green }")
        if s == 'red':
            self.connect_ind.setStyleSheet("QFrame { background-color: red }")

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "EEPROM EMULATOR BT", None))
        self.connect_btn.setText(_translate("MainWindow", "connect", None))
        #self.ping_btn.setText(_translate("MainWindow", "ping", None))

class EmulatorThread(QThread):
    console_output = QtCore.pyqtSignal(object)
    status_signal = QtCore.pyqtSignal(object)
    progress_signal = QtCore.pyqtSignal(object)
    def __init__(self):
        QThread.__init__(self)
        self.emulator = Emulator_2(self.console_output.emit, self.progress_signal.emit)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.emulator_handler = False

    def kill(self):
        #self.emu_connection = False
        self.status_signal.emit("nok")
        self.emu_connection.close()
        self.terminate()

    def run(self):
        #self.emulator.load_config_file()
        self.emu_connection = self.emulator.call_emulator()
        if self.emu_connection:
            self.status_signal.emit("ok")

class EmulationThread(QThread):
    def __init__(self, method, args=None):
        QThread.__init__(self)
        self.method = method
        self.stop_method = False
        self.args = args

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.emulator_handler = False

    def kill(self):
        self.stop_method = True
        self.terminate()

    def run(self):
        while not self.stop_method:
            self.method(*self.args)
            time.sleep(0.5)


class Emulator_gui(QtGui.QMainWindow, Ui_MainWindow):
    rw_ind_signal = QtCore.pyqtSignal(object)
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.rw_ind_signal.connect(self.rw_indicator_ctrl)
        self.setupUi(self)
        self.emu = EmulatorThread()
        self.emu.status_signal.connect(self.change_connect_status)
        self.emu.progress_signal.connect(self.progress_bar_update)
        self.emu.console_output.connect(self.print_to_console)
        self.binary_editor = "okteta"
        self.default_binary_name = "emulator_tmp.bin"
        self.emulation_pulse = None
        self.connection_status = False
        self.emulation = None
        self.flashBankFrame.setDisabled(True)
        self.connect_button_slot()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.emu.emu_connection:
            self.emu.emu_connection.close()

    def emulation_btn_pulse(self):
        emulation_btn_clr = "QPushButton {{ background-color: rgb{} }}".format(tuple(self.clr))
        self.emulation_btn.setStyleSheet(emulation_btn_clr)
        if self.clr[1] <= 150:
            self.clr_step = 10
        if self.clr[1] >= 240:
            self.clr_step = -10
        self.clr[1]+=self.clr_step

    def emulation_btn_slot(self):
        if not self.emulation_pulse:
            self.clr = [10, 255, 150]
            self.clr_step = 15
            self.emulation_btn.clearFocus()
            self.read_flash_btn_slot()
            _file = self._get_filename_form_text_box()
            self.file_monitor = FileMonitor(_file, self.print_to_console)
            if self.file_monitor.file_content:
                self.emu.emulator.keep_emulator_awaken()
                self.emulation_pulse = PeriodicThread(period=0.05)
                self.emulation_pulse.periodic_signal.connect(self.emulation_btn_pulse)
                self.emulation_pulse.start()
                self.emulation = EmulationThread(self.emu.emulator.emulate, (self.file_monitor, self.rw_ind_signal.emit))
                self.emulation.start()
        else:
            self.emulation_disable()

    def emulation_disable(self):
        self.emulation_pulse.kill()
        self.emu.emulator.let_emulator_sleep()
        self.emulation_btn.clearFocus()
        self.emulation_btn.setStyleSheet("")
        self.emulation_pulse = None
        if self.emulation:
            self.emulation.kill()
            self.emulation = None

    def progress_bar_update(self, val):
        self.progressBar.setValue(val)

    def read_sram_btn_slot(self):
        self.rw_ind.set_active_clr()
        _file = self.default_binary_name
        if self.fileInUse.text():
            _file = self.fileInUse.text()
        _file = self.emu.emulator.read_sram(_file)
        self.rw_ind.set_inactive_clr()
        self.set_file_name_if_not_present_and_auto_open(_file)

    def flash_bank_radio_btn_slot1(self):
        self.emu.emulator.set_flash_bank(1)
        self.get_flash_stats()

    def flash_bank_radio_btn_slot2(self):
        self.emu.emulator.set_flash_bank(2)
        self.get_flash_stats()

    def flash_bank_radio_btn_slot3(self):
        self.emu.emulator.set_flash_bank(3)
        self.get_flash_stats()

    def rw_indicator_ctrl(self, state):
        if state:
            self.rw_ind.set_active_clr()
        elif state==0:
            self.rw_ind.set_inactive_clr()

    def set_file_name_if_not_present_and_auto_open(self, _file):
        if not self.fileInUse.text() and _file:
            self.fileInUse.setText(_file)
        if self.auto_open_checkbox.isChecked():
            self.edit_button_slot()

    def read_flash_btn_slot(self):
        self.rw_ind.set_active_clr()
        if self.fileInUse.text():
            _file = self.fileInUse.text()
        else:
            _file = self.default_binary_name
        _file = self.emu.emulator.read_flash(_file)
        self.rw_ind.set_inactive_clr()
        self.set_file_name_if_not_present_and_auto_open(_file)
        return _file

    def _get_filename_form_text_box(self):
        if self.fileInUse.text():
            _file = self.fileInUse.text()
        else:
            _file = QFileDialog.getOpenFileName(self, 'Open file',
                                                os.getcwd(), "binary files (*.bin *.BIN)")
            self.fileInUse.setText(_file)
        return _file

    def write_flash_btn_slot(self):
        _file = self._get_filename_form_text_box()
        if _file:
            self.rw_ind.set_clr("rgb(213, 29, 29)")
            self.emu.emulator.write_flash(_file)
            self.rw_ind.set_inactive_clr()
            self.get_flash_stats()

    def connect_button_slot(self):
        self.ping_ind.set_inactive_clr()
        if self.connection_status:
            self.emu.emu_connection.close()
            #self.change_connect_status("nok")
            self.connect_btn.setText(_translate("MainWindow", "connect", None))
            self.emu.kill()
        else:
            self.connect_ind.blink(-0.5)
            self.emu.start()

    def browse_button_slot(self):
        _file = QFileDialog.getOpenFileName(self, 'Open file',
                                            os.getcwd(), "binary files (*.bin *.BIN)")
        self.fileInUse.setText(_file)

    def edit_button_slot(self):
        text = self.fileInUse.text()
        if text:
            Popen([self.binary_editor, text], stdout=PIPE, stdin=PIPE, stderr=PIPE)

    def ping_button_slot(self):
        self.emu.emulator.ping_emulator(self.ping_ind)

    def get_flash_stats(self):
        flash_stats = self.emu.emulator.get_flash_stats()
        bank_no = flash_stats['bankInUse']
        flash_wear1 = flash_stats['flashWear1']
        flash_wear2 = flash_stats['flashWear2']
        flash_wear3 = flash_stats['flashWear3']
        if bank_no == 1:
            self.flash_bank1_radio_btn.setChecked(1)
        if bank_no == 2:
            self.flash_bank2_radio_btn.setChecked(1)
        if bank_no == 3:
            self.flash_bank3_radio_btn.setChecked(1)
        self.lcd_flash_wear1.display(flash_wear1)
        self.lcd_flash_wear2.display(flash_wear2)
        self.lcd_flash_wear3.display(flash_wear3)

    def change_connect_status(self, message):
        if message == 'ok':
            self.connect_ind.stop_blink()
            self.connect_ind.set_active_clr()
            self.connect_btn.setText(_translate("MainWindow", "disconnect", None))
            self.connect_btn.setFocus()
            self.emulationFrame.setEnabled(True)
            self.emulation_frame_blur_effect.setBlurRadius(0)
            self.emulationFrame.setEnabled(True)
            self.connection_status = True
            self.flashBankFrame.setDisabled(False)
            self.get_flash_stats()
            self.print_to_console(" ")
            self.print_to_console("##SESSION STARTED########")
        elif message == 'nok':
            if self.emulation_pulse:
                self.emulation_disable()
            self.connection_status = False
            self.connect_btn.setText(_translate("MainWindow", "connect", None))
            self.connect_btn.clearFocus()
            self.connect_ind.set_inactive_clr()
            self.emulationFrame.setEnabled(False)
            self.emulation_frame_blur_effect.setBlurRadius(2)
            self.flashBankFrame.setDisabled(True)
            self.print_to_console("##SESSION END############")
        else:
            self.main_output.append(message)

    def print_to_console(self, text):
        T = time.ctime(time.time())
        T = T.split(" ")[3]
        text = "{}|  {}".format(T, text)
        self.main_output.append(text)



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = Emulator_gui()
    myapp.show()
    sys.exit(app.exec_())
