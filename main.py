# #This is optional, but it will make running the program easier if we combine everything here.
# from PyQt6.QtWidgets import QApplication
# from gui import MainWindow
# import sys

# def main():
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec())

# if __name__ == "__main__":
#     main()
from PyQt6.QtWidgets import QApplication
from gui import MainWindow
import sys

def main():
    print("Starting app...")
    app = QApplication(sys.argv)

    print("Creating main window...")
    window = MainWindow()

    print("Showing window...")
    window.show()

    print("Entering app loop...")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
