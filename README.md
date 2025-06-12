# 📅 Kalender Sync Ultra v2.2.0

Eine leistungsstarke macOS-Anwendung zur intelligenten Synchronisation von Kalendern mit fortschrittlicher Duplikatserkennung.

## ✨ Hauptfunktionen

### 🔄 Automatische Synchronisation
- **Smart Sync**: Intelligente Erkennung und Vermeidung von Duplikaten
- **Zeitplan**: Automatische Synchronisation nach Zeitplan
- **Selektiv**: Wählbare Kalender und Zeiträume

### 🎯 Manuelle Synchronisation (NEU in v2.2.0!)
- **Duplikatsprüfung**: Intelligente Erkennung von Duplikaten
- **5-Spalten-Ansicht**: Detaillierte Event-Informationen
- **Status-Anzeige**: Farbkodierte Status (✅ Neu/⚠️ Duplikat)
- **Warnungsdialog**: Sicherheitsabfrage vor Sync
- **Responsive UI**: Background-Threading für flüssige Bedienung

## 🚀 Installation

1. Repository klonen
2. Python-Umgebung einrichten:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Anwendung starten:
   ```bash
   python3 src/simple_gui.py
   ```

## 📋 Systemanforderungen

- macOS 10.15 oder neuer
- Python 3.8+
- EventKit-Berechtigung

## 🛠️ Konfiguration

1. Beim ersten Start Kalender-Zugriff erlauben
2. Quell- und Zielkalender auswählen
3. Optional: Auto-Sync konfigurieren

## 🔒 Sicherheit

- Keine Cloud-Speicherung
- Lokale Verarbeitung
- Nur Lese-/Schreibzugriff auf ausgewählte Kalender

## 🤝 Mitwirken

Beiträge sind willkommen! Bitte beachten:
1. Fork des Repositories
2. Feature-Branch erstellen
3. Änderungen committen
4. Pull Request erstellen

## 📝 Lizenz

MIT License - siehe [LICENSE](LICENSE) Datei

## 🙏 Danksagung

- EventKit-Team für die Kalender-API
- Alle Mitwirkenden und Tester

---

**Version**: 2.2.0
**Kompatibilität**: macOS 10.15+ (Universal Binary)
**Release-Datum**: März 2024
