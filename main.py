import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont, QIcon
from gui.main_window import HackerMainWindow

def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Consolas", 10))
    
    # Set App Icon
    icon_path = os.path.join(os.path.dirname(__file__), "gui", "logo.ico")
    if os.path.isfile(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    style_path = os.path.join(os.path.dirname(__file__), "gui", "styles.qss")
    if os.path.isfile(style_path):
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
            
    window = HackerMainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
