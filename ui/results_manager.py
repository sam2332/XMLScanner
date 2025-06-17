from PyQt5.QtWidgets import QWidget

class ResultsManager:
    def __init__(self, xml_results_window_class, dll_results_window_class):
        self.xml_results_window = None
        self.dll_results_window = None
        self.xml_results_window_class = xml_results_window_class
        self.dll_results_window_class = dll_results_window_class

    def show_results(self, xml_results, dll_results, search_string):
        if xml_results:
            self.xml_results_window = self.xml_results_window_class()
            self.xml_results_window.display_results(xml_results, search_string)
            self.xml_results_window.show()
        if dll_results:
            self.dll_results_window = self.dll_results_window_class()
            self.dll_results_window.display_results(dll_results, search_string)
            self.dll_results_window.show()
