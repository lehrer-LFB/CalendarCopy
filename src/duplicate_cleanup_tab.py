import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QComboBox, QLabel, QTableWidget, QTableWidgetItem, 
                            QCheckBox, QProgressBar, QTextEdit, QMessageBox,
                            QHeaderView, QFrame)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont
from typing import List, Dict, Any
import logging
from dataclasses import dataclass
from datetime import datetime

# Import des vereinfachten Clients
from simple_calendar_client import SimpleCalendarClient, DuplicateCheckMode

logger = logging.getLogger(__name__)

@dataclass
class DuplicateGroup:
    """Repräsentiert eine Gruppe von Duplikaten"""
    events: List[Dict[str, Any]]
    key: str
    
    def __len__(self):
        return len(self.events)

class DuplicateSearchWorker(QThread):
    """Worker für Duplikatsuche"""
    progress = pyqtSignal(str)
    duplicates_found = pyqtSignal(list)  # List[DuplicateGroup]
    error = pyqtSignal(str)

    def __init__(self, client, calendar_name, check_mode):
        super().__init__()
        self.client = client
        self.calendar_name = calendar_name
        self.check_mode = check_mode

    def run(self):
        try:
            self.progress.emit(f"🔍 Lade Events aus '{self.calendar_name}'...")
            
            # Events laden
            events = self.client.get_events(self.calendar_name, 'all')
            if not events:
                self.progress.emit("❌ Keine Events gefunden")
                self.duplicates_found.emit([])
                return
                
            self.progress.emit(f"📊 {len(events)} Events geladen, suche Duplikate...")
            
            # Duplikate finden
            duplicate_groups = self._find_duplicates(events)
            
            if duplicate_groups:
                total_duplicates = sum(len(group) for group in duplicate_groups)
                self.progress.emit(f"✅ {len(duplicate_groups)} Duplikatgruppen mit {total_duplicates} Events gefunden")
            else:
                self.progress.emit("✅ Keine Duplikate gefunden")
                
            self.duplicates_found.emit(duplicate_groups)
            
        except Exception as e:
            logger.error(f"Fehler bei Duplikatsuche: {e}")
            self.error.emit(f"Fehler bei Duplikatsuche: {e}")

    def _find_duplicates(self, events: List[Dict[str, Any]]) -> List[DuplicateGroup]:
        """Findet Duplikate basierend auf dem gewählten Modus"""
        groups = {}
        
        for event in events:
            key = self._generate_key(event)
            if key not in groups:
                groups[key] = []
            groups[key].append(event)
        
        # Nur Gruppen mit mehr als einem Event sind Duplikate
        duplicate_groups = []
        for key, group_events in groups.items():
            if len(group_events) > 1:
                duplicate_groups.append(DuplicateGroup(group_events, key))
        
        return duplicate_groups

    def _generate_key(self, event: Dict[str, Any]) -> str:
        """Generiert einen Schlüssel für Duplikatsprüfung"""
        title = event.get('title', '').strip().lower()
        start_date = event.get('start_date', '')
        
        if self.check_mode == DuplicateCheckMode.LOOSE:
            # Nur Titel + Datum
            if isinstance(start_date, datetime):
                date_str = start_date.strftime('%Y-%m-%d')
            else:
                date_str = str(start_date)[:10] if start_date else ''
            return f"{title}|{date_str}"
            
        elif self.check_mode == DuplicateCheckMode.MODERATE:
            # Titel + Datum + Zeit
            if isinstance(start_date, datetime):
                datetime_str = start_date.strftime('%Y-%m-%d %H:%M')
            else:
                datetime_str = str(start_date)[:16] if start_date else ''
            return f"{title}|{datetime_str}"
            
        else:  # STRICT
            # Titel + Datum + Zeit + Ort
            location = event.get('location', '').strip().lower()
            if isinstance(start_date, datetime):
                datetime_str = start_date.strftime('%Y-%m-%d %H:%M')
            else:
                datetime_str = str(start_date)[:16] if start_date else ''
            return f"{title}|{datetime_str}|{location}"

