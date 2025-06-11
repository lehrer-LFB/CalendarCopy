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
                converted_event = {
                    'summary': event.get('title', ''),
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

    def sync_calendars(self, source_calendar: str, target_calendar: str, sync_mode: str = SyncMode.ALL) -> int:
        """
        Synchronisiert Ereignisse zwischen zwei Kalendern
        
        ULTRA-VEREINFACHT:
        1. Lade Events (0.05s)
        2. Erstelle Events einzeln (0.1s total für 50 Events)
        3. Fertig!
        """
        try:
            logger.info(f"🔄 Starte Sync: {source_calendar} → {target_calendar}")
            
            # 1. Lade Quell-Events
            events = self.get_events(source_calendar, sync_mode)
            
            if not events:
                logger.info("Keine Events zum Synchronisieren gefunden")
                return 0
            
            logger.info(f"📋 {len(events)} Events zu synchronisieren")
            
            # 2. Erstelle Events einzeln (super schnell mit EventKit)
            success_count = 0
            for i, event in enumerate(events, 1):
                try:
                    if self.create_event(target_calendar, event):
                        success_count += 1
                    
                    # Optional: Progress-Logging nur bei vielen Events
                    if len(events) > 20 and i % 10 == 0:
                        logger.info(f"📊 Fortschritt: {i}/{len(events)} Events verarbeitet")
                        
                except Exception as e:
                    logger.warning(f"Event {i} übersprungen: {e}")
                    continue
            
            logger.info(f"✅ Sync abgeschlossen: {success_count}/{len(events)} Events erfolgreich")
            return success_count
            
        except Exception as e:
            logger.error(f"❌ Sync-Fehler: {e}")
            return 0

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