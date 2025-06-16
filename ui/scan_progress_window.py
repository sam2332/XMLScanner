"""
Scan progress window showing real-time scanning status
"""

import os
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QProgressBar, QTextEdit, QMessageBox)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont

class ScanProgressWindow(QWidget):
    """Window showing scan progress and status"""
    scan_cancelled = pyqtSignal()
    scan_finished = pyqtSignal(list)  # results list
    
    def __init__(self):
        super().__init__()
        self.scan_worker = None
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("XML Scanner - Scanning in Progress")
        self.setGeometry(300, 300, 700, 500)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Scanning XML Files")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title_label)
        
        # Progress section
        progress_layout = QVBoxLayout()
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(25)
        progress_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Initializing scan...")
        self.status_label.setFont(QFont("Arial", 10))
        progress_layout.addWidget(self.status_label)
        
        # Current stats
        self.stats_label = QLabel("Files found: 0")
        self.stats_label.setFont(QFont("Arial", 10))
        progress_layout.addWidget(self.stats_label)
        
        layout.addLayout(progress_layout)
        
        # Log section
        log_label = QLabel("Scan Log:")
        log_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        layout.addWidget(self.log_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel Scan")
        self.cancel_button.clicked.connect(self.cancel_scan)
        self.cancel_button.setMaximumWidth(120)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        self.close_button.setEnabled(False)  # Disabled until scan completes
        self.close_button.setMaximumWidth(100)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Track results
        self.scan_results = []
        self.files_found_count = 0
        
    def start_scan(self, scan_worker):
        """Start the scan with the given worker"""
        self.scan_worker = scan_worker
        self.scan_results.clear()
        self.files_found_count = 0
        
        # Connect signals
        self.scan_worker.progress_updated.connect(self.update_progress)
        self.scan_worker.status_updated.connect(self.update_status)
        self.scan_worker.file_found.connect(self.file_found)
        self.scan_worker.scan_completed.connect(self.scan_completed)
        
        # Reset UI
        self.progress_bar.setValue(0)
        self.log_text.clear()
        self.cancel_button.setEnabled(True)
        self.close_button.setEnabled(False)
        
        # Start the worker
        self.scan_worker.start()
        
    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)
        
    def update_status(self, message):
        """Update status label and log"""
        self.status_label.setText(message)
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.append(f"[{timestamp}] {message}")
        
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def file_found(self, filename, occurrence_count):
        """Handle file found event"""
        self.files_found_count += 1
        self.stats_label.setText(f"Files found: {self.files_found_count}")
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        basename = os.path.basename(filename)
        self.log_text.append(f"[{timestamp}] ✓ Found match: {basename} ({occurrence_count} occurrences)")
        
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def scan_completed(self, results):
        """Handle scan completion"""
        self.scan_results = results
        self.cancel_button.setEnabled(False)
        self.close_button.setEnabled(True)
        
        # Update final status
        if results:
            self.status_label.setText(f"Scan completed! Found {len(results)} files with matches.")
            self.progress_bar.setValue(100)
            
            # Emit signal to show results
            self.scan_finished.emit(results)
        else:
            self.status_label.setText("Scan completed. No matches found.")
            
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.append(f"[{timestamp}] === SCAN COMPLETE ===")
        
    def cancel_scan(self):
        """Cancel the running scan"""
        if self.scan_worker and self.scan_worker.isRunning():
            reply = QMessageBox.question(self, "Cancel Scan", 
                                       "Are you sure you want to cancel the scan?",
                                       QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.scan_worker.terminate()
                self.scan_worker.wait()  # Wait for thread to finish
                
                self.status_label.setText("Scan cancelled by user")
                self.cancel_button.setEnabled(False)
                self.close_button.setEnabled(True)
                
                timestamp = datetime.now().strftime('%H:%M:%S')
                self.log_text.append(f"[{timestamp}] === SCAN CANCELLED ===")
                
                self.scan_cancelled.emit()
                
    def closeEvent(self, event):
        """Handle window close event"""
        if self.scan_worker and self.scan_worker.isRunning():
            reply = QMessageBox.question(self, "Close Window", 
                                       "Scan is still running. Cancel scan and close?",
                                       QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.scan_worker.terminate()
                self.scan_worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
