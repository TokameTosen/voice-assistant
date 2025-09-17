from PyQt5 import QtWidgets
import sys

class VoiceAssistantWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Voice Assistant")
        self.setGeometry(100, 100, 600, 400)
        
        # Create a central widget
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)
        
        # Layout
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)
        
        # Add a label
        self.label = QtWidgets.QLabel("Welcome to the Voice Assistant!", self)
        self.layout.addWidget(self.label)
        
        # Add a button to start voice commands
        self.start_button = QtWidgets.QPushButton("Start Listening", self)
        self.start_button.clicked.connect(self.start_listening)
        self.layout.addWidget(self.start_button)
        
        # Add a button to exit the application
        self.exit_button = QtWidgets.QPushButton("Exit", self)
        self.exit_button.clicked.connect(self.close)
        self.layout.addWidget(self.exit_button)

    def start_listening(self):
        # Placeholder for the function to start voice recognition
        self.label.setText("Listening for commands...")

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = VoiceAssistantWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()