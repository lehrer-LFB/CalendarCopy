import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# EventKit-Integration
try:
    from src.calendar_client_eventkit import EventKitCalendarClient
    EVENTKIT_AVAILABLE = True
    logger.info("✅ EventKit-Integration verfügbar")
except ImportError:
    try:
        from calendar_client_eventkit import EventKitCalendarClient
        EVENTKIT_AVAILABLE = True
        logger.info("✅ EventKit-Integration verfügbar")
    except ImportError as e:
        EVENTKIT_AVAILABLE = False
        logger.error(f"❌ EventKit nicht verfügbar: {e}")
        raise ImportError("EventKit wird für den vereinfachten Client benötigt")

class SyncMode:
    ALL = "all"
    FUTURE = "future"

class DuplicateCheckMode:
    LOOSE = "loose"
    MODERATE = "moderate"
    STRICT = "strict"

class SimpleCalendarClient:
    """
    Vereinfachter Kalender-Client nur mit EventKit
    - Keine Batching-Komplexität
    - Keine Cache-Komplexität  
    - Maximale Zuverlässigkeit
    - Gleiche Performance wie komplexe Version
    """
    
    def __init__(self):
        """Initialisiert den vereinfachten EventKit-Client"""
        if not EVENTKIT_AVAILABLE:
            raise RuntimeError("EventKit ist nicht verfügbar")
            
        self.eventkit_client = EventKitCalendarClient()
        
        if not self.eventkit_client.is_available():
            raise RuntimeError("EventKit konnte nicht initialisiert werden")
            
        logger.info("🚀 Vereinfachter EventKit-Client initialisiert")

    def list_calendars(self) -> List[str]:
        """Listet alle verfügbaren Kalender auf"""
        try:
            calendars = self.eventkit_client.list_calendars()
            logger.debug(f"Gefunden: {len(calendars)} Kalender")
            return calendars
        except Exception as e:
            logger.error(f"Fehler beim Laden der Kalender: {e}")
            return []

    def get_events(self, calendar_name: str, sync_mode: str = SyncMode.ALL) -> List[Dict[str, Any]]:
        """Holt Ereignisse aus einem Kalender"""
        try:
            # Berechne Zeitraum basierend auf SyncMode
            if sync_mode == SyncMode.FUTURE:
                start_date = datetime.now()
                end_date = datetime.now() + timedelta(days=365)
            else:  # SyncMode.ALL
                start_date = datetime.now() - timedelta(days=365)
                end_date = datetime.now() + timedelta(days=365)
            
            # Hole Events direkt von EventKit
            events = self.eventkit_client.get_events(calendar_name, start_date, end_date)
            
            # Konvertiere zu einheitlichem Format
            converted_events = []
            for event in events:
                title = event.get('title', '')
                converted_event = {
                    'summary': title,
                    'title': title,  # Für Kompatibilität mit duplicate_cleanup_tab
                    'start_date': event.get('start_date'),
                    'end_date': event.get('end_date'),
                    'description': event.get('description', ''),
                    'location': event.get('location', ''),
                    'allday_event': event.get('all_day', False),
                    'modified_date': event.get('start_date', datetime.now())
                }
                converted_events.append(converted_event)
            
            logger.info(f"🚀 {len(converted_events)} Events geladen aus '{calendar_name}'")
            return converted_events
            
        except Exception as e:
            logger.error(f"Fehler beim Laden der Events aus '{calendar_name}': {e}")
            return []

    def create_event(self, calendar_name: str, event_data: Dict[str, Any]) -> bool:
        """Erstellt ein einzelnes Event"""
        try:
            success = self.eventkit_client.create_event(
                calendar_name=calendar_name,
                title=event_data.get('summary', 'Kein Titel'),
                start_date=event_data.get('start_date'),
                end_date=event_data.get('end_date'),
                description=event_data.get('description', ''),
                location=event_data.get('location', '')
            )
            
            if success:
                logger.debug(f"✅ Event erstellt: {event_data.get('summary', 'Unbekannt')}")
            else:
                logger.warning(f"❌ Event-Erstellung fehlgeschlagen: {event_data.get('summary', 'Unbekannt')}")
                
            return success
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Events: {e}")
            return False

    def sync_calendars(self, source_calendar: str, target_calendar: str, sync_mode: str = SyncMode.ALL, duplicate_check_mode: str = DuplicateCheckMode.MODERATE) -> int:
        """
        Synchronisiert Ereignisse zwischen zwei Kalendern mit Duplikatsprüfung
        
        INKREMENTELLER SYNC:
        1. Lade Quell-Events
        2. Lade Ziel-Events für Duplikatsprüfung
        3. Filtere bereits existierende Events heraus
        4. Erstelle nur neue Events
        """
        try:
            logger.info(f"🔄 Starte Sync mit Duplikatsprüfung: {source_calendar} → {target_calendar}")
            logger.info(f"📋 Modus: {sync_mode}, Duplikatsprüfung: {duplicate_check_mode}")
            
            # 1. Lade Quell-Events
            source_events = self.get_events(source_calendar, sync_mode)
            
            if not source_events:
                logger.info("Keine Events zum Synchronisieren gefunden")
                return 0
            
            # 2. Lade existierende Events aus Zielkalender
            logger.info("🔍 Lade existierende Events aus Zielkalender...")
            target_events = self.get_events(target_calendar, SyncMode.ALL)
            
            logger.info(f"📊 {len(source_events)} Quell-Events, {len(target_events)} Ziel-Events")
            
            # 3. Filtere Duplikate heraus
            new_events = self._filter_duplicates(source_events, target_events, duplicate_check_mode)
            
            if not new_events:
                logger.info("✅ Sync mit Duplikatsprüfung abgeschlossen:")
                logger.info(f"   📝 0 Events erstellt")
                logger.info(f"   ⏭️ {len(source_events)} Duplikate übersprungen")
                logger.info(f"   ❌ 0 Fehler")
                return 0
            
            logger.info(f"📋 {len(new_events)} neue Events zu erstellen (von {len(source_events)} Quell-Events)")
            
            # 4. Erstelle nur neue Events
            success_count = 0
            error_count = 0
            
            for i, event in enumerate(new_events, 1):
                try:
                    if self.create_event(target_calendar, event):
                        success_count += 1
                    else:
                        error_count += 1
                    
                    # Progress-Logging
                    if len(new_events) > 10 and i % 10 == 0:
                        logger.info(f"📊 Fortschritt: {i}/{len(new_events)} Events verarbeitet")
                        
                except Exception as e:
                    error_count += 1
                    logger.warning(f"Event {i} übersprungen: {e}")
                    continue
            
            # Finale Statistik
            duplicates_skipped = len(source_events) - len(new_events)
            logger.info(f"✅ Sync mit Duplikatsprüfung abgeschlossen:")
            logger.info(f"   📝 {success_count} Events erstellt")
            logger.info(f"   ⏭️ {duplicates_skipped} Duplikate übersprungen")
            logger.info(f"   ❌ {error_count} Fehler")
            
            return success_count
            
        except Exception as e:
            logger.error(f"❌ Sync-Fehler: {e}")
            return 0

    def _filter_duplicates(self, source_events: List[Dict[str, Any]], target_events: List[Dict[str, Any]], check_mode: str) -> List[Dict[str, Any]]:
        """
        Filtert Duplikate aus den Quell-Events basierend auf bereits existierenden Ziel-Events
        
        Args:
            source_events: Events aus dem Quellkalender
            target_events: Events aus dem Zielkalender
            check_mode: Duplikatsprüfungs-Modus (loose, moderate, strict)
            
        Returns:
            Liste der Events, die noch nicht im Zielkalender existieren
        """
        if not target_events:
            return source_events
        
        new_events = []
        
        for source_event in source_events:
            is_duplicate = False
            
            for target_event in target_events:
                if self._is_duplicate_event(source_event, target_event, check_mode):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                new_events.append(source_event)
        
        return new_events

    def _is_duplicate_event(self, event1: Dict[str, Any], event2: Dict[str, Any], check_mode: str) -> bool:
        """
        Prüft, ob zwei Events Duplikate sind basierend auf dem Check-Modus
        
        Args:
            event1: Erstes Event
            event2: Zweites Event
            check_mode: Prüfmodus (loose, moderate, strict)
            
        Returns:
            True wenn Events als Duplikate gelten
        """
        try:
            # Titel vergleichen (case-insensitive)
            title1 = (event1.get('title', '') or event1.get('summary', '')).strip().lower()
            title2 = (event2.get('title', '') or event2.get('summary', '')).strip().lower()
            
            if not title1 or not title2 or title1 != title2:
                return False
            
            # Datum vergleichen
            start1 = event1.get('start_date')
            start2 = event2.get('start_date')
            
            if not start1 or not start2:
                return False
            
            # Konvertiere zu datetime falls nötig
            if isinstance(start1, str):
                try:
                    start1 = datetime.fromisoformat(start1.replace('Z', '+00:00'))
                except ValueError:
                    # Fallback für andere Datumsformate
                    from dateutil import parser
                    start1 = parser.parse(start1)
            if isinstance(start2, str):
                try:
                    start2 = datetime.fromisoformat(start2.replace('Z', '+00:00'))
                except ValueError:
                    # Fallback für andere Datumsformate
                    from dateutil import parser
                    start2 = parser.parse(start2)
            
            # Datum-Vergleich (nur Tag bei loose, sonst mit Zeit)
            if check_mode == DuplicateCheckMode.LOOSE:
                # Nur Datum vergleichen
                if start1.date() != start2.date():
                    return False
            else:
                # Datum + Zeit vergleichen (mit Toleranz von 1 Minute)
                time_diff = abs((start1 - start2).total_seconds())
                if time_diff > 60:  # Mehr als 1 Minute Unterschied
                    return False
            
            # Bei strict mode auch Ort vergleichen
            if check_mode == DuplicateCheckMode.STRICT:
                location1 = (event1.get('location', '') or '').strip().lower()
                location2 = (event2.get('location', '') or '').strip().lower()
                
                if location1 != location2:
                    return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Fehler beim Duplikat-Vergleich: {e}")
            return False

    def create_events_simple(self, calendar_name: str, events: List[Dict[str, Any]]) -> tuple:
        """Erstellt mehrere Events ohne Batching-Komplexität"""
        if not events:
            return 0, 0
            
        success_count = 0
        error_count = 0
        
        logger.info(f"🔄 Erstelle {len(events)} Events in '{calendar_name}'")
        
        for i, event in enumerate(events, 1):
            try:
                if self.create_event(calendar_name, event):
                    success_count += 1
                else:
                    error_count += 1
                    
                # Progress bei vielen Events
                if len(events) > 10 and i % 5 == 0:
                    logger.debug(f"📊 {i}/{len(events)} Events verarbeitet")
                    
            except Exception as e:
                error_count += 1
                logger.warning(f"Event {i} fehlgeschlagen: {e}")
        
        logger.info(f"✅ Event-Erstellung: {success_count} erfolgreich, {error_count} Fehler")
        return success_count, error_count

    def get_calendar_info(self) -> Dict[str, Any]:
        """Gibt einfache Kalender-Informationen zurück"""
        calendars = self.list_calendars()
        return {
            'total_calendars': len(calendars),
            'calendar_names': calendars,
            'eventkit_available': True,
            'client_type': 'SimpleEventKit'
        }

    def is_available(self) -> bool:
        """Prüft ob der Client verfügbar ist"""
        return self.eventkit_client.is_available()
    
    def delete_event(self, calendar_name: str, event_data: Dict[str, Any]) -> bool:
        """
        Löscht ein Event aus dem angegebenen Kalender
        
        Args:
            calendar_name: Name des Kalenders
            event_data: Event-Daten mit ID oder anderen Identifikatoren
            
        Returns:
            bool: True wenn erfolgreich gelöscht, False bei Fehler
        """
        try:
            return self.eventkit_client.delete_event(calendar_name, event_data)
        except Exception as e:
            logger.error(f"❌ Fehler beim Löschen von Event: {e}")
            return False 