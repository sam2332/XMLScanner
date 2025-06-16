"""
Results window displaying scan results in a table
"""

import os
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                            QMessageBox, QFileDialog, QGroupBox, QLineEdit)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from libs.util import shorten_path
class ResultsWindow(QWidget):
    """Window displaying scan results in a table format"""
    new_scan_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.scan_results = []
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("XML Scanner - Results")
        self.setGeometry(150, 150, 1200, 700)
        
        layout = QVBoxLayout()
        
        # Title and summary
        title_layout = QHBoxLayout()
        title_label = QLabel("Scan Results")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        
        self.summary_label = QLabel("No results")
        self.summary_label.setFont(QFont("Arial", 10))
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.summary_label)
        
        layout.addLayout(title_layout)
        
        # Filter section
        filter_group = QGroupBox("Filter Results")
        filter_layout = QHBoxLayout()
        
        filter_label = QLabel("Filter by filename:")
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Enter filename filter...")
        self.filter_input.textChanged.connect(self.filter_results)
        
        self.clear_filter_button = QPushButton("Clear Filter")
        self.clear_filter_button.clicked.connect(self.clear_filter)
        self.clear_filter_button.setMaximumWidth(100)
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_input)
        filter_layout.addWidget(self.clear_filter_button)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels([
            "File Path", "Filename", "Directory", "Last Modified", "Occurrences"
        ])
        
        # Set column widths
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # File Path
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Filename
        header.setSectionResizeMode(2, QHeaderView.Interactive)  # Directory
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Last Modified
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Occurrences
        
        # Enable sorting
        self.results_table.setSortingEnabled(True)
        
        # Enable row selection
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(self.results_table)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        # File actions
        self.open_file_button = QPushButton("Open File")
        self.open_file_button.clicked.connect(self.open_selected_file)
        self.open_file_button.setEnabled(False)
        
        self.open_dir_button = QPushButton("Open Directory")
        self.open_dir_button.clicked.connect(self.open_selected_directory)
        self.open_dir_button.setEnabled(False)
        
        self.copy_path_button = QPushButton("Copy Path")
        self.copy_path_button.clicked.connect(self.copy_selected_path)
        self.copy_path_button.setEnabled(False)
        
        # Export actions
        self.export_button = QPushButton("Export Results...")
        self.export_button.clicked.connect(self.export_results)
        self.export_button.setEnabled(False)
        
        # Navigation actions
        self.new_scan_button = QPushButton("New Scan")
        self.new_scan_button.clicked.connect(self.request_new_scan)
        
        self.clear_results_button = QPushButton("Clear Results")
        self.clear_results_button.clicked.connect(self.clear_results)
        
        # Add buttons to layout
        button_layout.addWidget(self.open_file_button)
        button_layout.addWidget(self.open_dir_button)
        button_layout.addWidget(self.copy_path_button)
        button_layout.addStretch()
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.clear_results_button)
        button_layout.addWidget(self.new_scan_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Connect table selection change
        self.results_table.selectionModel().selectionChanged.connect(self.on_selection_changed)
        
    def display_results(self, results, search_string=""):
        """Display scan results in the table"""
        self.scan_results = results
        self.populate_table(results)
        
        # Update summary
        if results:
            self.summary_label.setText(f"Found {len(results)} files")
            self.export_button.setEnabled(True)
        else:
            self.summary_label.setText("No results found")
            self.export_button.setEnabled(False)
            
        # Update window title with search string
        if search_string:
            self.setWindowTitle(f"XML Scanner - Results for '{search_string}'")
        else:
            self.setWindowTitle("XML Scanner - Results")
            
    def populate_table(self, results):
        """Populate the table with results"""
        self.results_table.setRowCount(len(results))
        for row, (filepath, occurrence_count) in enumerate(results):
            # Shortened file path for display
            short_path = shorten_path(filepath)
            item = QTableWidgetItem(short_path)
            item.setData(Qt.UserRole, filepath)  # Store full path
            self.results_table.setItem(row, 0, item)
            # Filename
            filename = os.path.basename(filepath)
            self.results_table.setItem(row, 1, QTableWidgetItem(filename))
            # Directory
            directory = os.path.dirname(filepath)
            self.results_table.setItem(row, 2, QTableWidgetItem(directory))
            # Last modified
            try:
                mtime = os.path.getmtime(filepath)
                modified_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            except:
                modified_time = "Unknown"
            self.results_table.setItem(row, 3, QTableWidgetItem(modified_time))
            # Occurrences
            occurrence_item = QTableWidgetItem()
            occurrence_item.setData(Qt.DisplayRole, occurrence_count)  # For proper numeric sorting
            self.results_table.setItem(row, 4, occurrence_item)
        # Sort by filename by default
        self.results_table.sortItems(1)
        
    def filter_results(self):
        """Filter results based on filename filter"""
        filter_text = self.filter_input.text().lower()
        
        for row in range(self.results_table.rowCount()):
            filename_item = self.results_table.item(row, 1)
            if filename_item:
                filename = filename_item.text().lower()
                should_show = filter_text in filename
                self.results_table.setRowHidden(row, not should_show)
                
    def clear_filter(self):
        """Clear the filename filter"""
        self.filter_input.clear()
        
        # Show all rows
        for row in range(self.results_table.rowCount()):
            self.results_table.setRowHidden(row, False)
            
    def on_selection_changed(self):
        """Handle table selection changes"""
        has_selection = len(self.results_table.selectedItems()) > 0
        self.open_file_button.setEnabled(has_selection)
        self.open_dir_button.setEnabled(has_selection)
        self.copy_path_button.setEnabled(has_selection)
        
    def open_selected_file(self):
        """Open the selected file in its default application"""
        current_row = self.results_table.currentRow()
        if current_row >= 0:
            item = self.results_table.item(current_row, 0)
            filepath = item.data(Qt.UserRole) if item else None
            if filepath:
                try:
                    os.startfile(filepath)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")
                
    def open_selected_directory(self):
        """Open the directory containing the selected file"""
        current_row = self.results_table.currentRow()
        if current_row >= 0:
            item = self.results_table.item(current_row, 0)
            filepath = item.data(Qt.UserRole) if item else None
            if filepath:
                directory = os.path.dirname(filepath)
                try:
                    os.startfile(directory)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Could not open directory: {str(e)}")
                
    def copy_selected_path(self):
        """Copy the selected file path to clipboard"""
        current_row = self.results_table.currentRow()
        if current_row >= 0:
            item = self.results_table.item(current_row, 0)
            filepath = item.data(Qt.UserRole) if item else None
            if filepath:
                from PyQt5.QtWidgets import QApplication
                clipboard = QApplication.clipboard()
                clipboard.setText(filepath)
                QMessageBox.information(self, "Copied", f"File path copied to clipboard:\n{filepath}")
            
    def export_results(self):
        """Export results to a CSV file"""
        if not self.scan_results:
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Results", "scan_results.csv", "CSV Files (*.csv)")
            
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    f.write("File Path,Filename,Directory,Last Modified,Occurrences\n")
                    
                    for filepath, occurrence_count in self.scan_results:
                        filename_only = os.path.basename(filepath)
                        directory = os.path.dirname(filepath)
                        
                        try:
                            mtime = os.path.getmtime(filepath)
                            modified_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            modified_time = "Unknown"
                            
                        # Escape quotes in CSV
                        filepath_escaped = filepath.replace('"', '""')
                        filename_escaped = filename_only.replace('"', '""')
                        directory_escaped = directory.replace('"', '""')
                        
                        f.write(f'"{filepath_escaped}","{filename_escaped}","{directory_escaped}","{modified_time}",{occurrence_count}\n')
                        
                QMessageBox.information(self, "Export Complete", f"Results exported to:\n{filename}")
                
            except Exception as e:
                QMessageBox.error(self, "Export Error", f"Could not export results: {str(e)}")
                
    def clear_results(self):
        """Clear all results"""
        self.results_table.setRowCount(0)
        self.scan_results.clear()
        self.summary_label.setText("No results")
        self.export_button.setEnabled(False)
        self.clear_filter()
        
    def request_new_scan(self):
        """Request a new scan"""
        self.new_scan_requested.emit()
        
