"""
Main window that orchestrates the XML Scanner application
"""

from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import pyqtSignal

from .setup_window import SetupWindow
from .scan_progress_window import ScanProgressWindow
from .results_window import ResultsWindow
from .no_results_dialog import NoResultsDialog
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.scanner import ScanWorker

class XMLScannerMainWindow(QMainWindow):
    """Main window that manages the scanning workflow"""
    
    def __init__(self):
        super().__init__()
        self.setup_window = None
        self.progress_window = None
        self.results_window = None
        self.current_search_string = ""
        self.current_directories = []
        self.total_files_scanned = 0
        
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("XML Scanner - Waste Not Want Not Mod")
        self.setGeometry(100, 100, 400, 200)
        
        # Hide the main window - we only use it as a controller
        self.hide()
        
        # Start with setup window
        self.show_setup_window()
        
    def show_setup_window(self):
        """Show the setup/configuration window"""
        if self.setup_window is None:
            self.setup_window = SetupWindow()
            self.setup_window.scan_requested.connect(self.start_scan)
            
        self.setup_window.show()
        self.setup_window.raise_()
        self.setup_window.activateWindow()        
        # Hide main window as we're using separate windows
        self.hide()
        
    def start_scan(self, base_dir, search_string, scan_dlls=True, scan_xmls=True):
        """Start the scanning process"""
        self.current_search_string = search_string
        self.current_directories = [d.strip() for d in base_dir.split(';') if d.strip()]
        
        # Hide setup window
        if self.setup_window:
            self.setup_window.hide()
            
        # Create and show progress window
        if self.progress_window is None:
            self.progress_window = ScanProgressWindow()
            self.progress_window.scan_cancelled.connect(self.on_scan_cancelled)
            self.progress_window.scan_finished.connect(self.on_scan_finished)
            
        # Create scan worker with scan_dlls and scan_xmls arguments
        scan_worker = ScanWorker(base_dir, search_string, scan_dlls, scan_xmls)
        
        # Connect total files signal to track scan progress
        scan_worker.total_files_found.connect(self.on_total_files_found)
        
        # Show progress window and start scan
        self.progress_window.show()
        self.progress_window.raise_()
        self.progress_window.activateWindow()
        self.progress_window.start_scan(scan_worker)
    def on_total_files_found(self, total_files):
        """Handle total files found signal from scanner worker"""
        self.total_files_scanned = total_files
        
    def on_scan_cancelled(self):
        """Handle scan cancellation"""
        # Don't automatically hide progress window - let user close it manually  
        # if self.progress_window:
        #     self.progress_window.hide()
            
        # Show setup window again
        self.show_setup_window()
        
    def on_scan_finished(self, results):
        """Handle scan completion"""
        # Don't automatically hide the progress window - let user close it manually
        # if self.progress_window:
        #     self.progress_window.hide()
            
        if results:
            # Show results window
            self.show_results_window(results)
        else:
            self.show_no_results_dialog()
    def show_no_results_dialog(self):
        """Show dialog when no results are found"""
        if self.total_files_scanned == 0:
            QMessageBox.information(self, "No Files Scanned", 
                                    "No files were scanned. Please check your directory selection.")
            return
        
        no_results_dialog = NoResultsDialog(self.current_search_string, 
                                            self.current_directories, 
                                            self.total_files_scanned)
        no_results_dialog.new_scan_requested.connect(self.on_new_scan_requested)
        no_results_dialog.exec_()
            
        
    def show_results_window(self, results):
        """Show the results window with scan results"""
        if self.results_window is None:
            self.results_window = ResultsWindow()
            self.results_window.new_scan_requested.connect(self.on_new_scan_requested)
            
        self.results_window.display_results(results, self.current_search_string)
        self.results_window.show()
        self.results_window.raise_()
        self.results_window.activateWindow()
        
    def on_new_scan_requested(self):
        """Handle request for new scan from results window"""
        # Hide results window
        if self.results_window:
            self.results_window.hide()
            
        
        # Show setup window
        self.show_setup_window()
        
    def closeEvent(self, event):
        """Handle application close"""
        # Close all windows
        if self.setup_window:
            self.setup_window.close()
        if self.progress_window:
            self.progress_window.close()
        if self.results_window:
            self.results_window.close()
            
        event.accept()
