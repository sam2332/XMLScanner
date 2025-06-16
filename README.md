# XML Scanner - RimWorld Mod Development Tool

A comprehensive GUI application for scanning XML definition files and DLL assemblies in RimWorld and mods. This tool helps modders and developers find specific content across RimWorld's vast collection of definition files and compiled assemblies.

## Features

### Core Functionality
- **Multi-format scanning**: Scan both XML files and .NET DLL assemblies
- **DLL decompilation**: Automatically decompiles .NET assemblies using ILSpy and searches the source code
- **Multi-directory scanning**: Scan RimWorld core defs, workshop mods, and custom directories simultaneously
- **Intelligent caching**: Caches decompiled DLL content to avoid re-processing identical files
- **Multi-threaded processing**: Parallel processing of DLL files for improved performance

### User Interface
- **Modular windows**: Separate windows for setup, progress monitoring, and results viewing
- **Real-time progress tracking**: Live scan progress with detailed logging and status updates
- **Comprehensive results table**: View files with occurrence counts, modification dates, and matched terms
- **Advanced filtering**: Filter results by filename with real-time updates
- **Sorting capabilities**: Sort by any column (filename, directory, occurrences, etc.)

### File Operations
- **Open files**: Open XML files or decompiled DLL source in default editor
- **Open directories**: Navigate to file locations in Windows Explorer
- **Copy paths**: Copy full file paths to clipboard
- **Export results**: Save scan results to CSV format
- **DLL-specific operations**: Open original DLL directory or decompiled source directory

## Project Structure

```
XMLScanner/
├── XML Scanner.pyw             # Main application entry point
├── settings.json               # Application settings and configuration
├── core/
│   ├── __init__.py
│   └── scanner.py              # Core scanning logic, DLL decompilation, worker threads
├── ui/
│   ├── __init__.py
│   ├── main_window.py          # Main application orchestrator
│   ├── setup_window.py         # Configuration and setup interface
│   ├── scan_progress_window.py # Real-time scan progress monitoring
│   ├── results_window.py       # Results display and management
│   ├── no_results_dialog.py    # Dialog shown when no matches found
│   └── dll_dialogs.py          # DLL-specific operation dialogs
├── libs/
│   ├── Settings.py             # JSON-based settings management
│   └── util.py                 # Utility functions (path shortening, CPU detection)
└── decomp_cache/               # Cache directory for decompiled DLL content
```

## Installation & Requirements

### Prerequisites
- **Python 3.6+** with PyQt5
- **ILSpy Command Line Tool** for DLL decompilation:
  ```bash
  dotnet tool install -g ilspycmd
  ```
- **Windows 10+** (for file system operations)

### Python Dependencies
```bash
pip install PyQt5
```

## Usage

### GUI Mode (Recommended)
Simply run the main application file:
```bash
python "XML Scanner.pyw"
```

The application will launch with the setup window where you can configure:
- Base directories to scan
- Search terms (supports multiple terms separated by semicolons)
- Whether to scan XML files, DLL files, or both

### Command Line Mode
For programmatic access:
```python
from core.scanner import scan_for_string
results = scan_for_string("path1;path2", "search_string")
```

## Workflow

1. **Setup Window**: Configure scan parameters
   - Select directories to scan (multiple paths separated by `;`)
   - Enter search terms (multiple terms separated by `;`)
   - Choose file types to scan (XML, DLL, or both)

2. **Progress Window**: Monitor scan execution
   - Real-time progress bar and status updates
   - File count statistics (XML vs DLL files)
   - Detailed logging of decompilation and scanning process
   - Ability to cancel long-running scans

3. **Results Window**: Interact with scan results
   - Sortable table with file paths, occurrence counts, and matched terms
   - Filter results by filename
   - Open files, directories, or copy paths
   - Export results to CSV format

## Default Scan Locations

The application comes pre-configured with common RimWorld directories:

