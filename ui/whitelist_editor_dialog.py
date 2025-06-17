"""
Whitelist editor dialog for XMLScanner
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout, QLineEdit, QMessageBox, QLabel
from PyQt5.QtCore import Qt

class WhitelistEditorDialog(QDialog):
    def __init__(self, whitelist, parent=None, name=None):
        super().__init__(parent)
        self.setWindowTitle("Edit SHA1 Whitelist")
        self.setMinimumSize(400, 300)
        self.whitelist = set(whitelist)
        self.name = name or ""
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        # Whitelist name edit
        name_layout = QHBoxLayout()
        name_label = QLabel("Whitelist Name:")
        self.name_edit = QLineEdit(self.name)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        self.list_widget = QListWidget()
        self.list_widget.addItems(sorted(self.whitelist))
        layout.addWidget(QLabel("SHA1 Whitelist (one per line):"))
        layout.addWidget(self.list_widget)

        input_layout = QHBoxLayout()
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("Enter SHA1 hash...")
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_hash)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(add_btn)
        layout.addLayout(input_layout)

        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_selected)
        layout.addWidget(remove_btn)

        save_btn = QPushButton("Save and Close")
        save_btn.clicked.connect(self.accept)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def add_hash(self):
        sha1 = self.input_edit.text().strip()
        if len(sha1) == 40 and all(c in '0123456789abcdefABCDEF' for c in sha1):
            if sha1 not in self.whitelist:
                self.whitelist.add(sha1)
                self.list_widget.addItem(sha1)
                self.input_edit.clear()
            else:
                QMessageBox.information(self, "Duplicate", "SHA1 already in whitelist.")
        else:
            QMessageBox.warning(self, "Invalid SHA1", "Please enter a valid 40-character SHA1 hash.")

    def remove_selected(self):
        for item in self.list_widget.selectedItems():
            sha1 = item.text()
            self.whitelist.discard(sha1)
            self.list_widget.takeItem(self.list_widget.row(item))

    def get_whitelist(self):
        return sorted(self.whitelist)

    def get_name(self):
        return self.name_edit.text().strip()
