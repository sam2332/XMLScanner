import os
import glob
from PyQt5.QtCore import QThread, pyqtSignal

class ScanWorker(QThread):
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    file_found = pyqtSignal(str, int)
    scan_completed = pyqtSignal(list)
    total_files_found = pyqtSignal(int)
    
    def __init__(self, base_dir, search_string):
        super().__init__()
        self.base_dirs = [d.strip() for d in base_dir.split(';') if d.strip()]
        self.search_terms = [s.strip().lower() for s in search_string.split(';') if s.strip()]
    
    def run(self):
        all_files = []
        found_files = []

        self.status_updated.emit("Collecting XML files...")

        for directory in self.base_dirs:
            if not os.path.exists(directory):
                self.status_updated.emit(f"Warning: Directory does not exist: {directory}")
                continue

            self.status_updated.emit(f"Scanning directory: {directory}")
            dir_files = glob.glob(os.path.join(directory, '**', '*.xml'), recursive=True)
            all_files.extend(dir_files)
            self.status_updated.emit(f"Found {len(dir_files)} XML files in {directory}")

        total_files = len(all_files)
        self.total_files_found.emit(total_files)

        if total_files == 0:
            self.status_updated.emit("No XML files found.")
            self.scan_completed.emit([])
            return

        for i, filename in enumerate(all_files):
            occurrences = 0
            try:
                self.status_updated.emit(f"Scanning: {os.path.basename(filename)}")

                with open(filename, 'rb') as file:
                    content = file.read().lower()

                for term in self.search_terms:
                    term_bytes = term.encode('utf-8')
                    count = content.count(term_bytes)
                    occurrences += count

                if occurrences > 0:
                    found_files.append((filename, occurrences))
                    self.file_found.emit(filename, occurrences)

                progress = int((i + 1) / total_files * 100)
                self.progress_updated.emit(progress)

            except Exception as e:
                self.status_updated.emit(f"Error reading {filename}: {e}")
                continue

        self.status_updated.emit(f"Scan completed. Found {len(found_files)} matching files.")
        self.scan_completed.emit(found_files)

def scan_for_string(base_dir, search_string):
    found_files = []
    base_dirs = [d.strip() for d in base_dir.split(';') if d.strip()]
    search_terms = [s.strip().lower().encode('utf-8') for s in search_string.split(';') if s.strip()]

    for directory in base_dirs:
        if os.path.exists(directory):
            xml_files = glob.glob(os.path.join(directory, '**', '*.xml'), recursive=True)
            for xml_file in xml_files:
                occurrences = 0
                try:
                    with open(xml_file, 'rb') as f:
                        content = f.read().lower()
                        for term in search_terms:
                            occurrences += content.count(term)

                    if occurrences > 0:
                        found_files.append((xml_file, occurrences))

                except Exception as e:
                    print(f"Error reading {xml_file}: {e}")

    return found_files
