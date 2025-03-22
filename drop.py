from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import QtWidgets, uic
import sys
import pdfTools

class FileDropWindow(QMainWindow):   
    def __init__(self):
        super().__init__()
        # Load UI
        uic.loadUi('pdfTools.ui', self)
        # Enable drag and drop functionality
        self.setAcceptDrops(True)
        self.lblOriginalFileName.setText("Arrastra un pdf para cargarlo")
        self.fileLoaded = False

    def dragEnterEvent(self, event):
        # Accept the drag event if files are being dragged
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if self.fileLoaded:
            return
        # Get the dropped file paths
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        
        # Print each file path
        for f in files:
            if f.lower().endswith(('.pdf')):
                print(f"Dropped file: {f}")
                self.lblOriginalFileName.setText(f)
                self.fileLoaded = True
                self.group01.setEnabled(True)
                #self.btnProcess.setEnabled(True)
                return#Only accept one file

if __name__ == '__main__':
    # Create the application
    app = QApplication(sys.argv)
    
    # Create and show the window
    window = FileDropWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec_())