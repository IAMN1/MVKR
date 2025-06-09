import sys
from PyQt6.QtWidgets import QApplication
from Controllers.main_window_controller import MainWindowController
#from Views.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    controller = MainWindowController()
    controller.view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()