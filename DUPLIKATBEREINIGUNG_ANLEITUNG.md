# 🧹 Duplikatbereinigung - Detaillierte Anleitung

## ✨ Überblick

Die **Duplikatbereinigung** ist eine neue, leistungsstarke Funktion in Kalender Sync Pro v2.1.0, die es ermöglicht, Duplikate innerhalb eines einzelnen Kalenders intelligent zu erkennen und sicher zu entfernen.

## 🎯 Wann ist diese Funktion nützlich?

### 📋 Typische Szenarien:
- **Nach Kalender-Importen**: Mehrfache Importe derselben .ics-Datei
- **Sync-Probleme**: Fehlerhafte Synchronisation zwischen Geräten
- **Manuelle Duplikate**: Versehentlich doppelt erstellte Termine
- **Kalender-Migration**: Übertragung zwischen verschiedenen Systemen
- **Backup-Wiederherstellung**: Mehrfache Wiederherstellung von Sicherungen

## 🚀 Schritt-für-Schritt-Anleitung

### Schritt 1: App starten und Tab öffnen

```bash
# App starten
python3 src/simple_gui.py
# oder
open "dist/Kalender Sync Pro.app"
```

1. **Kalender Sync Pro** öffnen
2. Tab **"🧹 Duplikatbereinigung"** auswählen
3. Warten bis alle Kalender geladen sind

### Schritt 2: Kalender auswählen

1. **Dropdown-Menü "Kalender"** öffnen
2. **Zu bereinigenden Kalender** auswählen
   - Nur ein Kalender pro Durchgang möglich
   - Alle verfügbaren macOS-Kalender werden angezeigt

### Schritt 3: Prüfmodus festlegen

Wählen Sie den passenden Modus für Ihre Bedürfnisse:

#### 🔍 **Locker (Titel + Datum)**
- **Kriterien**: Nur Titel und Datum werden verglichen
- **Verwendung**: Maximale Duplikaterfassung
- **Beispiel**: "Meeting" am 15.12.2024 → alle "Meeting"-Termine an diesem Tag
- **⚠️ Vorsicht**: Kann legitime Events als Duplikate erkennen

#### ⚖️ **Moderat (Titel + Datum + Zeit)** ⭐ **EMPFOHLEN**
- **Kriterien**: Titel, Datum und Uhrzeit werden verglichen
- **Verwendung**: Beste Balance zwischen Genauigkeit und Erfassung
- **Beispiel**: "Meeting" am 15.12.2024 um 14:00 → nur exakt gleiche Termine
- **✅ Optimal**: Für die meisten Anwendungsfälle geeignet

#### 🎯 **Strikt (Titel + Datum + Zeit + Ort)**
- **Kriterien**: Titel, Datum, Uhrzeit und Ort werden verglichen
- **Verwendung**: Höchste Präzision, minimale False-Positives
- **Beispiel**: "Meeting" am 15.12.2024 um 14:00 in "Raum A" → nur 100% identische Events
- **🎯 Präzise**: Für kritische Kalender mit vielen ähnlichen Terminen

### Schritt 4: Duplikate suchen

1. **Button "🔍 Duplikate suchen"** klicken
2. **Progress-Bar** beobachten (zeigt Suchfortschritt)
3. **Status-Meldungen** in der unteren Textbox verfolgen

#### Was passiert während der Suche:
```
[14:23:15] 🔍 Lade Events aus 'MeinKalender'...
[14:23:16] 📊 228 Events geladen, suche Duplikate...
[14:23:17] ✅ 96 Duplikatgruppen mit 192 Events gefunden
```

### Schritt 5: Ergebnisse analysieren

Nach der Suche wird eine **detaillierte Tabelle** angezeigt:

| Spalte | Beschreibung | Beispiel |
|--------|--------------|----------|
| **Auswahl** | Checkbox zum Markieren | ☑️ / ☐ |
| **Titel** | Event-Titel | "Zahnarzttermin" |
| **Datum** | Datum des Events | "15.12.2024" |
| **Zeit** | Uhrzeit des Events | "14:00" |
| **Ort** | Veranstaltungsort | "Praxis Dr. Müller" |
| **Gruppe** | Duplikatgruppen-Nummer | "#1", "#2", "#3" |

#### 📊 Duplikatgruppen verstehen:
- **Gruppe #1**: Alle Events mit identischen Kriterien
- **Gruppe #2**: Nächste Gruppe identischer Events
- **Farb-Kodierung**: Gruppen sind visuell getrennt

