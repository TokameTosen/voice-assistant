import sys
from PyQt5.QtWidgets import QApplication
from ui.window import MainWindow
from helper import VoiceAssistant

def main():
    app = QApplication(sys.argv)
    assistant = VoiceAssistant()
    window = MainWindow(assistant)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()