class DuplicateCleanupWorker(QThread):
    """Worker für Duplikat-Löschung"""
    progress = pyqtSignal(str)
    cleanup_complete = pyqtSignal(int, int)  # deleted_count, error_count
    error = pyqtSignal(str)

    def __init__(self, client, calendar_name, events_to_delete):
        super().__init__()
        self.client = client
        self.calendar_name = calendar_name
        self.events_to_delete = events_to_delete

    def run(self):
        try:
            self.progress.emit(f"🗑️ Lösche {len(self.events_to_delete)} Events...")
            
            deleted_count = 0
            error_count = 0
            
            for i, event in enumerate(self.events_to_delete, 1):
                try:
                    # Event löschen
                    success = self.client.delete_event(self.calendar_name, event)
                    if success:
                        deleted_count += 1
                        self.progress.emit(f"✅ {i}/{len(self.events_to_delete)}: '{event.get('title', 'Unbekannt')}' gelöscht")
                    else:
                        error_count += 1
                        self.progress.emit(f"❌ {i}/{len(self.events_to_delete)}: Fehler beim Löschen von '{event.get('title', 'Unbekannt')}'")
                        
                except Exception as e:
                    error_count += 1
                    logger.error(f"Fehler beim Löschen von Event: {e}")
                    self.progress.emit(f"❌ {i}/{len(self.events_to_delete)}: Fehler - {e}")
            
            self.cleanup_complete.emit(deleted_count, error_count)
            
        except Exception as e:
            logger.error(f"Fehler bei Duplikat-Löschung: {e}")
            self.error.emit(f"Fehler bei Duplikat-Löschung: {e}")

