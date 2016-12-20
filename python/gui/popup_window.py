from PyQt4.QtGui import QMessageBox

def warning_box(msg, title = "Warning !", detailed_msg="", ):
    mbox = QMessageBox()
    mbox.setIcon(QMessageBox.Warning)
    mbox.setText(msg)
    mbox.setStandardButtons(QMessageBox.Ok)
    mbox.setDetailedText(detailed_msg)
    mbox.setWindowTitle(title)
    mbox.exec_()