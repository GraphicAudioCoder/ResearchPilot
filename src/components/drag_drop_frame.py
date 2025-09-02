from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import Qt

class DragDropFrame(QFrame):
    """A QFrame that accepts file drops and updates an internal label."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dragDropFrame")
        self.setAcceptDrops(True)
        self.main_window = parent

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        # Add files to the main window's file list
        if self.main_window:
            self.main_window.add_files_to_list(files)
