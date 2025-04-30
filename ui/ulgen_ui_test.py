import sys
import cv2
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
    QFrame
)
from PySide6.QtGui import QFont, QPixmap, QImage, QAction
from PySide6.QtCore import Qt, QTimer

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
        self.label.setMinimumSize(640, 360)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        self.cap = cv2.VideoCapture(0)   # Not: Raspberry Pi kamera için gerekirse 0,1 veya /dev/videoX yapılmalı.
        if not self.cap.isOpened():
            self.label.setText("Kamera açılmadı")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)
    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            image = QImage(frame, w, h, w*ch, QImage.Format_RGB888)
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
        self.setWindowTitle("ÜLGEN DASHBOARD")
        self.setMinimumSize(1400, 900)

        ### ANA LAYOUT BAŞLANGIÇ ###
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # ---------- SOL MENÜ ----------
        side_menu = QVBoxLayout()
        menu_widget = QWidget()
        menu_widget.setLayout(side_menu)
        menu_widget.setFixedWidth(80)
        menu_widget.setStyleSheet("background: #F6F7FB; border-right: 1px solid #e0e0e0;")
        side_menu.addStretch()
        side_menu.addWidget(make_icon_button("🧪", "#ffb300"))
        side_menu.addWidget(make_icon_button("🟦", "#616161"))
        side_menu.addWidget(make_icon_button("📡", "#8e24aa"))
        side_menu.addWidget(make_icon_button("🛞", "#0288d1"))
        side_menu.addStretch()
        power_btn = make_icon_button("🔋", "#ffb300")
        side_menu.addWidget(power_btn)
        side_menu.addSpacing(20)
        layout.addWidget(menu_widget)

        # ---------- ANA ORTA ALAN ----------
        main_area = QVBoxLayout()
        layout.addLayout(main_area)

        ### --- ÜST BAR: Sol başta başlık + Cast/casting bilgisi, ortada bilgi barı --- ###
        top_bar = QHBoxLayout()
        # Sol üst köşe: başlık + cast bilgisi
        cast_icon = QLabel("📡")
        cast_icon.setFont(QFont("Arial", 19))
        cast_label = QLabel("Raspberry Pi 5")
        cast_label.setFont(QFont("Arial", 10, QFont.Bold))
        cast_label.setStyleSheet("margin-left: 4px; color: #888;")
        logo_label = QLabel("<b>ÜLGEN</b>")
        logo_label.setFont(QFont("Arial", 22, QFont.Bold))
        logo_label.setStyleSheet("color:#ffb300; margin-left: 16px;")
        left = QVBoxLayout()
        top_title_row = QHBoxLayout()
        top_title_row.addWidget(cast_icon)
        top_title_row.addWidget(logo_label)
        left.addLayout(top_title_row)
        left.addWidget(cast_label)
        left.setAlignment(Qt.AlignLeft)
        top_bar.addLayout(left)
        top_bar.addSpacing(14)
        # ORTADA BİLGİ BAR
        nav_bar = QHBoxLayout()
        def info_box(icon, val, desc, color):
            l = QLabel(f"<span style='font-size:24px;'>{icon}</span> <span style='font-weight:bold;color:{color};font-size:18px'>{val}</span><br><span style='color:#888;font-size:11px;'>{desc}</span>")
            l.setFixedWidth(90)
            l.setStyleSheet("text-align:center;")
            return l
        nav_bar.addStretch()
        nav_bar.addWidget(info_box("🌡️","13%","Temp","#ffb300"))
        nav_bar.addSpacing(16)
        nav_bar.addWidget(info_box("🔋","73%","Battery","#43a047"))
        nav_bar.addSpacing(16)
        nav_bar.addWidget(info_box("🔄","45","Bearings","#f45b69"))
        nav_bar.addSpacing(16)
        nav_bar.addWidget(info_box("🛞","2500","Torque","#ab47bc"))
        nav_bar.addSpacing(16)
        nav_bar.addWidget(info_box("⚡","10W","Watt","#1976d2"))
        nav_bar.addStretch()
        top_bar.addLayout(nav_bar)
        # Sağ boşluk
        top_bar.addStretch()
        main_area.addLayout(top_bar)
        main_area.addSpacing(12)

        # -- ORTADA ANA GRID ALAN (3 KART: Sol - Orta - Sağ) --
        grid = QGridLayout()
        grid.setHorizontalSpacing(32)
        grid.setVerticalSpacing(18)

        # SOL: Canlı video + status
        video_card = QFrame()
        video_card.setStyleSheet("""
            background: #fff;
            border-radius: 18px;
            border: 2px solid #f5f5f8;
        """)
        video_layout = QVBoxLayout(video_card)
        video_status = QLabel("System idle - Waiting for processing command")
        video_status.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        video_status.setFont(QFont("Arial", 11))
        self.video_widget = VideoFeedWidget()
        video_layout.addWidget(self.video_widget)
        video_layout.addWidget(video_status)
        grid.addWidget(video_card, 0, 0, 2, 1)

        # ORTA: İşlem/Görev Info
        middle_card = QFrame()
        middle_card.setStyleSheet("background:#fff;border-radius:18px;border:2px solid #f5f5f8;")
        middle_layout = QVBoxLayout(middle_card)
        middle_layout.setSpacing(8)
        check_label = QLabel("<b>Check data</b><br><small style='color:#757575;'>Image Processing</small>")
        check_label.setFont(QFont("Arial", 15, QFont.Bold))
        check_label.setStyleSheet("color:#232323;")
        accuracy_label = QLabel("Accuracy Rate")
        accuracy_label.setFont(QFont("Arial", 12))
        acc_gauge = QLabel("10%")  # ilerisi gauge olabilir
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

        # ALT ORTA: Datasets (örnek)
        datasets_card = QFrame()
        datasets_card.setStyleSheet("background:#fff; border-radius:18px; border:2px solid #f5f5f8;")
        dataset_layout = QVBoxLayout(datasets_card)
        dataset_layout.setAlignment(Qt.AlignTop)
        dataset_layout.addWidget(QLabel("DATASETS<br><b>Mode:</b> Performance<br><b>Intake:</b> Neutral<br><b>Frequency:</b> 10.7Hz"))
        srcs_card = QFrame()
        srcs_card.setStyleSheet("background:#f5f5fa; border-radius:18px;")
        srcs_layout = QHBoxLayout(srcs_card)
        srcs_layout.addWidget(QLabel("SOURCES<br><b>ACTIVE</b>"))
        dataset_layout.addWidget(srcs_card)
        grid.addWidget(datasets_card, 1, 1)

        # SAĞ: Analyze Card --- GÜNCELLEME BURADA YAPILDI ------
        analyze_card = QFrame()
        analyze_card.setStyleSheet("background:#fff; border-radius:18px; border:2px solid #f5f5f8;")
        analyze_layout = QVBoxLayout(analyze_card)
        preview_img = QLabel()
        preview_img.setPixmap(QPixmap(320, 160))
        preview_img.setStyleSheet("background:#ebeefb; border-radius:8px;")
        preview_img.setFixedHeight(160)
        analyze_layout.addWidget(preview_img)
        # YENİ: Sadece simgeli butonlar!
        eject_btn = QPushButton("⏏ Eject")
        upload_btn = QPushButton("⏫ Upload")
        cnn_btn = QPushButton("🔎 CNN")
        settings_btn = QPushButton("⚙")
        analyze_btn = QPushButton(f"▶  Analyze Image")
        # gradient stilleri
        eject_btn.setStyleSheet("""
        QPushButton {
            background: linear-gradient(90deg, #d500f9, #448aff);
            color: white; border-radius:8px; font-weight: bold;padding:13px;
        }
        """)
        upload_btn.setStyleSheet("""
        QPushButton {
            background: #ede7f6;
            color: #8e24aa; border-radius:8px; font-weight:bold;padding:8px 26px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c4dff, stop:1 #536dfe);
            color:white;
        }
        """)
        cnn_btn.setStyleSheet("""
        QPushButton {
            background: #ede7f6;
            color: #1a237e; border-radius:8px; font-weight:bold;padding:8px 26px;
        }
        QPushButton:hover {
            background: qlineargradient(x1::0, y1:0, x2:1, y2:0, stop:0 #00897b, stop:1 #43a047);
            color:white;
        }
        """)
        settings_btn.setStyleSheet("""
        QPushButton {
            background: #ede7f6;
            color: #757575; border-radius:8px; font-weight:bold;padding:8px 22px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ffd600, stop:1 #ffc107);
            color:#424242;
        }
        """)
        analyze_btn.setStyleSheet("""
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #d500f9, stop:1 #2979ff);
            color: white; border-radius:8px; font-weight: bold; padding:14px 28px;
            font-size: 16px;
            margin-top:12px;
            margin-bottom:8px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2979ff, stop:1 #d500f9);
        }
        """)

        btn_bar = QHBoxLayout()
        btn_bar.addWidget(upload_btn)
        btn_bar.addWidget(cnn_btn)
        btn_bar.addWidget(settings_btn)
        analyze_layout.addWidget(eject_btn)
        analyze_layout.addLayout(btn_bar)
        analyze_layout.addWidget(analyze_btn)
        grid.addWidget(analyze_card, 0, 2, 2, 1)

        # --- GRID ANA ALANA EKLENİYOR ---
        main_area.addLayout(grid)
        main_area.addStretch()

        # --- ALT BİLDİRİM BAR ---
        issue_card = QFrame()
        issue_card.setStyleSheet("background:qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff8373, stop:1 #ffd600); color:white; border-radius:13px;")
        issue_card.setFixedHeight(36)
        issue_label = QLabel("1 Issue")
        issue_label.setFont(QFont("Arial", 12, QFont.Bold))
        issue_card_layout = QHBoxLayout(issue_card)
        issue_card_layout.addWidget(issue_label)
        issue_card_layout.addSpacing(10)
        issue_card_layout.addWidget(QLabel("❌"))
        main_area.addWidget(issue_card)

        # --- GENEL PENCERE ARKAPLAN STİLİ ---
        self.setStyleSheet("""
            QMainWindow { background: #F6F7FB; }
            QLabel { color: #111; }
            QPushButton {
                font-weight: bold;
                border: none;
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UlgenDashboard()
    window.show()
    sys.exit(app.exec())