from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView, QLabel, QWidget, QVBoxLayout, QHeaderView, QMenu, QAction
from PyQt5.QtCore import Qt, QMimeData, pyqtSignal
from PyQt5.QtGui import QDrag, QPixmap


class CustomTableWidget(QTableWidget):
    cellClickedSignal = pyqtSignal(int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDragDropOverwriteMode(False)
        self.setDropIndicatorShown(True)
        self.horizontalHeader().ResizeMode(QHeaderView.ResizeToContents)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.dragged_item = None
        self.dragged_index = None
        self.fila_origen = None  # Para almacenar la fila de origen
        self.cellClicked.connect(self.onClickRow)
        self.customContextMenuRequested.connect(self.show_table_menu)
        self.setContextMenuPolicy(3)
        
    def show_table_menu(self, position):
        clicked_index = self.indexAt(position)
        if not clicked_index.isValid():
            return
        clicked_row = clicked_index.row()

        menu = QMenu(self)
        delete_action = QAction("Borrar", self)
        delete_action.triggered.connect(lambda: self.deleteItem(clicked_row))
        rotate_action = QAction("Rotar", self)
        move_menu = QMenu("Mover", self) 
        for i in range(1, self.rowCount()+1):#crearemos un submenú para cada página.
            move_sub_action = QAction(f"Mover esta página a {i}", self)
            move_sub_action.triggered.connect(lambda checked, row=i-1: self.move_to_row(clicked_row, row)) 
            move_menu.addAction(move_sub_action)       
        #rotate_action.triggered.connect(self.rotatete_item)
        menu.addAction(delete_action)
        menu.addAction(rotate_action)
        menu.addMenu(move_menu)
        menu.exec_(self.viewport().mapToGlobal(position))

    def deleteItem(self, row):
        print ("to delete "+str(row))
        if row<0 or row>=self.rowCount():
            print("Error, fila a borrar fuera de rango")
            return        
        self.removeRow(row)
        
    def move_to_row(self, from_row, to_row):
        try:
            # Verificar si el movimiento es válido
            if from_row == to_row or from_row < 0 or to_row < 0 or from_row >= self.rowCount() or to_row >= self.rowCount():
                print("Movimiento no válido")
                return
            print(f"Moviendo de la fila {from_row} a la fila {to_row}")
            # Guardar el QWidget de la primera columna y los textos de las otras dos columnas
            widget_item = self.cellWidget(from_row, 0)  # Obtener el QWidget en la primera columna
            print("A")
     
            # Guardar los textos en las otras dos columnas
            text_col_1 = self.item(from_row, 1).text() if self.item(from_row, 1) else ""
            text_col_2 = self.item(from_row, 2).text() if self.item(from_row, 2) else ""
            print(f"B [{text_col_1}, {text_col_2}]")
               
     
            # Insertar una nueva fila en la posición de destino
            self.insertRow(to_row)
            print("C")
            



            # Restaurar el QWidget en la nueva fila en la primera columna
            if widget_item:
                print("D")
                # Aseguramos que estamos utilizando un QWidget válido
                if isinstance(widget_item, QWidget):
                    self.setCellWidget(to_row, 0, widget_item)
                else:
                    print("Error: El item no es un QWidget válido.")
            
            # Restaurar los textos en las otras dos columnas
            print("E")
            self.setItem(to_row, 1, QTableWidgetItem(text_col_1))
            self.setItem(to_row, 2, QTableWidgetItem(text_col_2))
            
            print("F")
            # Eliminar la fila original
            self.removeRow(from_row)
            print("G")
            
        except Exception as e:
            print(f"Se ha producido un error: {e}")
            import traceback
            traceback.print_exc()
            
    def onClickRow(self, row, col):
        self.cellClickedSignal.emit(row)            
        
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
            img_label = QLabel()
            img_label.setPixmap(snapshot.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            img_label.setAlignment(Qt.AlignCenter)
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.addWidget(img_label)
            layout.setContentsMargins(0, 0, 0, 0)
            self.setRowHeight(curRow, 150) 
            self.setCellWidget(curRow , 0, container)
            self.setItem(curRow , 1, QTableWidgetItem(valu1))
            self.setItem(curRow , 2, QTableWidgetItem(valu2))
        else:                
            self.setItem(curRow , 0, QTableWidgetItem(snapshot))
            self.setItem(curRow , 1, QTableWidgetItem(valu1))
            self.setItem(curRow , 2, QTableWidgetItem(valu2))