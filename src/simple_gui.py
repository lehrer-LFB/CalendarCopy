#!/usr/bin/env python3
"""
Vereinfachte GUI für Kalender-Synchronisation
- Nur EventKit (ultra-schnell)
- Keine Batching/Caching-Komplexität
- Maximale Zuverlässigkeit
"""

import sys
import logging
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QComboBox, QPushButton, 
                            QTextEdit, QProgressBar, QCheckBox, QSpinBox,
                            QTabWidget, QTableWidget, QTableWidgetItem,
                            QHeaderView, QMessageBox)
from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot, Qt
from PyQt6.QtGui import QFont

# Import des vereinfachten Clients
from simple_calendar_client import SimpleCalendarClient, SyncMode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleBackgroundWorker(QThread):
    """Einfacher Background-Worker ohne Komplexität"""
    result = pyqtSignal(object)
    error = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.result.emit(result)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()

class SimpleSyncWorker(QThread):
    """Einfacher Sync-Worker ohne Timer-Komplexität"""
    progress = pyqtSignal(str)
    sync_complete = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, client, source_calendar, target_calendar, sync_mode):
        super().__init__()
        self.client = client
        self.source_calendar = source_calendar
        self.target_calendar = target_calendar
        self.sync_mode = sync_mode
        self.is_running = True

    def run(self):
        try:
            self.progress.emit("🔄 Starte Synchronisation...")
            
            count = self.client.sync_calendars(
                self.source_calendar, 
                self.target_calendar, 
                self.sync_mode
            )
            
            self.sync_complete.emit(count)
            
        except Exception as e:
            self.error.emit(str(e))

    def stop(self):
        self.is_running = False
        self.quit()
        self.wait()

