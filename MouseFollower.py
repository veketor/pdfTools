from PyQt5.QtWidgets import QLabel, QMainWindow, QApplication
from PyQt5.QtCore import Qt, QPoint
import sys

class MouseFollower(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize window
        self.setWindowTitle("Mouse Follower")
        self.setGeometry(100, 100, 800, 600)
        
        # Create and configure the follower label
        self.follower_label = QLabel(self)
        self.follower_label.setFixedSize(256, 128)  # Set dimensions to 128x256
        self.follower_label.setStyleSheet("background-color: lightblue; border: 1px solid black")
        self.follower_label.setText("Following mouse...")
        
        # Enable mouse tracking
        self.setMouseTracking(True)
        
        # Show initial position
        self.update_follower_position()
    
    def update_follower_position(self):
        # Get global mouse position
        global_pos = self.mapFromGlobal(self.cursor().pos())
        
        # Position label near cursor but slightly offset
        x = global_pos.x() - self.follower_label.width()
        y = global_pos.y() - self.follower_label.height()
        
        # Ensure label stays within window bounds
        x = max(0, min(x, self.width() - self.follower_label.width()))
        y = max(0, min(y, self.height() - self.follower_label.height()))
        
        self.follower_label.move(x, y)
    
    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.update_follower_position()
        
def main():
    app = QApplication(sys.argv)
    window = MouseFollower()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()