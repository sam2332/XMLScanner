# XMLScanner Memory Document

This is a comprehensive technical memory document for the XMLScanner project, designed to help with development, debugging, and feature enhancements.

## Project Overview

XMLScanner is a comprehensive GUI application for scanning XML definition files and DLL assemblies in RimWorld and mods. It helps modders and developers find specific content across RimWorld's vast collection of definition files and compiled assemblies.

### Primary Use Cases
1. **RimWorld Mod Development**: Find specific classes, methods, or definitions across mod files
2. **Security Analysis**: Scan DLL files for potentially malicious code patterns
3. **Code Research**: Locate implementation details across decompiled assemblies
4. **Definition Lookup**: Find XML definitions by content, tags, or attributes

## Architecture & Code Organization

### Entry Point
- **File**: `XML Scanner.pyw`
- **Purpose**: Main application entry point with argument parsing
- **Key Features**:
  - GUI mode (default) vs command-line mode
  - PyQt5 application initialization
  - Path management for module imports
  - Minimal command-line interface for programmatic access

### Core Scanning Engine
- **File**: `core/scanner.py`
- **Key Classes**:
  - `ScanWorker(QThread)`: Multi-threaded scanning worker
  - Functions: `decompile_assembly()`, `index_decompiled_files()`, `scan_for_string()`

#### ScanWorker Architecture
- **Threading**: Inherits from QThread for non-blocking UI
- **Multi-format**: Handles both XML and DLL files
- **Signals**: Uses PyQt signals for progress/status communication
  - `progress_updated(int)`: Progress percentage
  - `status_updated(str)`: Status messages for logging
  - `file_found(str, int, list)`: File path, occurrence count, matched terms
  - `scan_completed(list)`: Final results list
  - `total_files_found(int)`: Total file count for progress calculation
  - `files_counted(int, int)`: XML count, DLL count

#### DLL Processing Pipeline
1. **Hash Calculation**: SHA-1 hash of DLL for deduplication
2. **Cache Check**: Look for cached decompilation in `decomp_cache/`
3. **ILSpy Decompilation**: Use `ilspycmd` for C# source generation
4. **File Indexing**: Find all `.cs` files in decompiled output
5. **Content Scanning**: Search decompiled source for terms
6. **Result Aggregation**: Collect matches with occurrence counts

#### Performance Optimizations
- **Global Hash Tracking**: `scanned_dll_hashes` set prevents duplicate processing
- **Parallel Processing**: ThreadPoolExecutor for concurrent DLL processing
- **CPU-Aware Threading**: Uses `get_cpu_count() // 2` for optimal performance
- **Intelligent Caching**: Persistent cache in `decomp_cache/` directory
- **Memory Management**: Temporary files cleaned up automatically

### User Interface Layer

#### Main Window Orchestrator
- **File**: `ui/main_window.py`
- **Class**: `XMLScannerMainWindow(QMainWindow)`
- **Purpose**: Controller that manages workflow between windows
- **Key Features**:
  - Hidden main window (pure controller)
  - Window lifecycle management
  - Signal routing between components
  - State tracking for scan parameters

#### Setup Window
- **File**: `ui/setup_window.py`
- **Class**: `SetupWindow(QWidget)`
- **Purpose**: Configuration interface for scan parameters
- **Key Features**:
  - Multi-directory path configuration (semicolon-separated)
  - Search term input (multiple terms with semicolon separation)
  - File type selection (XML, DLL, or both)
  - Settings persistence via Settings class
  - Path validation and user feedback

#### Progress Window
- **File**: `ui/scan_progress_window.py`
- **Class**: `ScanProgressWindow(QWidget)`
- **Purpose**: Real-time scan monitoring and logging
- **Key Features**:
  - Live progress bar with percentage
  - Detailed logging with timestamps
  - File count statistics (XML vs DLL breakdown)
  - Scan cancellation functionality
  - Auto-scrolling log view
  - Window state management (scan vs completed)

#### Results Window
- **File**: `ui/results_window.py`
- **Class**: `ResultsWindow(QWidget)`
- **Purpose**: Interactive display of scan results
- **Key Features**:
  - Sortable table with 6 columns
  - Real-time filename filtering
  - File operations (open, directory, copy path)
  - CSV export functionality
  - Dual-mode display (XML vs DLL results)
  - Context-aware button enabling

