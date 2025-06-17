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
from libs.Settings import Settings

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
    file_found = pyqtSignal(str, int, list)  # filename, occurrence_count, matched_terms
    scan_completed = pyqtSignal(list)
    total_files_found = pyqtSignal(int)
    files_counted = pyqtSignal(int, int)  # xml_count, dll_count

    def __init__(self, base_dir, search_string, scan_dlls=True, scan_xmls=True, cache_dir="decomp_cache"):
        super().__init__()
        self.base_dirs = [d.strip() for d in base_dir.split(';') if d.strip()]
        self.search_terms = [s.strip().lower().encode('utf-8') for s in search_string.split(';') if s.strip()]
        self.scan_dlls = scan_dlls
        self.scan_xmls = scan_xmls
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        # Load DLL whitelist from settings
        self.settings = Settings()
        self.dll_whitelist = set([x.strip().lower() for x in self.settings.get('dll_whitelist', []) if x.strip()])

    def process_dll_file(self, dll_path, search_terms):
        # Whitelist check
        dll_name = os.path.basename(dll_path).lower()
        if any(whitelisted.lower() == dll_name.lower() for whitelisted in self.dll_whitelist):
            self.status_updated.emit(f"Skipping whitelisted DLL: {dll_name}")
            return None
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
        matched_files = []
        for file_path in index_decompiled_files(decomp_dir):
            total_scanned += 1
            try:
                with open(file_path, 'rb') as f:
                    content = f.read().lower()
                    occ = sum(content.count(term) for term in search_terms)
                    matched_line = None
                    if occ > 0:
                        # Find the first line containing any search term
                        try:
                            lines = content.split(b'\n')
                            for line in lines:
                                if any(term in line for term in search_terms):
                                    matched_line = line.decode('utf-8', errors='ignore').strip()
                                    if len(matched_line) > 50:
                                        matched_line = matched_line[:50] + '...'
                                    break
                        except Exception:
                            matched_line = ''
                        occurrences_total += occ
                        matched_files.append((dll_path, file_path, occ, matched_line))
            except Exception as e:
                self.status_updated.emit(f"Error reading decompiled file: {e}")
                had_error = True
        if not had_error:
            self.status_updated.emit(f"Scanned {total_scanned} files, found {occurrences_total} occurrences. Took: {time.time() - start_time:.2f} seconds")
        # Return all matched files for this DLL
        return matched_files if matched_files else None
        
    def run(self):
        # Clear the global hash set at the start of each new scan
        global scanned_dll_hashes
        scanned_dll_hashes.clear()
        
        all_files = []
        found_files = []
        self.status_updated.emit("Collecting XML and DLL files...")
        for directory in self.base_dirs:
            if not os.path.exists(directory):
                self.status_updated.emit(f"Warning: Directory does not exist: {directory}")
                continue
            self.status_updated.emit(f"Scanning directory: {directory}")
            xml_files = glob.glob(os.path.join(directory, '**', '*.xml'), recursive=True) if self.scan_xmls else []
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
        if self.scan_xmls:
            for filename in xml_files:
                occurrences = 0
                matched_terms = []
                matched_line = None
                try:
                    self.status_updated.emit(f"Scanning: {shorten_path(filename)}")
                    with open(filename, 'r', encoding='utf-8', errors='ignore') as file:
                        lines = file.readlines()
                        content = ''.join(lines).lower()
                        for idx, term in enumerate(self.search_terms):
                            term_str = term.decode('utf-8')
                            count = content.count(term_str)
                            if count > 0:
                                occurrences += count
                                matched_terms.append(term_str)
                        # Find the first line containing any search term
                        for line in lines:
                            lcline = line.lower()
                            if any(term.decode('utf-8') in lcline for term in self.search_terms):
                                matched_line = line.strip()
                                if len(matched_line) > 50:
                                    matched_line = matched_line[:50] + '...'
                                break
                    if occurrences > 0:
                        # Always use 5-tuple for XML: (filepath, filepath, occurrences, matched_terms, matched_line)
                        found_files.append((filename, filename, occurrences, matched_terms, matched_line))
                        self.file_found.emit(filename, occurrences, matched_terms)
                except Exception as e:
                    self.status_updated.emit(f"Error processing {filename}: {e}")
                processed += 1
                self.progress_updated.emit(int(processed / total_files * 100))

        # Process DLL files in a thread pool
        if self.scan_dlls:
            max_workers = max(1, int(get_cpu_count() // 2))
            def dll_worker(filename):
                result = self.process_dll_file(filename, self.search_terms)
                matched_results = []
                if result:
                    for dll_path, decomp_file, occ, matched_line in result:
                        matched_terms = []
                        try:
                            with open(decomp_file, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read().lower()
                                for term in self.search_terms:
                                    term_str = term.decode('utf-8')
                                    if content.count(term_str) > 0:
                                        matched_terms.append(term_str)
                        except Exception:
                            pass
                        matched_results.append((dll_path, decomp_file, occ, matched_terms, matched_line))
                return matched_results
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_file = {executor.submit(dll_worker, filename): filename for filename in dll_files}
                for future in concurrent.futures.as_completed(future_to_file):
                    filename = future_to_file[future]
                    try:
                        self.status_updated.emit(f"Scanning: {shorten_path(filename)}")
                        result = future.result()
                        if result:
                            for dll_path, decomp_file, occ, matched_terms, matched_line in result:
                                found_files.append((dll_path, decomp_file, occ, matched_terms, matched_line))
                                self.file_found.emit(decomp_file, occ, matched_terms)
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
