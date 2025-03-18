import sys
from PyQt5.QtWidgets import QApplication
from app.GUI.main_window import QuestManusGUI

def main():
    app = QApplication(sys.argv)
    window = QuestManusGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()