- **RimWorld Core Defs**: `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Core\Defs`
- **Workshop Mods**: `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100`
- **Local Mods**: `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods`
- **User Data**: `%USERPROFILE%\AppData\LocalLow\Ludeon Studios\`

## Search Examples

### XML Content Searches
- **Class names**: `Pawn`, `Building_WorkTable`, `ThingDef`
- **Def names**: `Steel`, `ComponentIndustrial`, `Apparel_Pants`
- **XML tags**: `<defName>`, `<workType>`, `<thingClass>`
- **Attributes**: `Abstract="true"`, `Name="BaseWeapon"`
- **Values**: `<damage>15</damage>`, `<marketValue>2.8</marketValue>`

### DLL/Code Searches
- **Security concerns**: `WebClient.DownloadFile`, `HttpClient`, `Registry`
- **Class names**: `Pawn`, `Building`, `CompProperties`
- **Method names**: `GetInspectString`, `PostMake`, `DrawGhost`
- **Namespaces**: `Verse`, `RimWorld`, `HarmonyLib`

## DLL Scanning Features

### Decompilation Process
1. **Hash-based deduplication**: Identical DLL files are only processed once
2. **ILSpy integration**: Uses ILSpy command-line tool for reliable decompilation
3. **Intelligent caching**: Decompiled content is cached in `decomp_cache/` directory
4. **Error handling**: Graceful handling of protected or corrupted assemblies

### Performance Optimizations
- **Parallel processing**: Multiple DLL files processed simultaneously
- **CPU-aware threading**: Automatically adjusts thread count based on available cores
- **Memory management**: Temporary files cleaned up automatically
- **Progress tracking**: Real-time updates on decompilation progress

## Configuration

Settings are stored in `settings.json` and include:
- **base_directory**: Default directories to scan
- **search_string**: Last used search terms
- **scan_dlls**: Whether to scan DLL files by default
- **scan_xmls**: Whether to scan XML files by default

Settings persist between application sessions and can be modified through the GUI.

## Development

### Architecture
The application follows a clean separation of concerns:

- **Core Layer** (`core/scanner.py`): 
  - File scanning and processing logic
  - DLL decompilation and caching
  - Multi-threaded worker implementation
  - Search term matching algorithms

- **UI Layer** (`ui/`):
  - PyQt5-based user interface components
  - Signal/slot communication between windows
  - Real-time progress updates and logging
  - Results display and interaction

- **Utilities** (`libs/`):
  - Settings management with JSON persistence
  - Path manipulation and display utilities
  - System resource detection

### Extending the Scanner
To add support for additional file types:

1. Modify `ScanWorker` in `core/scanner.py` to handle new file extensions
2. Add appropriate processing logic for the new file type
3. Update the UI to include options for the new file type
4. Add any required external tools or dependencies

### Error Handling
The application includes comprehensive error handling:
- **File access errors**: Graceful handling of locked or inaccessible files
- **Decompilation failures**: Fallback behavior for protected assemblies
- **Missing dependencies**: Clear error messages for missing tools (ILSpy)
- **Invalid paths**: User-friendly warnings for non-existent directories

## Troubleshooting

### Common Issues

1. **"ilspycmd not found" error**:
   - Install ILSpy command-line tool: `dotnet tool install -g ilspycmd`
   - Ensure .NET SDK is installed and in PATH

2. **Slow DLL scanning**:
   - DLL decompilation is CPU-intensive; consider scanning fewer directories
   - First-time scans are slower; subsequent scans use cached results

3. **No results found**:
   - Verify search terms are spelled correctly
   - Search is case-sensitive; try variations
   - Check that target directories contain expected files

4. **Memory issues with large scans**:
   - Scan smaller directory sets
   - Close other applications to free memory
   - Consider excluding very large DLL files if not needed

## Contributing

This tool is designed for RimWorld modding community. Contributions welcome for:
- Additional file format support
- UI/UX improvements
- Performance optimizations
- Cross-platform compatibility

## License

This project is designed as a development tool for the RimWorld modding community.
