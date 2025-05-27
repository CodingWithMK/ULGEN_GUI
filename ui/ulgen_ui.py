import sys
import cv2
import platform
import json
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
    QFrame, QSizePolicy, QScrollArea, QMenu
)
from PySide6.QtGui import QFont, QPixmap, QImage, QPalette, QColor, QAction, QCursor
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
                "info_color": "#42A5F5"
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
                    "info_color": "#1E88E5"
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
                    "info_color": "#1E88E5"
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
                    "info_color": "#1E88E5"
                }

class VideoFeedWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMinimumSize(320, 180)
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        
        self.cap = cv2.VideoCapture()
        if not self.cap.isOpened():
            self.label.setText("Unable to open camera.")
            
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
                self.label.width(), self.label.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
            self.label.setPixmap(pixmap)
            
    def closeEvent(self, event):
        if self.cap.isOpened():
            self.cap.release()
        event.accept()

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
    """Tam responsive kart bileşeni"""
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
        self.scroll_area.setWidget(self.central_widget)
        
        # Ana layout
        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sol menü
        side_menu = self.create_side_menu()
        main_layout.addWidget(side_menu)
        
        # Ana içerik alanı
        content_area = QWidget()
        content_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(24, 24, 24, 24)
        
        # Üst bar
        topbar = self.create_topbar()
        content_layout.addLayout(topbar)
        
        # Ana içerik grid'i - tam responsive grid
        grid = QGridLayout()
        grid.setSpacing(20)
        
        # SOL: Video kartı (büyük, 2 satır)
        video_card = ResponsiveCard()
        video_card.setStyleSheet(f"""
            background: {self.card_color};
            border-radius: {self.radius};
            border: 1px solid {self.card_border};
        """)
        
        video_layout = QVBoxLayout()
        
        video_title = QLabel("Live Video Feed")
        video_title.setFont(QFont(self.font_family, 14, QFont.Bold))
        video_title.setStyleSheet(f"color: {self.text_color};")
        
        self.video_widget = VideoFeedWidget()
        
        status_container = QHBoxLayout()
        status_icon = QLabel("🟢")
        status_text = QLabel("System idle - Waiting for processing command")
        status_text.setFont(QFont(self.font_family, 11))
        status_text.setStyleSheet(f"color: {self.text_secondary};")
        
        status_container.addWidget(status_icon)
        status_container.addWidget(status_text, 1)
        
        video_layout.addWidget(video_title)
        video_layout.addWidget(self.video_widget, 1)  # 1 = stretch faktörü
        video_layout.addLayout(status_container)
        
        video_card.add_layout(video_layout, 1)
        grid.addWidget(video_card, 0, 0, 2, 6)  # 2 satır, 6 sütun
        
        # SAĞ ÜST: Data kartı
        data_card = ResponsiveCard()
        data_card.setStyleSheet(f"""
            background: {self.card_color};
            border-radius: {self.radius};
            border: 1px solid {self.card_border};
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
        
        # SAĞ ALT: Datasets kartı
        datasets_card = ResponsiveCard()
        datasets_card.setStyleSheet(f"""
            background: {self.card_color};
            border-radius: {self.radius};
            border: 1px solid {self.card_border};
        """)
        
        datasets_layout = QVBoxLayout()
        
        datasets_title = QLabel("DATASETS")
        datasets_title.setFont(QFont(self.font_family, 14, QFont.Bold))
        datasets_title.setStyleSheet(f"color: {self.text_color};")
        
        params_grid = QGridLayout()
        params_grid.setHorizontalSpacing(12)
        params_grid.setVerticalSpacing(8)
        
        # Dataset parametreleri
        params = [
            ("Mode", "Performance", "⚡"),
            ("Intake", "Neutral", "📥"),
            ("Frequency", "10.7Hz", "🔄")
        ]
        
        row = 0
        for label, value, icon in params:
            icon_label = QLabel(icon)
            icon_label.setFont(QFont(self.font_family, 16))
            
            name_label = QLabel(f"{label}:")
            name_label.setFont(QFont(self.font_family, 11))
            name_label.setStyleSheet(f"color: {self.text_secondary};")
            
            value_label = QLabel(f"<b>{value}</b>")
            value_label.setFont(QFont(self.font_family, 11))
            value_label.setStyleSheet(f"color: {self.text_color};")
            
            params_grid.addWidget(icon_label, row, 0)
            params_grid.addWidget(name_label, row, 1)
            params_grid.addWidget(value_label, row, 2)
            row += 1
        
        # Source box - koyu tema uyumlu
        source_box = QFrame()
        source_box.setStyleSheet(f"""
            background: {self.bg_color};
            border-radius: {self.radius};
            padding: 6px;
        """)
        
        source_layout = QHBoxLayout(source_box)
        source_icon = QLabel("🔗")
        source_icon.setFont(QFont(self.font_family, 16))
        
        source_text = QLabel("<b>SOURCES</b><br>ACTIVE")
        source_text.setFont(QFont(self.font_family, 11))
        source_text.setStyleSheet(f"color: {self.text_color};")
        
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
        
        # SAĞ: Analiz kartı
        analyze_card = ResponsiveCard()
        analyze_card.setStyleSheet(f"""
            background: {self.card_color};
            border-radius: {self.radius};
            border: 1px solid {self.card_border};
        """)
        
        analyze_layout = QVBoxLayout()
        
        analyze_title = QLabel("Image Analysis")
        analyze_title.setFont(QFont(self.font_family, 14, QFont.Bold))
        analyze_title.setStyleSheet(f"color: {self.text_color};")
        
        # Tema uyumlu önizleme alanı (koyu temada siyah, açık temada açık mavi)
        preview_bg = "#212121" if self.theme_manager.get_theme() == "dark" else "#ebeefb" 
        
        preview_img = QLabel()
        preview_img.setPixmap(QPixmap(320, 160))
        preview_img.setStyleSheet(f"background: {preview_bg}; border-radius: {self.radius};")
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
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #448aff, stop:1 #d500f9);
            }}
        """)
        
        # Alt buton grubu
        button_row = QHBoxLayout()
        button_row.setSpacing(8)
        
        # Buton oluşturma fonksiyonu - koyu tema desteği eklendi
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
        
        # Alt bildirim bar
        issue_card = QFrame()
        issue_card.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff8373, stop:1 #ffd600); 
            color: white; 
            border-radius: {self.radius};
        """)
        issue_card.setFixedHeight(36)
        
        issue_layout = QHBoxLayout(issue_card)
        issue_layout.setContentsMargins(16, 0, 16, 0)
        
        issue_icon = QLabel("⚠️")
        issue_icon.setFont(QFont(self.font_family, 14))
        
        issue_text = QLabel("1 Issue Detected")
        issue_text.setFont(QFont(self.font_family, 12, QFont.Bold))
        
        close_btn = QLabel("❌")
        close_btn.setFont(QFont(self.font_family, 14))
        close_btn.setCursor(Qt.PointingHandCursor)
        
        issue_layout.addWidget(issue_icon)
        issue_layout.addWidget(issue_text)
        issue_layout.addStretch()
        issue_layout.addWidget(close_btn)
        
        content_layout.addWidget(issue_card)
        
        # Ana içerik alanını ana layout'a ekle
        main_layout.addWidget(content_area, 1)  # 1 = stretch
        
        # İşletim sistemine göre tema uygula
        self.apply_platform_theme()
        
        # Resize olayını özelleştir - responsive davranış için
        self.resizeEvent = self.on_resize
    
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
        
        # Logo
        logo = QLabel("🚁")
        logo.setFont(QFont(self.font_family, 24))
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet(f"color: {self.primary_color}; margin-bottom: 30px;")
        
        side_menu.addWidget(logo)
        side_menu.addStretch()
        
        # Menü butonları
        side_menu.addWidget(make_icon_button("🧪", self.primary_color, self.bg_color))
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
        cast_icon.setStyleSheet(f"color: {self.gray_color};")
        
        title_container = QVBoxLayout()
        title_container.setSpacing(2)
        
        logo_label = QLabel("<b>ÜLGEN</b>")
        logo_label.setFont(QFont(self.font_family, 22, QFont.Bold))
        logo_label.setStyleSheet(f"color: {self.primary_color};")
        
        system_label = QLabel(f"Raspberry Pi 5 • {self.platform_name}")
        system_label.setFont(QFont(self.font_family, 10))
        system_label.setStyleSheet(f"color: {self.text_secondary};")
        
        title_container.addWidget(logo_label)
        title_container.addWidget(system_label)
        
        logo_container.addWidget(cast_icon)
        logo_container.addSpacing(10)
        logo_container.addLayout(title_container)
        
        top_bar.addLayout(logo_container)
        top_bar.addStretch()
        
        # Orta: Bilgi çubuğu (navigasyon) - tüm tema tipleri için uyumlu
        nav_container = QHBoxLayout()
        nav_container.setSpacing(16)
        nav_container.setAlignment(Qt.AlignCenter)
        
        # Bilgi kutusu oluşturma fonksiyonu - tema uyumlu
        def create_info_box(icon, value, label, color):
            frame = QFrame()
            frame.setStyleSheet(f"""
                background: {self.card_color};
                border: 1px solid {self.card_border};
                border-radius: {self.radius};
            """)
            
            layout = QVBoxLayout(frame)
            layout.setContentsMargins(10, 8, 10, 8)
            layout.setSpacing(2)
            
            icon_label = QLabel(icon)
            icon_label.setFont(QFont(self.font_family, 18))
            icon_label.setAlignment(Qt.AlignCenter)
            
            value_label = QLabel(value)
            value_label.setFont(QFont(self.font_family, 14, QFont.Bold))
            value_label.setStyleSheet(f"color: {color};")
            value_label.setAlignment(Qt.AlignCenter)
            
            desc_label = QLabel(label)
            desc_label.setFont(QFont(self.font_family, 10))
            desc_label.setStyleSheet(f"color: {self.text_secondary};")
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
        # Genel stil
        self.setStyleSheet(f"""
            QMainWindow {{ 
                background: {self.bg_color}; 
            }}
            QLabel {{ 
                color: {self.text_color}; 
                font-family: {self.font_family};
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
            }}
        """)

# Ana uygulama
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Tutarlı görünüm için
    window = UlgenDashboard()
    window.show()
    sys.exit(app.exec())