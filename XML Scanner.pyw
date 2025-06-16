#!/usr/bin/env python3
"""
XML Scanner - RimWorld Mod Development Tool
Main entry point for the XML Scanner GUI application
"""

import sys
import os
import argparse
from PyQt5.QtWidgets import QApplication

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from ui.main_window import XMLScannerMainWindow
from core.scanner import scan_for_string

def parse_arguments():
    parser = argparse.ArgumentParser(description="Scan XML files for a specific string.")
    parser.add_argument("base_dir", type=str, nargs='?', 
                       help="Base directory to scan (multiple directories separated by ;).")
    parser.add_argument("search_string", type=str, nargs='?', 
                       help="String to search for in XML files.")
    parser.add_argument("--gui", action="store_true", help="Launch GUI interface")
    return parser.parse_args()

def main():
    args = parse_arguments()
      # Launch GUI if no arguments provided or --gui flag is used
    if args.gui or (not args.base_dir and not args.search_string):
        app = QApplication(sys.argv)
        window = XMLScannerMainWindow()
        # Don't show the main window - it will show the setup window automatically
        sys.exit(app.exec_())
    else:
        # Legacy command line mode
        if not args.base_dir or not args.search_string:
            print("Error: Both base_dir and search_string are required for command line mode")
            print("Use semicolon (;) to separate multiple directories")
            sys.exit(1)
            
        results = scan_for_string(args.base_dir, args.search_string)
        
        for result in results:
            print(f"Found in: {result}")

if __name__ == "__main__":
    main()
