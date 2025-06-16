"""
Core scanning functionality for XML files
"""

import os
import glob
from PyQt5.QtCore import QThread, pyqtSignal

class ScanWorker(QThread):
    """Worker thread for scanning XML files"""
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    file_found = pyqtSignal(str, int)  # filename, occurrence_count
    scan_completed = pyqtSignal(list)
    total_files_found = pyqtSignal(int)  # Total number of files that will be scanned
    
    def __init__(self, base_dir, search_string):
        super().__init__()
        self.base_dir = base_dir
        self.search_string = search_string
        self.search_bytes = search_string.encode('utf-8')
        # Also search for case variations
        self.lower_search_bytes = search_string.lower().encode('utf-8')
        self.upper_search_bytes = search_string.upper().encode('utf-8')
        self.all_search_variants = [self.search_bytes, self.lower_search_bytes, self.upper_search_bytes]
        
    def run(self):
        try:
            self.status_updated.emit("Collecting XML files...")
            
            # Handle multiple directories separated by semicolon
            directories = [d.strip() for d in self.base_dir.split(';') if d.strip()]
            all_files = []
            
            for directory in directories:
                if os.path.exists(directory):
                    self.status_updated.emit(f"Scanning directory: {directory}")
                    dir_files = list(glob.glob(os.path.join(directory, '**', '*.xml'), recursive=True))
                    all_files.extend(dir_files)                   
                    self.status_updated.emit(f"Found {len(dir_files)} XML files in {directory}")
                else:
                    self.status_updated.emit(f"Warning: Directory does not exist: {directory}")
            
            total_files = len(all_files)
            
            if total_files == 0:
                self.status_updated.emit("No XML files found in any directory")
                self.total_files_found.emit(0)
                self.scan_completed.emit([])
                return
                
            self.status_updated.emit(f"Found {total_files} XML files total. Starting scan...")
            self.total_files_found.emit(total_files)
            
            found_files = []
            
            for i, filename in enumerate(all_files):
                try:
                    self.status_updated.emit(f"Scanning: {os.path.basename(filename)}")
                    
                    with open(filename, 'rb') as file:
                        content = file.read()
                        # Check if any of the search variants are in the content
                        if any(search_variant in content for search_variant in self.all_search_variants):
                            # Count occurrences (use original search bytes for counting)
                            occurrence_count = content.count(self.search_bytes)
                            found_files.append((filename, occurrence_count))
                            self.file_found.emit(filename, occurrence_count)
                            
                    progress = int(((i + 1) / total_files) * 100)
                    self.progress_updated.emit(progress)
                    
                except Exception as e:
                    self.status_updated.emit(f"Error reading {filename}: {str(e)}")
                    continue
                    
            self.status_updated.emit(f"Scan completed. Found {len(found_files)} files with matches.")
            self.scan_completed.emit(found_files)
            
        except Exception as e:
            self.status_updated.emit(f"Scan failed: {str(e)}")
            self.scan_completed.emit([])

def scan_for_string(base_dir, search_string):
    """Legacy command-line function for backward compatibility"""
    found_files = []
    search_bytes = search_string.encode('utf-8')
    lower_search_string = search_string.lower().encode('utf-8')
    upper_search_string = search_string.upper().encode('utf-8')
    all_search_strings = [search_bytes, lower_search_string, upper_search_string]
    
    # Handle multiple directories separated by semicolon
    directories = [d.strip() for d in base_dir.split(';') if d.strip()]
    
    for directory in directories:
        if os.path.exists(directory):
            # Get a list of all XML files in this directory
            for file,dirs in os.walk(directory):
                xml_files = glob.glob(os.path.join(file, '*.xml'))
                for xml_file in xml_files:
                    try:
                        with open(xml_file, 'rb') as f:
                            content = f.read()
                            if any(search_bytes in content for search_bytes in all_search_strings):
                                # Count occurrences
                                occurrence_count = content.count(search_bytes)
                                found_files.append((xml_file, occurrence_count))
                    except Exception as e:
                        print(f"Error reading {xml_file}: {str(e)}")

    return found_files
