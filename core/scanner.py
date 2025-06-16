import os
import glob
import tempfile
import shutil
import time
import hashlib
from PyQt5.QtCore import QThread, pyqtSignal
import concurrent.futures

# -- ILSpy-based decompiler integration --
import subprocess
import re
from typing import List, Dict
from libs.util import shorten_path,get_cpu_count
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

# Global set to track scanned DLL hashes
scanned_dll_hashes = set()

# -- Worker thread --
class ScanWorker(QThread):
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    file_found = pyqtSignal(str, int)
    scan_completed = pyqtSignal(list)
    total_files_found = pyqtSignal(int)
    files_counted = pyqtSignal(int, int)  # xml_count, dll_count

    def __init__(self, base_dir, search_string, scan_dlls=True, cache_dir="decomp_cache"):
        super().__init__()
        self.base_dirs = [d.strip() for d in base_dir.split(';') if d.strip()]
        self.search_terms = [s.strip().lower().encode('utf-8') for s in search_string.split(';') if s.strip()]
        self.scan_dlls = scan_dlls
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def process_dll_file(self, dll_path, search_terms):
        # Compute SHA-1 hash of the DLL file
        try:
            with open(dll_path, 'rb') as f:
                file_hash = hashlib.sha1(f.read()).hexdigest()
        except Exception as e:
            self.status_updated.emit(f"Error hashing DLL: {dll_path} - {e}")
            return None
        global scanned_dll_hashes
        if file_hash in scanned_dll_hashes:
            self.status_updated.emit(f"Skipping duplicate DLL (already scanned): {shorten_path(dll_path)})")
            return None
        scanned_dll_hashes.add(file_hash)
        cache_path = os.path.join(self.cache_dir, file_hash)
        if os.path.exists(cache_path):
            self.status_updated.emit(f"Using cached decompilation for {shorten_path(dll_path)}")
            decomp_dir = cache_path
            cleanup = False
        else:
            temp_dir = tempfile.mkdtemp()
            try:
                self.status_updated.emit(f"Decompiling {shorten_path(dll_path)}...")
                start_time = time.time()
                decompile_assembly(dll_path, temp_dir)
                self.status_updated.emit(f"Decompilation complete: {shorten_path(dll_path)} Took: {time.time() - start_time:.2f} seconds")
                shutil.move(temp_dir, cache_path)
                decomp_dir = cache_path
                cleanup = False
            except Exception as e:
                self.status_updated.emit(f"Decompilation failed: {dll_path}\n{e}")
                shutil.rmtree(temp_dir, ignore_errors=True)
                return None
        occurrences_total = 0
        total_scanned = 0
        had_error = False
        start_time = time.time()
        for file_path in index_decompiled_files(decomp_dir):
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

        xml_files = [f for f in all_files if f.endswith('.xml')]
        dll_files = [f for f in all_files if f.endswith('.dll')]
        self.files_counted.emit(len(xml_files), len(dll_files))

        if total_files == 0:
            self.status_updated.emit("No XML or DLL files found.")
            self.scan_completed.emit([])
            return

        processed = 0
        # Process XML files sequentially
        for filename in xml_files:
            occurrences = 0
            try:
                self.status_updated.emit(f"Scanning: {shorten_path(filename)}")
                with open(filename, 'rb') as file:
                    content = file.read().lower()
                    occurrences = sum(content.count(term) for term in self.search_terms)
                if occurrences > 0:
                    found_files.append((filename, occurrences))
                    self.file_found.emit(filename, occurrences)
            except Exception as e:
                self.status_updated.emit(f"Error processing {filename}: {e}")
            processed += 1
            self.progress_updated.emit(int(processed / total_files * 100))

        # Process DLL files in a thread pool
        max_workers = max(1, int(get_cpu_count() // 2))
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {executor.submit(self.process_dll_file, filename, self.search_terms): filename for filename in dll_files}
            # This loop will not finish until all DLLs are processed
            for future in concurrent.futures.as_completed(future_to_file):
                filename = future_to_file[future]
                occurrences = 0
                try:
                    self.status_updated.emit(f"Scanning: {shorten_path(filename)}")
                    result = future.result()
                    occurrences = result if result else 0
                    if occurrences > 0:
                        found_files.append((filename, occurrences))
                        self.file_found.emit(filename, occurrences)
                except Exception as e:
                    self.status_updated.emit(f"Error processing {filename}: {e}")
                processed += 1
                self.progress_updated.emit(int(processed / total_files * 100))

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
