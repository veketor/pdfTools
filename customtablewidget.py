from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag

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
            item1 = self.item(fila1, col)
            item2 = self.item(fila2, col)
                        
            texto1 = item1.text() if item1 else ""
            texto2 = item2.text() if item2 else ""

            # Intercambiar valores
            self.setItem(fila1, col, QTableWidgetItem(texto2))
            self.setItem(fila2, col, QTableWidgetItem(texto1))