class DuplicateCleanupTab(QWidget):
    """Tab für Duplikatbereinigung"""
    
    status_message = pyqtSignal(str)
    error_message = pyqtSignal(str)
    
    def __init__(self, calendar_client: SimpleCalendarClient):
        super().__init__()
        self.calendar_client = calendar_client
        self.duplicate_groups = []
        self.search_worker = None
        self.cleanup_worker = None
        
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("🧹 Duplikatbereinigung")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        # Beschreibung
        desc_label = QLabel("Entfernt Duplikate innerhalb eines einzelnen Kalenders")
        desc_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(desc_label)
        
        # Kalender-Auswahl
        calendar_layout = QHBoxLayout()
        calendar_layout.addWidget(QLabel("Kalender:"))
        self.cleanup_calendar_combo = QComboBox()
        self.cleanup_calendar_combo.setMinimumWidth(200)
        calendar_layout.addWidget(self.cleanup_calendar_combo)
        calendar_layout.addStretch()
        layout.addLayout(calendar_layout)
        
        # Prüfmodus-Auswahl
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Prüfmodus:"))
        self.check_mode_combo = QComboBox()
        self.check_mode_combo.addItems([
            "🔍 Locker (Titel + Datum)",
            "⚖️ Moderat (Titel + Datum + Zeit)",
            "🎯 Strikt (Titel + Datum + Zeit + Ort)"
        ])
        self.check_mode_combo.setCurrentIndex(1)  # Moderat als Standard
        self.check_mode_combo.setMinimumWidth(300)
        mode_layout.addWidget(self.check_mode_combo)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)
        
        # Such-Button
        search_layout = QHBoxLayout()
        self.search_button = QPushButton('🔍 Duplikate suchen')
        self.search_button.clicked.connect(self.search_duplicates)
        self.search_button.setStyleSheet("QPushButton { background-color: #2196F3; color: white; font-weight: bold; padding: 8px; }")
        search_layout.addWidget(self.search_button)
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Trennlinie
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)
        
        # Duplikate-Tabelle
        table_label = QLabel("Gefundene Duplikate:")
        table_label.setFont(QFont("", 12, QFont.Weight.Bold))
        layout.addWidget(table_label)
        
        self.duplicates_table = QTableWidget()
        self.duplicates_table.setColumnCount(6)
        self.duplicates_table.setHorizontalHeaderLabels([
            "Auswahl", "Titel", "Datum", "Zeit", "Ort", "Gruppe"
        ])
        
        # Spaltenbreiten anpassen
        header = self.duplicates_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        
        self.duplicates_table.setColumnWidth(0, 80)
        self.duplicates_table.setColumnWidth(5, 80)
        
        layout.addWidget(self.duplicates_table)
        
        # Auswahl-Buttons
        selection_layout = QHBoxLayout()
        
        self.select_all_button = QPushButton('✅ Alle auswählen')
        self.select_all_button.clicked.connect(self.select_all)
        self.select_all_button.setEnabled(False)
        selection_layout.addWidget(self.select_all_button)
        
        self.select_none_button = QPushButton('❌ Alle abwählen')
        self.select_none_button.clicked.connect(self.select_none)
        self.select_none_button.setEnabled(False)
        selection_layout.addWidget(self.select_none_button)
        
        self.smart_select_button = QPushButton('🎯 Smart Select')
        self.smart_select_button.clicked.connect(self.smart_select)
        self.smart_select_button.setEnabled(False)
        self.smart_select_button.setToolTip("Wählt automatisch Duplikate aus, behält Originale")
        selection_layout.addWidget(self.smart_select_button)
        
        selection_layout.addStretch()
        layout.addLayout(selection_layout)
        
        # Bereinigung-Button
        cleanup_layout = QHBoxLayout()
        self.cleanup_button = QPushButton('🗑️ Ausgewählte Events löschen')
        self.cleanup_button.clicked.connect(self.cleanup_selected)
        self.cleanup_button.setEnabled(False)
        self.cleanup_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; padding: 8px; }")
        cleanup_layout.addWidget(self.cleanup_button)
        cleanup_layout.addStretch()
        layout.addLayout(cleanup_layout)
        
        # Status-Anzeige
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(100)
        self.status_text.setPlaceholderText("Status-Meldungen erscheinen hier...")
        layout.addWidget(self.status_text)
        
        self.setLayout(layout)

    def update_calendars(self, calendars: List[str]):
        """Aktualisiert die Kalender-Liste"""
        self.cleanup_calendar_combo.clear()
        self.cleanup_calendar_combo.addItems(calendars)

    def search_duplicates(self):
        """Startet die Duplikatsuche"""
        calendar_name = self.cleanup_calendar_combo.currentText()
        if not calendar_name:
            self.error_message.emit("❌ Kein Kalender ausgewählt")
            return
            
        # Prüfmodus bestimmen
        mode_index = self.check_mode_combo.currentIndex()
        if mode_index == 0:
            check_mode = DuplicateCheckMode.LOOSE
        elif mode_index == 1:
            check_mode = DuplicateCheckMode.MODERATE
        else:
            check_mode = DuplicateCheckMode.STRICT
        
        # UI für Suche vorbereiten
        self.search_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.duplicates_table.setRowCount(0)
        self.duplicate_groups = []
        
        # Worker starten
        self.search_worker = DuplicateSearchWorker(
            self.calendar_client, calendar_name, check_mode
        )
        self.search_worker.progress.connect(self.update_status)
        self.search_worker.duplicates_found.connect(self.display_duplicates)
        self.search_worker.error.connect(self.handle_error)
        self.search_worker.finished.connect(self.search_finished)
        self.search_worker.start()

    def display_duplicates(self, duplicate_groups: List[DuplicateGroup]):
        """Zeigt gefundene Duplikate in der Tabelle an"""
        self.duplicate_groups = duplicate_groups
        
        if not duplicate_groups:
            self.update_status("✅ Keine Duplikate gefunden")
            return
        
        # Tabelle füllen
        total_events = sum(len(group) for group in duplicate_groups)
        self.duplicates_table.setRowCount(total_events)
        
        row = 0
        for group_idx, group in enumerate(duplicate_groups, 1):
            for event_idx, event in enumerate(group.events):
                # Checkbox
                checkbox = QCheckBox()
                self.duplicates_table.setCellWidget(row, 0, checkbox)
                
                # Event-Details
                title = event.get('title', 'Unbekannt')
                start_date = event.get('start_date', '')
                
                if isinstance(start_date, datetime):
                    date_str = start_date.strftime('%d.%m.%Y')
                    time_str = start_date.strftime('%H:%M')
                else:
                    date_str = str(start_date)[:10] if start_date else ''
                    time_str = str(start_date)[11:16] if len(str(start_date)) > 10 else ''
                
                location = event.get('location', '')
                
                self.duplicates_table.setItem(row, 1, QTableWidgetItem(title))
                self.duplicates_table.setItem(row, 2, QTableWidgetItem(date_str))
                self.duplicates_table.setItem(row, 3, QTableWidgetItem(time_str))
                self.duplicates_table.setItem(row, 4, QTableWidgetItem(location))
                self.duplicates_table.setItem(row, 5, QTableWidgetItem(f"#{group_idx}"))
                
                row += 1
        
        # Buttons aktivieren
        self.select_all_button.setEnabled(True)
        self.select_none_button.setEnabled(True)
        self.smart_select_button.setEnabled(True)
        self.cleanup_button.setEnabled(True)
        
        self.update_status(f"✅ {len(duplicate_groups)} Duplikatgruppen mit {total_events} Events gefunden")

    def select_all(self):
        """Wählt alle Duplikate aus"""
        for row in range(self.duplicates_table.rowCount()):
            checkbox = self.duplicates_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(True)

    def select_none(self):
        """Wählt alle Duplikate ab"""
        for row in range(self.duplicates_table.rowCount()):
            checkbox = self.duplicates_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(False)

    def smart_select(self):
        """Intelligente Auswahl: Behält das erste Event jeder Gruppe, markiert den Rest"""
        self.select_none()  # Erst alle abwählen
        
        row = 0
        for group in self.duplicate_groups:
            # Erstes Event der Gruppe überspringen (Original behalten)
            row += 1
            
            # Restliche Events der Gruppe auswählen (Duplikate)
            for _ in range(len(group.events) - 1):
                checkbox = self.duplicates_table.cellWidget(row, 0)
                if checkbox:
                    checkbox.setChecked(True)
                row += 1
        
        self.update_status("🎯 Smart Select: Originale behalten, Duplikate ausgewählt")

    def cleanup_selected(self):
        """Löscht ausgewählte Events"""
        calendar_name = self.cleanup_calendar_combo.currentText()
        if not calendar_name:
            self.error_message.emit("❌ Kein Kalender ausgewählt")
            return
            
        # Sammle ausgewählte Events
        selected_count = 0
        selected_events = []
        
        row = 0
        for group in self.duplicate_groups:
            for event in group.events:
                checkbox = self.duplicates_table.cellWidget(row, 0)
                if checkbox and checkbox.isChecked():
                    selected_count += 1
                    selected_events.append(event)
                row += 1
        
        if selected_count == 0:
            self.error_message.emit("❌ Keine Events ausgewählt")
            return
        
        # Bestätigung
        reply = QMessageBox.question(
            self, 
            "Duplikate löschen",
            f"Möchten Sie wirklich {selected_count} Events löschen?\n\n"
            f"⚠️ Diese Aktion kann nicht rückgängig gemacht werden!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # UI für Löschung vorbereiten
        self.cleanup_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        # Worker starten
        self.cleanup_worker = DuplicateCleanupWorker(
            self.calendar_client, calendar_name, selected_events
        )
        self.cleanup_worker.progress.connect(self.update_status)
        self.cleanup_worker.cleanup_complete.connect(self.cleanup_finished)
        self.cleanup_worker.error.connect(self.handle_error)
        self.cleanup_worker.finished.connect(self.cleanup_worker_finished)
        self.cleanup_worker.start()

    def cleanup_finished(self, deleted_count: int, error_count: int):
        """Wird aufgerufen, wenn die Bereinigung abgeschlossen ist"""
        if error_count == 0:
            self.update_status(f"✅ Bereinigung abgeschlossen: {deleted_count} Events gelöscht")
            self.status_message.emit(f"✅ {deleted_count} Duplikate erfolgreich gelöscht")
        else:
            self.update_status(f"⚠️ Bereinigung abgeschlossen: {deleted_count} gelöscht, {error_count} Fehler")
            self.error_message.emit(f"⚠️ {deleted_count} gelöscht, aber {error_count} Fehler aufgetreten")
        
        # Neue Suche starten, um aktualisierte Ergebnisse zu zeigen
        self.search_duplicates()

    def cleanup_worker_finished(self):
        """Wird aufgerufen, wenn der Cleanup-Worker beendet ist"""
        self.progress_bar.setVisible(False)
        self.cleanup_button.setEnabled(True)

    def search_finished(self):
        """Wird aufgerufen, wenn die Suche beendet ist"""
        self.progress_bar.setVisible(False)
        self.search_button.setEnabled(True)

    def update_status(self, message: str):
        """Aktualisiert die Status-Anzeige"""
        self.status_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        self.status_text.verticalScrollBar().setValue(
            self.status_text.verticalScrollBar().maximum()
        )

    def handle_error(self, error_message: str):
        """Behandelt Fehlermeldungen"""
        self.update_status(f"❌ {error_message}")
        self.error_message.emit(error_message) 