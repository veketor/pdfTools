from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView, QLabel, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag, QPixmap


class CustomTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDragDropOverwriteMode(False)
        self.setDropIndicatorShown(True)
        
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.dragged_item = None
        self.dragged_index = None
        self.fila_origen = None  # Para almacenar la fila de origen
        
    def startDrag(self, supportedActions):
        item = self.currentItem()  # Obtener el elemento seleccionado
        if item:
            self.fila_origen = item.row() 
            row = self.row(item)  # Obtener fila
            col = self.column(item)  # Obtener columna
            self.dragged_item = item  # Guardar el elemento
            self.dragged_index = row
            print(f"Elemento cogido: '{item.text()}', Fila: {self.dragged_index}")
        drag = QDrag(self)
        mimeData = QMimeData()
        drag.setMimeData(mimeData)
        drag.exec_(Qt.MoveAction)
        
    def dragEnterEvent(self, event):
        event.accept()  # Aceptar el evento de arrastre

    def dragMoveEvent(self, event):
        event.accept()  # Permitir que el elemento se mueva dentro de la tabl
        
    def dropEvent(self, event):
        print("Soltamos")
        # Obtener la posición donde se suelta el elemento
        pos = event.pos()
        row = self.rowAt(pos.y())
        col = self.columnAt(pos.x())
        fila_destino = self.rowAt(pos.y())  # Determinamos la fila de destino
        if self.fila_origen is not None and fila_destino != -1 and self.fila_origen != fila_destino:
            print(f"Intercambiando Fila {self.fila_origen} con Fila {fila_destino}")
            self.intercambiar_filas(self.fila_origen, fila_destino)

        event.accept()

    def intercambiar_filas(self, fila1, fila2):
        for col in range(3):  # Suponiendo 3 columnas
            if col == 0:
                widget1 = self.cellWidget(fila1, col)
                widget2 = self.cellWidget(fila2, col)

                if widget1 and widget2:
                    # Crear contenedores nuevos para intercambiar los layouts
                    nuevo_widget1 = QWidget()
                    nuevo_widget2 = QWidget()

                    # Extraer los layouts de los widgets originales
                    layout1 = widget1.layout()
                    layout2 = widget2.layout()

                    # Asignar los layouts a los nuevos widgets
                    nuevo_widget1.setLayout(layout2)
                    nuevo_widget2.setLayout(layout1)

                    # Colocar los nuevos widgets en la tabla
                    self.setCellWidget(fila1, col, nuevo_widget1)
                    self.setCellWidget(fila2, col, nuevo_widget2)

                    continue  # Pasar a la siguiente columna sin cambiar texto
            item1 = self.item(fila1, col)
            item2 = self.item(fila2, col)
                        
            texto1 = item1.text() if item1 else ""
            texto2 = item2.text() if item2 else ""

            # Intercambiar valores
            self.setItem(fila1, col, QTableWidgetItem(texto2))
            self.setItem(fila2, col, QTableWidgetItem(texto1))
            
    def addFila(self, snapshot, valu1, valu2):
        curRow = self.rowCount()
        self.insertRow(curRow)
        if isinstance(snapshot, QPixmap):
            print("Imagen")        
            img_label = QLabel()
            img_label.setPixmap(snapshot.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            img_label.setAlignment(Qt.AlignCenter)
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.addWidget(img_label)
            layout.setContentsMargins(0, 0, 0, 0)
            self.setRowHeight(curRow, 128) 
            self.setCellWidget(curRow , 0, container)
            self.setItem(curRow , 1, QTableWidgetItem(valu1))
            self.setItem(curRow , 2, QTableWidgetItem(valu2))
        else:                
            self.setItem(curRow , 0, QTableWidgetItem(snapshot))
            self.setItem(curRow , 1, QTableWidgetItem(valu1))
            self.setItem(curRow , 2, QTableWidgetItem(valu2))