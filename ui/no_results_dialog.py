"""
No Results dialog for when scan finds no matches
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QTextEdit)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont, QIcon

class NoResultsDialog(QDialog):
    """Dialog shown when scan finds no results"""
    new_scan_requested = pyqtSignal()
    
    def __init__(self, search_string, directories_scanned, total_files_scanned, parent=None):
        super().__init__(parent)
        self.search_string = search_string
        self.directories_scanned = directories_scanned
        self.total_files_scanned = total_files_scanned
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("No Results Found")
        self.setModal(True)
        self.setGeometry(300, 300, 500, 400)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("No Results Found")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Message
        message_label = QLabel(f"No files were found containing: '{self.search_string}'")
        message_label.setFont(QFont("Arial", 12))
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # Scan details
        details_text = QTextEdit()
        details_text.setReadOnly(True)
        details_text.setMaximumHeight(150)
        
        details_content = f"""Scan Details:
• Search term: {self.search_string}
• Files scanned: {self.total_files_scanned}
• Directories scanned: {len(self.directories_scanned)}

Directories:
"""
        for directory in self.directories_scanned:
            details_content += f"• {directory}\n"
            
        details_content += f"""
Suggestions:
• Check spelling of search term
• Try searching for partial terms
• Search is case-sensitive - try different cases
• Verify the directories contain the expected files"""
        
        details_text.setText(details_content)
        layout.addWidget(details_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.new_scan_button = QPushButton("New Scan")
        self.new_scan_button.clicked.connect(self.request_new_scan)
        self.new_scan_button.setMinimumHeight(35)
        self.new_scan_button.setFont(QFont("Arial", 11, QFont.Bold))
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.reject)
        self.close_button.setMinimumHeight(35)
        
        button_layout.addWidget(self.close_button)
        button_layout.addStretch()
        button_layout.addWidget(self.new_scan_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Set focus to New Scan button
        self.new_scan_button.setFocus()
        
    def request_new_scan(self):
        """Request a new scan"""
        self.new_scan_requested.emit()
        self.accept()
        
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Escape:
            self.reject()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.request_new_scan()
        else:
            super().keyPressEvent(event)
