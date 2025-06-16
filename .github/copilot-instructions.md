# XMLScanner Project Instructions

## Overview
XMLScanner is a PyQt5 GUI application for scanning XML and DLL files in RimWorld mod development. It helps find specific content across definition files and decompiled assemblies.

## Key Guidelines

### Always Reference Memory.md
- **Memory.md** contains comprehensive technical documentation
- Use it to understand architecture, data flow, and implementation details
- Refer to it before making changes to understand component interactions

### Project Structure
- `XML Scanner.pyw` - Main entry point
- `core/scanner.py` - Scanning engine with threading
- `ui/` - PyQt5 interface components (setup, progress, results windows)
- `libs/` - Utilities (Settings, path helpers)
- `decomp_cache/` - Cached decompiled DLL content

### Development Principles
1. **Threading**: All heavy operations use QThread to keep UI responsive
2. **Settings Persistence**: Use Settings class for configuration storage
3. **Error Handling**: Graceful handling with user-friendly messages
4. **Performance**: Cache decompiled DLLs, use parallel processing
5. **User Experience**: Real-time progress updates and detailed logging

### Common Tasks
- **Adding file types**: Modify ScanWorker in scanner.py
- **UI changes**: Update respective window classes in ui/ directory
- **Settings**: Use Settings class for persistent configuration
- **External tools**: Handle ILSpy integration and validation

### Dependencies
- PyQt5 for GUI
- ILSpy command line tool for DLL decompilation
- Standard Python libraries for file operations

### Testing
- Test with RimWorld directories
- Verify DLL decompilation works
- Check multi-threading performance
- Validate settings persistence