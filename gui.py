#!/usr/bin/env python3
"""
Aim Assist Gui
"""

import sys
import json
import time
from typing import Dict, Any
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QPushButton, QLabel, QSlider, QCheckBox, QFrame,
    QGridLayout, QGroupBox, QProgressBar, QComboBox, QSpinBox,
    QFileDialog, QMessageBox, QStatusBar, QSplitter
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon, QPixmap, QPainter, QLinearGradient

from config import Config
from core import Core

THEMES = {
    'dark': {
        'bg': '#1e1e1e',
        'fg': '#ffffff',
        'accent': '#007acc',
        'success': '#28a745',
        'warning': '#ffc107',
        'danger': '#dc3545',
        'secondary': '#6c757d',
        'card_bg': '#2d2d2d',
        'border': '#404040',
        'text_muted': '#adb5bd'
    },
    'light': {
        'bg': '#f8f9fa',
        'fg': '#212529',
        'accent': '#007acc',
        'success': '#28a745',
        'warning': '#ffc107',
        'danger': '#dc3545',
        'secondary': '#6c757d',
        'card_bg': '#ffffff',
        'border': '#dee2e6',
        'text_muted': '#6c757d'
    }
}

translations = {
    'pt': {
        'start_system': "Iniciar Sistema",
        'stop_system': "Parar Sistema",
        'enable_mapping': "Ativar Mapeamento",
        'disable_mapping': "Desativar Mapeamento",
        'system_running': "Sistema em Execução",
        'system_stopped': "Sistema Parado",
        'mapping_enabled': "Mapeamento Ativado",
        'mapping_disabled': "Mapeamento Desativado",
        'save_settings': "Salvar Configurações",
        'load_settings': "Carregar Configurações",
        'restore_defaults': "Restaurar Padrões",
        'sensitivity': "Sensibilidade",
        'deadzone': "Zona Morta",
        'recoil_strength': "Força do Recuo",
        'reset_delay': "Atraso de Reset (ms)",
        'recoil_enabled': "Controle de Recuo Ativo",
        'dashboard': "Painel Principal",
        'settings': "Configurações",
        'statistics': "Estatísticas",
        'runtime': "Tempo de Execução",
        'total_movements': "Movimentos Totais",
        'total_clicks': "Cliques Totais",
        'recoil_activations': "Ativações do Recuo",
        'movements_per_sec': "Movimentos/Segundo",
        'reset_stats': "Zerar Estatísticas",
        'status': "Status",
        'system_initialized': "Sistema Inicializado",
        'error_initializing': "Erro ao inicializar",
        'connected': "Conectado",
        'disconnected': "Desconectado"
    },
    'en': {
        'start_system': "Start System",
        'stop_system': "Stop System",
        'enable_mapping': "Enable Mapping",
        'disable_mapping': "Disable Mapping",
        'system_running': "System Running",
        'system_stopped': "System Stopped",
        'mapping_enabled': "Mapping Enabled",
        'mapping_disabled': "Mapping Disabled",
        'save_settings': "Save Settings",
        'load_settings': "Load Settings",
        'restore_defaults': "Restore Defaults",
        'sensitivity': "Sensitivity",
        'deadzone': "Deadzone",
        'recoil_strength': "Recoil Strength",
        'reset_delay': "Reset Delay (ms)",
        'recoil_enabled': "Recoil Control Active",
        'dashboard': "Dashboard",
        'settings': "Settings",
        'statistics': "Statistics",
        'runtime': "Runtime",
        'total_movements': "Total Movements",
        'total_clicks': "Total Clicks",
        'recoil_activations': "Recoil Activations",
        'movements_per_sec': "Movements/Second",
        'reset_stats': "Reset Statistics",
        'status': "Status",
        'system_initialized': "System Initialized",
        'error_initializing': "Error during initialization",
        'connected': "Connected",
        'disconnected': "Disconnected"
    }
}