class SimpleCalendarGUI(QMainWindow):
    """
    Vereinfachte Kalender-Sync GUI
    - Ultra-schnell mit EventKit
    - Keine unnötige Komplexität
    - 100% zuverlässig
    """
    
    def __init__(self):
        super().__init__()
        
        try:
            logger.info("🚀 Initialisiere vereinfachte GUI...")
            self.calendar_client = SimpleCalendarClient()
            
            self.current_worker = None
            self.sync_worker = None
            self.is_syncing = False
            self.loaded_events = []
            
            self.init_ui()
            
            # Kalender laden NACH der UI-Initialisierung
            self.refresh_calendars_initial()
            
            logger.info("✅ Vereinfachte GUI erfolgreich gestartet")
            
        except Exception as e:
            logger.error(f"❌ GUI-Initialisierung fehlgeschlagen: {e}")
            QMessageBox.critical(None, "Fehler", f"GUI konnte nicht gestartet werden:\n{e}")
            sys.exit(1)

    def init_ui(self):
        """Initialisiert die einfache Benutzeroberfläche"""
        self.setWindowTitle('📅 Kalender Sync')
        self.setGeometry(100, 100, 700, 500)
        
        # Hauptwidget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Header
        header_label = QLabel("Sychronisation von Kalendern")
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(14)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Tabs
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Tab 1: Einfache Synchronisation
        self.sync_tab = QWidget()
        self.tab_widget.addTab(self.sync_tab, "🔄 Synchronisation")
        self.setup_sync_tab()
        
        # Tab 2: Manuelle Auswahl
        self.manual_tab = QWidget()
        self.tab_widget.addTab(self.manual_tab, "📋 Manuelle Auswahl der Ereignisse")
        self.setup_manual_tab()
        
        # Status-Bereich
        status_layout = QVBoxLayout()
        status_layout.addWidget(QLabel("📊 Status:"))
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(120)
        self.status_text.setFont(QFont("Monaco", 10))
        status_layout.addWidget(self.status_text)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        layout.addLayout(status_layout)
        
        # Info-Label
        info_label = QLabel("ℹ️ Powered by claude-4-sonnet")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(info_label)

    def setup_sync_tab(self):
        """Erstellt den einfachen Sync-Tab"""
        layout = QVBoxLayout(self.sync_tab)
        
        # Kalender-Auswahl
        calendar_layout = QHBoxLayout()
        
        calendar_layout.addWidget(QLabel('📁 Quelle:'))
        self.source_combo = QComboBox()
        self.source_combo.setMinimumWidth(200)
        calendar_layout.addWidget(self.source_combo)
        
        calendar_layout.addWidget(QLabel('📁 Ziel:'))
        self.target_combo = QComboBox()
        self.target_combo.setMinimumWidth(200)
        calendar_layout.addWidget(self.target_combo)
        
        layout.addLayout(calendar_layout)
        
        # Sync-Modus
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel('🕐 Modus:'))
        
        self.mode_all = QCheckBox('Alle Ereignisse')
        self.mode_all.setChecked(True)
        mode_layout.addWidget(self.mode_all)
        
        self.mode_future = QCheckBox('Nur zukünftige')
        mode_layout.addWidget(self.mode_future)
        
        # Gegenseitiger Ausschluss
        self.mode_all.toggled.connect(lambda checked: self.mode_future.setChecked(not checked) if checked else None)
        self.mode_future.toggled.connect(lambda checked: self.mode_all.setChecked(not checked) if checked else None)
        
        layout.addLayout(mode_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.sync_button = QPushButton('🚀 Synchronisation starten')
        self.sync_button.clicked.connect(self.start_sync)
        self.sync_button.setMinimumHeight(40)
        button_layout.addWidget(self.sync_button)
        
        self.refresh_button = QPushButton('🔄 Kalender aktualisieren')
        self.refresh_button.clicked.connect(self.refresh_calendars_threaded)
        button_layout.addWidget(self.refresh_button)
        
        layout.addLayout(button_layout)
        
        layout.addStretch()

    def setup_manual_tab(self):
        """Erstellt den Tab für manuelle Event-Auswahl"""
        layout = QVBoxLayout(self.manual_tab)
        
        # Kalender-Auswahl
        calendar_layout = QHBoxLayout()
        calendar_layout.addWidget(QLabel('📁 Quelle:'))
        self.manual_source_combo = QComboBox()
        calendar_layout.addWidget(self.manual_source_combo)
        
        calendar_layout.addWidget(QLabel('📁 Ziel:'))
        self.manual_target_combo = QComboBox()
        calendar_layout.addWidget(self.manual_target_combo)
        layout.addLayout(calendar_layout)
        
        # Load-Buttons
        load_layout = QHBoxLayout()
        self.load_events_button = QPushButton('📋 Events laden')
        self.load_events_button.clicked.connect(self.load_events_threaded)
        load_layout.addWidget(self.load_events_button)
        
        self.select_all_button = QPushButton('✅ Alle auswählen')
        self.select_all_button.clicked.connect(self.select_all_events)
        load_layout.addWidget(self.select_all_button)
        
        self.deselect_all_button = QPushButton('❌ Alle abwählen')
        self.deselect_all_button.clicked.connect(self.deselect_all_events)
        load_layout.addWidget(self.deselect_all_button)
        layout.addLayout(load_layout)
        
        # Event-Tabelle
        self.events_table = QTableWidget()
        self.events_table.setColumnCount(4)
        self.events_table.setHorizontalHeaderLabels(['✓', 'Titel', 'Datum', 'Beschreibung'])
        
        header = self.events_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.events_table)
        
        # Sync-Button
        self.sync_selected_button = QPushButton('🚀 Ausgewählte synchronisieren')
        self.sync_selected_button.clicked.connect(self.sync_selected_events)
        self.sync_selected_button.setEnabled(False)
        layout.addWidget(self.sync_selected_button)

    def refresh_calendars_initial(self):
        """Lädt Kalender beim Start ohne UI-Manipulation"""
        if self.current_worker and self.current_worker.isRunning():
            return
            
        self.log_status("📋 Lade Kalender...")
        
        self.current_worker = SimpleBackgroundWorker(self.calendar_client.list_calendars)
        self.current_worker.result.connect(self._on_calendars_loaded)
        self.current_worker.error.connect(self.log_error)
        self.current_worker.finished.connect(lambda: None)  # Keine Button-Updates beim Start
        self.current_worker.start()

    def refresh_calendars_threaded(self):
        """Lädt Kalender im Hintergrund (für Button-Klick)"""
        if self.current_worker and self.current_worker.isRunning():
            return
            
        self.refresh_button.setEnabled(False)
        self.log_status("📋 Lade Kalender...")
        
        self.current_worker = SimpleBackgroundWorker(self.calendar_client.list_calendars)
        self.current_worker.result.connect(self._on_calendars_loaded)
        self.current_worker.error.connect(self.log_error)
        self.current_worker.finished.connect(lambda: self.refresh_button.setEnabled(True))
        self.current_worker.start()

    def _on_calendars_loaded(self, calendars):
        """Verarbeitet geladene Kalender"""
        try:
            # Aktualisiere alle Dropdowns
            for combo in [self.source_combo, self.target_combo, 
                         self.manual_source_combo, self.manual_target_combo]:
                combo.clear()
                combo.addItems(calendars)
            
            self.log_status(f"✅ {len(calendars)} Kalender geladen")
            
        except Exception as e:
            self.log_error(f"Fehler beim Verarbeiten der Kalender: {e}")

    @pyqtSlot()
    def start_sync(self):
        """Startet die Synchronisation"""
        if self.is_syncing:
            self.stop_sync()
            return
            
        source = self.source_combo.currentText()
        target = self.target_combo.currentText()
        
        if not source or not target:
            self.log_error("❌ Bitte Quell- und Zielkalender auswählen")
            return
            
        if source == target:
            self.log_error("❌ Quell- und Zielkalender müssen unterschiedlich sein")
            return
        
        sync_mode = SyncMode.ALL if self.mode_all.isChecked() else SyncMode.FUTURE
        
        self.is_syncing = True
        self.sync_button.setText('⏹️ Stoppen')
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        self.sync_worker = SimpleSyncWorker(self.calendar_client, source, target, sync_mode)
        self.sync_worker.progress.connect(self.log_status)
        self.sync_worker.sync_complete.connect(self._on_sync_complete)
        self.sync_worker.error.connect(self.log_error)
        self.sync_worker.start()
        
        self.log_status(f"🚀 Sync gestartet: {source} → {target}")

    def stop_sync(self):
        """Stoppt die Synchronisation"""
        if self.sync_worker:
            self.sync_worker.stop()
            self.sync_worker = None
        
        self.is_syncing = False
        self.sync_button.setText('🚀 Synchronisation starten')
        self.progress_bar.setVisible(False)
        self.log_status("⏹️ Synchronisation gestoppt")

    def _on_sync_complete(self, count):
        """Verarbeitet Sync-Abschluss"""
        self.stop_sync()
        self.log_status(f"✅ Synchronisation abgeschlossen: {count} Ereignisse übertragen")

    def load_events_threaded(self):
        """Lädt Events für manuelle Auswahl"""
        source = self.manual_source_combo.currentText()
        if not source:
            self.log_error("❌ Bitte Quellkalender auswählen")
            return
        
        if self.current_worker and self.current_worker.isRunning():
            return
        
        self.load_events_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        self.current_worker = SimpleBackgroundWorker(
            self.calendar_client.get_events, source, SyncMode.FUTURE
        )
        self.current_worker.result.connect(self._on_events_loaded)
        self.current_worker.error.connect(self.log_error)
        self.current_worker.finished.connect(lambda: [
            self.load_events_button.setEnabled(True),
            self.progress_bar.setVisible(False)
        ])
        self.current_worker.start()

    def _on_events_loaded(self, events):
        """Verarbeitet geladene Events"""
        self.loaded_events = events or []
        
        if not self.loaded_events:
            self.log_status("ℹ️ Keine zukünftigen Events gefunden")
            self.events_table.setRowCount(0)
            self.sync_selected_button.setEnabled(False)
            return
        
        # Fülle Tabelle
        self.events_table.setRowCount(len(self.loaded_events))
        
        for row, event in enumerate(self.loaded_events):
            # Checkbox
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            self.events_table.setCellWidget(row, 0, checkbox)
            
            # Titel
            title = event.get('summary', 'Kein Titel')
            self.events_table.setItem(row, 1, QTableWidgetItem(title))
            
            # Datum
            start_date = event.get('start_date')
            date_str = start_date.strftime('%d.%m.%Y %H:%M') if start_date else 'Unbekannt'
            self.events_table.setItem(row, 2, QTableWidgetItem(date_str))
            
            # Beschreibung
            desc = event.get('description', '')[:50] + ('...' if len(event.get('description', '')) > 50 else '')
            self.events_table.setItem(row, 3, QTableWidgetItem(desc))
        
        self.sync_selected_button.setEnabled(True)
        self.log_status(f"📋 {len(self.loaded_events)} Events geladen")

    @pyqtSlot()
    def select_all_events(self):
        for row in range(self.events_table.rowCount()):
            checkbox = self.events_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(True)

    @pyqtSlot()
    def deselect_all_events(self):
        for row in range(self.events_table.rowCount()):
            checkbox = self.events_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(False)

    def sync_selected_events(self):
        """Synchronisiert ausgewählte Events"""
        target = self.manual_target_combo.currentText()
        if not target:
            self.log_error("❌ Bitte Zielkalender auswählen")
            return
        
        # Sammle ausgewählte Events
        selected_events = []
        for row in range(self.events_table.rowCount()):
            checkbox = self.events_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked() and row < len(self.loaded_events):
                selected_events.append(self.loaded_events[row])
        
        if not selected_events:
            self.log_error("❌ Keine Events ausgewählt")
            return
        
        self.sync_selected_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(selected_events))
        
        self.current_worker = SimpleBackgroundWorker(
            self.calendar_client.create_events_simple, target, selected_events
        )
        self.current_worker.result.connect(lambda result: [
            self.sync_selected_button.setEnabled(True),
            self.progress_bar.setVisible(False),
            self.log_status(f"✅ Manuelle Sync: {result[0]}/{len(selected_events)} Events erfolgreich")
        ])
        self.current_worker.error.connect(self.log_error)
        self.current_worker.start()

    def log_status(self, message):
        """Fügt Status-Nachricht hinzu"""
        self.status_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        scrollbar = self.status_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def log_error(self, message):
        """Fügt Fehler-Nachricht hinzu"""
        self.log_status(f"❌ FEHLER: {message}")

def main():
    app = QApplication(sys.argv)
    
    try:
        gui = SimpleCalendarGUI()
        gui.show()
        
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"❌ Anwendung konnte nicht gestartet werden: {e}")
        QMessageBox.critical(None, "Kritischer Fehler", 
                           f"Anwendung konnte nicht gestartet werden:\n{e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 