### Schritt 6: Auswahl treffen

Sie haben **drei Optionen** für die Auswahl:

#### Option A: **✅ Alle auswählen**
- Wählt **alle gefundenen Duplikate** aus
- ⚠️ **Vorsicht**: Löscht auch Originale!
- **Verwendung**: Nur wenn Sie sicher sind, dass alle Events Duplikate sind

#### Option B: **❌ Alle abwählen**
- Entfernt alle Markierungen
- **Verwendung**: Für manuelle, selektive Auswahl

#### Option C: **🎯 Smart Select** ⭐ **EMPFOHLEN**
- **Intelligente Auswahl**: Behält das erste Event jeder Gruppe (Original)
- **Markiert nur Duplikate**: Sichere, automatische Auswahl
- **Algorithmus**: 
  ```
  Für jede Duplikatgruppe:
  - Event #1: ✅ BEHALTEN (Original)
  - Event #2-n: ☑️ LÖSCHEN (Duplikate)
  ```

#### Option D: **Manuelle Auswahl**
- Klicken Sie einzelne Checkboxen an/ab
- **Vollständige Kontrolle** über jeden Löschvorgang
- **Empfohlen für**: Kritische Kalender oder unsichere Fälle

### Schritt 7: Bereinigung ausführen

1. **Button "🗑️ Ausgewählte Events löschen"** klicken
2. **Bestätigungsdialog** erscheint:
   ```
   Möchten Sie wirklich 45 Events löschen?
   
   ⚠️ Diese Aktion kann nicht rückgängig gemacht werden!
   
   [Ja] [Nein]
   ```
3. **"Ja"** klicken zur Bestätigung
4. **Progress-Bar** zeigt Löschfortschritt
5. **Live-Updates** in der Status-Anzeige:
   ```
   [14:25:30] 🗑️ Lösche 45 Events...
   [14:25:31] ✅ 1/45: 'Zahnarzttermin' gelöscht
   [14:25:32] ✅ 2/45: 'Meeting Projekt X' gelöscht
   ...
   [14:25:45] ✅ Bereinigung abgeschlossen: 45 Events gelöscht
   ```

### Schritt 8: Ergebnis überprüfen

Nach der Bereinigung:
1. **Automatische Neusuche** wird gestartet
2. **Aktualisierte Ergebnisse** werden angezeigt
3. **Bestätigung** der erfolgreichen Bereinigung
4. **Kalender-App** prüfen zur finalen Verifikation

## 🛡️ Sicherheitsfeatures

### 🔒 Mehrfache Sicherheitsstufen

1. **Vorschau-Modus**: Alle Duplikate werden vor Löschung angezeigt
2. **Manuelle Bestätigung**: Expliziter Bestätigungsdialog
3. **Smart Select**: Intelligente Auswahl behält Originale
4. **Live-Feedback**: Jeder Löschvorgang wird einzeln bestätigt
5. **Fehlerbehandlung**: Robuste Behandlung von Löschfehlern

### ⚠️ Wichtige Sicherheitshinweise

- **Backup empfohlen**: Erstellen Sie vor großen Bereinigungen ein Kalender-Backup
- **Test mit kleinen Kalendern**: Testen Sie die Funktion erst mit unwichtigen Kalendern
- **Smart Select verwenden**: Nutzen Sie die intelligente Auswahl für maximale Sicherheit
- **Manuelle Überprüfung**: Kontrollieren Sie die Auswahl vor der Bereinigung
- **Keine Undo-Funktion**: Gelöschte Events können nicht wiederhergestellt werden

## 🔧 Troubleshooting

### ❌ Häufige Probleme und Lösungen

#### Problem: "Keine Duplikate gefunden"
**Mögliche Ursachen:**
- Kalender enthält tatsächlich keine Duplikate
- Prüfmodus zu strikt gewählt
- Events haben unterschiedliche Zeiten/Orte

**Lösungen:**
- Prüfmodus auf "Locker" ändern
- Kalender in macOS Kalender-App überprüfen
- Andere Kalender testen

#### Problem: "Berechtigung verweigert"
**Ursache:** macOS-Kalender-Berechtigung fehlt

**Lösung:**
```
Systemeinstellungen → Datenschutz & Sicherheit → Kalender 
→ "Kalender Sync Pro" aktivieren
```

