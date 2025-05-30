# 🚁 ÜLGEN - AI-Driven Autonomous Vehicle & Drone Control System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)  
[![PySide6](https://img.shields.io/badge/PySide6-6.0%2B-green.svg)](https://wiki.qt.io/Qt_for_Python)  
[![OpenCV](https://img.shields.io/badge/OpenCV-4.0%2B-red.svg)](https://opencv.org/)  
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)  
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/)  

## 📋 Table of Contents
- [Overview](#overview)  
- [Features](#features)  
- [System Architecture](#system-architecture)  
- [Technology Stack](#technology-stack)  
- [Design Patterns](#design-patterns)  
- [Installation](#installation)  
- [Usage](#usage)  
- [Project Structure](#project-structure)  
- [Contributing](#contributing)  
- [License](#license)  
- [Acknowledgments](#acknowledgments)  

## 🎯 Overview
**ÜLGEN** is a sophisticated, cross-platform control interface designed for autonomous vehicles and drones. Built with Python and PySide6, it provides real-time telemetry visualization, AI-powered image analysis, and comprehensive vehicle control capabilities. Optimized for Raspberry Pi 5 and supporting Windows, Linux, and macOS.

## ✨ Features
- **Multi-Camera Support**  
  - Real-time video streaming (OpenCV)  
  - Switch between vehicle and drone cameras  
- **Advanced Telemetry Dashboard**  
  - QLCDNumber altitude & speed indicators  
  - Custom-painted artificial horizon & climb rate gauges  
  - Battery & signal strength bars (QProgressBar)  
- **Intelligent Theming**  
  - Auto OS detection (Light/Dark/System)  
  - Manual theme menu  
- **Responsive UI**  
  - Scales to any resolution (QGridLayout + QSizePolicy)  
  - Touch-friendly controls  
- **Modular Architecture**  
  - MVC separation, signal-slot Observer pattern  
  - Singleton ThemeManager, Factory widget creation

## 🏗️ System Architecture
```
Presentation Layer
├─ Main Dashboard (QStackedWidget)
├─ Drone Telemetry View
├─ Theme Manager
Business Logic Layer
├─ Video Engine
├─ Telemetry Handler
├─ AI/Image Analysis
Data Access Layer
├─ OpenCV Camera Interface
├─ Serial/UART (pyserial)
├─ Settings (QSettings)
Hardware Abstraction
├─ Camera Drivers
├─ Sensor Interfaces
├─ Communication Protocols
```

## 🛠️ Technology Stack
- **Python 3.8+**  
- **PySide6** (Qt for Python)  
- **OpenCV** (Computer vision)  
- **pyserial** (UART communication)  
- **QPainter** (Custom gauges)  
- **WebSocket/MQTT Ready** (future telemetry)

## 🎨 Design Patterns
- **MVC**: Models (telemetry/camera), Views (Qt widgets), Controllers (slots)  
- **Observer**: Qt signal-slot for theme & data updates  
- **Singleton**: ThemeManager  
- **Factory**: Widget creation helpers  
- **Strategy**: Platform-specific theming & camera strategies  

## 📦 Installation
### Prerequisites
- Python 3.8+, pip, Git  
- OS: Windows 10+, Ubuntu 18.04+, macOS 10.14+  
- RAM ≥ 4 GB, Display ≥ 1280×720  

### Steps
1. **Clone repo**  
   ```
   git clone https://github.com/yourusername/ulgen-dashboard.git
   cd ulgen-dashboard
   ```
2. **Virtual environment**  
   - Windows:  
     ```
     python -m venv venv
     venv\Scripts\activate
     ```  
   - Linux/macOS:  
     ```
     python3 -m venv venv
     source venv/bin/activate
     ```
3. **Install dependencies**  
   ```
   pip install -r requirements.txt
   ```
4. **Verify**  
   ```
   python -c "import PySide6, cv2, serial; print('OK')"
   ```

### Raspberry Pi 5
```
sudo apt update && sudo apt upgrade -y
sudo apt install python3-opencv python3-serial libqt6-dev -y
pip3 install -r requirements.txt
# raspi-config → Interface Options → Camera, Serial → Enable
```

## 🚀 Usage
```
# Activate venv
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

python main.py
```
- **Ctrl+Q**: Quit  
- **Ctrl+T**: Toggle theme  
- **Ctrl+D**: Drone telemetry view  
- **Ctrl+M**: Main view  
- **F11**: Fullscreen  

## 📁 Project Structure
```
ulgen-dashboard/
├── README.md
├── requirements.txt
├── main.py
├── src/
│   ├── ui/
│   │   ├── main_window.py
│   │   ├── drone_page.py
│   │   └── widgets/
│   ├── core/
│   │   ├── theme_manager.py
│   │   ├── camera_handler.py
│   │   └── telemetry_handler.py
│   └── utils/
├── assets/
│   ├── icons/
│   └── themes/
├── tests/
└── docs/
```

## 🤝 Contributing
1. Fork the repo  
2. Create feature branch  
3. Commit & push  
4. Open PR  

Please adhere to the existing code style and design patterns.

## ⚖️ License
This project is released under the **MIT License**. See [LICENSE](LICENSE) for details.

```markdown

## 🙏 Acknowledgments

- Special thanks to the **Qt for Python** team for enabling rapid GUI development with PySide6.  
- Thanks to the **OpenCV** community for their extensive computer vision library and documentation.  
- Appreciation to the **Raspberry Pi Foundation** for providing affordable hardware and excellent documentation.  
- Inspired by the **Ulurover** UI design—credit to the original designers for their clean, modern dashboard concepts.  
- Icons courtesy of [Font Awesome](https://fontawesome.com/) and [EmojiOne](https://www.emojione.com/).  
- Flight instrument gauge visuals adapted from open-source aviation gauge designs under creative commons licenses.  
- Thanks to all project contributors and the open-source community for feedback, bug reports, and pull requests.  
- This project would not be possible without the support of our internal engineering team and research collaborators.  

---
