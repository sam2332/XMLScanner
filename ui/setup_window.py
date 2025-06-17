"""
Setup/Configuration window for the XML Scanner
"""

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLineEdit, QLabel, QFileDialog, QGroupBox, 
                            QTextEdit, QMessageBox, QCheckBox)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont
from libs.Settings import Settings
settings = Settings()
class SetupWindow(QWidget):
    """Window for configuring scan parameters"""
    scan_requested = pyqtSignal(str, str, bool, bool)  # base_dir, search_string, scan_dlls, scan_xmls
    
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("XML Scanner Setup - Waste Not Want Not Mod")
        self.setGeometry(200, 200, 800, 500)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("XML Scanner Setup")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title_label)
        
        # Directory configuration group
        dir_group = QGroupBox("Directory Configuration")
        dir_layout = QVBoxLayout()
        
        # Directory selection
        dir_input_layout = QHBoxLayout()
        self.dir_label = QLabel("Base Directories (separate multiple paths with ;):")
        self.dir_input = QLineEdit()
        default_paths = r"c:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Core\Defs;C:\Program Files (x86)\Steam\steamapps\workshop\content\294100"
        if settings.get('base_directory'):
            default_paths = settings.get('base_directory')
        self.dir_input.setText(default_paths)
        self.dir_input.setMinimumHeight(30)
        
        self.dir_button = QPushButton("Browse...")
        self.dir_button.clicked.connect(self.browse_directory)
        self.dir_button.setMaximumWidth(100)
        
        dir_input_layout.addWidget(self.dir_input)
        dir_input_layout.addWidget(self.dir_button)
        
        
        # Add directory help text
        dir_help = QTextEdit()
        dir_help.setMaximumHeight(80)
        dir_help.setReadOnly(True)
        dir_help.setText("Default paths include:\n" +
                        "• RimWorld Core Defs: Game's base definitions\n" +
                        "• Workshop Content: Steam Workshop mods\n" +
                        "Use semicolon (;) to separate multiple directories.")
        
        dir_layout.addWidget(self.dir_label)
        dir_layout.addLayout(dir_input_layout)
        dir_layout.addWidget(dir_help)
        
        # DLL scan checkbox
        self.dll_checkbox = QCheckBox("Scan DLL files (decompile and search)")
        self.dll_checkbox.setChecked(settings.get('scan_dlls', True))
        dir_layout.addWidget(self.dll_checkbox)
        
        # XML scan checkbox
        self.xml_checkbox = QCheckBox("Scan XML files")
        self.xml_checkbox.setChecked(settings.get('scan_xmls', True))
        dir_layout.addWidget(self.xml_checkbox)
        
        dir_group.setLayout(dir_layout)

        # DLL Whitelist group
        whitelist_group = QGroupBox("DLL Whitelist (skip these DLLs)")
        whitelist_layout = QVBoxLayout()
        self.whitelist_edit = QTextEdit()
        self.whitelist_edit.setPlaceholderText("Enter DLL names to skip, one per line (e.g. UnityEngine.dll)")
        self.whitelist_edit.setMaximumHeight(80)
        # Load from settings
        dll_whitelist = settings.get('dll_whitelist', [])
        if dll_whitelist:
            self.whitelist_edit.setText("\n".join(dll_whitelist))
        whitelist_layout.addWidget(self.whitelist_edit)
        whitelist_group.setLayout(whitelist_layout)

        # Search configuration group
        search_group = QGroupBox("Search Configuration")
        search_layout = QVBoxLayout()
        
        # Search string
        self.search_label = QLabel("Search String:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter string to search for...")
        if settings.get('search_string'):
            self.search_input.setText(settings.get('search_string'))
        else:
            self.search_input.setText("Pawn;Building_WorkTable;Steel;ComponentIndustrial")
        self.search_input.setMinimumHeight(30)
        self.search_input.returnPressed.connect(self.start_scan)  # Allow Enter key to start scan
        
        # Search help text
        search_help = QTextEdit()
        search_help.setMaximumHeight(100)
        search_help.setReadOnly(True)
        search_help.setText("Search examples:\n" +
                           "• Class names: 'Pawn', 'Building_WorkTable'\n" +
                           "• Def names: 'Steel', 'ComponentIndustrial'\n" +
                           "• XML tags: '<defName>', '<workType>'\n" +
                           "• Attributes: 'Abstract=\"true\"'\n" +
                           "Search is case-sensitive and searches file content.")
        
        search_layout.addWidget(self.search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_help)
        search_group.setLayout(search_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.scan_button = QPushButton("Start Scan")
        self.scan_button.clicked.connect(self.start_scan)
        self.scan_button.setMinimumHeight(40)
        self.scan_button.setFont(QFont("Arial", 12, QFont.Bold))
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_fields)
        self.clear_button.setMaximumWidth(100)
        
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        button_layout.addWidget(self.scan_button)
        
        # Add all sections to main layout
        layout.addWidget(dir_group)
        layout.addWidget(whitelist_group)
        layout.addWidget(search_group)
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        
    def browse_directory(self):
        """Open directory browser and add to path list"""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory to Scan")
        if directory:
            # If there's already content, append with semicolon separator
            current_text = self.dir_input.text().strip()
            if current_text:
                self.dir_input.setText(current_text + ";" + directory)
            else:
                self.dir_input.setText(directory)
                
    def clear_fields(self):
        """Clear all input fields"""
        self.search_input.clear()
        # Don't clear directory input as it has useful defaults
        
    def start_scan(self):
        """Validate inputs and emit scan request"""
        base_dir = self.dir_input.text().strip()
        search_string = self.search_input.text().strip()
        scan_dlls = self.dll_checkbox.isChecked()
        scan_xmls = self.xml_checkbox.isChecked()
        
        if not base_dir or not search_string:
            QMessageBox.warning(self, "Warning", "Please provide both directory and search string.")
            return
            
        # Validate multiple directories
        directories = [d.strip() for d in base_dir.split(';') if d.strip()]
        invalid_dirs = [d for d in directories if not os.path.exists(os.path.expanduser(os.path.expandvars(d)))]
        
        if invalid_dirs:
            QMessageBox.critical(self, "Error", 
                                f"The following directories do not exist:\n" + "\n".join(invalid_dirs))
            return
            
        # Save settings
        settings.set('base_directory', base_dir)
        settings.set('search_string', search_string)
        settings.set('last_scan_date', '')
        settings.set('scan_results', [])
        settings.set('scan_dlls', scan_dlls)
        settings.set('scan_xmls', scan_xmls)
        # Save DLL whitelist
        whitelist_text = self.whitelist_edit.toPlainText()
        dll_whitelist = [x.strip() for x in whitelist_text.splitlines() if x.strip()]
        settings.set('dll_whitelist', dll_whitelist)
        # All validation passed, emit scan request
        self.scan_requested.emit(base_dir, search_string, scan_dlls, scan_xmls)
        
    def get_scan_parameters(self):
        """Get current scan parameters"""
        return self.dir_input.text().strip(), self.search_input.text().strip(), self.dll_checkbox.isChecked(), self.xml_checkbox.isChecked()
