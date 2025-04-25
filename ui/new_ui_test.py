import sys
import cv2
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
    QFrame, QStackedWidget, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QFont, QPixmap, QIcon, QImage
from PySide6.QtCore import Qt, QTimer, QSize

# --- Mevcut VideoFeedWidget ve DashboardWindow iç komponentleri aynen korunacak --- 

# Dikey yan menü bar simgeleri (örnek olarak unicode veya svg ile)
def make_icon_button(icon_text, color="black"):
    btn = QPushButton(icon_text)
    btn.setFont(QFont("Arial", 20, QFont.Bold))
    btn.setFixedSize(48, 48)
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #fff;
            color: {color};
            border-radius: 16px;
            border: none;
        }}
        QPushButton:hover {{
            background-color: #ffe082;
        }}
    """)
    return btn

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

class UlgenDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ULGEN UI")
        self.setMinimumSize(1400, 900)

        # ---------- Ana Kapsayıcı ----------
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # ---------- Sol Menü ----------
        side_menu = QVBoxLayout()
        menu_widget = QWidget()
        menu_widget.setLayout(side_menu)
        menu_widget.setFixedWidth(80)
        menu_widget.setStyleSheet("background: #F6F7FB;")

        # Menü İkonları (Örnek: Unicode, SVG ile de yapılabilir)
        side_menu.addStretch()
        side_menu.addWidget(make_icon_button("🧪", "#ffb300"))  # Science/Experiment
        side_menu.addWidget(make_icon_button("🟦", "#616161"))  # Cube
        side_menu.addWidget(make_icon_button("📡", "#8e24aa"))  # Antenna
        side_menu.addWidget(make_icon_button("🛞", "#0288d1"))  # Wheel
        side_menu.addStretch()
        power_btn = make_icon_button("🔋", "#ffb300")
        side_menu.addWidget(power_btn)
        side_menu.addSpacing(20)

        layout.addWidget(menu_widget)

        # ---------- Ana Orta Alan ----------
        main_area = QVBoxLayout()
        layout.addLayout(main_area)

        # ÜST BAR (durum, pil, sıcaklık vs.)
        topbar = QHBoxLayout()
        hi_label = QLabel("Welcome to, <span style='color:#ffb300;font-weight:bold'>ULGEN</span>")
        hi_label.setFont(QFont("Arial", 20, QFont.Bold))
        hi_label.setStyleSheet("color: #232323;")
        topbar.addWidget(hi_label)
        topbar.addSpacing(25)

        # Topbar Iconlar/bilgiler
        status_icons = QHBoxLayout()
        def info_label(icon, text, color="#2d3748", subtext=""):
            lbl = QLabel(f"<span style='font-size:24px'>{icon}</span> <b style='color:{color}'>{text}</b> <small>{subtext}</small>")
            lbl.setFont(QFont("Arial", 13))
            return lbl
        
        status_icons.addWidget(info_label("🌡️", "13%", "#ffb300", "+2.05%"))
        status_icons.addSpacing(10)
        status_icons.addWidget(info_label("🔄", "45", "#f45b69"))  # Bearings
        status_icons.addSpacing(10)
        status_icons.addWidget(info_label("🔋", "", "#5c6bc0"))
        status_icons.addSpacing(10)
        status_icons.addWidget(info_label("🛞", "TQ: <span style='color:#ab47bc'>2500</span>", "#ab47bc"))
        status_icons.addSpacing(10)
        status_icons.addWidget(info_label("⚡", "W: 10", "#fbc02d"))
        
        status_icons.addSpacing(20)
        topbar.addLayout(status_icons)
        topbar.addStretch()
        main_area.addLayout(topbar)

        main_area.addSpacing(10)

        # ------------- Orta Grid Alan -------------
        grid = QGridLayout()
        grid.setHorizontalSpacing(32)
        grid.setVerticalSpacing(18)

        # --- Sol: Canlı Video ve Durum ---
        video_card = QFrame()
        video_card.setStyleSheet("""
            background: #fff;
            border-radius: 18px;
            border: 2px solid #f5f5f8;
        """)
        video_layout = QVBoxLayout(video_card)
        video_label = QLabel("System idle - Waiting for processing command")
        video_label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        video_label.setFont(QFont("Arial", 11))
        # burada mevcut video widget'ı yerine yerleştir
        self.video_widget = VideoFeedWidget()
        video_layout.addWidget(self.video_widget)
        video_layout.addWidget(video_label)
        grid.addWidget(video_card, 0, 0, 2, 1)

        # --- Orta: İşlem / Görev Bilgi Alanı ---
        middle_card = QFrame()
        middle_card.setStyleSheet("background:#fff;border-radius:18px;border:2px solid #f5f5f8;")
        middle_layout = QVBoxLayout(middle_card)
        middle_layout.setSpacing(16)

        # Check Data KONTEYNERİ
        check_label = QLabel("Check data<br><small style='color:#757575;'>Image Processing</small>")
        check_label.setFont(QFont("Arial", 15, QFont.Bold))
        check_label.setStyleSheet("color:#232323;")
        accuracy_label = QLabel("Accuracy Rate")
        accuracy_label.setFont(QFont("Arial", 12))
        acc_gauge = QLabel("10%")  # burada basit text, ileride gauge grafik yapılabilir.

        current_task = QLabel("Current Task: <b>none</b>")
        current_task.setFont(QFont("Arial", 11))
        current_task.setStyleSheet("color: #616161;")
        epoch_label = QLabel("Epocs Available: <b style='color:#ab47bc'>false</b>")

        middle_layout.addWidget(check_label)
        middle_layout.addWidget(accuracy_label)
        middle_layout.addWidget(acc_gauge)
        middle_layout.addWidget(current_task)
        middle_layout.addWidget(epoch_label)
        middle_layout.addStretch()
        grid.addWidget(middle_card, 0, 1)

        # Dataset & Sources [Alt Orta]
        datasets_card = QFrame()
        datasets_card.setStyleSheet("background:#fff; border-radius:18px; border:2px solid #f5f5f8;")
        dataset_layout = QVBoxLayout(datasets_card)
        dataset_layout.setAlignment(Qt.AlignTop)
        dataset_layout.addWidget(QLabel("DATASETS<br><b>Mode:</b> Performance<br><b>Intake:</b> Neutral<br><b>Frequency:</b> 10.7Hz"))

        # SOURCES KARTI (ikon çizimi burada gösterilmeyecek)
        srcs_card = QFrame()
        srcs_card.setStyleSheet("background:#f5f5fa; border-radius:18px;")
        srcs_layout = QHBoxLayout(srcs_card)
        srcs_layout.addWidget(QLabel("SOURCES<br><b>ACTIVE</b>"))

        dataset_layout.addWidget(srcs_card)
        grid.addWidget(datasets_card, 1, 1)

        # --- Sağ: Analiz Kartı ve Kamera/Sensör Kartları ---
        analyze_card = QFrame()
        analyze_card.setStyleSheet("background:#fff; border-radius:18px; border:2px solid #f5f5f8;")
        analyze_layout = QVBoxLayout(analyze_card)

        preview_img = QLabel()
        preview_img.setPixmap(QPixmap(320, 160))
        preview_img.setStyleSheet("background:#ebeefb; border-radius:8px;")
        preview_img.setFixedHeight(160)
        analyze_layout.addWidget(preview_img)

        img_url_box = QPushButton("Paste image URL or chc")
        eject_btn = QPushButton("Eject")
        eject_btn.setStyleSheet("background:#c7bfff; color:white; border-radius:8px;")
        analyze_layout.addWidget(img_url_box)
        analyze_layout.addWidget(eject_btn)

        btn_bar = QHBoxLayout()
        btn_bar.addWidget(QPushButton("Upload"))
        btn_bar.addWidget(QPushButton("CNN"))
        btn_bar.addWidget(QPushButton("Sample 2"))
        analyze_layout.addLayout(btn_bar)

        analyze_layout.addWidget(QPushButton("Analyze Image"))
        grid.addWidget(analyze_card, 0, 2, 2, 1)

        # Grid'i ana alana yerleştir
        main_area.addLayout(grid)

        main_area.addStretch()

        # Alt hata bildirimi gibi (opsiyonel)
        issue_card = QFrame()
        issue_card.setStyleSheet("background:#ff8373; color:white; border-radius:13px;")
        issue_card.setFixedHeight(36)
        issue_label = QLabel("1 Issue")
        issue_label.setFont(QFont("Arial", 12, QFont.Bold))
        issue_card_layout = QHBoxLayout(issue_card)
        issue_card_layout.addWidget(issue_label)
        issue_card_layout.addSpacing(10)
        issue_card_layout.addWidget(QLabel("❌"))
        main_area.addWidget(issue_card)

        # Genel pencere arka planı
        self.setStyleSheet("""
            QMainWindow { background: #F6F7FB; }
            QLabel { color: #111; }
            QPushButton {
                padding: 8px 18px;
                background-color: #ede7f6;
                color: #1a237e;
                font-weight: bold;
            }
        """)

        # Eğer sensör/kamera alt komponentleri varsa, bunlar analyze_card veya datasets_card içine grid ile gömülebilir!
        # Orijinal kodundaki sensor/camera iç komponentleri buraya ekle **kopyala**.

# ------------- Ana kod bloğuna yönlendir -------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UlgenDashboard()
    window.show()
    sys.exit(app.exec())