class ModernCard(QFrame):
    def __init__(self, title: str = None, parent=None):
        super().__init__(parent)
        self.setObjectName("ModernCard")
        self.setStyleSheet("""
            QFrame#ModernCard {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(12)
        
        if title:
            title_label = QLabel(title)
            title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            title_label.setStyleSheet("color: #ffffff; margin-bottom: 8px;")
            self.layout.addWidget(title_label)

class StatusIndicator(QWidget):

    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel(label)
        self.label.setFont(QFont("Segoe UI", 10))
        self.label.setStyleSheet("color: #adb5bd;")
        layout.addWidget(self.label)
        
        self.status_label = QLabel("⭕ Offline")
        self.status_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.status_label.setStyleSheet("color: #dc3545;")
        layout.addWidget(self.status_label)
    
    def set_status(self, status: str):
        """Set the status indicator"""
        if status == "online" or status == "running":
            self.status_label.setText("🟢 Online")
            self.status_label.setStyleSheet("color: #28a745;")
        elif status == "offline" or status == "stopped":
            self.status_label.setText("⭕ Offline")
            self.status_label.setStyleSheet("color: #dc3545;")
        elif status == "warning":
            self.status_label.setText("🟡 Warning")
            self.status_label.setStyleSheet("color: #ffc107;")

class MetricCard(QWidget):
    """Modern metric display card"""
    
    def __init__(self, title: str, value: str = "0", icon: str = "📊", parent=None):
        super().__init__(parent)
        self.setObjectName("MetricCard")
        self.setStyleSheet("""
            QWidget#MetricCard {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 16))
        icon_label.setStyleSheet("color: #007acc;")
        header_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 10))
        title_label.setStyleSheet("color: #ffffff;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.value_label.setStyleSheet("color: #007acc; text-align: center;")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.value_label)
    
    def update_value(self, value: str):
        """Update the metric value"""
        self.value_label.setText(str(value))

class ModernSlider(QWidget):
    """Modern slider widget with value display"""
    
    def __init__(self, label: str, min_val: int, max_val: int, default_val: int, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        header_layout = QHBoxLayout()
        
        label_widget = QLabel(label)
        label_widget.setFont(QFont("Segoe UI", 10))
        label_widget.setStyleSheet("color: #ffffff;")
        header_layout.addWidget(label_widget)
        
        header_layout.addStretch()
        
        self.value_label = QLabel(str(default_val))
        self.value_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.value_label.setStyleSheet("color: #007acc;")
        header_layout.addWidget(self.value_label)
        
        layout.addLayout(header_layout)
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(min_val)
        self.slider.setMaximum(max_val)
        self.slider.setValue(default_val)
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #404040;
                height: 8px;
                background: #2d2d2d;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #007acc;
                border: 1px solid #007acc;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
            QSlider::sub-page:horizontal {
                background: #007acc;
                border-radius: 4px;
            }
        """)
        
        self.slider.valueChanged.connect(self.on_value_changed)
        layout.addWidget(self.slider)
    
    def on_value_changed(self, value):
        """Handle slider value change"""
        self.value_label.setText(str(value))
    
    def value(self):
        """Get current value"""
        return self.slider.value()
    
    def set_value(self, value):
        """Set slider value"""
        self.slider.setValue(value)

class StatsThread(QThread):
    """Thread for updating statistics"""
    stats_updated = pyqtSignal(dict)
    
    def __init__(self, core):
        super().__init__()
        self.core = core
        self.running = True
    
    def run(self):
        while self.running:
            if self.core:
                stats = self.core.stats
                current_time = time.time()
                runtime = current_time - stats['start_time']
                movements_per_sec = stats['total_movements'] / max(runtime, 1)
                
                stats_data = {
                    'runtime': f"{runtime:.1f}s",
                    'total_movements': str(stats['total_movements']),
                    'total_clicks': str(stats['total_clicks']),
                    'recoil_activations': str(stats['recoil_activations']),
                    'movements_per_sec': f"{movements_per_sec:.1f}"
                }
                
                self.stats_updated.emit(stats_data)
            
            time.sleep(1)
    
    def stop(self):
        """Stop the thread"""
        self.running = False

class AimAssistGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_theme = 'dark'
        self.current_language = 'en'
        self.config = Config()
        self.core = None
        self.system_running = False
        self.stats_thread = None
        
        self.setup_ui()
        self.apply_theme()
        self.initialize_core()
        self.start_stats_thread()
    
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("🎯 Aim Assist")
        self.setGeometry(100, 100, 1200, 1020)
        self.setMinimumSize(800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        self.setup_header(main_layout)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #404040;
                border-radius: 8px;
                background-color: #2d2d2d;
            }
            QTabBar::tab {
                background-color: #1e1e1e;
                color: #ffffff;
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background-color: #007acc;
            }
            QTabBar::tab:hover {
                background-color: #0056b3;
            }
        """)
        
        self.setup_dashboard_tab()
        self.setup_settings_tab()
        self.setup_statistics_tab()
        
        main_layout.addWidget(self.tab_widget)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("System Stopped")
    
    def setup_header(self, layout):
        """Setup the header with title and controls"""
        header_frame = QFrame()
        header_frame.setObjectName("HeaderFrame")
        header_frame.setStyleSheet("""
            QFrame#HeaderFrame {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        
        title_label = QLabel("🎯 Aim Assist Pro")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #ffffff;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        theme_label = QLabel("🎨 Theme:")
        theme_label.setStyleSheet("color: #adb5bd;")
        header_layout.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.setCurrentText("Dark")
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        self.theme_combo.setStyleSheet("""
            QComboBox {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
                min-width: 100px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
            }
        """)
        header_layout.addWidget(self.theme_combo)
        
        lang_label = QLabel("🌍 Language:")
        lang_label.setStyleSheet("color: #adb5bd;")
        header_layout.addWidget(lang_label)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Português"])
        self.lang_combo.setCurrentText("English")
        self.lang_combo.currentTextChanged.connect(self.change_language)
        self.lang_combo.setStyleSheet("""
            QComboBox {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
                min-width: 100px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
            }
        """)
        header_layout.addWidget(self.lang_combo)
        
        layout.addWidget(header_frame)
    
    def setup_dashboard_tab(self):
        """Setup the dashboard tab"""
        dashboard_widget = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_widget)
        dashboard_layout.setSpacing(20)
        
        status_card = ModernCard("System Status")
        status_layout = QHBoxLayout()
        
        self.system_status = StatusIndicator("System")
        self.mapping_status = StatusIndicator("Mapping")
        self.connection_status = StatusIndicator("Connection")
        
        status_layout.addWidget(self.system_status)
        status_layout.addWidget(self.mapping_status)
        status_layout.addWidget(self.connection_status)
        status_layout.addStretch()
        
        status_card.layout.addLayout(status_layout)
        
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("▶️ Start System")
        self.start_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e7e34;
            }
            QPushButton:pressed {
                background-color: #155724;
            }
        """)
        self.start_button.clicked.connect(self.toggle_system)
        button_layout.addWidget(self.start_button)
        
        self.enable_button = QPushButton("🎯 Enable Mapping")
        self.enable_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.enable_button.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.enable_button.clicked.connect(self.toggle_mapping)
        self.enable_button.setEnabled(False)
        button_layout.addWidget(self.enable_button)
        
        button_layout.addStretch()
        status_card.layout.addLayout(button_layout)
        
        dashboard_layout.addWidget(status_card)
        
        controls_card = ModernCard("Quick Controls")
        
        self.sens_slider = ModernSlider("🎯 Sensitivity", 1000, 20000, int(self.config.sens))
        self.sens_slider.slider.valueChanged.connect(self.on_sensitivity_change)
        
        self.deadzone_slider = ModernSlider("🎮 Deadzone", 0, 20, self.config.deadzone)
        self.deadzone_slider.slider.valueChanged.connect(self.on_deadzone_change)
        
        self.recoil_checkbox = QCheckBox("🔫 Recoil Control")
        self.recoil_checkbox.setFont(QFont("Segoe UI", 10))
        self.recoil_checkbox.setStyleSheet("""
            QCheckBox {
                color: #ffffff;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #404040;
                border-radius: 3px;
                background-color: #2d2d2d;
            }
            QCheckBox::indicator:checked {
                background-color: #007acc;
                border-color: #007acc;
            }
        """)
        self.recoil_checkbox.setChecked(self.config.recoil_enabled)
        self.recoil_checkbox.toggled.connect(self.on_recoil_toggle)
        
        controls_layout = QVBoxLayout()
        controls_layout.addWidget(self.sens_slider)
        controls_layout.addWidget(self.deadzone_slider)
        controls_layout.addWidget(self.recoil_checkbox)
        controls_card.layout.addLayout(controls_layout)
        
        dashboard_layout.addWidget(controls_card)
        
        metrics_card = ModernCard("Performance Metrics")
        metrics_layout = QGridLayout()
        
        self.runtime_metric = MetricCard("Runtime", "0.0s", "⏱️")
        self.movements_metric = MetricCard("Movements", "0", "🔄")
        self.clicks_metric = MetricCard("Clicks", "0", "🖱️")
        self.recoil_metric = MetricCard("Recoil", "0", "🔫")
        
        metrics_layout.addWidget(self.runtime_metric, 0, 0)
        metrics_layout.addWidget(self.movements_metric, 0, 1)
        metrics_layout.addWidget(self.clicks_metric, 1, 0)
        metrics_layout.addWidget(self.recoil_metric, 1, 1)
        
        metrics_card.layout.addLayout(metrics_layout)
        dashboard_layout.addWidget(metrics_card)
        
        dashboard_layout.addStretch()
        
        self.tab_widget.addTab(dashboard_widget, "📊 Dashboard")
    
    def setup_settings_tab(self):
        """Setup the settings tab"""
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.setSpacing(20)
        
        advanced_card = ModernCard("Advanced Settings")
        
        self.reset_delay_slider = ModernSlider("⏳ Reset Delay (ms)", 5, 100, int(self.config.reset_delay * 1000))
        self.reset_delay_slider.slider.valueChanged.connect(self.on_reset_delay_change)
        
        self.recoil_strength_slider = ModernSlider("💪 Recoil Strength", 100, 1500, self.config.recoil_strength)
        self.recoil_strength_slider.slider.valueChanged.connect(self.on_recoil_strength_change)
        
        advanced_layout = QVBoxLayout()
        advanced_layout.addWidget(self.reset_delay_slider)
        advanced_layout.addWidget(self.recoil_strength_slider)
        advanced_card.layout.addLayout(advanced_layout)
        
        settings_layout.addWidget(advanced_card)
        
        config_card = ModernCard("Configuration Management")
        config_layout = QHBoxLayout()
        
        save_button = QPushButton("💾 Save Settings")
        save_button.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        save_button.clicked.connect(self.save_config)
        config_layout.addWidget(save_button)
        
        load_button = QPushButton("📂 Load Settings")
        load_button.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        load_button.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        load_button.clicked.connect(self.load_config)
        config_layout.addWidget(load_button)
        
        reset_button = QPushButton("🔄 Restore Defaults")
        reset_button.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        reset_button.clicked.connect(self.reset_config)
        config_layout.addWidget(reset_button)
        
        config_layout.addStretch()
        config_card.layout.addLayout(config_layout)
        
        settings_layout.addWidget(config_card)
        settings_layout.addStretch()
        
        self.tab_widget.addTab(settings_widget, "⚙️ Settings")
    
    def setup_statistics_tab(self):
        """Setup the statistics tab"""
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)
        stats_layout.setSpacing(20)
        
        stats_card = ModernCard("System Statistics")
        
        self.detailed_stats = {}
        stats_info = [
            ('runtime', '⏱️ Runtime'),
            ('total_movements', '🔄 Total Movements'),
            ('total_clicks', '🖱️ Total Clicks'),
            ('recoil_activations', '🔫 Recoil Activations'),
            ('movements_per_sec', '⚡ Movements/Second'),
        ]
        
        stats_grid = QGridLayout()
        for i, (key, label) in enumerate(stats_info):
            label_widget = QLabel(label)
            label_widget.setFont(QFont("Segoe UI", 10))
            label_widget.setStyleSheet("color: #ffffff;")
            
            value_widget = QLabel("0")
            value_widget.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            value_widget.setStyleSheet("color: #007acc;")
            
            stats_grid.addWidget(label_widget, i, 0)
            stats_grid.addWidget(value_widget, i, 1)
            
            self.detailed_stats[key] = value_widget
        
        stats_card.layout.addLayout(stats_grid)
        
        reset_stats_button = QPushButton("🔄 Reset Statistics")
        reset_stats_button.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        reset_stats_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        reset_stats_button.clicked.connect(self.reset_stats)
        stats_card.layout.addWidget(reset_stats_button)
        
        stats_layout.addWidget(stats_card)
        stats_layout.addStretch()
        
        self.tab_widget.addTab(stats_widget, "📈 Statistics")
    
    def apply_theme(self):
        """Apply the current theme"""
        theme = THEMES[self.current_theme]
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(theme['bg']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(theme['fg']))
        palette.setColor(QPalette.ColorRole.Base, QColor(theme['card_bg']))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(theme['border']))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(theme['card_bg']))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(theme['fg']))
        palette.setColor(QPalette.ColorRole.Text, QColor(theme['fg']))
        palette.setColor(QPalette.ColorRole.Button, QColor(theme['accent']))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor('white'))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(theme['danger']))
        palette.setColor(QPalette.ColorRole.Link, QColor(theme['accent']))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(theme['accent']))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor('white'))
        
        self.setPalette(palette)
    
    def change_theme(self, theme_name):
        """Change the application theme"""
        self.current_theme = 'light' if theme_name == "Light" else 'dark'
        self.apply_theme()
    
    def change_language(self, language):
        """Change the application language"""
        self.current_language = 'pt' if language == "Português" else 'en'
        self.update_language()
    
    def update_language(self):
        """Update all text elements with current language"""
        lang = translations[self.current_language]
        
        if self.current_language == 'pt':
            self.setWindowTitle("🎯 Assistente de Mira Pro")
        else:
            self.setWindowTitle("🎯 Aim Assist Pro")
        
        if self.system_running:
            self.start_button.setText("⏹️ " + lang['stop_system'])
        else:
            self.start_button.setText("▶️ " + lang['start_system'])
        
        if hasattr(self, 'vars') and self.vars.get('enabled', False):
            self.enable_button.setText("⏹️ " + lang['disable_mapping'])
        else:
            self.enable_button.setText("🎯 " + lang['enable_mapping'])
        
        if self.system_running:
            self.system_status.set_status("running")
        else:
            self.system_status.set_status("stopped")
        
        if hasattr(self, 'vars') and self.vars.get('enabled', False):
            self.mapping_status.set_status("online")
        else:
            self.mapping_status.set_status("offline")
        
        if self.core:
            self.connection_status.set_status("online")
        else:
            self.connection_status.set_status("offline")
    
    def initialize_core(self):
        """Initialize the core system"""
        try:
            self.core = Core(self.config, self.gui_callback)
            self.status_bar.showMessage("System Initialized")
            self.connection_status.set_status("online")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to initialize system:\n{e}")
            self.status_bar.showMessage("Error during initialization")
            self.connection_status.set_status("offline")
    
    def start_stats_thread(self):
        """Start the statistics update thread"""
        if self.core:
            self.stats_thread = StatsThread(self.core)
            self.stats_thread.stats_updated.connect(self.update_stats)
            self.stats_thread.start()
    
    def gui_callback(self, msg_type, message):
        """Handle callbacks from the core system"""
        if msg_type == "error":
            QMessageBox.critical(self, "Error", message)
        elif msg_type == "info":
            self.status_bar.showMessage(message)
    
    def toggle_system(self):
        """Toggle the system on/off"""
        if not self.core:
            return
        
        if not self.system_running:
            if self.core.start():
                self.system_running = True
                self.start_button.setText("⏹️ Stop System")
                self.start_button.setStyleSheet("""
                    QPushButton {
                        background-color: #dc3545;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 12px 24px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #c82333;
                    }
                """)
                self.enable_button.setEnabled(True)
                self.system_status.set_status("running")
                self.status_bar.showMessage("System Started - use 'Enable Mapping' to begin")
            else:
                QMessageBox.critical(self, "Error", "Failed to start system")
        else:
            self.core.stop()
            self.system_running = False
            self.start_button.setText("▶️ Start System")
            self.start_button.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 12px 24px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1e7e34;
                }
            """)
            self.enable_button.setEnabled(False)
            self.enable_button.setText("🎯 Enable Mapping")
            self.system_status.set_status("stopped")
            self.mapping_status.set_status("offline")
            self.status_bar.showMessage("System Stopped")
    
    def toggle_mapping(self):
        """Toggle mapping on/off"""
        if not self.core:
            return
        
        enabled = getattr(self, 'mapping_enabled', False)
        self.core.set_enabled(not enabled)
        self.mapping_enabled = not enabled
        
        if not enabled:
            self.enable_button.setText("⏹️ Disable Mapping")
            self.enable_button.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 12px 24px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
            self.mapping_status.set_status("online")
            self.status_bar.showMessage("Mapping Enabled")
        else:
            self.enable_button.setText("🎯 Enable Mapping")
            self.enable_button.setStyleSheet("""
                QPushButton {
                    background-color: #007acc;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 12px 24px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
            """)
            self.mapping_status.set_status("offline")
            self.status_bar.showMessage("Mapping Disabled")
    
    def on_sensitivity_change(self, value):
        """Handle sensitivity change"""
        self.config.sens = value
        if self.core:
            self.core.config.sens = value
    
    def on_deadzone_change(self, value):
        """Handle deadzone change"""
        self.config.deadzone = value
        if self.core:
            self.core.config.deadzone = value
    
    def on_reset_delay_change(self, value):
        """Handle reset delay change"""
        self.config.reset_delay = value / 1000
        if self.core:
            self.core.config.reset_delay = value / 1000
    
    def on_recoil_strength_change(self, value):
        """Handle recoil strength change"""
        self.config.recoil_strength = value
        if self.core:
            self.core.config.recoil_strength = value
    
    def on_recoil_toggle(self, checked):
        """Handle recoil toggle"""
        self.config.recoil_enabled = checked
        if self.core:
            self.core.recoil_enabled = checked
    
    def save_config(self):
        """Save configuration to file"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Save Configurations", "", "JSON files (*.json);;All files (*.*)"
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.config.__dict__, f, indent=2, ensure_ascii=False)
                QMessageBox.information(self, "Success", f"Configurations saved to:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving configurations:\n{e}")
    
    def load_config(self):
        """Load configuration from file"""
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self, "Load Configurations", "", "JSON files (*.json);;All files (*.*)"
            )
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for key, value in data.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
                
                self.update_ui_from_config()
                
                if self.core:
                    self.core.config = self.config
                
                QMessageBox.information(self, "Success", f"Configurations loaded from:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading configurations:\n{e}")
    
    def reset_config(self):
        """Reset configuration to defaults"""
        reply = QMessageBox.question(
            self, "Confirm", "Restore all configurations to default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.config = Config()
            self.update_ui_from_config()
            if self.core:
                self.core.config = self.config
            QMessageBox.information(self, "Success", "Configurations restored to default values")
    
    def update_ui_from_config(self):
        """Update UI elements from configuration"""
        self.sens_slider.set_value(int(self.config.sens))
        self.deadzone_slider.set_value(self.config.deadzone)
        self.reset_delay_slider.set_value(int(self.config.reset_delay * 1000))
        self.recoil_strength_slider.set_value(self.config.recoil_strength)
        self.recoil_checkbox.setChecked(self.config.recoil_enabled)
    
    def reset_stats(self):
        """Reset statistics"""
        if self.core:
            self.core.stats = {
                'total_movements': 0,
                'total_clicks': 0,
                'recoil_activations': 0,
                'start_time': time.time()
            }
    
    def update_stats(self, stats_data):
        """Update statistics display"""
        self.runtime_metric.update_value(stats_data['runtime'])
        self.movements_metric.update_value(stats_data['total_movements'])
        self.clicks_metric.update_value(stats_data['total_clicks'])
        self.recoil_metric.update_value(stats_data['recoil_activations'])
        
        for key, value in stats_data.items():
            if key in self.detailed_stats:
                self.detailed_stats[key].setText(value)
    
    def closeEvent(self, event):
        """Handle application closing"""
        if self.system_running:
            reply = QMessageBox.question(
                self, "Confirm", "The system is running. Do you really want to exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.core:
                    self.core.stop()
                if self.stats_thread:
                    self.stats_thread.stop()
                    self.stats_thread.wait()
                event.accept()
            else:
                event.ignore()
        else:
            if self.stats_thread:
                self.stats_thread.stop()
                self.stats_thread.wait()
            event.accept()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    app.setApplicationName("Aim Assist Pro")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Aim Assist")
    
    window = AimAssistGUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
