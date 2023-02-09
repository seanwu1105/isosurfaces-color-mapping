from PySide6.QtWidgets import QGridLayout, QMainWindow, QWidget

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480


def build_default_window():
    window = QMainWindow()
    window.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
    central = QWidget()
    window.setCentralWidget(central)
    layout = QGridLayout()
    central.setLayout(layout)

    return window, central, layout
