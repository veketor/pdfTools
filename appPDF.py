from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel
from PyQt5.QtGui import QImage, QPixmap, QKeyEvent
from PyQt5.QtCore import QEvent, Qt, QPoint
from PyQt5 import QtWidgets, uic
import sys
#import pdfTools
import concurrent.futures
import fitz
from enum import Enum


class procesStatus(Enum):
    WAITINGFILE = 0
    PROCESSINGFILE = 1
    WAITINGNUMBER = 2
    CREATINGSECTIONS = 3
    PROCECSSINGSECTIONS = 4
    FINISHED = 5

# def pdf_to_qpixmaps(pdf_path):
    # doc = None
    # try:
        # # Open the PDF document
        # doc = fitz.open(pdf_path)
        # qpixmaps = []
        # for page_num in range(len(doc)):
            # page = doc.load_page(page_num)
            # pix = page.get_pixmap()
            # # Create QImage from pixmap samples
            # # Using RGBA8888 format for maximum compatibility
            # print ("1")
            # fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
            # print ("2")
            # qtimg = QImage(pix.samples_ptr, pix.width, pix.height, fmt)
            # print ("3")
            # # Create QPixmap from QImage
            # qpixmap = QPixmap.fromImage(qtimg)
            # print ("4")
            # qpixmaps.append(qpixmap)
            # print ("5")
        # print ("6")
        # return qpixmaps       
    # finally:
        # if doc:
            # doc.close()

def pdf_to_qpixmaps(pdf_path):
    doc = None
    try:
        doc = fitz.open(pdf_path)
        qpixmaps = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            mat = fitz.Matrix(0.75, 0.75) 
            try:
                pix = page.get_pixmap(matrix=mat, alpha=False)
                fmt = QImage.Format_RGB888
                qtimg = QImage(pix.samples_ptr, 
                             int(pix.width),
                             int(pix.height),
                             pix.stride,
                             fmt)
                qpixmap = QPixmap.fromImage(qtimg)
                if qpixmap.isNull():
                    raise Exception("QPixmap inválido")
                qpixmaps.append(qpixmap)
            except Exception as e:
                print(f"Error en página {page_num}: {str(e)}")
                continue
    finally:
        if doc:
            doc.close()
    return qpixmaps

class FileDropWindow(QMainWindow):   
    def __init__(self):
        super().__init__()
        self.status = procesStatus.WAITINGFILE
        # Load UI
        uic.loadUi('pdfTools.ui', self)
        # Enable drag and drop functionality
        self.setAcceptDrops(True)
        self.lblOriginalFileName.setText("Arrastra un pdf para cargarlo")
        self.fileLoaded = False
        self.btnConfNum.clicked.connect(self.btnSetNum)
        self.pbPrevPage.clicked.connect(self.prevPage)
        self.pbNextPage.clicked.connect(self.nextPage)
        self.imageIndex = 0
        self.imgArray = []
        self.sbPaciente.valueChanged.connect(self.onPacientChange)
        self.setMouseTracking(True)
        self.actionReset.triggered.connect(self.restart)
        self.actionQuit.triggered.connect(self.close)
        self.lblImagePdf.enterEvent = self.handle_mouse_enter
        self.lblImagePdf.leaveEvent = self.handle_mouse_leave
        self.follower_label = QLabel(self)
        self.follower_label.setFixedSize(256, 128)  # Set dimensions to 128x256
        self.follower_label.setStyleSheet("background-color: lightblue; border: 1px solid black")
        self.follower_label.setText("Following mouse...")
        self.follower_label.setHidden(True)
        self.overZoom = False        
 
    def restartProccess(self):
        self.status = procesStatus.WAITINGFILE
        self.lblOriginalFileName.clear()
        self.lblOriginalFileName.setText("Arrastra un pdf para cargarlo")
        self.lblImagePdf.clear()
        self.lblImagePdf.setText("Arrastra un pdf para cargarlo")
        self.fileLoaded = False
        self.imageIndex = 0
        self.imgArray = []
        self.overZoom = False        
        
    def close(self):
        print("Salimos")
        QApplication.quit()
   
    def restart(self):
        print("Restarting")
        self.restartProccess()
        
    def keyPressEvent(self, event):
        if isinstance(event, QKeyEvent):
            theKey = event.text()
            theKeyCode = event.key()
            if theKeyCode == 16777264:
                self.prevPage()
            if theKeyCode == 16777265:
                self.nextPage()
            
    def btnSetNum(self):
        if self.status == procesStatus.WAITINGNUMBER:
            self.sbPaciente.value()
            self.group02.setEnabled(True)
            self.tableWidget.setEnabled(True)
            self.group01.setEnabled(False)            
            print ("HURRA")
        print ("OK")
        
    def prevPage(self):
        if self.imageIndex > 0:
            self.imageIndex = self.imageIndex -1
            self.lblImagePdf.setPixmap(self.imgArray[self.imageIndex])
            self.updateLblPageNum()
            
    def nextPage(self):
        if self.imageIndex < len(self.imgArray)-1:
            self.imageIndex = self.imageIndex +1
            self.lblImagePdf.setPixmap(self.imgArray[self.imageIndex])
            self.updateLblPageNum()
            
    def updateLblPageNum(self):
        text = str(self.imageIndex+1) + "/" +str(len(self.imgArray))
        self.lblPageNum.setText(text)

    def onPacientChange(self):
        if self.sbPaciente.value() >0:
            self.btnConfNum.setEnabled(True)
        else:
            self.btnConfNum.setEnabled(False)
    
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
                self.btnConfNum.setEnabled(False)
                self.status = procesStatus.PROCESSINGFILE
                #self.btnProcess.setEnabled(True)
                print("TENEMOS IMAGEN PRE")
                self.imgArray = pdf_to_qpixmaps(f)
                print("TENEMOS IMAGEN POST")
                self.imageIndex = 0

                if len(self.imgArray) > 0:
                    print("TENEMOS IMAGEN")
                    self.lblImagePdf.setPixmap(self.imgArray[0])
                    self.lblImagePdf.setScaledContents(True)
                    print("OK IMAGE")
                    self.updateLblPageNum()
                    self.status = procesStatus.WAITINGNUMBER
                else:
                    print("Error")
                return#Only accept one file
    
    def handle_mouse_enter(self, event):
        print("Mouse entered lblImagePdf")
        self.follower_label.setHidden(False)
        self.overZoom = True
    
    def handle_mouse_leave(self, event):
        print("Mouse left lblImagePdf")
        self.follower_label.setHidden(True)
        self.overZoom = False
        
    def update_follower_position(self):
        # Get global mouse position
        global_pos = self.mapFromGlobal(self.cursor().pos())
        
        # Position label near cursor but slightly offset
        x = global_pos.x() - self.follower_label.width()
        y = global_pos.y() - self.follower_label.height()
        
        # Ensure label stays within window bounds
        x = max(0, min(x, self.width() - self.follower_label.width()))
        y = max(0, min(y, self.height() - self.follower_label.height()))
        print ("Muevo")
        self.follower_label.move(x, y)
    
    def mouseMoveEvent(self, event):             
        # print ("Mouse")
        if self.overZoom:
            print(f"Posición del ratón: {event.x()}, {event.y()}")
            # super().mouseMoveEvent(event)
            # self.update_follower_position()
        
if __name__ == '__main__':
    # Create the application
    app = QApplication(sys.argv)
    
    # Create and show the window
    window = FileDropWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec_())