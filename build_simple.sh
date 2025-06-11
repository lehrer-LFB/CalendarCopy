#!/bin/bash

# Build-Skript für Kalender Sync Ultra (Vereinfachte Version)

echo "🚀 Baue Kalender Sync Ultra (EventKit-Version)..."

# Lösche alte Builds
echo "🧹 Lösche alte Builds..."
rm -rf build dist

# Erstelle die App
echo "🔨 Erstelle App-Bundle..."
python setup_simple.py py2app

# Prüfe Ergebnis
if [ -d "dist/Kalender Sync Ultra.app" ]; then
    echo "✅ Build erfolgreich!"
    echo "📱 App erstellt: dist/Kalender Sync Ultra.app"
    
    # Zeige App-Größe
    APP_SIZE=$(du -sh "dist/Kalender Sync Ultra.app" | cut -f1)
    echo "📏 App-Größe: $APP_SIZE"
    
    echo ""
    echo "🎯 Zum Testen:"
    echo "   open 'dist/Kalender Sync Ultra.app'"
    echo ""
    echo "📦 Zum Verteilen:"
    echo "   Die App kann aus dem dist/ Ordner kopiert werden"
    
else
    echo "❌ Build fehlgeschlagen!"
    echo "🔍 Prüfe die Logs oben für Fehlerdetails"
    exit 1
fi 