#### Problem: "Löschung fehlgeschlagen"
**Mögliche Ursachen:**
- Netzwerk-Kalender (nur lesend)
- Kalender-Synchronisation läuft
- macOS-Berechtigung entzogen

**Lösungen:**
- Nur lokale Kalender verwenden
- Andere Kalender-Apps schließen
- App neu starten

#### Problem: "GUI friert ein"
**Ursache:** Sehr große Kalender (>1000 Events)

**Lösung:**
- Geduld haben (Background-Processing läuft)
- Prüfmodus "Strikt" für bessere Performance
- Kalender in kleinere Teile aufteilen

### 📊 Performance-Tipps

#### Für große Kalender (>500 Events):
- **Prüfmodus "Strikt"** verwenden (schnellere Verarbeitung)
- **Kleinere Zeiträume** bearbeiten (Events nach Jahren filtern)
- **Nicht-kritische Zeiten** wählen (weniger Kalender-Aktivität)

#### Für maximale Sicherheit:
- **Backup erstellen** vor Bereinigung
- **Test-Kalender** für erste Versuche verwenden
- **Smart Select** statt "Alle auswählen"
- **Manuelle Überprüfung** der Auswahl

## 📈 Erweiterte Verwendung

### 🎯 Strategien für verschiedene Kalender-Typen

#### **Persönliche Kalender**
- **Modus**: Moderat (empfohlen)
- **Strategie**: Smart Select verwenden
- **Häufigkeit**: Monatlich oder bei Bedarf

#### **Geschäfts-Kalender**
- **Modus**: Strikt (höchste Sicherheit)
- **Strategie**: Manuelle Auswahl nach Überprüfung
- **Häufigkeit**: Quartalsweise mit Backup

#### **Import-Kalender**
- **Modus**: Locker (maximale Erfassung)
- **Strategie**: Alle auswählen nach Verifikation
- **Häufigkeit**: Nach jedem Import

#### **Geteilte Kalender**
- **Modus**: Strikt (Vorsicht bei geteilten Daten)
- **Strategie**: Sehr selektive manuelle Auswahl
- **Häufigkeit**: Nur bei kritischen Duplikat-Problemen

### 🔄 Workflow-Integration

#### **Regelmäßige Wartung**
```
1. Wöchentlich: Schnelle Duplikatsuche (Modus: Moderat)
2. Monatlich: Gründliche Bereinigung (Modus: Locker)
3. Quartalsweise: Vollständige Kalender-Überprüfung
```

#### **Nach Kalender-Änderungen**
```
1. Nach Import: Sofortige Duplikatprüfung
2. Nach Sync-Problemen: Bereinigung mit Modus "Strikt"
3. Nach Migration: Vollständige Analyse aller Kalender
```

## 📚 Technische Details

### 🔍 Duplikat-Erkennungsalgorithmus

```python
# Vereinfachtes Beispiel der Duplikatserkennung
def generate_key(event, mode):
    if mode == "LOOSE":
        return f"{event.title}|{event.date}"
    elif mode == "MODERATE":
        return f"{event.title}|{event.datetime}"
    else:  # STRICT
        return f"{event.title}|{event.datetime}|{event.location}"
```

### ⚡ Performance-Charakteristiken

| Kalender-Größe | RAM-Verbrauch | CPU-Last | Analyse-Zeit |
|----------------|---------------|----------|--------------|
| 50 Events | ~5 MB | Niedrig | <1s |
| 200 Events | ~15 MB | Moderat | <3s |
| 500 Events | ~30 MB | Hoch | <8s |
| 1000+ Events | ~60 MB | Sehr hoch | <20s |

---

## 🎉 Fazit

Die **Duplikatbereinigung** in Kalender Sync Pro v2.1.0 bietet eine **professionelle, sichere und benutzerfreundliche** Lösung für eines der häufigsten Kalender-Probleme. Mit **drei intelligenten Prüfmodi**, **umfassenden Sicherheitsfeatures** und einer **intuitiven Benutzeroberfläche** können Sie Ihre Kalender effizient und sicher bereinigen.

**🎯 Empfehlung**: Beginnen Sie mit dem **"Moderat"-Modus** und **Smart Select** für die beste Balance zwischen Sicherheit und Effizienz.

---

*Für weitere Fragen oder Probleme, konsultieren Sie die [Release Notes](RELEASE_NOTES_v2.1.0.md) oder die Inline-Hilfe in der Anwendung.* 