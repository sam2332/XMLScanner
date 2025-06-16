from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QRadioButton

class OpenDllDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Open DLL File")
        layout = QVBoxLayout(self)
        self.radio_ilspy = QRadioButton("Open in ILSpy")
        self.radio_editor = QRadioButton("Open Decompiled File in Editor")
        self.radio_editor.setChecked(True)
        layout.addWidget(self.radio_ilspy)
        layout.addWidget(self.radio_editor)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    def get_choice(self):
        return 'ilspy' if self.radio_ilspy.isChecked() else 'editor'

class OpenDllFolderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Open Directory")
        layout = QVBoxLayout(self)
        self.radio_dll = QRadioButton("Open DLL Directory")
        self.radio_decompiled = QRadioButton("Open Decompiled Directory")
        self.radio_dll.setChecked(True)
        layout.addWidget(self.radio_dll)
        layout.addWidget(self.radio_decompiled)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    def get_choice(self):
        return 'dll' if self.radio_dll.isChecked() else 'decompiled'
