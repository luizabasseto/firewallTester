import sys
from PyQt5.QtWidgets import QApplication

from core.container_manager import ContainerManager
from ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    container_manager = ContainerManager()
    
    main_view = MainWindow(container_manager=container_manager)
    
    main_view.show()
    sys.exit(app.exec_())