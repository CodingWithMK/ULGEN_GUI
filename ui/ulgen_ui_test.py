import sys
import cv2
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QHBoxLayout, QVBoxLayout, QFrame, QStackedWidget
)
from PySide6.QtGui import QFont, QPalette, QColor, QImage, QPixmap
from PySide6.QtCore import Qt, QTimer, QSize

class VideoFeedWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        # 16:9 Format als Mindestgröße (z.B. 640x360)
        self.label.setMinimumSize(640, 360)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        
        # OpenCV VideoCapture initialisieren (0 = Standardkamera)
        self.cap = cv2.VideoCapture(1)
        if not self.cap.isOpened():
            self.label.setText("Kamera konnte nicht geöffnet werden")
        
        # Timer für die Frame-Aktualisierung
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # ca. 30ms (33fps)
    
    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Umwandlung von BGR zu RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Erhalte Frame-Größe und berechne 16:9 Ausschnitt
            h, w, ch = frame.shape
            target_ratio = 16 / 9
            current_ratio = w / h
            if current_ratio > target_ratio:
                # zu breit, horizontal zuschneiden
                new_width = int(h * target_ratio)
                offset = (w - new_width) // 2
                frame = frame[:, offset:offset+new_width]
            elif current_ratio < target_ratio:
                # zu hoch, vertikal zuschneiden
                new_height = int(w / target_ratio)
                offset = (h - new_height) // 2
                frame = frame[offset:offset+new_height, :]
            
            # Erstelle QImage und passe an die Label-Größe an
            image = QImage(frame, frame.shape[1], frame.shape[0], 
                           frame.shape[1]*ch, QImage.Format_RGB888)
            # Skalierung unter Wahrung des Aspektverhältnisses
            pixmap = QPixmap.fromImage(image).scaled(
                self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label.setPixmap(pixmap)
    
    def closeEvent(self, event):
        if self.cap.isOpened():
            self.cap.release()
        event.accept()

class DashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Autonomes Fahrzeug - ÜLGEN")
        self.setMinimumSize(1000, 700)
        
        # Haupt-Container (Header + Hauptbereich)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_vlayout = QVBoxLayout(central_widget)
        
        # Header: Titel "ÜLGEN"
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 10, 10, 10)
        title_label = QLabel("ÜLGEN")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        header_layout.addWidget(title_label, alignment=Qt.AlignLeft)
        header.setStyleSheet("background-color: #222;")
        main_vlayout.addWidget(header)
        
        # Hauptbereich: Drei Spalten Layout
        main_layout = QHBoxLayout()
        main_vlayout.addLayout(main_layout)
        
        # Linkes Panel: Tacho / km/h-Anzeige
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        speed_title = QLabel("KM/H")
        speed_title.setAlignment(Qt.AlignCenter)
        speed_title.setFont(QFont("Arial", 16, QFont.Bold))
        speed_title.setStyleSheet("""
            background-color: #444;
            color: white;
            padding: 20px;
            border-radius: 5px;
        """)
        
        current_speed = QLabel("0")
        current_speed.setAlignment(Qt.AlignCenter)
        current_speed.setFont(QFont("Arial", 24, QFont.Bold))
        current_speed.setStyleSheet("""
            background-color: #222;
            color: #00FF00;
            padding: 20px;
            border-radius: 5px;
        """)
        
        left_layout.addWidget(speed_title)
        left_layout.addWidget(current_speed)
        left_layout.addStretch()
        
        # Mittleres Panel: Kameraansicht mit QStackedWidget
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(10, 10, 10, 10)
        
        self.camera_stack = QStackedWidget()
        
        # Normale Kamera (Echtzeitvideo via OpenCV)
        normal_cam_widget = VideoFeedWidget()
        
        # Thermalkamera (Platzhalter)
        thermal_cam = QFrame()
        thermal_cam.setStyleSheet("""
            background-color: #aa4444;
            border: 2px solid #330000;
            border-radius: 10px;
        """)
        thermal_cam.setMinimumSize(640, 360)
        
        # Spektralkamera (Platzhalter)
        spectrum_cam = QFrame()
        spectrum_cam.setStyleSheet("""
            background-color: #4444aa;
            border: 2px solid #000033;
            border-radius: 10px;
        """)
        spectrum_cam.setMinimumSize(640, 360)
        
        self.camera_stack.addWidget(normal_cam_widget)   # Index 0: Echtzeitvideo
        self.camera_stack.addWidget(thermal_cam)           # Index 1
        self.camera_stack.addWidget(spectrum_cam)            # Index 2
        
        center_layout.addWidget(self.camera_stack)
        
        # Button-Leiste für Kameraansichten
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        normal_button = QPushButton("Normale Kamera")
        thermal_button = QPushButton("Thermalkamera")
        spectrum_button = QPushButton("Spektralkamera")
        
        normal_button.clicked.connect(lambda: self.camera_stack.setCurrentIndex(0))
        thermal_button.clicked.connect(lambda: self.camera_stack.setCurrentIndex(1))
        spectrum_button.clicked.connect(lambda: self.camera_stack.setCurrentIndex(2))
        
        button_layout.addWidget(normal_button)
        button_layout.addWidget(thermal_button)
        button_layout.addWidget(spectrum_button)
        
        center_layout.addWidget(button_widget)
        
        # Rechtes Panel: Sensorwerte und Status
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        
        # Batteriestatus
        battery_title = QLabel("Batterie")
        battery_title.setAlignment(Qt.AlignCenter)
        battery_title.setFont(QFont("Arial", 14, QFont.Bold))
        battery_title.setStyleSheet("""
            background-color: #444;
            color: white;
            padding: 10px;
            border-radius: 5px;
        """)
        
        battery_value = QLabel("80%")
        battery_value.setAlignment(Qt.AlignCenter)
        battery_value.setFont(QFont("Arial", 20, QFont.Bold))
        battery_value.setStyleSheet("""
            background-color: #222;
            color: #FFD700;
            padding: 10px;
            border-radius: 5px;
        """)
        
        # Sensordaten (Beispiel: Lidar, Radar, Kamera)
        sensor_title = QLabel("Sensoren")
        sensor_title.setAlignment(Qt.AlignCenter)
        sensor_title.setFont(QFont("Arial", 14, QFont.Bold))
        sensor_title.setStyleSheet("""
            background-color: #444;
            color: white;
            padding: 10px;
            border-radius: 5px;
        """)
        
        sensor_value = QLabel("Lidar: OK\nRadar: OK\nKamera: OK")
        sensor_value.setAlignment(Qt.AlignCenter)
        sensor_value.setFont(QFont("Arial", 12))
        sensor_value.setStyleSheet("""
            background-color: #222;
            color: #FFF;
            padding: 10px;
            border-radius: 5px;
        """)
        
        # Magnetometer-Daten
        magnetometer_title = QLabel("Magnetometer")
        magnetometer_title.setAlignment(Qt.AlignCenter)
        magnetometer_title.setFont(QFont("Arial", 14, QFont.Bold))
        magnetometer_title.setStyleSheet("""
            background-color: #444;
            color: white;
            padding: 10px;
            border-radius: 5px;
        """)
        
        magnetometer_value = QLabel("X: 0.0\nY: 0.0\nZ: 0.0")
        magnetometer_value.setAlignment(Qt.AlignCenter)
        magnetometer_value.setFont(QFont("Arial", 12))
        magnetometer_value.setStyleSheet("""
            background-color: #222;
            color: #FFF;
            padding: 10px;
            border-radius: 5px;
        """)
        
        # Systemstatus
        system_title = QLabel("Systemstatus")
        system_title.setAlignment(Qt.AlignCenter)
        system_title.setFont(QFont("Arial", 14, QFont.Bold))
        system_title.setStyleSheet("""
            background-color: #444;
            color: white;
            padding: 10px;
            border-radius: 5px;
        """)
        
        system_value = QLabel("Alles in Ordnung")
        system_value.setAlignment(Qt.AlignCenter)
        system_value.setFont(QFont("Arial", 12))
        system_value.setStyleSheet("""
            background-color: #222;
            color: #0F0;
            padding: 10px;
            border-radius: 5px;
        """)
        
        # Hinzufügen der Widgets zum rechten Layout
        right_layout.addWidget(battery_title)
        right_layout.addWidget(battery_value)
        right_layout.addWidget(sensor_title)
        right_layout.addWidget(sensor_value)
        right_layout.addWidget(magnetometer_title)
        right_layout.addWidget(magnetometer_value)
        right_layout.addWidget(system_title)
        right_layout.addWidget(system_value)
        right_layout.addStretch()
        
        # Zusammenbau des Hauptlayouts
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(center_panel, 3)
        main_layout.addWidget(right_panel, 1)
        
        # Gesamtstil des Fensters
        self.setStyleSheet("""
            QMainWindow {
                background-color: #333;
            }
            QPushButton {
                padding: 10px;
                background-color: #555;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #777;
            }
        """)

def main():
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
