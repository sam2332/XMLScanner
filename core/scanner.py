import os
import glob
import tempfile
import shutil
import time
from PyQt5.QtCore import QThread, pyqtSignal

# -- ILSpy-based decompiler integration --
import subprocess
import re
from typing import List, Dict
from libs.util import shorten_path
def decompile_assembly(dll_path: str, output_dir: str) -> str:
    

    if not os.path.exists(dll_path):
        raise FileNotFoundError(f"DLL not found at: {dll_path}")

    os.makedirs(output_dir, exist_ok=True)

    if subprocess.run(["where", "ilspycmd"], capture_output=True).returncode != 0:
        raise RuntimeError("ilspycmd not found. Install with: dotnet tool install -g ilspycmd")

    result = subprocess.run([
        "ilspycmd", dll_path, "-o", output_dir,
        "-p", "--no-dead-code", "--no-dead-stores"
    ])

    if result.returncode != 0:
        raise RuntimeError(f"Decompilation failed with code {result.returncode}")

    return output_dir

def index_decompiled_files(directory: str) -> List[str]:
    """ Return all .cs file paths under directory """
    cs_files = []
    for root, _, files in os.walk(directory):
        for f in files:
            if f.endswith(".cs"):
                cs_files.append(os.path.join(root, f))
    return cs_files

# -- Worker thread --
class ScanWorker(QThread):
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    file_found = pyqtSignal(str, int)
    scan_completed = pyqtSignal(list)
    total_files_found = pyqtSignal(int)

    def __init__(self, base_dir, search_string, scan_dlls=True):
        super().__init__()
        self.base_dirs = [d.strip() for d in base_dir.split(';') if d.strip()]
        self.search_terms = [s.strip().lower().encode('utf-8') for s in search_string.split(';') if s.strip()]
        self.scan_dlls = scan_dlls

    def process_dll_file(self, dll_path, search_terms):
        temp_dir = tempfile.mkdtemp()
        try:
            self.status_updated.emit(f"Decompiling {shorten_path(dll_path)}...")
            start_time = time.time()
            decompile_assembly(dll_path, temp_dir)
            self.status_updated.emit(f"Decompilation complete: {shorten_path(dll_path)} Took: {time.time() - start_time:.2f} seconds")
            occurrences_total = 0
            total_scanned = 0
            had_error = False
            start_time = time.time()
            for file_path in index_decompiled_files(temp_dir):
                total_scanned += 1
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read().lower()
                        occurrences_total += sum(content.count(term) for term in search_terms)
                except Exception as e:
                    self.status_updated.emit(f"Error reading decompiled file: {e}")
                    had_error = True
            if not had_error:
                self.status_updated.emit(f"Scanned {total_scanned} files, found {occurrences_total} occurrences. Took: {time.time() - start_time:.2f} seconds")
            
            return occurrences_total if occurrences_total > 0 else None
        except Exception as e:
            self.status_updated.emit(f"Decompilation failed: {dll_path}\n{e}")
            return None
        finally:
            shutil.rmtree(temp_dir)

    def run(self):
        all_files = []
        found_files = []
        self.status_updated.emit("Collecting XML and DLL files...")
        for directory in self.base_dirs:
            if not os.path.exists(directory):
                self.status_updated.emit(f"Warning: Directory does not exist: {directory}")
                continue
            self.status_updated.emit(f"Scanning directory: {directory}")
            xml_files = glob.glob(os.path.join(directory, '**', '*.xml'), recursive=True)
            dll_files = glob.glob(os.path.join(directory, '**', '*.dll'), recursive=True) if self.scan_dlls else []
            dir_files = xml_files + dll_files
            all_files.extend(dir_files)
            self.status_updated.emit(f"Found {len(dir_files)} total files in {directory}")
        total_files = len(all_files)
        self.total_files_found.emit(total_files)

        if total_files == 0:
            self.status_updated.emit("No XML or DLL files found.")
            self.scan_completed.emit([])
            return

        for i, filename in enumerate(all_files):
            occurrences = 0
            try:
                self.status_updated.emit(f"Scanning: {shorten_path(filename)}")

                if filename.endswith('.xml'):
                    with open(filename, 'rb') as file:
                        content = file.read().lower()
                        occurrences = sum(content.count(term) for term in self.search_terms)
                elif filename.endswith('.dll'):
                    result = self.process_dll_file(filename, self.search_terms)
                    occurrences = result if result else 0

                if occurrences > 0:
                    found_files.append((filename, occurrences))
                    self.file_found.emit(filename, occurrences)

                self.progress_updated.emit(int((i + 1) / len(all_files) * 100))
            except Exception as e:
                self.status_updated.emit(f"Error processing {filename}: {e}")

        self.status_updated.emit(f"Scan completed. Found {len(found_files)} matching files.")
        self.scan_completed.emit(found_files)

# -- Optional: Console-based utility call --
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
