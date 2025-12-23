import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QSlider, QLabel, QFileDialog,
                             QListWidget, QMenuBar, QStatusBar, QToolBar, QSplitter,
                             QMessageBox, QListWidgetItem, QDialog, QComboBox,
                             QGroupBox, QGridLayout, QCheckBox, QSizePolicy, QStackedWidget,
                             QLineEdit)
from PyQt6.QtCore import Qt, QTimer, QUrl, QSize, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence, QFont, QIcon, QPalette, QColor, QPainter, QLinearGradient
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

class ModernButton(QPushButton):
    """Custom styled button with better appearance"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(40)

class EqualizerDialog(QDialog):
    def __init__(self, player, parent=None):
        super().__init__(parent)
        self.player = player
        self.setWindowTitle("Audio Equalizer")
        self.setMinimumSize(600, 450)
        self.band_values = [0.0] * 10
        self.equalizer_enabled = False
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Enable checkbox
        self.enable_checkbox = QCheckBox("Enable Equalizer")
        self.enable_checkbox.setFont(QFont("Segoe UI", 11))
        self.enable_checkbox.stateChanged.connect(self.toggle_equalizer)
        layout.addWidget(self.enable_checkbox)
        
        # Presets
        preset_group = QGroupBox("Presets")
        preset_group.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(10)
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "Flat", "Classical", "Club", "Dance", "Full Bass", 
            "Full Treble", "Headphones", "Large Hall", "Live", 
            "Party", "Pop", "Reggae", "Rock", "Ska", "Soft", "Techno"
        ])
        self.preset_combo.currentIndexChanged.connect(self.apply_preset)
        preset_layout.addWidget(QLabel("Preset:"))
        preset_layout.addWidget(self.preset_combo)
        preset_layout.addStretch()
        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)
        
        # Equalizer bands
        bands_group = QGroupBox("Frequency Bands")
        bands_group.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        bands_layout = QGridLayout()
        bands_layout.setSpacing(15)
        
        self.band_sliders = []
        band_labels = ["60Hz", "170Hz", "310Hz", "600Hz", "1kHz", 
                      "3kHz", "6kHz", "12kHz", "14kHz", "16kHz"]
        
        for i, label in enumerate(band_labels):
            row = i // 5
            col = i % 5
            
            label_widget = QLabel(label)
            label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label_widget.setFont(QFont("Segoe UI", 9))
            bands_layout.addWidget(label_widget, row*2, col)
            
            slider = QSlider(Qt.Orientation.Vertical)
            slider.setMinimum(-20)
            slider.setMaximum(20)
            slider.setValue(0)
            slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
            slider.setTickInterval(5)
            slider.setMinimumHeight(180)
            slider.valueChanged.connect(lambda v, idx=i: self.update_band(idx, v))
            self.band_sliders.append(slider)
            bands_layout.addWidget(slider, row*2+1, col)
        
        bands_group.setLayout(bands_layout)
        layout.addWidget(bands_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        reset_btn = ModernButton("Reset")
        reset_btn.clicked.connect(self.reset_equalizer)
        close_btn = ModernButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def toggle_equalizer(self, state):
        self.equalizer_enabled = (state == Qt.CheckState.Checked.value)
        
    def update_band(self, index, value):
        self.band_values[index] = value / 10.0
        
    def apply_preset(self, index):
        presets = {
            0: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            1: [0, 0, 0, 0, 0, 0, -7, -7, -7, -9],
            2: [0, 0, 8, 5, 5, 5, 3, 0, 0, 0],
            3: [9, 7, 2, 0, 0, -5, -7, -7, 0, 0],
            4: [8, 9, 9, 5, 1, -4, -8, -10, -11, -11],
            5: [-9, -9, -9, -4, 2, 11, 16, 16, 16, 16],
            6: [4, 11, 5, -3, -2, 1, 4, 9, 12, 14],
            7: [10, 10, 5, 5, 0, -4, -4, -4, 0, 0],
            8: [-4, 0, 4, 5, 5, 5, 4, 2, 2, 2],
            9: [7, 7, 0, 0, 0, 0, 0, 0, 7, 7],
            10: [4, 4, 0, 0, -1, 0, 2, 3, 4, 4],
            11: [0, 0, 0, -3, 0, 0, 5, 5, 0, 0],
            12: [5, 4, -3, -4, -2, 2, 5, 7, 7, 7],
            13: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            14: [2, 1, 0, -1, -1, 0, 2, 4, 5, 7],
            15: [5, 4, 0, -4, -3, 0, 5, 6, 6, 5],
        }
        
        if index in presets:
            values = presets[index]
            for i, val in enumerate(values):
                if i < len(self.band_sliders):
                    self.band_sliders[i].setValue(val)
                    self.update_band(i, val)
    
    def reset_equalizer(self):
        for slider in self.band_sliders:
            slider.setValue(0)
        self.preset_combo.setCurrentIndex(0)
        self.band_values = [0.0] * 10

class MediaPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.media_player = None
        self.audio_output = None
        self.video_widget = None
        self.current_media_url = None
        self.playlist = []
        self.current_index = -1
        self.equalizer_dialog = None
        self.subtitle_file = None
        self.is_seeking = False
        self.ab_start = None
        self.ab_end = None
        self.bookmarks = []
        self.recent_files = []
        self.favorites = set()
        
        self.init_ui()
        self.setup_media_player()
        self.setup_timer()
        
    def init_ui(self):
        self.setWindowTitle("MediaPlayer - Professional Media Player")
        self.setMinimumSize(1400, 800)
        
        # Apply beautiful modern dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f0f0f;
            }
            QWidget {
                background-color: #0f0f0f;
                color: #ffffff;
                font-family: 'Segoe UI', 'Microsoft YaHei UI', Arial, sans-serif;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a, stop:1 #1a1a1a);
                border: 2px solid #3a3a3a;
                border-radius: 8px;
                padding: 12px 20px;
                min-width: 100px;
                min-height: 40px;
                font-size: 12pt;
                font-weight: 600;
                color: #ffffff;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a3a3a, stop:1 #2a2a2a);
                border: 2px solid #0078d4;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a1a, stop:1 #0a0a0a);
                border: 2px solid #005a9e;
            }
            QPushButton:checked {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0078d4, stop:1 #005a9e);
                border: 2px solid #004578;
            }
            QPushButton:disabled {
                background: #1a1a1a;
                color: #666666;
                border: 2px solid #2a2a2a;
            }
            QSlider::groove:vertical {
                border: 2px solid #2a2a2a;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a1a, stop:1 #2a2a2a);
                width: 12px;
                border-radius: 6px;
            }
            QSlider::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0078d4, stop:1 #005a9e);
                border: 2px solid #004578;
                width: 20px;
                height: 20px;
                margin: -4px 0;
                border-radius: 10px;
            }
            QSlider::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0098f4, stop:1 #0078d4);
            }
            QSlider::groove:horizontal {
                border: 2px solid #2a2a2a;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a1a, stop:1 #2a2a2a);
                height: 12px;
                border-radius: 6px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0078d4, stop:1 #005a9e);
                border: 2px solid #004578;
                width: 20px;
                height: 20px;
                margin: 0 -4px;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0098f4, stop:1 #0078d4);
            }
            QListWidget {
                background-color: #1a1a1a;
                border: 2px solid #2a2a2a;
                border-radius: 8px;
                padding: 5px;
                outline: none;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #2a2a2a;
                border-radius: 6px;
                margin: 3px;
                background-color: #1a1a1a;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0078d4, stop:1 #005a9e);
                color: #ffffff;
                border: 2px solid #004578;
            }
            QListWidget::item:hover {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
            }
            QLabel {
                color: #ffffff;
                font-size: 11pt;
            }
            QMenuBar {
                background-color: #1a1a1a;
                color: #ffffff;
                padding: 6px;
                border-bottom: 2px solid #2a2a2a;
            }
            QMenuBar::item {
                padding: 8px 15px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #0078d4;
            }
            QMenu {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 2px solid #2a2a2a;
                padding: 8px;
                border-radius: 6px;
            }
            QMenu::item {
                padding: 8px 30px 8px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #0078d4;
            }
            QStatusBar {
                background-color: #1a1a1a;
                color: #ffffff;
                border-top: 2px solid #2a2a2a;
                padding: 5px;
            }
            QToolBar {
                background-color: #1a1a1a;
                border: none;
                border-bottom: 2px solid #2a2a2a;
                padding: 10px;
                spacing: 10px;
            }
            QGroupBox {
                border: 2px solid #2a2a2a;
                border-radius: 8px;
                margin-top: 20px;
                padding-top: 20px;
                font-weight: bold;
                font-size: 11pt;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px;
                color: #0078d4;
            }
            QComboBox {
                background-color: #1a1a1a;
                border: 2px solid #2a2a2a;
                border-radius: 8px;
                padding: 8px;
                color: #ffffff;
                min-width: 120px;
                font-size: 11pt;
            }
            QComboBox:hover {
                border: 2px solid #0078d4;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
            }
            QComboBox QAbstractItemView {
                background-color: #1a1a1a;
                border: 2px solid #2a2a2a;
                selection-background-color: #0078d4;
                color: #ffffff;
            }
            QCheckBox {
                color: #ffffff;
                font-size: 11pt;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #2a2a2a;
                border-radius: 4px;
                background-color: #1a1a1a;
            }
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border-color: #005a9e;
            }
            QCheckBox::indicator:hover {
                border-color: #0078d4;
            }
        """)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(3)
        
        # Video/audio display area with proper layout
        video_container = QWidget()
        video_container.setStyleSheet("background-color: #000000;")
        video_layout = QVBoxLayout(video_container)
        video_layout.setContentsMargins(0, 0, 0, 0)
        
        self.video_widget = QVideoWidget()
        self.video_widget.setStyleSheet("background-color: #000000;")
        self.video_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.video_widget.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
        video_layout.addWidget(self.video_widget)
        
        splitter.addWidget(video_container)
        
        # Playlist panel
        playlist_panel = QWidget()
        playlist_panel.setMinimumWidth(280)
        playlist_panel.setMaximumWidth(400)
        playlist_layout = QVBoxLayout(playlist_panel)
        playlist_layout.setContentsMargins(15, 15, 15, 15)
        playlist_layout.setSpacing(15)
        
        # Search/filter
        search_box = QLineEdit()
        search_box.setPlaceholderText("Search playlist...")
        search_box.textChanged.connect(self.filter_playlist)
        playlist_layout.addWidget(search_box)

        playlist_label = QLabel("📋 Playlist")
        playlist_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        playlist_label.setStyleSheet("color: #0078d4; padding: 5px;")
        playlist_layout.addWidget(playlist_label)
        
        self.playlist_widget = QListWidget()
        self.playlist_widget.itemDoubleClicked.connect(self.play_selected_item)
        playlist_layout.addWidget(self.playlist_widget)
        
        playlist_buttons = QHBoxLayout()
        playlist_buttons.setSpacing(8)
        add_btn = ModernButton("➕ Add Files")
        add_btn.clicked.connect(self.add_files)
        remove_btn = ModernButton("➖ Remove")
        remove_btn.clicked.connect(self.remove_selected)
        clear_btn = ModernButton("🗑️ Clear")
        clear_btn.clicked.connect(self.clear_playlist)
        save_btn = ModernButton("💾 Save")
        save_btn.clicked.connect(self.save_playlist)
        load_btn = ModernButton("📂 Load")
        load_btn.clicked.connect(self.load_playlist)
        fav_btn = ModernButton("⭐ Favorite")
        fav_btn.clicked.connect(self.toggle_favorite)
        playlist_buttons.addWidget(add_btn)
        playlist_buttons.addWidget(remove_btn)
        playlist_buttons.addWidget(clear_btn)
        playlist_buttons.addWidget(save_btn)
        playlist_buttons.addWidget(load_btn)
        playlist_buttons.addWidget(fav_btn)
        playlist_layout.addLayout(playlist_buttons)
        
        splitter.addWidget(playlist_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Press Ctrl+O to open a media file")
        
        # Create control panel
        self.create_control_panel()
        
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        open_file_action = QAction("Open File...", self)
        open_file_action.setShortcut(QKeySequence("Ctrl+O"))
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)
        
        open_folder_action = QAction("Open Folder...", self)
        open_folder_action.setShortcut(QKeySequence("Ctrl+F"))
        open_folder_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_folder_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence("Alt+F4"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Playback menu
        playback_menu = menubar.addMenu("Playback")
        
        play_action = QAction("Play", self)
        play_action.setShortcut(QKeySequence("Space"))
        play_action.triggered.connect(self.toggle_play_pause)
        playback_menu.addAction(play_action)
        
        stop_action = QAction("Stop", self)
        stop_action.setShortcut(QKeySequence("S"))
        stop_action.triggered.connect(self.stop)
        playback_menu.addAction(stop_action)
        
        prev_action = QAction("Previous", self)
        prev_action.setShortcut(QKeySequence("Ctrl+Left"))
        prev_action.triggered.connect(self.play_previous)
        playback_menu.addAction(prev_action)
        
        next_action = QAction("Next", self)
        next_action.setShortcut(QKeySequence("Ctrl+Right"))
        next_action.triggered.connect(self.play_next)
        playback_menu.addAction(next_action)
        
        # Audio menu
        audio_menu = menubar.addMenu("Audio")
        
        equalizer_action = QAction("Equalizer...", self)
        equalizer_action.triggered.connect(self.show_equalizer)
        audio_menu.addAction(equalizer_action)
        
        # Video menu
        video_menu = menubar.addMenu("Video")
        
        fullscreen_action = QAction("Fullscreen", self)
        fullscreen_action.setShortcut(QKeySequence("F"))
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        video_menu.addAction(fullscreen_action)
        
        # Subtitle menu
        subtitle_menu = menubar.addMenu("Subtitle")
        
        load_subtitle_action = QAction("Load Subtitle File...", self)
        load_subtitle_action.triggered.connect(self.load_subtitle)
        subtitle_menu.addAction(load_subtitle_action)
        
    def create_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        self.play_btn = ModernButton("▶ Play")
        self.play_btn.setMinimumWidth(120)
        self.play_btn.clicked.connect(self.toggle_play_pause)
        toolbar.addWidget(self.play_btn)
        
        self.stop_btn = ModernButton("⏹ Stop")
        self.stop_btn.setMinimumWidth(120)
        self.stop_btn.clicked.connect(self.stop)
        toolbar.addWidget(self.stop_btn)
        
        toolbar.addSeparator()
        
        self.prev_btn = ModernButton("⏮ Previous")
        self.prev_btn.setMinimumWidth(120)
        self.prev_btn.clicked.connect(self.play_previous)
        toolbar.addWidget(self.prev_btn)
        
        self.next_btn = ModernButton("⏭ Next")
        self.next_btn.setMinimumWidth(120)
        self.next_btn.clicked.connect(self.play_next)
        toolbar.addWidget(self.next_btn)
        
    def create_control_panel(self):
        control_panel = QWidget()
        control_panel.setMinimumHeight(140)
        control_panel.setMaximumHeight(140)
        control_panel.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1a1a1a, stop:1 #0f0f0f);
            border-top: 3px solid #2a2a2a;
        """)
        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(20, 15, 20, 15)
        control_layout.setSpacing(15)
        
        # Progress bar and time
        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(15)
        
        self.time_label = QLabel("00:00")
        self.time_label.setMinimumWidth(80)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.time_label.setStyleSheet("color: #0078d4;")
        progress_layout.addWidget(self.time_label)
        
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setMinimum(0)
        self.progress_slider.setMaximum(10000)
        self.progress_slider.sliderPressed.connect(self.seek_pressed)
        self.progress_slider.sliderReleased.connect(self.seek_released)
        self.progress_slider.valueChanged.connect(self.seek_changed)
        progress_layout.addWidget(self.progress_slider)
        
        self.duration_label = QLabel("00:00")
        self.duration_label.setMinimumWidth(80)
        self.duration_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.duration_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.duration_label.setStyleSheet("color: #0078d4;")
        progress_layout.addWidget(self.duration_label)
        
        control_layout.addLayout(progress_layout)
        
        # Volume and other controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(20)
        
        # Volume control
        volume_label = QLabel("🔊")
        volume_label.setMinimumWidth(40)
        volume_label.setFont(QFont("Segoe UI", 14))
        controls_layout.addWidget(volume_label)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(70)
        self.volume_slider.setMaximumWidth(250)
        self.volume_slider.valueChanged.connect(self.set_volume)
        controls_layout.addWidget(self.volume_slider)
        
        self.volume_label = QLabel("70%")
        self.volume_label.setMinimumWidth(60)
        self.volume_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.volume_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        controls_layout.addWidget(self.volume_label)
        
        controls_layout.addStretch()
        
        # Speed control
        speed_label = QLabel("Speed:")
        speed_label.setFont(QFont("Segoe UI", 11))
        controls_layout.addWidget(speed_label)
        
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.25x", "0.5x", "0.75x", "1.0x", "1.25x", "1.5x", "1.75x", "2.0x"])
        self.speed_combo.setCurrentIndex(3)
        self.speed_combo.currentIndexChanged.connect(self.set_speed)
        controls_layout.addWidget(self.speed_combo)
        
        controls_layout.addStretch()
        
        # Repeat and shuffle
        self.repeat_btn = ModernButton("🔁 Repeat")
        self.repeat_btn.setCheckable(True)
        self.repeat_btn.setMinimumWidth(110)
        controls_layout.addWidget(self.repeat_btn)
        
        self.shuffle_btn = ModernButton("🔀 Shuffle")
        self.shuffle_btn.setCheckable(True)
        self.shuffle_btn.setMinimumWidth(110)
        controls_layout.addWidget(self.shuffle_btn)
        
        control_layout.addLayout(controls_layout)

        # Advanced controls row
        advanced_layout = QHBoxLayout()
        advanced_layout.setSpacing(12)

        self.ab_set_a_btn = ModernButton("A⏺")
        self.ab_set_a_btn.clicked.connect(self.set_ab_start)
        advanced_layout.addWidget(self.ab_set_a_btn)

        self.ab_set_b_btn = ModernButton("B⏺")
        self.ab_set_b_btn.clicked.connect(self.set_ab_end)
        advanced_layout.addWidget(self.ab_set_b_btn)

        self.ab_clear_btn = ModernButton("Clear AB")
        self.ab_clear_btn.clicked.connect(self.clear_ab_loop)
        advanced_layout.addWidget(self.ab_clear_btn)

        frame_back = ModernButton("⏪ Frame-")
        frame_back.clicked.connect(lambda: self.frame_step(-50))
        advanced_layout.addWidget(frame_back)

        frame_forward = ModernButton("⏩ Frame+")
        frame_forward.clicked.connect(lambda: self.frame_step(50))
        advanced_layout.addWidget(frame_forward)

        screenshot_btn = ModernButton("📸 Shot")
        screenshot_btn.clicked.connect(self.take_screenshot)
        advanced_layout.addWidget(screenshot_btn)

        bookmark_btn = ModernButton("🔖 Add Mark")
        bookmark_btn.clicked.connect(self.add_bookmark)
        advanced_layout.addWidget(bookmark_btn)

        self.bookmark_combo = QComboBox()
        self.bookmark_combo.setMinimumWidth(180)
        self.bookmark_combo.currentIndexChanged.connect(self.jump_bookmark)
        advanced_layout.addWidget(self.bookmark_combo)

        control_layout.addLayout(advanced_layout)
        
        # Add control panel to main window
        main_layout = self.centralWidget().layout()
        main_layout.addWidget(control_panel)
        
    def setup_media_player(self):
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(0.7)
        
        self.media_player = QMediaPlayer()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)
        
        # Connect signals
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
        self.media_player.playbackStateChanged.connect(self.playback_state_changed)
        self.media_player.errorOccurred.connect(self.handle_error)
        self.media_player.mediaStatusChanged.connect(self.media_status_changed)
            
    def setup_timer(self):
        self.timer = QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start()
        
    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Media File", "",
            "Media Files (*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm *.mp3 *.wav *.flac *.ogg *.m4a *.aac);;All Files (*)"
        )
        if file_path:
            self.add_to_playlist(file_path)
            self.play_file(file_path)
            
    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Open Folder")
        if folder_path:
            media_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm',
                              '.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac']
            count = 0
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in media_extensions):
                        file_path = os.path.join(root, file)
                        self.add_to_playlist(file_path)
                        count += 1
            if count > 0:
                self.status_bar.showMessage(f"Added {count} media files to playlist")
                if self.playlist:
                    self.play_file(self.playlist[0])
            else:
                self.status_bar.showMessage("No media files found in selected folder")
                
    def add_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Add Media Files", "",
            "Media Files (*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm *.mp3 *.wav *.flac *.ogg *.m4a *.aac);;All Files (*)"
        )
        if file_paths:
            for file_path in file_paths:
                self.add_to_playlist(file_path)
            self.status_bar.showMessage(f"Added {len(file_paths)} file(s) to playlist")
            if self.playlist and not self.media_player.source():
                self.play_file(self.playlist[0])
            
    def add_to_playlist(self, file_path):
        if file_path not in self.playlist:
            self.playlist.append(file_path)
            item = QListWidgetItem(os.path.basename(file_path))
            item.setData(Qt.ItemDataRole.UserRole, file_path)
            self.playlist_widget.addItem(item)
            
    def play_file(self, file_path):
        try:
            url = QUrl.fromLocalFile(file_path)
            self.media_player.setSource(url)
            self.current_media_url = url
            self.current_index = self.playlist.index(file_path) if file_path in self.playlist else -1
            self.update_playlist_selection()
            self.status_bar.showMessage(f"Loading: {os.path.basename(file_path)}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load file: {str(e)}")
            self.status_bar.showMessage(f"Error loading file: {str(e)}")
        
    def toggle_play_pause(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.play_btn.setText("▶ Play")
        else:
            if not self.media_player.source():
                if self.playlist:
                    self.play_file(self.playlist[0])
            self.media_player.play()
            self.play_btn.setText("⏸ Pause")
            
    def stop(self):
        self.media_player.stop()
        self.play_btn.setText("▶ Play")
        self.progress_slider.setValue(0)
        self.time_label.setText("00:00")
        self.status_bar.showMessage("Stopped")
        
    def play_previous(self):
        if self.playlist and self.current_index > 0:
            self.current_index -= 1
            self.play_file(self.playlist[self.current_index])
        elif self.playlist and self.repeat_btn.isChecked():
            self.current_index = len(self.playlist) - 1
            self.play_file(self.playlist[self.current_index])
            
    def play_next(self):
        if self.playlist and self.current_index < len(self.playlist) - 1:
            self.current_index += 1
            self.play_file(self.playlist[self.current_index])
        elif self.playlist and self.repeat_btn.isChecked():
            self.current_index = 0
            self.play_file(self.playlist[self.current_index])
        elif self.playlist:
            self.stop()
            
    def play_selected_item(self, item):
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if file_path:
            self.current_index = self.playlist.index(file_path)
            self.play_file(file_path)
            
    def remove_selected(self):
        current_item = self.playlist_widget.currentItem()
        if current_item:
            file_path = current_item.data(Qt.ItemDataRole.UserRole)
            if file_path in self.playlist:
                index = self.playlist.index(file_path)
                self.playlist.remove(file_path)
                self.playlist_widget.takeItem(self.playlist_widget.row(current_item))
                if index == self.current_index:
                    if self.playlist:
                        self.current_index = min(index, len(self.playlist) - 1)
                        if self.current_index >= 0:
                            self.play_file(self.playlist[self.current_index])
                    else:
                        self.stop()
                elif index < self.current_index:
                    self.current_index -= 1
                        
    def clear_playlist(self):
        reply = QMessageBox.question(self, "Clear Playlist", 
                                    "Are you sure you want to clear the playlist?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.playlist.clear()
            self.playlist_widget.clear()
            self.stop()
            self.status_bar.showMessage("Playlist cleared")
        
    def set_volume(self, value):
        self.audio_output.setVolume(value / 100.0)
        self.volume_label.setText(f"{value}%")
        
    def set_speed(self, index):
        speeds = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
        if index < len(speeds):
            self.media_player.setPlaybackRate(speeds[index])
            self.status_bar.showMessage(f"Playback speed: {speeds[index]}x")
            
    def seek_pressed(self):
        self.is_seeking = True
        
    def seek_released(self):
        self.is_seeking = False
        position = self.progress_slider.value() / 10000.0
        duration = self.media_player.duration()
        if duration > 0:
            self.media_player.setPosition(int(position * duration))
        
    def seek_changed(self, value):
        if self.is_seeking:
            position = value / 10000.0
            duration = self.media_player.duration()
            if duration > 0:
                self.media_player.setPosition(int(position * duration))
                
    def position_changed(self, position):
        if not self.is_seeking:
            duration = self.media_player.duration()
            if duration > 0:
                progress = position / duration
                self.progress_slider.setValue(int(progress * 10000))
                self.time_label.setText(self.format_time(position // 1000))
                
    def duration_changed(self, duration):
        if duration > 0:
            self.duration_label.setText(self.format_time(duration // 1000))
            self.status_bar.showMessage(f"Playing: {os.path.basename(self.playlist[self.current_index]) if self.current_index >= 0 and self.current_index < len(self.playlist) else 'Media'}")
            
    def playback_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_btn.setText("⏸ Pause")
        elif state == QMediaPlayer.PlaybackState.PausedState:
            self.play_btn.setText("▶ Play")
        elif state == QMediaPlayer.PlaybackState.StoppedState:
            self.play_btn.setText("▶ Play")
            # Auto-play next
            if self.playlist and self.current_index >= 0 and self.current_index < len(self.playlist) - 1:
                self.play_next()
            elif self.playlist and self.repeat_btn.isChecked() and len(self.playlist) > 0:
                self.current_index = 0
                self.play_file(self.playlist[0])
                
    def media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            self.media_player.play()
                
    def handle_error(self, error, error_string):
        error_msg = error_string if error_string else "Unknown error occurred"
        QMessageBox.warning(self, "Playback Error", f"Error: {error_msg}\n\nMake sure the file format is supported and codecs are installed.")
        self.status_bar.showMessage(f"Error: {error_msg}")
        
    def update_ui(self):
        # UI updates are handled by signals now
        pass
                
    def format_time(self, seconds):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"
        
    def toggle_fullscreen(self):
        if self.video_widget:
            if self.video_widget.isFullScreen():
                self.video_widget.setFullScreen(False)
                self.show()
            else:
                self.video_widget.setFullScreen(True)
            
    def show_equalizer(self):
        if not self.equalizer_dialog:
            self.equalizer_dialog = EqualizerDialog(self.media_player, self)
        self.equalizer_dialog.show()
        
    def load_subtitle(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Subtitle File", "",
            "Subtitle Files (*.srt *.vtt *.ass *.ssa);;All Files (*)"
        )
        if file_path:
            self.subtitle_file = file_path
            self.status_bar.showMessage(f"Subtitle loaded: {os.path.basename(file_path)}")
            
    def update_playlist_selection(self):
        if self.current_index >= 0 and self.current_index < len(self.playlist):
            for i in range(self.playlist_widget.count()):
                item = self.playlist_widget.item(i)
                if item and item.data(Qt.ItemDataRole.UserRole) == self.playlist[self.current_index]:
                    self.playlist_widget.setCurrentItem(item)
                    break
                
    def closeEvent(self, event):
        if self.media_player:
            self.media_player.stop()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application properties
    app.setApplicationName("MediaPlayer")
    app.setOrganizationName("MediaPlayer")
    
    player = MediaPlayer()
    player.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
