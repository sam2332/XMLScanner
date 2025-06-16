# XML Scanner - RimWorld Mod Development Tool

A comprehensive GUI application for scanning XML definition files in RimWorld and mods.

## Features

- **Multi-directory scanning**: Scan RimWorld core defs and workshop mods simultaneously
- **Separate windows for different tasks**: Setup, progress monitoring, and results viewing
- **Real-time progress tracking**: See scan progress with detailed logging
- **Comprehensive results table**: View files with occurrence counts, modification dates
- **File operations**: Open files, directories, copy paths, export results
- **Filtering and sorting**: Filter results by filename, sort by any column

## Project Structure

```
Source/XMLScanner/
├── main.py                     # Application entry point
├── core/
│   ├── __init__.py
│   └── scanner.py              # Core scanning logic and worker thread
├── ui/
│   ├── __init__.py
│   ├── main_window.py          # Main orchestrator window
│   ├── setup_window.py         # Configuration/setup window
│   ├── scan_progress_window.py # Real-time scan progress window
│   └── results_window.py       # Results display and management
└── README.md                   # This file
```

## Usage

### GUI Mode (Recommended)
Run the batch file:
```
run_xml_scanner.bat
```

Or run directly:
```
python Source\XMLScanner\main.py --gui
```

### Command Line Mode
```
python Source\XMLScanner\main.py "path1;path2" "search_string"
```

## Workflow

1. **Setup Window**: Configure directories to scan and search string
2. **Progress Window**: Monitor scan progress with real-time updates
3. **Results Window**: View, filter, and interact with results

## Default Scan Locations

- **RimWorld Core Defs**: `c:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Core\Defs`
- **Workshop Mods**: `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100`

## Search Examples

- Class names: `Pawn`, `Building_WorkTable`
- Def names: `Steel`, `ComponentIndustrial`
- XML tags: `<defName>`, `<workType>`
- Attributes: `Abstract="true"`

## Results Features

- **Open File**: Open XML file in default editor
- **Open Directory**: Open containing folder in Windows Explorer
- **Copy Path**: Copy full file path to clipboard
- **Export Results**: Save results to CSV file
- **Filter**: Filter results by filename
- **Sort**: Click column headers to sort

## Requirements

- Python 3.6+
- PyQt5
- Windows 10+ (for file operations)

## Development

The application is modular with separate concerns:
- `core/scanner.py`: Scanning logic and threading
- `ui/setup_window.py`: Configuration interface
- `ui/scan_progress_window.py`: Progress monitoring
- `ui/results_window.py`: Results display and management
- `ui/main_window.py`: Application orchestration
