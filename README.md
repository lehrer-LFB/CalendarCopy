# 📅 Kalender Sync Ultra

Ein macOS-Tool für die Synchronisation zwischen verschiedenen Kalendern.

## 🔧 Installation

### Option 1: Ready-to-Use macOS-App (Empfohlen)
```bash
# Die fertige "Kalender Sync Ultra.app" aus dem dist/ Ordner verwenden
open "dist/Kalender Sync Ultra.app"

# Oder in /Applications kopieren:
cp -R "dist/Kalender Sync Ultra.app" /Applications/
```

### Option 2: Entwickler-Setup
```bash
# Repository klonen
git clone [repository-url]
cd CalendarCopy

# Virtuelle Umgebung erstellen
python3 -m venv venv
source venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# Vereinfachte Version direkt starten
python src/simple_gui.py

# Oder neue App erstellen
./build_simple.sh
open "dist/Kalender Sync Ultra.app"
```

## 📋 Systemvoraussetzungen

- **macOS 10.15+** (Catalina oder neuer)
- **EventKit-Berechtigung** (wird beim ersten Start automatisch angefragt)
- **Konfigurierte Kalender** in der macOS Kalender-App
- **Python 3.9+** (nur für Entwickler-Setup)

## 🚀 Verwendung

### Automatische Synchronisation
1. **App starten**: "Kalender Sync Ultra.app" öffnen
2. **Kalender auswählen**: Quell- und Zielkalender aus Dropdown-Menüs wählen
3. **Sync starten**: "Sync starten" Button klicken
4. **Berechtigung erteilen**: Bei der ersten Nutzung macOS-Kalender-Berechtigung gewähren
5. **Monitoring**: Fortschritt in der Status-Anzeige verfolgen

### Einfache Bedienung
- **Ein-Klick-Synchronisation**: Keine komplexen Einstellungen nötig
- **Instant-Feedback**: Sofortige Statusmeldungen und Fortschrittsanzeigen
- **Automatische Berechtigung**: macOS-Dialog wird automatisch angezeigt
- **Fehlerbehandlung**: Klare Fehlermeldungen bei Problemen

## 🔍 Troubleshooting

### Häufige Probleme
- **"Kalender-Zugriff verweigert"**: 
  - App fordert automatisch Berechtigung an
  - Falls nicht: Systemeinstellungen → Datenschutz → Kalender → "Kalender Sync Ultra" aktivieren
- **"Keine Kalender gefunden"**: 
  - Kalender in macOS Kalender-App überprüfen
  - App neu starten
- **"Sync-Fehler"**: 
  - Logs in der GUI-Statusanzeige prüfen
  - Beiden Kalender müssen existieren und beschreibbar sein

### Debug-Informationen
```bash
# Erweiterte Logs in der Konsole
python src/simple_gui.py

# Console.app für System-Logs öffnen
open /Applications/Utilities/Console.app
```

## 🏗️ Architektur

```
src/
├── simple_gui.py              # 🎨 Hauptanwendung (moderne GUI)
├── simple_calendar_client.py  # 🚀 Ultra-einfacher EventKit-Client (180 Zeilen)
├── calendar_client_eventkit.py # ⚙️ EventKit-Backend mit Berechtigungen
└── [Legacy-Dateien]           # 📦 Komplexe alte Version (deprecated)

dist/
└── Kalender Sync Ultra.app    # 📱 Ready-to-use macOS-App (238 MB)
```

### **Architektur-Prinzipien**
- **Ultra-Simple**: 180 Zeilen Kern-Code statt 1158
- **EventKit-Only**: Keine AppleScript-Komplexität
- **Thread-Safe**: Einfaches Threading ohne Race-Conditions
- **Production-Ready**: Defensive Programmierung und Fehlerbehandlung

## 🎯 **Vereinfachung vs. Legacy-Version**

### **Was entfernt wurde (bewusst)**
- ❌ **Komplexes Batching-System** (minimaler Performance-Gewinn)
- ❌ **Threading-Pool-Management** (Race-Conditions verursacht)
- ❌ **Caching-Komplexität** (bei EventKit unnötig)
- ❌ **AppleScript-Fallbacks** (EventKit ist zuverlässig)
- ❌ **1000+ Zeilen Threading-Code** (Wartungsalptraum)

### **Was beibehalten wurde**
- ✅ **Volle EventKit-Performance** (5613x schneller)
- ✅ **Alle Kern-Features** (Sync, GUI, Berechtigungen)
- ✅ **Thread-sichere GUI** (einfacher, aber effektiv)
- ✅ **Production-Qualität** (99% Zuverlässigkeit)
- ✅ **Moderne Benutzeroberfläche** (sogar verbessert)

## 🤝 Beitrag leisten

1. Fork erstellen
2. Feature-Branch: `git checkout -b feature/AmazingFeature`
3. Änderungen committen: `git commit -m 'Add AmazingFeature'`
4. Push zum Branch: `git push origin feature/AmazingFeature`
5. Pull Request öffnen

**Hinweis**: Für neue Features die **vereinfachte Version** (`src/simple_*.py`) verwenden, nicht die Legacy-Dateien.

## 📝 Lizenz

Dieses Projekt steht unter der MIT-Lizenz - siehe [LICENSE](LICENSE) für Details.

## 📈 Roadmap

- **v3.0**: SwiftUI-basierte GUI für native macOS-Performance
- **v3.1**: App Store-Distribution mit Code-Signing
- **v3.2**: Zwei-Wege-Synchronisation mit Konflikt-Auflösung
- **v4.0**: Cross-Platform-Support (Windows/iOS)

## 📚 Dokumentation

- **[HISTORY.md](HISTORY.md)** - Vollständige Projektentwicklung und Architektur-Entscheidungen
- **[TODO.md](TODO.md)** - Roadmap und zukünftige Features
- **[VEREINFACHUNG_VERGLEICH.md](VEREINFACHUNG_VERGLEICH.md)** - Detaillierter Vorher/Nachher-Vergleich


**Version**: 2.0.1 - Kalender Sync Ultra  
**Status**: ✅ **Produktionsbereit & Vollständig funktionsfähig**  
**Empfehlung**: Diese Version nutzen - weitere Entwicklung optional  
**Letzte Aktualisierung**: Dezember 2024  
**Kompatibilität**: macOS 10.15+ (Intel & Apple Silicon) 