#### Dialog Components
- **File**: `ui/no_results_dialog.py`
  - **Class**: `NoResultsDialog(QDialog)` 
  - **Purpose**: User feedback when no matches found
  - **Features**: Scan details, suggestions, new scan option

- **File**: `ui/dll_dialogs.py`
  - **Classes**: `OpenDllDialog`, `OpenDllFolderDialog`
  - **Purpose**: DLL-specific operation choices
  - **Features**: Choice between ILSpy vs editor, DLL vs decompiled directory

### Utility Layer

#### Settings Management
- **File**: `libs/Settings.py`
- **Class**: `Settings`
- **Purpose**: JSON-based configuration persistence
- **Key Methods**:
  - `get(key, default)`: Retrieve setting with fallback
  - `set(key, value)`: Store and persist setting
  - Dictionary-like access with `__getitem__`, `__setitem__`
  - Automatic JSON file management

#### Utility Functions
- **File**: `libs/util.py`
- **Functions**:
  - `shorten_path(filepath, segments=7)`: Truncate long paths for display
  - `get_cpu_count()`: Cross-platform CPU detection with fallback

## Data Flow & State Management

### Scan Workflow
1. **Setup**: User configures directories and search terms
2. **Validation**: Path existence and parameter validation
3. **Initialization**: ScanWorker created with parameters
4. **File Discovery**: Recursive glob search for XML/DLL files
5. **Processing**: Sequential XML + parallel DLL processing
6. **Results**: Display in table or show no-results dialog

### Settings Persistence
- **File**: `settings.json`
- **Automatic**: Save on every configuration change
- **Keys**:
  - `base_directory`: Last used scan directories
  - `search_string`: Last used search terms
  - `scan_dlls`: DLL scanning preference
  - `scan_xmls`: XML scanning preference
  - `last_scan_date`: Timestamp tracking
  - `scan_results`: Result caching (currently unused)

### Cache Management
- **Directory**: `decomp_cache/`
- **Structure**: SHA-1 hash subdirectories containing decompiled source
- **Persistence**: Survives application restarts
- **Deduplication**: Identical DLLs only processed once
- **Performance**: Dramatically speeds up repeat scans

## External Dependencies

### Required Tools
- **ILSpy Command Line**: `ilspycmd` for DLL decompilation
  - Installation: `dotnet tool install -g ilspycmd`
  - Validation: `where ilspycmd` check in scanner
  - Error handling: Clear user messages for missing tool

### Python Dependencies
- **PyQt5**: GUI framework with threading support
- **Standard Library**: 
  - `os`, `glob`: File system operations
  - `tempfile`, `shutil`: Temporary file management
  - `hashlib`: SHA-1 hashing for cache keys
  - `subprocess`: External tool execution
  - `concurrent.futures`: Thread pool management

## Search Functionality

### Search Term Processing
- **Multiple Terms**: Semicolon-separated input
- **Case Sensitivity**: All searches are case-sensitive
- **Encoding**: UTF-8 byte-level searching for reliability
- **Occurrence Counting**: Cumulative counts across all terms

### XML Search Patterns
- **Class Names**: `Pawn`, `Building_WorkTable`, `ThingDef`
- **Definition Names**: `Steel`, `ComponentIndustrial`, `Apparel_Pants`
- **XML Tags**: `<defName>`, `<workType>`, `<thingClass>`
- **Attributes**: `Abstract="true"`, `Name="BaseWeapon"`
- **Values**: `<damage>15</damage>`, `<marketValue>2.8</marketValue>`

### DLL/Code Search Patterns
- **Security Keywords**: `LoadLibrary`, `VirtualAlloc`, `CreateProcess`
- **RimWorld Classes**: `Pawn`, `Building`, `CompProperties`
- **Methods**: `GetInspectString`, `PostMake`, `DrawGhost`
- **Namespaces**: `Verse`, `RimWorld`, `HarmonyLib`

## Configuration Details

