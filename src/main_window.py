from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMenuBar,
    QWidget,
    QLabel,
    QHBoxLayout,
    QFrame,
    QPushButton,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
)
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtCore import Qt
import sys
import os
import constants
from components.drag_drop_frame import DragDropFrame

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_list = []
        self.setWindowTitle(constants.PROGRAM_NAME)
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.load_poppins_font()
        self.init_menu()
        self.apply_stylesheet()
        self.setup_main_layout()

    def load_poppins_font(self):
        font_dir = constants.FONT_DIR
        if os.path.isdir(font_dir):
            for font_file in os.listdir(font_dir):
                if font_file.endswith(".ttf") or font_file.endswith(".otf"):
                    QFontDatabase.addApplicationFont(os.path.join(font_dir, font_file))

    def init_menu(self):
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)
        project_menu = menubar.addMenu(constants.MENU_PROJECT)
        project_menu.addAction(constants.MENU_NEW_PROJECT)
        project_menu.addAction(constants.MENU_OPEN_PROJECT)

    def apply_stylesheet(self):
        qss_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), constants.STYLE_SHEET)
        try:
            with open(qss_path, "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Could not load stylesheet: {e}")

    def setup_main_layout(self):
        main_widget = QWidget()
        layout = QHBoxLayout(main_widget)

        # Left panel with drag & drop and file list
        left_panel = QWidget()
        left_panel.setObjectName("leftPanel")
        left_panel.setMinimumWidth(300)
        left_panel.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_panel)

        # Drag & drop area (top left)
        self.drag_drop = DragDropFrame(self)
        self.drag_drop.setMinimumHeight(120)
        self.drag_drop.setMaximumHeight(150)

        drag_container = QVBoxLayout(self.drag_drop)
        self.drag_label = QLabel(constants.DRAG_LABEL_PROMPT)
        self.drag_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drag_label.setObjectName("dragLabel")
        drag_container.addWidget(self.drag_label, stretch=1)

        left_layout.addWidget(self.drag_drop)

        # File list section (below drag & drop)
        file_list_label = QLabel(constants.FILE_LIST_TITLE)
        file_list_label.setObjectName("fileListTitle")
        left_layout.addWidget(file_list_label)

        self.file_list_widget = QListWidget()
        self.file_list_widget.setObjectName("fileListWidget")
        # Enable inline editing on Enter key press
        self.file_list_widget.keyPressEvent = self.file_list_key_press_event
        # Connect item changed signal to preserve file extension
        self.file_list_widget.itemChanged.connect(self.on_item_changed)
        left_layout.addWidget(self.file_list_widget, stretch=1)

        # Remove button
        self.remove_button = QPushButton(constants.REMOVE_FILE_BUTTON_TEXT)
        self.remove_button.setObjectName("removeButton")
        self.remove_button.clicked.connect(self.remove_selected_file)
        left_layout.addWidget(self.remove_button)

        layout.addWidget(left_panel)

        # Toggle / Import button to show/hide the left panel
        self.import_button = QPushButton(constants.IMPORT_BUTTON_HIDE_TEXT)
        self.import_button.setObjectName("importButton")
        self.import_button.setMaximumWidth(90)
        self.import_button.setMinimumHeight(200)
        self.import_button.clicked.connect(self.toggle_left_panel)
        layout.addWidget(self.import_button)

        # Center label
        self.center_label = QLabel(constants.CENTER_LABEL_TEXT)
        self.center_label.setObjectName("centerLabel")
        self.center_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.center_label, stretch=1)

        self.setCentralWidget(main_widget)

    def add_files_to_list(self, files):
        """Add files to the file list widget and internal list."""
        for file_path in files:
            if file_path not in self.file_list:
                self.file_list.append(file_path)
                filename = os.path.basename(file_path)
                item = QListWidgetItem(filename)
                item.setData(Qt.ItemDataRole.UserRole, file_path)
                # Make the item editable for GUI display name changes
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                self.file_list_widget.addItem(item)

    def remove_selected_file(self):
        """Remove the selected file from the list."""
        current_item = self.file_list_widget.currentItem()
        if current_item:
            file_path = current_item.data(Qt.ItemDataRole.UserRole)
            if file_path in self.file_list:
                self.file_list.remove(file_path)
            row = self.file_list_widget.row(current_item)
            self.file_list_widget.takeItem(row)

    def file_list_key_press_event(self, event):
        """Handle key press events for the file list widget."""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            current_item = self.file_list_widget.currentItem()
            if current_item:
                # Enable editing for the current item
                self.file_list_widget.editItem(current_item)
        else:
            # Call the parent's keyPressEvent for other keys
            QListWidget.keyPressEvent(self.file_list_widget, event)

    def on_item_changed(self, item):
        """Handle item text changes to preserve file extension."""
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if file_path:
            # Get the original filename and extract extension
            original_filename = os.path.basename(file_path)
            _, original_extension = os.path.splitext(original_filename)
            
            # Get the new text and ensure it has the original extension
            new_text = item.text()
            new_name, new_extension = os.path.splitext(new_text)
            
            # If extension is missing or different, restore the original extension
            if new_extension != original_extension:
                corrected_name = new_name + original_extension
                item.setText(corrected_name)

    def toggle_left_panel(self):
        """Show/hide the left panel and reset the drag label when showing."""
        left_panel = self.findChild(QWidget, "leftPanel")
        if left_panel and left_panel.isVisible():
            left_panel.hide()
            self.import_button.setText(constants.IMPORT_BUTTON_SHOW_TEXT)
        else:
            # reset drag label when reopening
            try:
                self.drag_label.setText(constants.DRAG_LABEL_PROMPT)
            except Exception:
                pass
            if left_panel:
                left_panel.show()
            self.import_button.setText(constants.IMPORT_BUTTON_HIDE_TEXT)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
