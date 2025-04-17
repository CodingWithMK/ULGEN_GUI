import sys
import cv2
import random  # zum Simulieren von Sensordaten
import serial  # pip install pyserial

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QHBoxLayout, QVBoxLayout, QFrame, QStackedWidget
)
from PySide6.QtGui import QFont, QPalette, QColor, QImage, QPixmap
from PySide6.QtCore import Qt, QTimer, QSize

# Widget für den Live-Videofeed (16:9 Format) über OpenCV
class VideoFeedWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        # Mindestgröße im 16:9 Format, z. B. 640x360
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
        self.timer.start(30)  # ca. 30 ms -> ca. 33 fps

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # BGR zu RGB konvertieren
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            target_ratio = 16 / 9
            current_ratio = w / h
            if current_ratio > target_ratio:
                # Zu breit: horizontal zuschneiden
                new_width = int(h * target_ratio)
                offset = (w - new_width) // 2
                frame = frame[:, offset:offset + new_width]
            elif current_ratio < target_ratio:
                # Zu hoch: vertikal zuschneiden
                new_height = int(w / target_ratio)
                offset = (h - new_height) // 2
                frame = frame[offset:offset + new_height, :]
            
            image = QImage(frame, frame.shape[1], frame.shape[0],
                           frame.shape[1]*ch, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image).scaled(
                self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label.setPixmap(pixmap)

    def closeEvent(self, event):
        if self.cap.isOpened():
            self.cap.release()
        event.accept()

# Hauptfenster-Dashboard
class DashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Autonomes Fahrzeug - ÜLGEN")
        self.setMinimumSize(1200, 800)
        
        # Versuche, den UART-Port zu öffnen (angepasster Port, evtl. '/dev/ttyS0' auf dem Raspberry Pi)
        try:
            self.uart = serial.Serial('/dev/ttyS0', 9600, timeout=1)
        except Exception as e:
            print("UART konnte nicht geöffnet werden:", e)
            self.uart = None

        # Hauptcontainer: vertikales Layout (Header, Hauptbereich, Steuerung)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_vlayout = QVBoxLayout(central_widget)
        
        # -----------------------------
        # Header mit Titel "ÜLGEN"
        # -----------------------------
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 10, 10, 10)
        title_label = QLabel("ÜLGEN")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        header_layout.addWidget(title_label, alignment=Qt.AlignLeft)
        header.setStyleSheet("background-color: #222;")
        main_vlayout.addWidget(header)
        
        # -----------------------------
        # Hauptbereich: Drei Spalten Layout
        # (Links: Tacho, Mitte: Kameras, Rechts: Sensoren & UART)
        # -----------------------------
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
        
        self.current_speed = QLabel("0")
        self.current_speed.setAlignment(Qt.AlignCenter)
        self.current_speed.setFont(QFont("Arial", 24, QFont.Bold))
        self.current_speed.setStyleSheet("""
            background-color: #222;
            color: #00FF00;
            padding: 20px;
            border-radius: 5px;
        """)
        
        left_layout.addWidget(speed_title)
        left_layout.addWidget(self.current_speed)
        left_layout.addStretch()
        
        # Mittleres Panel: Kameraansichten (QStackedWidget)
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
        
        self.camera_stack.addWidget(normal_cam_widget)   # Index 0
        self.camera_stack.addWidget(thermal_cam)           # Index 1
        self.camera_stack.addWidget(spectrum_cam)            # Index 2
        
        center_layout.addWidget(self.camera_stack)
        
        # Buttons zur Kameraumschaltung
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
        
        # Rechtes Panel: Sensoren, UART, Motor, Gyro, etc.
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
        
        # Allgemeine Sensordaten (z.B. Lidar, Radar, Kamera)
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
        
        # Gyrosensor-Daten (neu)
        gyro_title = QLabel("Gyrosensor")
        gyro_title.setAlignment(Qt.AlignCenter)
        gyro_title.setFont(QFont("Arial", 14, QFont.Bold))
        gyro_title.setStyleSheet("""
            background-color: #444;
            color: white;
            padding: 10px;
            border-radius: 5px;
        """)
        gyro_value = QLabel("X: 0.0\nY: 0.0\nZ: 0.0")
        gyro_value.setAlignment(Qt.AlignCenter)
        gyro_value.setFont(QFont("Arial", 12))
        gyro_value.setStyleSheet("""
            background-color: #222;
            color: #FFF;
            padding: 10px;
            border-radius: 5px;
        """)
        
        # Motorstatus (als Beispiel)
        motor_title = QLabel("Motorstatus")
        motor_title.setAlignment(Qt.AlignCenter)
        motor_title.setFont(QFont("Arial", 14, QFont.Bold))
        motor_title.setStyleSheet("""
            background-color: #444;
            color: white;
            padding: 10px;
            border-radius: 5px;
        """)
        motor_value = QLabel("Leerlauf")
        motor_value.setAlignment(Qt.AlignCenter)
        motor_value.setFont(QFont("Arial", 12))
        motor_value.setStyleSheet("""
            background-color: #222;
            color: #FFF;
            padding: 10px;
            border-radius: 5px;
        """)
        
        # UART-Daten (Daten vom Raspberry Pi per UART)
        uart_title = QLabel("UART-Daten")
        uart_title.setAlignment(Qt.AlignCenter)
        uart_title.setFont(QFont("Arial", 14, QFont.Bold))
        uart_title.setStyleSheet("""
            background-color: #444;
            color: white;
            padding: 10px;
            border-radius: 5px;
        """)
        self.uart_value = QLabel("Keine Daten")
        self.uart_value.setAlignment(Qt.AlignCenter)
        self.uart_value.setFont(QFont("Arial", 12))
        self.uart_value.setStyleSheet("""
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

        # Widgets zum rechten Layout hinzufügen
        right_layout.addWidget(battery_title)
        right_layout.addWidget(battery_value)
        right_layout.addWidget(sensor_title)
        right_layout.addWidget(sensor_value)
        right_layout.addWidget(magnetometer_title)
        right_layout.addWidget(magnetometer_value)
        right_layout.addWidget(gyro_title)
        right_layout.addWidget(gyro_value)
        right_layout.addWidget(motor_title)
        right_layout.addWidget(motor_value)
        right_layout.addWidget(uart_title)
        right_layout.addWidget(self.uart_value)
        right_layout.addWidget(system_title)
        right_layout.addWidget(system_value)
        right_layout.addStretch()
        
        # Hinzufügen der drei Panels in das Hauptlayout
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(center_panel, 3)
        main_layout.addWidget(right_panel, 1)
        
        # -----------------------------
        # Steuerungsbereich: Pfeiltasten (Touchscreen-optimiert)
        # -----------------------------
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(10, 10, 10, 10)
        
        forward_button = QPushButton("▲")
        backward_button = QPushButton("▼")
        forward_button.setFont(QFont("Arial", 24, QFont.Bold))
        backward_button.setFont(QFont("Arial", 24, QFont.Bold))
        forward_button.setMinimumSize(QSize(100, 100))
        backward_button.setMinimumSize(QSize(100, 100))
        
        # Beispielhafte Klick-Handler (diese sollten mit der Fahrzeugsteuerung verbunden werden)
        forward_button.clicked.connect(lambda: print("Fahrzeug vorwärts"))
        backward_button.clicked.connect(lambda: print("Fahrzeug rückwärts"))
        
        control_layout.addWidget(forward_button)
        control_layout.addWidget(backward_button)
        main_vlayout.addWidget(control_panel)
        
        # Gesamtstil für das Fenster
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
        
        # Timer für die Aktualisierung von UART & Sensor-Daten
        self.data_timer = QTimer(self)
        self.data_timer.timeout.connect(lambda: self.update_sensor_data(gyro_value, motor_value))
        self.data_timer.start(500)  # alle 500ms
        
        # Timer zum Lesen der UART-Daten
        self.uart_timer = QTimer(self)
        self.uart_timer.timeout.connect(self.read_uart_data)
        self.uart_timer.start(500)

    def update_sensor_data(self, gyro_widget, motor_widget):
        # Hier simulieren wir beispielhafte Sensordaten.
        # Diese Funktion könntest du anpassen, um echte Sensordaten (z.B. über I2C, SPI etc.)
        # auszulesen.
        # Gyrosensor: Dummywerte
        gyro_x = round(random.uniform(-180, 180), 2)
        gyro_y = round(random.uniform(-180, 180), 2)
        gyro_z = round(random.uniform(-180, 180), 2)
        gyro_widget.setText(f"X: {gyro_x}\nY: {gyro_y}\nZ: {gyro_z}")
        
        # Motorstatus: Simuliere Wechsel zwischen "Leerlauf" und "Fahren"
        motor_status = random.choice(["Leerlauf", "Fahren"])
        motor_widget.setText(motor_status)
        
        # Zusätzlich kannst du hier auch andere Sensordaten (Geschwindigkeit, Batterie, etc.) aktualisieren.
        # Beispiel: Geschwindigkeit erhöhen/senken (dummy)
        current_speed = int(self.current_speed.text() or 0)
        current_speed = (current_speed + random.randint(-3, 3)) % 200
        self.current_speed.setText(str(current_speed))
    
    def read_uart_data(self):
        # Lies Daten vom UART-Port (falls verfügbar)
        if self.uart is not None and self.uart.in_waiting:
            try:
                # Lese eine Zeile von UART
                line = self.uart.readline().decode('utf-8').strip()
                self.uart_value.setText(line)
            except Exception as e:
                self.uart_value.setText("UART Fehler")
        else:
            # Simuliere hier Dummy-Daten, falls kein UART-Datenstrom vorliegt
            dummy_data = f"Dummy: {random.randint(0, 100)}"
            self.uart_value.setText(dummy_data)
    
    def closeEvent(self, event):
        if self.uart and self.uart.is_open:
            self.uart.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()