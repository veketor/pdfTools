from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QTableWidgetItem, QTableWidget, QMenu, QAction, QMessageBox
from PyQt5.QtGui import QImage, QPixmap, QKeyEvent
from PyQt5.QtCore import QEvent, Qt, QPoint
from PyQt5 import QtWidgets, uic
import sys
import concurrent.futures
import fitz
import os
from enum import Enum
import sqlite3
from customtablewidget import CustomTableWidget 

class procesStatus(Enum):
    WAITINGFILE = 0
    PROCESSINGFILE = 1
    WAITINGNUMBER = 2
    CREATINGSECTIONS = 3
    PROCECSSINGSECTIONS = 4
    FINISHED = 5

def pdf_to_qpixmaps(pdf_path):
    doc = None
    try:
        doc = fitz.open(pdf_path)
        qpixmapsArray = []
        mat = fitz.Matrix(0.75, 0.75)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
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
                qpixmapsArray.append(qpixmap)
            except Exception as e:
                print(f"Error en página {page_num}: {str(e)}")
                continue
    finally:
        if doc:
            doc.close()
    return qpixmapsArray

class pdfMegaTools(QMainWindow):   
    def __init__(self):
        super().__init__()
        self.pathToSave = "reports"
        if not os.path.exists(self.pathToSave):
            os.makedirs(self.pathToSave)
        self.status = procesStatus.WAITINGFILE
        # Load UI
        uic.loadUi('pdfMagic.ui', self)
        self.tbPagesConf = self.findChild(CustomTableWidget, 'tbPagesConf')
        #uic.loadUi('configPdfTools.ui', self)
        # Enable drag and drop functionality
        self.setAcceptDrops(True)
        self.lblOriginalFileName.setText("Arrastra un pdf para cargarlo")
        self.fileLoaded = False
        self.currentPDFpath = ""
        self.btnConfNum.clicked.connect(self.btnSetNum)
        self.pbPrevPage.clicked.connect(self.prevPage)
        self.pbNextPage.clicked.connect(self.nextPage)
        self.sbPagFin.valueChanged.connect(self.checkMax)
        self.sbPagIni.valueChanged.connect(self.incrementFin)
        self.imageIndex = 0
        self.imgArray = []
        self.sbPaciente.valueChanged.connect(self.onPacientChange)
        self.pbAdd.clicked.connect(self.addSectionToTable)
        self.setMouseTracking(True)
        self.actionReset.triggered.connect(self.restart)
        self.actionConfig.triggered.connect(self.config)
        self.actionQuit.triggered.connect(self.close)
        self.lblImagePdf.enterEvent = self.handle_mouse_enter
        self.lblImagePdf.leaveEvent = self.handle_mouse_leave
        self.follower_label = QLabel(self)
        self.follower_label.setFixedSize(256, 128)  # Set dimensions to 128x256
        self.follower_label.setStyleSheet("background-color: lightblue; border: 1px solid black")
        self.follower_label.setText("Following mouse...")
        self.follower_label.setHidden(True)
        self.tableWidget.setContextMenuPolicy(3)
        self.tableWidget.customContextMenuRequested.connect(self.show_context_menu)
        self.btnProcess.clicked.connect(self.batchSplit)
        self.conn = sqlite3.connect("mostodent.db")
        #To delete
        self.tbPagesConf.addFila("img1","A","1")
        self.tbPagesConf.addFila("img2","B","2")
        self.tbPagesConf.addFila("img3","C","3")
        self.tbPagesConf.addFila("img4","D","4")
        self.tbPagesConf.addFila("img5","E","5")
    
    def checkMax(self):
        if self.sbPagIni.value() > len(self.imgArray):
            self.sbPagIni.setValue(len(self.imgArray))
        if self.sbPagFin.value() > len(self.imgArray):
            self.sbPagFin.setValue(len(self.imgArray))
        else:
            if (self.sbPagFin.value() <= self.sbPagIni.value()):
                self.sbPagFin.setValue(self.sbPagIni.value())
            self.imageIndex = self.sbPagFin.value()-1
            self.setPdfPageInView(self.imageIndex)
            
    def incrementFin(self):
        if self.sbPagIni.value() > len(self.imgArray):
            self.sbPagIni.setValue(len(self.imgArray))
        if self.sbPagFin.value() < (len(self.imgArray)):
            if self.sbPagIni.value() < (len(self.imgArray)+1):
                self.sbPagFin.setValue(self.sbPagIni.value()+0)
        
    def addSectionToTable(self):
        startPage = str(self.sbPagIni.value())
        endPage = str(self.sbPagFin.value())
        docType = str(self.cbTipoDoc.currentText())
        date = str(self.dateEdit.date().toPyDate())
        curRow = self.tableWidget.rowCount()
        self.tableWidget.insertRow(curRow)
        self.tableWidget.setItem(curRow , 0, QTableWidgetItem(startPage))
        self.tableWidget.setItem(curRow , 1, QTableWidgetItem(endPage))
        self.tableWidget.setItem(curRow , 2, QTableWidgetItem(docType))
        self.tableWidget.setItem(curRow , 3, QTableWidgetItem(date))
        self.btnProcess.setEnabled(True)
        if self.sbPagFin.value()+1 < len(self.imgArray):
            self.sbPagIni.setValue(self.sbPagFin.value()+1)
        self.cbTipoDoc.setFocusPolicy(Qt.StrongFocus)   
        self.cbTipoDoc.setFocus()
        if self.sbPagIni.value() <= len(self.imgArray):
            self.imageIndex = self.sbPagIni.value()-1
            self.setPdfPageInView(self.imageIndex)
        self.make_columns_readonly()
  
    def restartProccess(self):
        self.status = procesStatus.WAITINGFILE
        self.currentPDFpath = ""
        self.lblOriginalFileName.clear()
        self.lblOriginalFileName.setText("Arrastra un pdf para cargarlo")
        self.lblImagePdf.clear()
        self.lblImagePdf.setText("Arrastra un pdf para cargarlo")
        self.fileLoaded = False
        self.imageIndex = 0
        self.imgArray = []
        self.sbPagIni.setValue(1)
        self.sbPagFin.setValue(2)
        self.tableWidget.setRowCount(0)
        self.lblNombrePacienteDB.setText(" ..............................................................")
        
    def close(self):
        self.conn.close()
        QApplication.quit()
   
    def config(self):
        print("Abrir ventana")
        
    def restart(self):
        self.restartProccess()
        
    def keyPressEvent(self, event):
        if isinstance(event, QKeyEvent):
            theKey = event.text()
            theKeyCode = event.key()
            if theKeyCode == 16777264: #F1
                self.prevPage()
            if theKeyCode == 16777265: #F2
                self.nextPage()
            if theKeyCode == 16777216: #escape
                self.cbTipoDoc.setFocus(True)
            
    def btnSetNum(self):
        if self.status == procesStatus.WAITINGNUMBER:
            self.sbPaciente.value()
            self.group02.setEnabled(True)
            self.tableWidget.setEnabled(True)
            self.group01.setEnabled(False)
            self.cbTipoDoc.setFocusPolicy(Qt.StrongFocus)   
            self.cbTipoDoc.setFocus()
            cur = self.conn.cursor()
            cur.execute('select name, surname from tbl_patient where id = '+str(self.sbPaciente.value()))
            row = cur.fetchone()    
            if row is None:
                self.lblNombrePacienteDB.setText(" ..............................................................")
                return 
            if len(row) > 0:               
                self.lblNombrePacienteDB.setText(row[0]+" "+row[1])

    
    def setPdfPageInView(self, pageNum):        
        self.lblImagePdf.setPixmap(self.imgArray[pageNum])
        self.updateLblPageNum()
    
    def prevPage(self):
        if self.imageIndex > 0:
            self.imageIndex = self.imageIndex -1
            self.setPdfPageInView(self.imageIndex)
            
    def nextPage(self):
        if self.imageIndex < len(self.imgArray)-1:
            self.imageIndex = self.imageIndex +1
            self.setPdfPageInView(self.imageIndex)
            
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

        files = [u.toLocalFile() for u in event.mimeData().urls()]

        for f in files:
            if f.lower().endswith(('.pdf')):
                self.lblOriginalFileName.setText(f)
                self.fileLoaded = True
                self.group01.setEnabled(True)
                self.btnConfNum.setEnabled(False)
                self.status = procesStatus.PROCESSINGFILE
                self.imgArray = pdf_to_qpixmaps(f)
                self.imageIndex = 0

                if len(self.imgArray) > 0:
                    self.lblImagePdf.setPixmap(self.imgArray[self.imageIndex])
                    self.lblImagePdf.setScaledContents(True)
                    self.updateLblPageNum()
                    self.status = procesStatus.WAITINGNUMBER
                    self.sbPaciente.setFocus()
                    self.currentPDFpath = f
                    print ("Ruta del pdf: "+f)
                    self.sbPagIni.setMaximum = len(self.imgArray)
                    self.sbPagFin.setMaximum = len(self.imgArray)
                    print("Puesto el máximo")
                else:
                    print("Error")
                    self.currentPDFpath = ""
                return
    
    def handle_mouse_enter(self, event):
        return
        #print("Mouse entered lblImagePdf")
        #self.follower_label.setHidden(False)
    
    def handle_mouse_leave(self, event):
        self.follower_label.setHidden(True)
        
    def update_follower_position(self):
        global_pos = self.mapFromGlobal(self.cursor().pos())
        yOffsetUpdatePos = int(self.follower_label.height()/2)
        x = global_pos.x() - self.follower_label.width()
        y = global_pos.y() - (self.follower_label.height() - 128)
        
        pX = max(0, min(x, self.width() - self.follower_label.width()))
        pY = max(0, min(y, self.height() - self.follower_label.height()))
        self.follower_label.move(pX, pY)
  
    def constrain(value, min_val=0.1, max_val=1.0):
        return max(min_val, min(value, max_val))

  
    def mouseMoveEvent(self, event):
        scaleAdjustment = 0.9
        if self.lblImagePdf.geometry().contains(event.x(), int(event.y()*scaleAdjustment)):
            if len(self.imgArray) == 0:
                return
            yOffset = 0
            scaleX = max(1.35, self.imgArray[self.imageIndex].width() / self.lblImagePdf.width())
            scaleY = max(1.35, self.imgArray[self.imageIndex].width() / self.lblImagePdf.width())
            sectorX = max(0,int(event.x()-self.lblImagePdf.pos().x()*scaleX))
            sectorY = max(0, int(event.y()-self.lblImagePdf.pos().y()*scaleY + yOffset))
            self.follower_label.setHidden(False)
            self.update_follower_position()
            recorte = self.imgArray[self.imageIndex].copy(sectorX, sectorY, 256, 128)
            self.follower_label.setPixmap(recorte)

    def make_columns_readonly(self):
        row_count = self.tableWidget.rowCount()
        col_indices = [2, 3]

        for row in range(row_count):
            for col in col_indices:
                item = self.tableWidget.item(row, col)
                if item is None:
                    item = QTableWidgetItem("")  # Si la celda está vacía, crea un item
                    self.tableWidget.setItem(row, col, item)

                item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Deshabilitar edición

    def show_context_menu(self, position):
        menu = QMenu(self)

        delete_action = QAction("Borrar", self)
        delete_action.triggered.connect(self.delete_item)
        menu.addAction(delete_action)

        #modify_action = QAction("Modificar", self)
        #modify_action.triggered.connect(self.modify_item)
        #menu.addAction(modify_action)

        menu.exec_(self.tableWidget.viewport().mapToGlobal(position))

    def modify_item(self):
        selected = self.tableWidget.currentItem()
        if selected:
            QMessageBox.information(self, "Modificar", f"Modificando: {selected.text()}")
        else:
            QMessageBox.warning(self, "Modificar", "No hay ninguna celda seleccionada.")

    def delete_item(self):
        selected = self.tableWidget.currentItem()
        if selected:
            row = selected.row()
            self.tableWidget.removeRow(row)
        else:
            QMessageBox.warning(self, "Borrar", "No hay ninguna celda seleccionada.")

    def batchSplit(self):
        row_count = self.tableWidget.rowCount()
        values = []
        pathFolder = self.pathToSave+"\\"+str(self.sbPaciente.value())
        if not os.path.exists(pathFolder):
            os.makedirs(pathFolder)
        for row in range(row_count):
            rowValues = []
            for col in range(4):
                item = self.tableWidget.item(row, col)
                value = item.text() if item is not None else ""
                rowValues.append(value)
            pdfName = str(self.sbPaciente.value())+"_"+rowValues[2].replace(" ", "")+"_"+rowValues[3]
            fileIndex = ""                
            #print("\t".join(rowValues))
            #print (pdfName+".pdf" +" | [" +str(rowValues[0])+", "+str(rowValues[1])+"]")
            self.saveSubPDF(self.currentPDFpath, int(rowValues[0]), int(rowValues[1]), pathFolder, pdfName, ".pdf")
            values.append(rowValues)
            os.startfile(self.pathToSave+"\\"+str(self.sbPaciente.value()))
            
    def saveSubPDF(self, path, pageFrom, pageTo, folderName, fileName, extension):
        doc = fitz.open(path)             
        if pageFrom < 1:
            raise ValueError(f"Error: La página inicial {pageFrom} debe ser mayor o igual a 1")
        if pageTo > doc.page_count:
            raise ValueError(f"Error: La página final {pageTo} excede el número total de páginas ({doc.page_count})")
        if pageFrom > pageTo:
            pTemp = pageFrom
            pageTo = pageFrom
            pageFrom = pTemp            
        newPDF = fitz.open()       
        for pageNum in range(pageFrom - 1, pageTo):
            newPDF.insert_pdf(doc, from_page=pageNum, to_page=pageNum)
        valName = self.getValidName(folderName, fileName, extension)
        #print ("-->"+valName)
        newPDF.save(folderName+"\\"+valName)
        doc.close()
        newPDF.close()
    
    def getValidName(self, folderName, fileName, extension):
        if not os.path.exists(folderName+"\\"+fileName+extension):
            return fileName+extension
        numIndex = 1
        while os.path.exists(folderName+"\\"+fileName+"_"+str(numIndex).zfill(3)+extension):
            numIndex = numIndex+1  
        return fileName+"_"+str(numIndex).zfill(3)+extension
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    myPdfApp = pdfMegaTools()
    myPdfApp.show()

    sys.exit(app.exec_())