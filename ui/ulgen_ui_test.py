import sys
import cv2
import platform
import math
import random
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
    QFrame, QSizePolicy, QScrollArea, QMenu, QStackedWidget, QLCDNumber, QDial, QProgressBar,
    QComboBox
)
from PySide6.QtGui import QFont, QPixmap, QImage, QPalette, QColor, QAction, QCursor, QPainter, QPen, QBrush, QRadialGradient
from PySide6.QtCore import Qt, QTimer, QSize, QRect, QSettings, QPoint

class ThemeManager:
    """Tema yönetimi için sınıf"""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"
    
    def __init__(self):
        self.settings = QSettings("ULGEN", "Dashboard")
        self.current_theme = self.settings.value("theme", self.SYSTEM)
        
    def get_theme(self):
        """Mevcut temayı döndürür"""
        if self.current_theme == self.SYSTEM:
            # Sistem temasını kontrol et
            palette = QApplication.palette()
            if palette.color(QPalette.Window).lightness() < 128:
                return self.DARK
            return self.LIGHT
        return self.current_theme
    
    def set_theme(self, theme):
        """Temayı ayarlar ve kaydeder"""
        self.current_theme = theme
        self.settings.setValue("theme", theme)
    
    def get_colors(self, platform_name):
        """Mevcut tema ve platforma göre renkleri döndürür"""
        theme = self.get_theme()
        
        if theme == self.DARK:
            # Koyu tema renkleri
            return {
                "bg_color": "#212121",
                "card_color": "#2D2D2D",
                "card_border": "#3D3D3D",
                "text_color": "#E0E0E0",
                "text_secondary": "#9E9E9E",
                "primary_color": "#FFB300",
                "accent_color": "#BA68C8",
                "gray_color": "#9E9E9E",
                "success_color": "#66BB6A",
                "warning_color": "#FFA726",
                "danger_color": "#EF5350",
                "info_color": "#42A5F5",
                "preview_bg": "#212121"  # Önizleme arka planı
            }
        else:
            # Açık tema renkleri - işletim sistemine göre hafif farklılıklar
            if platform_name == "Darwin":  # macOS
                return {
                    "bg_color": "#F6F6F6",
                    "card_color": "#FFFFFF",
                    "card_border": "#E5E5E5",
                    "text_color": "#333333",
                    "text_secondary": "#757575",
                    "primary_color": "#FFB300",
                    "accent_color": "#AB47BC",
                    "gray_color": "#757575",
                    "success_color": "#43A047",
                    "warning_color": "#FB8C00",
                    "danger_color": "#E53935",
                    "info_color": "#1E88E5",
                    "preview_bg": "#ebeefb"  # Önizleme arka planı
                }
            elif platform_name == "Windows":
                return {
                    "bg_color": "#F0F0F0",
                    "card_color": "#FFFFFF",
                    "card_border": "#E0E0E0",
                    "text_color": "#333333",
                    "text_secondary": "#757575",
                    "primary_color": "#FFB300",
                    "accent_color": "#AB47BC",
                    "gray_color": "#757575",
                    "success_color": "#43A047",
                    "warning_color": "#FB8C00",
                    "danger_color": "#E53935",
                    "info_color": "#1E88E5",
                    "preview_bg": "#ebeefb"  # Önizleme arka planı
                }
            else:  # Linux ve diğerleri
                return {
                    "bg_color": "#F5F5F5",
                    "card_color": "#FFFFFF",
                    "card_border": "#DDDDDD",
                    "text_color": "#333333",
                    "text_secondary": "#757575",
                    "primary_color": "#FFB300",
                    "accent_color": "#AB47BC",
                    "gray_color": "#757575",
                    "success_color": "#43A047",
                    "warning_color": "#FB8C00",
                    "danger_color": "#E53935",
                    "info_color": "#1E88E5",
                    "preview_bg": "#ebeefb"  # Önizleme arka planı
                }

