"""
Results window displaying scan results in a table
"""

import os
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                            QMessageBox, QFileDialog, QGroupBox, QLineEdit, QDialog, QDialogButtonBox, QRadioButton)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from libs.util import shorten_path
from ui.dll_dialogs import OpenDllDialog, OpenDllFolderDialog

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
        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels([
            "File Path", "Filename", "Directory", "Last Modified", "Occurrences", "Matched Terms", "Matched Line"
        ])
        # Make all columns user-resizeable
        header = self.results_table.horizontalHeader()
        for i in range(self.results_table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.Interactive)
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
        # Determine if any DLL results (tuple of 4 or 5)
        has_dll = any(isinstance(r, tuple) and (len(r) == 4 or len(r) == 5) for r in results)
        if has_dll:
            self.results_table.setColumnCount(7)
            self.results_table.setHorizontalHeaderLabels([
                "DLL Path", "Decompiled File", "Directory", "Last Modified", "Occurrences", "Matched Terms", "Matched Line"
            ])
        else:
            self.results_table.setColumnCount(7)
            self.results_table.setHorizontalHeaderLabels([
                "File Path", "Filename", "Directory", "Last Modified", "Occurrences", "Matched Terms", "Matched Line"
            ])
        self.results_table.setRowCount(len(results))
        for row, result in enumerate(results):
            if has_dll and isinstance(result, tuple) and (len(result) == 4 or len(result) == 5):
                # DLL: (dll_path, decomp_file, occ, matched_terms, matched_line) or (dll_path, decomp_file, occ, matched_terms)
                if len(result) == 5:
                    dll_path, decomp_file, occurrence_count, matched_terms, matched_line = result
                else:
                    dll_path, decomp_file, occurrence_count, matched_terms = result
                    matched_line = ''
                self.results_table.setItem(row, 0, QTableWidgetItem(shorten_path(dll_path)))
                decomp_item = QTableWidgetItem(shorten_path(decomp_file))
                decomp_item.setData(Qt.UserRole, (dll_path, decomp_file))
                self.results_table.setItem(row, 1, decomp_item)
                self.results_table.setItem(row, 2, QTableWidgetItem(shorten_path(dll_path)))
                try:
                    mtime = os.path.getmtime(decomp_file)
                    modified_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    modified_time = "Unknown"
                self.results_table.setItem(row, 3, QTableWidgetItem(modified_time))
                occurrence_item = QTableWidgetItem()
                occurrence_item.setData(Qt.DisplayRole, occurrence_count)
                self.results_table.setItem(row, 4, occurrence_item)
                matched_terms_item = QTableWidgetItem(", ".join(matched_terms))
                matched_terms_item.setData(Qt.UserRole, len(matched_terms))
                self.results_table.setItem(row, 5, matched_terms_item)
                self.results_table.setItem(row, 6, QTableWidgetItem(matched_line or ''))
            else:
                # XML: (filepath, filepath, occ, matched_terms, matched_line) or (filepath, occ, matched_terms)
                if len(result) == 5:
                    filepath, _, occurrence_count, matched_terms, matched_line = result
                elif len(result) == 3:
                    filepath, occurrence_count, matched_terms = result
                    matched_line = ''
                else:
                    filepath, occurrence_count = result
                    matched_terms = []
                    matched_line = ''
                item = QTableWidgetItem(shorten_path(filepath))
                item.setData(Qt.UserRole, filepath)
                self.results_table.setItem(row, 0, item)
                filename = os.path.basename(filepath)
                self.results_table.setItem(row, 1, QTableWidgetItem(filename))
                self.results_table.setItem(row, 2, QTableWidgetItem(os.path.dirname(filepath)))
                try:
                    mtime = os.path.getmtime(filepath)
                    modified_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    modified_time = "Unknown"      
                self.results_table.setItem(row, 3, QTableWidgetItem(modified_time))
                occurrence_item = QTableWidgetItem()
                occurrence_item.setData(Qt.DisplayRole, occurrence_count)
                self.results_table.setItem(row, 4, occurrence_item)
                matched_terms_item = QTableWidgetItem(", ".join(matched_terms))
                matched_terms_item.setData(Qt.UserRole, len(matched_terms))
                self.results_table.setItem(row, 5, matched_terms_item)
                self.results_table.setItem(row, 6, QTableWidgetItem(matched_line or ''))
        # Sort by occurrences (column 4) in descending order so items with more matches are at the top
        self.results_table.sortItems(4, Qt.DescendingOrder)
        self.results_table.resizeColumnsToContents()

        # Enable custom sorting for Matched Terms column (by number of terms)
        self.results_table.horizontalHeader().sectionClicked.connect(self.handle_section_clicked)

    def handle_section_clicked(self, logicalIndex):
        # Custom sort for Matched Terms column (index 5)
        if logicalIndex == 5:
            self.results_table.setSortingEnabled(False)
            # Extract (row, count) pairs
            row_counts = []
            for row in range(self.results_table.rowCount()):
                item = self.results_table.item(row, 5)
                count = item.data(Qt.UserRole) if item else 0
                row_counts.append((row, count))
            # Sort rows by count descending
            sorted_rows = sorted(row_counts, key=lambda x: x[1], reverse=True)
            # Rearrange rows
            for new_row, (old_row, _) in enumerate(sorted_rows):
                for col in range(self.results_table.columnCount()):
                    item = self.results_table.takeItem(old_row, col)
                    self.results_table.setItem(new_row, col, item)
            self.results_table.setSortingEnabled(True)
        else:
            # Default sorting
            self.results_table.setSortingEnabled(True)
            self.results_table.sortItems(logicalIndex, Qt.DescendingOrder)

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
        """Open the selected file in its default application (for DLLs, open the decompiled file)"""
        current_row = self.results_table.currentRow()
        if current_row >= 0:
            has_dll = self.results_table.horizontalHeaderItem(0).text().lower().startswith("dll")
            if has_dll:
                item = self.results_table.item(current_row, 1)
                data = item.data(Qt.UserRole) if item else None
                if data and isinstance(data, tuple) and len(data) == 2:
                    dll_path, decomp_file = data
                    dialog = OpenDllDialog(self)
                    if dialog.exec_() == QDialog.Accepted:
                        choice = dialog.get_choice()
                        if choice == 'ilspy':
                            try:
                                import subprocess
                                # Assuming ILSpy is installed and available in PATH
                                subprocess.run(['ilspy', dll_path], check=True)
                            except Exception as e:
                                QMessageBox.critical(self, "Error", f"Could not open DLL in ILSpy: {str(e)}")
                        else:
                            try:
                                os.startfile(decomp_file)
                            except Exception as e:
                                QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")
                else:
                    filepath = None
            else:
                item = self.results_table.item(current_row, 0)
                filepath = item.data(Qt.UserRole) if item else None
                if filepath:
                    try:
                        os.startfile(filepath)
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")
                
    def open_selected_directory(self):
        """Open the directory containing the selected file or DLL/decompiled file"""
        current_row = self.results_table.currentRow()
        if current_row >= 0:
            has_dll = self.results_table.horizontalHeaderItem(0).text().lower().startswith("dll")
            if has_dll:
                item = self.results_table.item(current_row, 1)
                data = item.data(Qt.UserRole) if item else None
                if data and isinstance(data, tuple) and len(data) == 2:
                    dll_path, decomp_file = data
                    dialog = OpenDllFolderDialog(self)
                    if dialog.exec_() == QDialog.Accepted:
                        choice = dialog.get_choice()
                        if choice == 'dll':
                            directory = os.path.dirname(dll_path)
                        else:
                            directory = os.path.dirname(decomp_file)
                        try:
                            os.startfile(directory)
                        except Exception as e:
                            QMessageBox.critical(self, "Error", f"Could not open directory: {str(e)}")
            else:
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
                    f.write("File Path,Filename,Directory,Last Modified,Occurrences,Matched Line\n")
                    for result in self.scan_results:
                        # Handle DLL and XML result formats
                        if len(result) == 5:
                            # DLL or XML: (..., ..., occurrence_count, matched_terms, matched_line)
                            filepath, _, occurrence_count, _, matched_line = result
                        elif len(result) == 4:
                            # DLL: (dll_path, decomp_file, occurrence_count, matched_terms)
                            filepath, _, occurrence_count, _ = result
                            matched_line = ''
                        elif len(result) == 3:
                            # XML: (filepath, occurrence_count, matched_terms)
                            filepath, occurrence_count, _ = result
                            matched_line = ''
                        else:
                            # XML: (filepath, occurrence_count)
                            filepath, occurrence_count = result
                            matched_line = ''
                        filename_only = os.path.basename(filepath)
                        directory = os.path.dirname(filepath)
                        try:
                            mtime = os.path.getmtime(filepath)
                            modified_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            modified_time = "Unknown"
                        filepath_escaped = filepath.replace('"', '""')
                        filename_escaped = filename_only.replace('"', '""')
                        directory_escaped = directory.replace('"', '""')
                        matched_line_escaped = (matched_line or '').replace('"', '""')
                        f.write(f'"{filepath_escaped}","{filename_escaped}","{directory_escaped}","{modified_time}",{occurrence_count},"{matched_line_escaped}"\n')
                QMessageBox.information(self, "Export Complete", f"Results exported to:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Could not export results: {str(e)}")
                
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