### Default Scan Locations
1. **RimWorld Core**: `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Core\Defs`
2. **Workshop Mods**: `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100`
3. **Local Mods**: `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods`
4. **User Data**: `%USERPROFILE%\AppData\LocalLow\Ludeon Studios\`

### Security Search Configuration
The default settings.json contains an extensive list of Windows API security indicators:
- Memory manipulation: `VirtualAlloc`, `WriteProcessMemory`, `ReadProcessMemory`
- Process creation: `CreateProcess`, `CreateThread`, `CreateRemoteThread`
- Library loading: `LoadLibrary`, `GetProcAddress`
- Networking: `WSASocket`, `connect`, `send`, `recv`
- Shell execution: `ShellExecute`, `WinExec`, `system`

## Error Handling & Edge Cases

### File Access Errors
- **Locked Files**: Graceful handling with status messages
- **Permission Issues**: Clear error reporting
- **Missing Files**: Path validation before processing
- **Corrupted DLLs**: Decompilation failure handling

### Decompilation Edge Cases
- **Protected Assemblies**: Error handling for obfuscated/protected DLLs
- **Large Files**: Memory management for massive assemblies
- **Invalid DLLs**: Format validation and error reporting
- **Tool Missing**: Clear instructions for ILSpy installation

### UI State Management
- **Long Operations**: Non-blocking progress updates
- **Cancellation**: Clean termination of background threads
- **Window Lifecycle**: Proper cleanup on application exit
- **Memory Usage**: Result table optimization for large datasets

## Performance Considerations

### Threading Strategy
- **UI Thread**: Handles interface updates and user interaction
- **Worker Thread**: Manages file discovery and XML processing
- **Thread Pool**: Parallel DLL decompilation (CPU_COUNT/2 workers)
- **Signal Communication**: Thread-safe updates via PyQt signals

### Memory Optimization
- **Streaming**: Large files read in chunks
- **Cleanup**: Temporary files removed after processing
- **Cache Efficiency**: Persistent decompilation cache
- **Result Storage**: Efficient table population for large result sets

### Scalability Limits
- **File Count**: Tested with thousands of files
- **DLL Size**: Limited by available RAM and ILSpy capabilities
- **Search Terms**: Multiple terms increase processing time linearly
- **Directory Depth**: Recursive scanning can be deep but manageable

## Development & Extension Points

### Adding New File Types
1. Modify `ScanWorker.run()` to include new extensions in glob patterns
2. Add processing logic in the main scanning loop
3. Update UI to include new file type options
4. Add appropriate external tool integration if needed

### Improving Performance
1. **Async Processing**: Convert more operations to async/await pattern
2. **Streaming Search**: Process large files without full memory load
3. **Index Building**: Pre-build searchable indexes for frequently scanned directories
4. **Parallel XML**: Add threading to XML processing (currently sequential)

### UI Enhancements
1. **Progress Granularity**: More detailed progress reporting
2. **Result Previews**: Show file content snippets in results
3. **Search History**: Track and reuse previous search terms
4. **Batch Operations**: Multi-file operations in results window

### Error Resilience
1. **Retry Logic**: Automatic retry for transient failures
2. **Partial Results**: Continue processing after individual file failures
3. **Recovery**: Resume interrupted scans from checkpoints
4. **Validation**: More comprehensive input validation

## Debugging & Troubleshooting

### Common Issues
1. **ILSpy Missing**: Check PATH and .NET installation
2. **Slow Performance**: Monitor CPU usage and thread count
3. **Memory Issues**: Watch for memory leaks in long scans
4. **File Locks**: Handle Windows file system restrictions
5. **Path Length**: Windows MAX_PATH limitations

### Debug Information
- **Log Files**: Progress window provides detailed operation log
- **Settings**: Current configuration visible in settings.json
- **Cache State**: Inspect decomp_cache directory for cached files
- **Thread State**: Monitor for hanging worker threads

### Performance Profiling
- **File Counts**: Track XML vs DLL processing times
- **Cache Hits**: Monitor decompilation cache effectiveness
- **Memory Usage**: Watch for memory growth during large scans
- **Thread Utilization**: Ensure optimal CPU usage

## Future Development Considerations

### Cross-Platform Support
- **Path Handling**: Use `os.path` consistently for cross-platform paths
- **Tool Integration**: Alternative decompilers for non-Windows platforms
- **File Operations**: Abstract file system operations

### Advanced Search Features
- **Regex Support**: Pattern-based searching
- **Context Windows**: Show surrounding code for matches
- **Filtering**: Advanced result filtering and sorting
- **Bookmarks**: Save and organize search results

### Integration Options
- **VS Code Extension**: Direct IDE integration
- **Command Line Interface**: Headless operation for CI/CD
- **API Interface**: REST API for external tool integration
- **Plugin System**: Extensible architecture for custom processors

This memory document serves as a comprehensive reference for understanding, maintaining, and extending the XMLScanner codebase.