class VideoFeedWidget(QWidget):
    def __init__(self, parent=None, bg_color="#FFFFFF"):
        super().__init__(parent)
        self.bg_color = bg_color
        self.camera_source = 0  # Varsayılan kamera
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Kamera seçim menüsü oluştur
        self.toolbar = QHBoxLayout()
        self.camera_selector = QComboBox()
        self.camera_selector.addItem("Araç Kamerası", 0)
        self.camera_selector.addItem("Dron Kamerası", 1)
        self.camera_selector.setStyleSheet(f"""
            QComboBox {{
                background: {bg_color};
                color: #333;
                padding: 4px;
                border-radius: 4px;
                border: 1px solid #ccc;
            }}
        """)
        self.camera_selector.currentIndexChanged.connect(self.change_camera)
        
        self.toolbar.addWidget(QLabel("Kamera:"))
        self.toolbar.addWidget(self.camera_selector)
        self.toolbar.addStretch()
        
        # Video etiketi
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMinimumSize(320, 180)
        self.label.setStyleSheet(f"background-color: {self.bg_color};")
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.layout.addLayout(self.toolbar)
        self.layout.addWidget(self.label)
        
        # OpenCV video yakalama
        self.cap = cv2.VideoCapture()
        if not self.cap.isOpened():
            self.label.setText("Unable to open camera.")
            
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)
        
    def change_camera(self, index):
        """Kamera kaynağını değiştirir"""
        camera_id = self.camera_selector.currentData()
        
        if self.cap.isOpened():
            self.cap.release()
            
        self.cap = cv2.VideoCapture(camera_id)
        if not self.cap.isOpened():
            self.label.setText(f"Unable to open camera source: {camera_id}")
    
    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            image = QImage(frame, w, h, w*ch, QImage.Format_RGB888)
            
            pixmap = QPixmap.fromImage(image).scaled(
                self.label.width(), self.label.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
            self.label.setPixmap(pixmap)
            
    def closeEvent(self, event):
        if self.cap.isOpened():
            self.cap.release()
        event.accept()
        
    def set_bg_color(self, color):
        """Video arka plan rengini günceller"""
        self.bg_color = color
        self.label.setStyleSheet(f"background-color: {self.bg_color};")
        self.camera_selector.setStyleSheet(f"""
            QComboBox {{
                background: {color};
                color: #333;
                padding: 4px;
                border-radius: 4px;
                border: 1px solid #ccc;
            }}
        """)

class ArtificialHorizon(QWidget):
    """Dron için yapay ufuk göstergesi"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self.roll = 0
        self.pitch = 0
        
        # Örnek veri güncelleme zamanlayıcısı
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_values)
        self.timer.start(100)  # 100ms'de bir güncelle
        
    def update_values(self):
        """Simüle edilmiş değerlerle ufuk çizgisini günceller"""
        # Gerçek sistemde WebSocket veya benzeri bir teknoloji ile drondan veri alınır
        self.roll += random.uniform(-1, 1)
        self.pitch += random.uniform(-0.5, 0.5)
        
        # Değerleri sınırla
        self.roll = max(min(self.roll, 30), -30)  # -30 ile 30 derece arası
        self.pitch = max(min(self.pitch, 15), -15)  # -15 ile 15 derece arası
        
        self.update()
        
    def paintEvent(self, event):
        """Yapay ufuk çizimi"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2 - 10
        
        # Arka plan gradient (gökyüzü ve yer)
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(-self.roll)
        
        # Gökyüzü (mavi)
        sky_rect = QRect(-radius, -radius - self.pitch * 5, radius * 2, radius * 2)
        sky_gradient = QRadialGradient(0, 0, radius * 2)
        sky_gradient.setColorAt(0, QColor(135, 206, 250))  # Açık mavi
        sky_gradient.setColorAt(1, QColor(0, 0, 139))  # Koyu mavi
        painter.setBrush(QBrush(sky_gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRect(sky_rect)
        
        # Yer (kahverengi)
        ground_rect = QRect(-radius, 0 - self.pitch * 5, radius * 2, radius * 2)
        ground_gradient = QRadialGradient(0, 0, radius * 2)
        ground_gradient.setColorAt(0, QColor(139, 69, 19))  # Açık kahverengi
        ground_gradient.setColorAt(1, QColor(101, 67, 33))  # Koyu kahverengi
        painter.setBrush(QBrush(ground_gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRect(ground_rect)
        
        # Ufuk çizgisi
        painter.setPen(QPen(Qt.white, 2))
        painter.drawLine(-radius, -self.pitch * 5, radius, -self.pitch * 5)
        
        painter.restore()
        
        # Dış çerçeve
        painter.setPen(QPen(Qt.gray, 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QPoint(center_x, center_y), radius, radius)
        
        # Merkez uçak göstergesi
        painter.setPen(QPen(Qt.yellow, 2))
        painter.drawLine(center_x - 20, center_y, center_x + 20, center_y)
        painter.drawLine(center_x, center_y - 5, center_x, center_y + 5)
        painter.drawLine(center_x - 5, center_y + 10, center_x + 5, center_y + 10)

class ClimbIndicator(QWidget):
    """Tırmanma hızı göstergesi"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(120, 200)
        self.climb_rate = 0  # ft/min
        
        # Örnek veri güncelleme zamanlayıcısı
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_values)
        self.timer.start(200)  # 200ms'de bir güncelle
        
    def update_values(self):
        """Simüle edilmiş değerlerle tırmanma hızını günceller"""
        self.climb_rate = random.uniform(-800, 800)  # -800 ile 800 ft/min arası
        self.update()
        
    def paintEvent(self, event):
        """Tırmanma hızı göstergesini çizer"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2 - 10
        
        # Arka plan
        painter.setBrush(QBrush(Qt.black))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPoint(center_x, center_y), radius, radius)
        
        # Rakamlar ve çizgiler
        painter.setPen(QPen(Qt.white, 1))
        painter.setFont(QFont("Arial", 8))
        
        # Çizgiler ve rakamlar
        for i in range(9):
            angle = (i - 4) * 30
            x1 = center_x + radius * 0.8 * math.sin(math.radians(angle))
            y1 = center_y - radius * 0.8 * math.cos(math.radians(angle))
            x2 = center_x + radius * 0.9 * math.sin(math.radians(angle))
            y2 = center_y - radius * 0.9 * math.cos(math.radians(angle))
            
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
            
            # Rakamlar
            value = (i - 4) * 2
            text = str(value)
            text_width = painter.fontMetrics().horizontalAdvance(text)
            text_x = center_x + radius * 0.7 * math.sin(math.radians(angle)) - text_width / 2
            text_y = center_y - radius * 0.7 * math.cos(math.radians(angle)) + 4
            painter.drawText(int(text_x), int(text_y), text)
        
        # Orta yazı
        painter.setFont(QFont("Arial", 8, QFont.Bold))
        painter.drawText(center_x - 20, center_y - radius * 0.3, "CLIMB")
        painter.drawText(center_x - 30, center_y - radius * 0.15, "1000 FT PER MINUTE")
        
        # İbre
        painter.save()
        angle = self.climb_rate / 1000.0 * 120  # 1000 ft/min = 60 derece
        angle = max(min(angle, 120), -120)  # -120 ile 120 derece arası sınırla
        
        painter.translate(center_x, center_y)
        painter.rotate(-angle)
        
        painter.setPen(QPen(Qt.white, 2))
        painter.drawLine(0, 0, 0, -radius * 0.8)
        
        painter.restore()
        
        # Dış çerçeve
        painter.setPen(QPen(Qt.gray, 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QPoint(center_x, center_y), radius, radius)

def make_icon_button(icon_text, color="white", bg_color="#333333"):
    btn = QPushButton(icon_text)
    btn.setFont(QFont("Arial", 20, QFont.Bold))
    btn.setFixedSize(48, 48)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {bg_color};
            color: {color};
            border-radius: 16px;
            border: none;
        }}
        QPushButton:hover {{
            background-color: #ffe082;
            color: #333;
        }}
    """)
    return btn

class ResponsiveCard(QFrame):
    """Tam responsive kart bileşeni - Border olmadan"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(12, 12, 12, 12)
        
    def add_widget(self, widget, stretch=0):
        self.layout.addWidget(widget, stretch)
            
    def add_layout(self, layout, stretch=0):
        self.layout.addLayout(layout, stretch)

class UlgenDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ÜLGEN AI-DRIVEN EXPLORATION")
        
        # Tema yöneticisi oluştur
        self.theme_manager = ThemeManager()
        
        # İşletim sistemi tespiti
        self.detect_platform()
        
        # Ana UI yapısını oluştur
        self.init_ui()
        
        # Telemetri verilerini simüle etmek için zamanlayıcı
        self.telemetry_timer = QTimer(self)
        self.telemetry_timer.timeout.connect(self.update_telemetry)
        self.telemetry_timer.start(500)  # 500ms'de bir güncelle
        
    def detect_platform(self):
        """İşletim sistemini tespit eder ve tema değişkenleri ayarlar"""
        self.platform_name = platform.system()
        
        # Font ailesi ayarla
        if self.platform_name == "Darwin":  # macOS
            self.font_family = "SF Pro Display, -apple-system"
            self.radius = "12px"
        elif self.platform_name == "Windows":
            self.font_family = "Segoe UI"
            self.radius = "8px"
        else:  # Linux ve diğerleri
            self.font_family = "Ubuntu, Noto Sans"
            self.radius = "10px"
            
        # Tema renklerini al
        colors = self.theme_manager.get_colors(self.platform_name)
        self.bg_color = colors["bg_color"]
        self.card_color = colors["card_color"]
        self.card_border = colors["card_border"]
        self.text_color = colors["text_color"]
        self.text_secondary = colors["text_secondary"]
        self.primary_color = colors["primary_color"]
        self.accent_color = colors["accent_color"]
        self.gray_color = colors["gray_color"]
        self.success_color = colors["success_color"]
        self.warning_color = colors["warning_color"]
        self.danger_color = colors["danger_color"]
        self.info_color = colors["info_color"]
        self.preview_bg = colors["preview_bg"]
        
    def update_telemetry(self):
        """Telemetri verilerini simüle et ve göstergeleri güncelle"""
        if hasattr(self, 'altitude_lcd'):
            # Rastgele yükseklik değeri (gerçek sistemde drone'dan alınır)
            altitude = random.uniform(20, 150)
            self.altitude_lcd.display(f"{altitude:.1f}")
            
            # Hız değeri
            speed = random.uniform(0, 45)
            self.speed_lcd.display(f"{speed:.1f}")
            
            # Batarya seviyesi
            battery = random.randint(60, 100)
            self.battery_progress.setValue(battery)
            
            # Sinyal gücü
            signal = random.randint(70, 100)
            self.signal_progress.setValue(signal)
            
    def init_ui(self):
        # Ekran boyutunu al ve %90'ını kullan
        available_geometry = QApplication.primaryScreen().availableGeometry()
        width = int(available_geometry.width() * 0.9)
        height = int(available_geometry.height() * 0.9)
        
        # Pencereyi ortala ve boyutlandır
        self.setGeometry(
            int((available_geometry.width() - width) / 2),
            int((available_geometry.height() - height) / 2),
            width, height
        )
        
        # Ana widget'ı responsive yapmak için scroll area içine yerleştir
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.setCentralWidget(self.scroll_area)
        
        # Ana içerik widget'ı
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet(f"background-color: {self.bg_color};")
        self.scroll_area.setWidget(self.central_widget)
        
        # Ana layout
        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sol menü
        side_menu = self.create_side_menu()
        main_layout.addWidget(side_menu)
        
        # Çoklu sayfa sistemi - Ana ekran ve Dron ekranı için
        self.stacked_widget = QStackedWidget()
        
        # Ana sayfa oluştur
        main_page = self.create_main_page()
        
        # Dron telemetri sayfası oluştur
        drone_page = self.create_drone_telemetry_page()
        
        # Sayfaları stack widget'a ekle
        self.stacked_widget.addWidget(main_page)  # index 0 - Ana sayfa
        self.stacked_widget.addWidget(drone_page)  # index 1 - Dron sayfası
        
        main_layout.addWidget(self.stacked_widget, 1)
        
        # İşletim sistemine göre tema uygula
        self.apply_platform_theme()
        
        # Resize olayını özelleştir - responsive davranış için
        self.resizeEvent = self.on_resize
    
    def create_main_page(self):
        """Ana sayfa içeriğini oluşturur"""
        page = QWidget()
        page.setStyleSheet(f"background-color: {self.bg_color};")
        
        content_layout = QVBoxLayout(page)
        content_layout.setContentsMargins(24, 24, 24, 24)
        
        # Üst bar
        topbar = self.create_topbar()
        content_layout.addLayout(topbar)
        
        # Ana içerik grid'i - tam responsive grid
        grid = QGridLayout()
        grid.setSpacing(20)
        
        # SOL: Video kartı (büyük, 2 satır) - BORDER YOK
        video_card = ResponsiveCard()
        video_card.setStyleSheet(f"""
            background: {self.card_color};
            border-radius: {self.radius};
            border: none;
        """)
        
        video_layout = QVBoxLayout()
        
        video_title = QLabel("Live Video Feed")
        video_title.setFont(QFont(self.font_family, 14, QFont.Bold))
        video_title.setStyleSheet(f"color: {self.text_color};")
        
        # Doğru tema rengiyle video widget oluştur
        self.video_widget = VideoFeedWidget(bg_color=self.card_color)
        
        # Durum çubuğu - BORDER YOK
        status_container = QFrame()
        status_container.setStyleSheet(f"""
            background: {self.card_color};
            border: none;
        """)
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(0, 8, 0, 0)
        
        status_icon = QLabel("🟢")
        status_text = QLabel("System idle - Waiting for processing command")
        status_text.setFont(QFont(self.font_family, 11))
        status_text.setStyleSheet(f"color: {self.text_secondary};")
        
        status_layout.addWidget(status_icon)
        status_layout.addWidget(status_text, 1)
        
        video_layout.addWidget(video_title)
        video_layout.addWidget(self.video_widget, 1)  # 1 = stretch faktörü
        video_layout.addWidget(status_container)
        
        video_card.add_layout(video_layout, 1)
        grid.addWidget(video_card, 0, 0, 2, 6)  # 2 satır, 6 sütun
        
        # SAĞ ÜST: Data kartı - BORDER YOK
        data_card = ResponsiveCard()
        data_card.setStyleSheet(f"""
            background: {self.card_color};
            border-radius: {self.radius};
            border: none;
        """)
        
        data_layout = QVBoxLayout()
        
        data_title = QLabel("Image Analysis")
        data_title.setFont(QFont(self.font_family, 14, QFont.Bold))
        data_title.setStyleSheet(f"color: {self.text_color};")
        
        accuracy_container = QHBoxLayout()
        accuracy_label = QLabel("Accuracy Rate:")
        accuracy_label.setFont(QFont(self.font_family, 12))
        accuracy_label.setStyleSheet(f"color: {self.text_color};")
        
        accuracy_value = QLabel("10%")
        accuracy_value.setFont(QFont(self.font_family, 12, QFont.Bold))
        accuracy_value.setStyleSheet(f"color: {self.accent_color}")
        
        accuracy_container.addWidget(accuracy_label)
        accuracy_container.addWidget(accuracy_value)
        accuracy_container.addStretch()
        
        task_layout = QVBoxLayout()
        current_task = QLabel(f"Current Task: <b>none</b>")
        current_task.setFont(QFont(self.font_family, 11))
        current_task.setStyleSheet(f"color: {self.text_secondary};")
        
        epochs_label = QLabel(f"Epochs Available: <span style='color:{self.accent_color}'><b>false</b></span>")
        epochs_label.setFont(QFont(self.font_family, 11))
        epochs_label.setStyleSheet(f"color: {self.text_secondary};")
        
        task_layout.addWidget(current_task)
        task_layout.addWidget(epochs_label)
        
        data_layout.addWidget(data_title)
        data_layout.addLayout(accuracy_container)
        data_layout.addSpacing(10)
        data_layout.addLayout(task_layout)
        data_layout.addStretch()
        
        data_card.add_layout(data_layout, 1)
        grid.addWidget(data_card, 0, 6, 1, 4)  # 1 satır, 4 sütun
        
        # SAĞ ALT: Datasets kartı - BORDER YOK
        datasets_card = ResponsiveCard()
        datasets_card.setStyleSheet(f"""
            background: {self.card_color};
            border-radius: {self.radius};
            border: none;
        """)
        
        datasets_layout = QVBoxLayout()
        
        datasets_title = QLabel("DATASETS")
        datasets_title.setFont(QFont(self.font_family, 14, QFont.Bold))
        datasets_title.setStyleSheet(f"color: {self.text_color};")
        
        params_grid = QGridLayout()
        params_grid.setHorizontalSpacing(12)
        params_grid.setVerticalSpacing(8)
        
        # Dataset parametreleri - Borderlar kaldırıldı
        params = [
            ("Mode", "Performance", "⚡"),
            ("Intake", "Neutral", "📥"),
            ("Frequency", "10.7Hz", "🔄")
        ]
        
        row = 0
        for label, value, icon in params:
            icon_label = QLabel(icon)
            icon_label.setFont(QFont(self.font_family, 16))
            icon_label.setStyleSheet("border: none;")
            
            name_label = QLabel(f"{label}:")
            name_label.setFont(QFont(self.font_family, 11))
            name_label.setStyleSheet(f"color: {self.text_secondary}; border: none;")
            
            value_label = QLabel(f"<b>{value}</b>")
            value_label.setFont(QFont(self.font_family, 11))
            value_label.setStyleSheet(f"color: {self.text_color}; border: none;")
            
            params_grid.addWidget(icon_label, row, 0)
            params_grid.addWidget(name_label, row, 1)
            params_grid.addWidget(value_label, row, 2)
            row += 1
        
        # Source box - Koyu tema uyumlu ve Border YOK
        source_box = QFrame()
        source_box.setStyleSheet(f"""
            background: {self.bg_color};
            border-radius: {self.radius};
            border: none;
            padding: 6px;
        """)
        
        source_layout = QHBoxLayout(source_box)
        source_icon = QLabel("🔗")
        source_icon.setFont(QFont(self.font_family, 16))
        source_icon.setStyleSheet("border: none;")
        
        source_text = QLabel("<b>SOURCES</b><br>ACTIVE")
        source_text.setFont(QFont(self.font_family, 11))
        source_text.setStyleSheet(f"color: {self.text_color}; border: none;")
        
        source_layout.addWidget(source_icon)
        source_layout.addWidget(source_text)
        source_layout.addStretch()
        
        datasets_layout.addWidget(datasets_title)
        datasets_layout.addLayout(params_grid)
        datasets_layout.addSpacing(12)
        datasets_layout.addWidget(source_box)
        datasets_layout.addStretch()
        
        datasets_card.add_layout(datasets_layout, 1)
        grid.addWidget(datasets_card, 1, 6, 1, 4)  # 1 satır, 4 sütun
        
        # SAĞ: Analiz kartı - BORDER YOK
        analyze_card = ResponsiveCard()
        analyze_card.setStyleSheet(f"""
            background: {self.card_color};
            border-radius: {self.radius};
            border: none;
        """)
        
        analyze_layout = QVBoxLayout()
        
        analyze_title = QLabel("Image Analysis")
        analyze_title.setFont(QFont(self.font_family, 14, QFont.Bold))
        analyze_title.setStyleSheet(f"color: {self.text_color}; border: none;")
        
        # Tema uyumlu önizleme alanı (koyu temada siyah, açık temada açık mavi)
        preview_img = QLabel()
        preview_img.setPixmap(QPixmap(320, 160))
        preview_img.setStyleSheet(f"""
            background: {self.preview_bg}; 
            border-radius: {self.radius};
            border: none;
        """)
        preview_img.setMinimumHeight(160)
        preview_img.setAlignment(Qt.AlignCenter)
        preview_img.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Butonlar - gradient'ler tema değişimine uygun hale getirildi
        eject_btn = QPushButton("⏏ Eject")
        eject_btn.setCursor(Qt.PointingHandCursor)
        eject_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #d500f9, stop:1 #448aff);
                color: white; 
                border-radius: {self.radius}; 
                font-weight: bold;
                padding: 12px;
                font-size: 13px;
                border: none;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #448aff, stop:1 #d500f9);
            }}
        """)
        
        # Alt buton grubu
        button_row = QHBoxLayout()
        button_row.setSpacing(8)
        
        # Buton oluşturma fonksiyonu - koyu tema desteği eklendi, borderlar kaldırıldı
        def create_button(text, icon, hover_gradient):
            btn = QPushButton(f"{icon} {text}")
            btn.setCursor(Qt.PointingHandCursor)
            
            # Tema uyumlu buton renkleri
            bg_color = "#333333" if self.theme_manager.get_theme() == "dark" else "#ede7f6"
            text_color = "white" if self.theme_manager.get_theme() == "dark" else "#673ab7"
            
            btn.setStyleSheet(f"""
                                QPushButton {{
                    background: {bg_color};
                    color: {text_color}; 
                    border-radius: {self.radius}; 
                    font-weight: bold;
                    padding: 8px 12px;
                    font-size: 13px;
                    border: none;
                }}
                QPushButton:hover {{
                    background: {hover_gradient};
                    color: white;
                }}
            """)
            return btn
        
        upload_btn = create_button(
            "Upload", "⏫", 
            "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c4dff, stop:1 #536dfe)"
        )
        
        cnn_btn = create_button(
            "CNN", "🔎", 
            "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00897b, stop:1 #43a047)"
        )
        
        settings_btn = create_button(
            "", "⚙", 
            "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ffd600, stop:1 #ffc107)"
        )
        settings_btn.setFixedWidth(42)
        
        button_row.addWidget(upload_btn)
        button_row.addWidget(cnn_btn)
        button_row.addWidget(settings_btn)
        
        # Analiz butonu
        analyze_btn = QPushButton("▶  Analyze Image")
        analyze_btn.setCursor(Qt.PointingHandCursor)
        analyze_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #d500f9, stop:1 #2979ff);
                color: white; 
                border-radius: {self.radius}; 
                font-weight: bold;
                padding: 14px 24px;
                font-size: 15px;
                margin-top: 12px;
                border: none;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2979ff, stop:1 #d500f9);
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #aa00ff, stop:1 #2962ff);
            }}
        """)
        
        analyze_layout.addWidget(analyze_title)
        analyze_layout.addWidget(preview_img, 1)  # 1 = stretch
        analyze_layout.addWidget(eject_btn)
        analyze_layout.addLayout(button_row)
        analyze_layout.addWidget(analyze_btn)
        
        analyze_card.add_layout(analyze_layout, 1)
        grid.addWidget(analyze_card, 0, 10, 2, 4)  # 2 satır, 4 sütun
        
        # Grid için column stretch faktörlerini ayarla - responsive grid
        for col in range(14):
            grid.setColumnStretch(col, 1)
        
        # Grid'i ana layout'a ekle
        content_layout.addLayout(grid, 1)  # 1 = stretch
        
        # Alt bildirim bar - BORDER YOK
        issue_card = QFrame()
        issue_card.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff8373, stop:1 #ffd600); 
            color: white; 
            border-radius: {self.radius};
            border: none;
        """)
        issue_card.setFixedHeight(36)
        
        issue_layout = QHBoxLayout(issue_card)
        issue_layout.setContentsMargins(16, 0, 16, 0)
        
        issue_icon = QLabel("⚠️")
        issue_icon.setFont(QFont(self.font_family, 14))
        issue_icon.setStyleSheet("border: none;")
        
        issue_text = QLabel("1 Issue Detected")
        issue_text.setFont(QFont(self.font_family, 12, QFont.Bold))
        issue_text.setStyleSheet("border: none;")
        
        close_btn = QLabel("❌")
        close_btn.setFont(QFont(self.font_family, 14))
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("border: none;")
        
        issue_layout.addWidget(issue_icon)
        issue_layout.addWidget(issue_text)
        issue_layout.addStretch()
        issue_layout.addWidget(close_btn)
        
        content_layout.addWidget(issue_card)
        
        return page
    
    def create_drone_telemetry_page(self):
        """Dron telemetri sayfasını oluşturur"""
        page = QWidget()
        page.setStyleSheet(f"background-color: {self.bg_color};")
        
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Başlık
        header = QHBoxLayout()
        title = QLabel("ÜLGEN DRONE TELEMETRY")
        title.setFont(QFont(self.font_family, 22, QFont.Bold))
        title.setStyleSheet(f"color: {self.primary_color};")
        
        header.addWidget(title)
        header.addStretch()
        
        # Durum göstergesi
        status_label = QLabel("🟢 Online - Aktif Uçuş")
        status_label.setFont(QFont(self.font_family, 14))
        status_label.setStyleSheet(f"color: {self.success_color};")
        
        header.addWidget(status_label)
        
        layout.addLayout(header)
        layout.addSpacing(20)
        
        # Telemetri Grid Layout
        telemetry_grid = QGridLayout()
        telemetry_grid.setSpacing(20)
        
        # SOL ÜST: Drone Yükseklik ve Hız Göstergesi
        flight_data_card = ResponsiveCard()
        flight_data_card.setStyleSheet(f"""
            background: {self.card_color};
            border-radius: {self.radius};
            border: none;
        """)
        
        flight_layout = QVBoxLayout()
        
        flight_title = QLabel("Uçuş Verileri")
        flight_title.setFont(QFont(self.font_family, 16, QFont.Bold))
        flight_title.setStyleSheet(f"color: {self.text_color};")
        
        # Yükseklik ve Hız LCD göstergeleri
        data_grid = QGridLayout()
        data_grid.setSpacing(15)
        
        # Yükseklik
        altitude_label = QLabel("Yükseklik (m)")
        altitude_label.setFont(QFont(self.font_family, 12))
        altitude_label.setStyleSheet(f"color: {self.text_color};")
        
        self.altitude_lcd = QLCDNumber()
        self.altitude_lcd.setDigitCount(5)  # 123.4 için 5 hane
        self.altitude_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.altitude_lcd.setStyleSheet(f"""
            background: {self.bg_color};
            color: {self.primary_color};
            border: none;
        """)
        self.altitude_lcd.setMinimumHeight(60)
        self.altitude_lcd.display("123.4")
        
        # Hız
        speed_label = QLabel("Hız (km/s)")
        speed_label.setFont(QFont(self.font_family, 12))
        speed_label.setStyleSheet(f"color: {self.text_color};")
        
        self.speed_lcd = QLCDNumber()
        self.speed_lcd.setDigitCount(5)  # 45.6 için 5 hane
        self.speed_lcd.setSegmentStyle(QLCDNumber.Flat)
        self.speed_lcd.setStyleSheet(f"""
            background: {self.bg_color};
            color: {self.info_color};
            border: none;
        """)
        self.speed_lcd.setMinimumHeight(60)
        self.speed_lcd.display("45.6")
        
        data_grid.addWidget(altitude_label, 0, 0)
        data_grid.addWidget(self.altitude_lcd, 1, 0)
        data_grid.addWidget(speed_label, 0, 1)
        data_grid.addWidget(self.speed_lcd, 1, 1)
        
        # Batarya ve Sinyal göstergeleri
        status_grid = QGridLayout()
        status_grid.setSpacing(15)
        
        # Batarya
        battery_label = QLabel("Batarya")
        battery_label.setFont(QFont(self.font_family, 12))
        battery_label.setStyleSheet(f"color: {self.text_color};")
        
        self.battery_progress = QProgressBar()
        self.battery_progress.setRange(0, 100)
        self.battery_progress.setValue(80)
        self.battery_progress.setTextVisible(True)
        self.battery_progress.setFormat("%p%")
        self.battery_progress.setStyleSheet(f"""
            QProgressBar {{
                background: {self.bg_color};
                border: none;
                border-radius: 5px;
                text-align: center;
                height: 20px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #43a047, stop:1 #66bb6a);
                border-radius: 5px;
            }}
        """)
        
        # Sinyal
        signal_label = QLabel("Sinyal Gücü")
        signal_label.setFont(QFont(self.font_family, 12))
        signal_label.setStyleSheet(f"color: {self.text_color};")
        
        self.signal_progress = QProgressBar()
        self.signal_progress.setRange(0, 100)
        self.signal_progress.setValue(90)
        self.signal_progress.setTextVisible(True)
        self.signal_progress.setFormat("%p%")
        self.signal_progress.setStyleSheet(f"""
            QProgressBar {{
                background: {self.bg_color};
                border: none;
                border-radius: 5px;
                text-align: center;
                height: 20px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1976d2, stop:1 #42a5f5);
                border-radius: 5px;
            }}
        """)
        
        status_grid.addWidget(battery_label, 0, 0)
        status_grid.addWidget(self.battery_progress, 1, 0)
        status_grid.addWidget(signal_label, 0, 1)
        status_grid.addWidget(self.signal_progress, 1, 1)
        
        flight_layout.addWidget(flight_title)
        flight_layout.addSpacing(10)
        flight_layout.addLayout(data_grid)
        flight_layout.addSpacing(20)
        flight_layout.addLayout(status_grid)
        flight_layout.addStretch()
        
        flight_data_card.add_layout(flight_layout)
        telemetry_grid.addWidget(flight_data_card, 0, 0, 1, 3)
        
        # SOL ALT: Video Feed
        video_card = ResponsiveCard()
        video_card.setStyleSheet(f"""
            background: {self.card_color};
            border-radius: {self.radius};
            border: none;
        """)
        
        video_layout = QVBoxLayout()
        video_title = QLabel("Drone Kamera")
        video_title.setFont(QFont(self.font_family, 16, QFont.Bold))
        video_title.setStyleSheet(f"color: {self.text_color};")
        
        # Video widget (ana sayfadaki ile aynı video widget'ı kullanabilirsiniz)
        drone_video = VideoFeedWidget(bg_color=self.card_color)
        drone_video.camera_selector.setCurrentIndex(1)  # Dron kamerasını seç
        
        video_layout.addWidget(video_title)
        video_layout.addWidget(drone_video, 1)
        
        video_card.add_layout(video_layout)
        telemetry_grid.addWidget(video_card, 1, 0, 1, 3)
        
        # ORTA: Yapay Ufuk ve Tırmanma Göstergesi
        instruments_card = ResponsiveCard()
        instruments_card.setStyleSheet(f"""
            background: {self.card_color};
            border-radius: {self.radius};
            border: none;
        """)
        
        instruments_layout = QVBoxLayout()
        instruments_title = QLabel("Uçuş Enstrümanları")
        instruments_title.setFont(QFont(self.font_family, 16, QFont.Bold))
        instruments_title.setStyleSheet(f"color: {self.text_color};")
        
        # Yapay ufuk ve tırmanma göstergeleri
        gauges_layout = QHBoxLayout()
        
        # Yapay ufuk göstergesi
        artificial_horizon = ArtificialHorizon()
        
        # Tırmanma hızı göstergesi
        climb_indicator = ClimbIndicator()
        
        gauges_layout.addWidget(artificial_horizon, 3)  # 3:1 oranında daha geniş
        gauges_layout.addWidget(climb_indicator, 1)
        
        instruments_layout.addWidget(instruments_title)
        instruments_layout.addSpacing(10)
        instruments_layout.addLayout(gauges_layout, 1)
        
        instruments_card.add_layout(instruments_layout)
        telemetry_grid.addWidget(instruments_card, 0, 3, 2, 3)
        
        # Grid'i layout'a ekle
        layout.addLayout(telemetry_grid, 1)
        
        # Kontrol düğmeleri
        control_layout = QHBoxLayout()
        
        back_btn = QPushButton("◀ Ana Sayfaya Dön")
        back_btn.setFont(QFont(self.font_family, 12, QFont.Bold))
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self.bg_color};
                color: {self.text_color};
                border: 1px solid {self.card_border};
                border-radius: {self.radius};
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background: {self.card_border};
            }}
        """)
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        
        takeoff_btn = QPushButton("▲ Kalkış")
        takeoff_btn.setFont(QFont(self.font_family, 12, QFont.Bold))
        takeoff_btn.setCursor(Qt.PointingHandCursor)
        takeoff_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #66bb6a, stop:1 #43a047);
                color: white;
                border: none;
                border-radius: {self.radius};
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #43a047, stop:1 #2e7d32);
            }}
        """)
        
        land_btn = QPushButton("▼ İniş")
        land_btn.setFont(QFont(self.font_family, 12, QFont.Bold))
        land_btn.setCursor(Qt.PointingHandCursor)
        land_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ef5350, stop:1 #e53935);
                color: white;
                border: none;
                border-radius: {self.radius};
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e53935, stop:1 #c62828);
            }}
        """)
        
        control_layout.addWidget(back_btn)
        control_layout.addStretch()
        control_layout.addWidget(takeoff_btn)
        control_layout.addWidget(land_btn)
        
        layout.addSpacing(15)
        layout.addLayout(control_layout)
        
        return page
    
    def on_resize(self, event):
        """Pencere boyutlandırıldığında responsive davranış için çağrılır"""
        width = event.size().width()
        
        # Responsive davranış kuralları
        if width < 1000:
            # Dar ekranlarda küçük ayarlamalar
            self.adjust_for_small_screen()
        else:
            # Geniş ekranlarda normal görünüm
            self.adjust_for_large_screen()
            
    def adjust_for_small_screen(self):
        """Küçük ekranlarda UI ayarlamaları"""
        # Bu metod daha dar ekranlarda arayüz ayarlamaları yapabilir
        pass
        
    def adjust_for_large_screen(self):
        """Büyük ekranlarda UI ayarlamaları"""
        # Bu metod geniş ekranlarda arayüz ayarlamaları yapabilir
        pass
    
    def create_side_menu(self):
        """Sol kenar menüsü oluşturur"""
        menu_widget = QWidget()
        menu_widget.setFixedWidth(80)
        menu_widget.setStyleSheet(f"""
            background: {self.bg_color}; 
            border-right: 1px solid {self.card_border};
        """)
        
        side_menu = QVBoxLayout(menu_widget)
        side_menu.setContentsMargins(0, 20, 0, 20)
        side_menu.setSpacing(20)
        side_menu.setAlignment(Qt.AlignHCenter)
        
        # Dron butonu - Ana sayfaya yönlendirir
        drone_btn = make_icon_button("🛸", self.primary_color, self.bg_color)
        drone_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        
        # Diğer menü butonları
        side_menu.addWidget(drone_btn)
        side_menu.addWidget(make_icon_button("🟦", self.gray_color, self.bg_color))
        side_menu.addWidget(make_icon_button("📡", self.accent_color, self.bg_color))
        side_menu.addWidget(make_icon_button("🛞", self.info_color, self.bg_color))
        side_menu.addStretch()
        
                # Alt menü butonları
        power_btn = make_icon_button("🔋", self.primary_color, self.bg_color)
        
        # Tema değiştirme butonu
        theme_btn = make_icon_button("🎨", self.gray_color, self.bg_color)
        theme_btn.setContextMenuPolicy(Qt.CustomContextMenu)
        theme_btn.customContextMenuRequested.connect(self.show_theme_menu)
        theme_btn.clicked.connect(self.show_theme_menu_from_click)
        
        side_menu.addWidget(power_btn)
        side_menu.addWidget(theme_btn)
        
        return menu_widget
    
    def show_theme_menu_from_click(self):
        """Tema değiştirme butonuna tıklandığında menüyü göster"""
        # Butona tıklandığında imlecin altında menüyü göster
        sender = self.sender()
        if sender:
            pos = sender.mapToGlobal(sender.rect().bottomLeft())
            self.show_theme_menu(pos)
    
    def show_theme_menu(self, position=None):
        """Tema değiştirme menüsünü göster"""
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {self.card_color};
                color: {self.text_color};
                border: 1px solid {self.card_border};
                border-radius: {self.radius};
                padding: 5px;
            }}
            QMenu::item {{
                padding: 5px 25px 5px 25px;
                border-radius: 3px;
                border: none;
            }}
            QMenu::item:selected {{
                background-color: {self.accent_color};
                color: white;
            }}
        """)
        
        # Tema seçenekleri
        system_action = QAction("System Theme", self)
        light_action = QAction("Light Theme", self)
        dark_action = QAction("Dark Theme", self)
        
        # Mevcut temayı işaretle
        current_theme = self.theme_manager.current_theme
        if current_theme == ThemeManager.SYSTEM:
            system_action.setCheckable(True)
            system_action.setChecked(True)
        elif current_theme == ThemeManager.LIGHT:
            light_action.setCheckable(True)
            light_action.setChecked(True)
        else:
            dark_action.setCheckable(True)
            dark_action.setChecked(True)
        
        # Menüye ekle
        menu.addAction(system_action)
        menu.addAction(light_action)
        menu.addAction(dark_action)
        
        # Eylemleri bağla
        system_action.triggered.connect(lambda: self.change_theme(ThemeManager.SYSTEM))
        light_action.triggered.connect(lambda: self.change_theme(ThemeManager.LIGHT))
        dark_action.triggered.connect(lambda: self.change_theme(ThemeManager.DARK))
        
        # Menüyü göster
        if isinstance(position, QPoint):
            menu.exec(position)
        else:
            menu.exec(QCursor.pos())
    
    def change_theme(self, theme):
        """Tema değiştirme işlemini yap ve UI'yi güncelle"""
        if self.theme_manager.current_theme != theme:
            self.theme_manager.set_theme(theme)
            # Temayı uygula
            self.detect_platform()  # Renkleri yeniden çek
            self.apply_platform_theme()  # Temayı uygula
            
            # UI'yi yeniden oluştur
            self.central_widget.deleteLater()
            self.scroll_area.deleteLater()
            self.init_ui()
    
    def create_topbar(self):
        """Üst bilgi çubuğunu oluşturur"""
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 24)
        
        # Sol: Logo ve sistem bilgisi
        logo_container = QHBoxLayout()
        
        cast_icon = QLabel("📡")
        cast_icon.setFont(QFont(self.font_family, 18))
        cast_icon.setStyleSheet(f"color: {self.gray_color}; border: none;")
        
        title_container = QVBoxLayout()
        title_container.setSpacing(2)
        
        logo_label = QLabel("<b>ÜLGEN</b>")
        logo_label.setFont(QFont(self.font_family, 22, QFont.Bold))
        logo_label.setStyleSheet(f"color: {self.primary_color}; border: none;")
        
        system_label = QLabel(f"Raspberry Pi 5 • {self.platform_name}")
        system_label.setFont(QFont(self.font_family, 10))
        system_label.setStyleSheet(f"color: {self.text_secondary}; border: none;")
        
        title_container.addWidget(logo_label)
        title_container.addWidget(system_label)
        
        logo_container.addWidget(cast_icon)
        logo_container.addSpacing(10)
        logo_container.addLayout(title_container)
        
        top_bar.addLayout(logo_container)
        top_bar.addStretch()
        
        # Orta: Bilgi çubuğu (navigasyon) - tüm tema tipleri için uyumlu ve BORDER YOK
        nav_container = QHBoxLayout()
        nav_container.setSpacing(16)
        nav_container.setAlignment(Qt.AlignCenter)
        
        # Bilgi kutusu oluşturma fonksiyonu - tema uyumlu, borderlar kaldırıldı
        def create_info_box(icon, value, label, color):
            frame = QFrame()
            frame.setStyleSheet(f"""
                background: {self.card_color};
                border-radius: {self.radius};
                border: none;
            """)
            
            layout = QVBoxLayout(frame)
            layout.setContentsMargins(10, 8, 10, 8)
            layout.setSpacing(2)
            
            icon_label = QLabel(icon)
            icon_label.setFont(QFont(self.font_family, 18))
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setStyleSheet("border: none;")
            
            value_label = QLabel(value)
            value_label.setFont(QFont(self.font_family, 14, QFont.Bold))
            value_label.setStyleSheet(f"color: {color}; border: none;")
            value_label.setAlignment(Qt.AlignCenter)
            
            desc_label = QLabel(label)
            desc_label.setFont(QFont(self.font_family, 10))
            desc_label.setStyleSheet(f"color: {self.text_secondary}; border: none;")
            desc_label.setAlignment(Qt.AlignCenter)
            
            layout.addWidget(icon_label)
            layout.addWidget(value_label)
            layout.addWidget(desc_label)
            
            return frame
        
        # Bilgi kutuları - tema uyumlu renklerle
        temp_box = create_info_box("🌡️", "13%", "Temp", self.primary_color)
        battery_box = create_info_box("🔋", "73%", "Battery", self.success_color)
        bearings_box = create_info_box("🔄", "45", "Bearings", self.danger_color)
        torque_box = create_info_box("🛞", "2500", "Torque", self.accent_color)
        watt_box = create_info_box("⚡", "10W", "Watt", self.info_color)
        
        nav_container.addWidget(temp_box)
        nav_container.addWidget(battery_box)
        nav_container.addWidget(bearings_box)
        nav_container.addWidget(torque_box)
        nav_container.addWidget(watt_box)
        
        top_bar.addLayout(nav_container)
        top_bar.addStretch()
        
        return top_bar
    
    def apply_platform_theme(self):
        """İşletim sistemine ve seçilen temaya özgü tema ayarlarını uygular"""
        # Genel stil - tüm border referansları kaldırıldı
        self.setStyleSheet(f"""
            QMainWindow {{ 
                background: {self.bg_color}; 
            }}
            QLabel {{ 
                color: {self.text_color}; 
                font-family: {self.font_family};
                border: none;
            }}
            QPushButton {{
                font-family: {self.font_family};
                font-weight: bold;
                border: none;
            }}
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {self.card_border};
                width: 8px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.gray_color};
                min-height: 20px;
                border-radius: 4px;
            }}
            QWidget {{
                font-family: {self.font_family};
                border: none;
            }}
            QFrame {{
                border: none;
            }}
            QLCDNumber {{
                border: none;
                color: {self.primary_color};
            }}
        """)

# Ana uygulama
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Tutarlı görünüm için
    window = UlgenDashboard()
    window.show()
    sys.exit(app.exec())