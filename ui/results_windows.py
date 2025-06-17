from PyQt5.QtWidgets import QWidget
from .results_window import ResultsWindow

class XMLResultsWindow(ResultsWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("XML Scanner - XML Results")

class DLLResultsWindow(ResultsWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("XML Scanner - DLL Results")
