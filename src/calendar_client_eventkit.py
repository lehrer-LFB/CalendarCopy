#!/usr/bin/env python3
"""
EventKit-basierter Calendar Client für macOS
Verwendet PyObjC für direkten Zugriff auf das EventKit Framework
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from enum import Enum

# Ultra-defensive EventKit-Imports für maximale App-Bundle-Kompatibilität
EVENTKIT_AVAILABLE = False
EventKit = None
Foundation = None

def safe_import_eventkit():
    """Sichere EventKit-Import-Funktion mit mehreren Fallback-Strategien"""
    global EVENTKIT_AVAILABLE, EventKit, Foundation
    
    if EVENTKIT_AVAILABLE:
        return True
        
    try:
        # Ersten Import-Versuch
        import EventKit as EK
        import Foundation as F
        
        # Test, ob die Module tatsächlich funktionieren
        event_store = EK.EKEventStore.alloc().init()
        if event_store is None:
            raise ImportError("EventStore konnte nicht erstellt werden")
            
        # Erfolg - setze globale Variablen
        EventKit = EK
        Foundation = F
        EVENTKIT_AVAILABLE = True
        print("✅ EventKit erfolgreich importiert")
        return True
        
    except Exception as e:
        print(f"⚠️ EventKit nicht verfügbar: {e}")
        EVENTKIT_AVAILABLE = False
        
        # Erstelle Stub-Klassen für komplette Kompatibilität
        class EventKitStub:
            @staticmethod
            def EKEventStore():
                return None
            @staticmethod
            def authorizationStatusForEntityType_(entity_type):
                return 0
            EKAuthorizationStatusAuthorized = 3
            EKEntityTypeEvent = 0
            EKRecurrenceFrequencyDaily = 0
            EKRecurrenceFrequencyWeekly = 1
            EKRecurrenceFrequencyMonthly = 2
            EKRecurrenceFrequencyYearly = 3
        
        class FoundationStub:
            @staticmethod
            def NSDate():
                return None
            @staticmethod
            def NSTimeZone():
                return None
        
        EventKit = EventKitStub()
        Foundation = FoundationStub()
        return False

# Führe den sicheren Import beim Modul-Load durch
safe_import_eventkit()

class SyncMode(Enum):
    """Synchronisationsmodi für Event-Abfragen"""
    FUTURE = "future"
    PAST = "past"
    ALL = "all"

class EventPriority(Enum):
    """Event-Prioritätsstufen"""
    LOW = 1
    NORMAL = 2  
    HIGH = 3

class EventKitCalendarClient:
    """
    EventKit-basierter Calendar Client für native macOS-Integration
    """
    
    def __init__(self):
        """Initialisiert den EventKit Calendar Client"""
        self.event_store = None
        self.logger = logging.getLogger(__name__)
        
        # Prüfe EventKit-Verfügbarkeit bei jeder Instanziierung
        if not safe_import_eventkit():
            self.logger.warning("EventKit nicht verfügbar - Client wird als Stub laufen")
            return
            
        try:
            self._initialize_event_store()
            
            # WICHTIG: Berechtigung beim Start anfordern
            if self.event_store:
                permission_granted = self.request_calendar_access()
                if not permission_granted:
                    self.logger.warning("⚠️ Kalender-Berechtigung nicht gewährt - App funktioniert möglicherweise eingeschränkt")
            
        except Exception as e:
            self.logger.error(f"EventKit-Initialisierung fehlgeschlagen: {e}")
            global EVENTKIT_AVAILABLE
            EVENTKIT_AVAILABLE = False

    def _initialize_event_store(self):
        """Initialisiert den Event Store"""
        if not EVENTKIT_AVAILABLE:
            return False
            
        try:
            self.event_store = EventKit.EKEventStore.alloc().init()
            if self.event_store is None:
                raise Exception("Event Store konnte nicht erstellt werden")
                
            self.logger.info("EventStore erfolgreich initialisiert")
            return True
        except Exception as e:
            self.logger.error(f"Event Store Initialisierung fehlgeschlagen: {e}")
            return False

    def request_calendar_access(self) -> bool:
        """Fordert Kalender-Berechtigung aktiv an"""
        if not EVENTKIT_AVAILABLE or not self.event_store:
            return False
            
        try:
            import time
            
            status = EventKit.EKEventStore.authorizationStatusForEntityType_(EventKit.EKEntityTypeEvent)
            
            if status == EventKit.EKAuthorizationStatusAuthorized:
                self.logger.info("✅ Kalender-Berechtigung bereits gewährt")
                return True
            elif status == EventKit.EKAuthorizationStatusDenied:
                self.logger.error("❌ Kalender-Berechtigung verweigert - bitte in Systemeinstellungen aktivieren")
                return False
            elif status == EventKit.EKAuthorizationStatusRestricted:
                self.logger.error("❌ Kalender-Zugriff eingeschränkt")
                return False
            else:
                # Status ist "Not Determined" (0) - Berechtigung AKTIV anfordern
                self.logger.info("🔐 Fordere Kalender-Berechtigung an...")
                
                # WICHTIG: Berechtigung anfordern (asynchron, aber wir warten)
                self.event_store.requestAccessToEntityType_completion_(
                    EventKit.EKEntityTypeEvent, 
                    None  # Completion handler - None für synchrone Verarbeitung
                )
                
                # Warten und Status mehrmals prüfen
                for i in range(10):  # Bis zu 10 Sekunden warten
                    time.sleep(1.0)
                    new_status = EventKit.EKEventStore.authorizationStatusForEntityType_(EventKit.EKEntityTypeEvent)
                    
                    if new_status == EventKit.EKAuthorizationStatusAuthorized:
                        self.logger.info("✅ Kalender-Berechtigung erfolgreich gewährt!")
                        return True
                    elif new_status == EventKit.EKAuthorizationStatusDenied:
                        self.logger.error("❌ Kalender-Berechtigung wurde verweigert")
                        return False
                    
                    # Noch wartend...
                    self.logger.debug(f"⏳ Warte auf Berechtigungsantwort... ({i+1}/10)")
                
                # Nach 10 Sekunden immer noch nicht beantwortet
                self.logger.warning("⚠️ Kalender-Berechtigung nicht rechtzeitig erhalten - bitte Dialog bestätigen")
                return False
                    
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Anfordern der Kalender-Berechtigung: {e}")
            return False

    def is_available(self) -> bool:
        """Überprüft, ob EventKit verfügbar ist"""
        return EVENTKIT_AVAILABLE and self.event_store is not None

    def list_calendars(self) -> List[str]:
        """Listet alle verfügbaren Kalender auf"""
        if not self.is_available():
            self.logger.warning("EventKit nicht verfügbar für list_calendars")
            return []
            
        try:
            calendars = self.event_store.calendarsForEntityType_(EventKit.EKEntityTypeEvent)
            calendar_names = [calendar.title() for calendar in calendars if calendar.title()]
            
            self.logger.info(f"Gefundene Kalender: {calendar_names}")
            return calendar_names
            
        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Kalender: {e}")
            return []

    def get_events(self, calendar_name: str, start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, Any]]:
        """Holt Events aus dem angegebenen Kalender"""
        if not self.is_available():
            self.logger.warning("EventKit nicht verfügbar für get_events")
            return []
            
        try:
            # Standard-Zeitraum: letztes Jahr bis nächstes Jahr
            if start_date is None:
                start_date = datetime.now() - timedelta(days=365)
            if end_date is None:
                end_date = datetime.now() + timedelta(days=365)
            
            self.logger.debug(f"Suche Events von {start_date} bis {end_date}")
            
            # Validiere Datum-Objekte
            if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
                self.logger.error(f"Ungültige Datumstypen: start_date={type(start_date)}, end_date={type(end_date)}")
                return []
            
            # Konvertiere zu NSDate
            start_ns = self._datetime_to_nsdate(start_date)
            end_ns = self._datetime_to_nsdate(end_date)
            
            # Prüfe ob Konvertierung erfolgreich war
            if start_ns is None or end_ns is None:
                self.logger.error("NSDate-Konvertierung fehlgeschlagen")
                return []
            
            # Erstelle Predicate für Events
            predicate = self.event_store.predicateForEventsWithStartDate_endDate_calendars_(
                start_ns, end_ns, None
            )
            
            # Hole alle Events
            all_events = self.event_store.eventsMatchingPredicate_(predicate)
            
            # Filtere nach Kalender
            calendar_events = []
            for event in all_events:
                if event.calendar().title() == calendar_name:
                    event_dict = self._convert_event_to_dict(event)
                    calendar_events.append(event_dict)
            
            self.logger.info(f"Gefundene Events: {len(calendar_events)} in '{calendar_name}'")
            return calendar_events
            
        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Events: {e}")
            return []

    def create_event(self, calendar_name: str, title: str, start_date: datetime, 
                    end_date: datetime, description: str = "", location: str = "") -> bool:
        """Erstellt ein neues Event"""
        if not self.is_available():
            self.logger.warning("EventKit nicht verfügbar für create_event")
            return False
            
        try:
            # Finde den Zielkalender
            target_calendar = self._find_calendar(calendar_name)
            if not target_calendar:
                self.logger.error(f"Kalender '{calendar_name}' nicht gefunden")
                return False
            
            # Erstelle neues Event
            event = EventKit.EKEvent.eventWithEventStore_(self.event_store)
            if not event:
                self.logger.error("Event konnte nicht erstellt werden")
                return False
            
            # Setze Event-Eigenschaften
            event.setTitle_(title)
            event.setStartDate_(self._datetime_to_nsdate(start_date))
            event.setEndDate_(self._datetime_to_nsdate(end_date))
            
            if description:
                event.setNotes_(description)
            if location:
                event.setLocation_(location)
                
            event.setCalendar_(target_calendar)
            
            # Speichere Event
            success = self.event_store.saveEvent_span_error_(event, 0, None)
            
            if success:
                self.logger.debug(f"Event '{title}' erfolgreich erstellt")
                return True
            else:
                self.logger.error(f"Event '{title}' konnte nicht gespeichert werden")
                return False
                
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen des Events: {e}")
            return False

    def create_events_batch(self, calendar_name: str, events: List[Dict[str, Any]], batch_size: int = 10) -> tuple:
        """Erstellt mehrere Events in einem Batch"""
        if not self.is_available():
            self.logger.warning("EventKit nicht verfügbar für create_events_batch")
            return 0, len(events)
            
        if not events:
            return 0, 0
            
        success_count = 0
        error_count = 0
        
        try:
            # Finde den Zielkalender
            target_calendar = self._find_calendar(calendar_name)
            if not target_calendar:
                self.logger.error(f"Kalender '{calendar_name}' nicht gefunden")
                return 0, len(events)
            
            for event_data in events:
                try:
                    if self._create_single_event(target_calendar, event_data):
                        success_count += 1
                    else:
                        error_count += 1
                except Exception as e:
                    self.logger.error(f"Fehler beim Erstellen eines Events: {e}")
                    error_count += 1
            
            self.logger.info(f"Batch-Erstellung abgeschlossen: {success_count}/{len(events)} Events erstellt")
            return success_count, error_count
            
        except Exception as e:
            self.logger.error(f"Fehler beim Batch-Erstellen der Events: {e}")
            return success_count, len(events)

    # Hilfsmethoden
    def _find_calendar(self, calendar_name: str):
        """Findet einen Kalender anhand des Namens"""
        if not self.is_available():
            return None
            
        try:
            calendars = self.event_store.calendarsForEntityType_(EventKit.EKEntityTypeEvent)
            for calendar in calendars:
                if calendar.title() == calendar_name:
                    return calendar
            return None
        except Exception:
            return None

    def _create_single_event(self, target_calendar, event_data: Dict[str, Any]) -> bool:
        """Erstellt ein einzelnes Event"""
        if not self.is_available():
            return False
            
        try:
            event = EventKit.EKEvent.eventWithEventStore_(self.event_store)
            if not event:
                return False
            
            # Setze Event-Eigenschaften
            event.setTitle_(event_data.get('title', 'Untitled'))
            event.setStartDate_(self._datetime_to_nsdate(event_data['start_date']))
            event.setEndDate_(self._datetime_to_nsdate(event_data['end_date']))
            
            if 'description' in event_data and event_data['description']:
                event.setNotes_(event_data['description'])
            if 'location' in event_data and event_data['location']:
                event.setLocation_(event_data['location'])
                
            event.setCalendar_(target_calendar)
            
            # Speichere Event
            return self.event_store.saveEvent_span_error_(event, 0, None)
            
        except Exception:
            return False

    def _convert_event_to_dict(self, event) -> Dict[str, Any]:
        """Konvertiert ein EventKit-Event zu einem Dictionary"""
        if not EVENTKIT_AVAILABLE:
            return {}
            
        try:
            return {
                'title': event.title() or '',
                'start_date': self._nsdate_to_datetime(event.startDate()),
                'end_date': self._nsdate_to_datetime(event.endDate()),
                'description': event.notes() or '',
                'location': event.location() or '',
                'all_day': event.isAllDay(),
                'recurrence': self._format_recurrence(event.recurrenceRules()),
                'calendar': event.calendar().title() if event.calendar() else '',
                'id': event.eventIdentifier() or ''
            }
        except Exception as e:
            self.logger.error(f"Fehler beim Konvertieren des Events: {e}")
            return {}

    def _datetime_to_nsdate(self, dt: datetime):
        """Konvertiert Python datetime zu NSDate"""
        if not EVENTKIT_AVAILABLE or not dt:
            self.logger.warning(f"Ungültiges Datum für NSDate-Konvertierung: {dt}")
            return None
            
        try:
            timestamp = dt.timestamp()
            nsdate = Foundation.NSDate.dateWithTimeIntervalSince1970_(timestamp)
            if nsdate is None:
                self.logger.error(f"NSDate-Konvertierung fehlgeschlagen für: {dt}")
            return nsdate
        except Exception as e:
            self.logger.error(f"Fehler bei NSDate-Konvertierung: {e}")
            return None

    def _nsdate_to_datetime(self, nsdate) -> datetime:
        """Konvertiert NSDate zu Python datetime"""
        if not EVENTKIT_AVAILABLE or not nsdate:
            return datetime.now()
            
        try:
            # NSDate zu Python timestamp
            timestamp = nsdate.timeIntervalSince1970()
            return datetime.fromtimestamp(timestamp)
        except Exception:
            return datetime.now()
    
    def _format_recurrence(self, recurrence_rules) -> str:
        """Formatiert Wiederholungsregeln"""
        if not EVENTKIT_AVAILABLE or not recurrence_rules:
            return ""
            
        try:
            # Vereinfachte Wiederholungsinfo
            rule = recurrence_rules[0]  # Erste Regel verwenden
            frequency = rule.frequency()
            
            frequency_map = {
                EventKit.EKRecurrenceFrequencyDaily: "täglich",
                EventKit.EKRecurrenceFrequencyWeekly: "wöchentlich", 
                EventKit.EKRecurrenceFrequencyMonthly: "monatlich",
                EventKit.EKRecurrenceFrequencyYearly: "jährlich"
            }
            
            return frequency_map.get(frequency, "unbekannt")
        except Exception:
            return ""


def test_eventkit_client():
    """Test-Funktion für EventKit-Integration"""
    print("🧪 Teste EventKit Calendar Client...")
    
    if not EVENTKIT_AVAILABLE:
        print("❌ EventKit nicht verfügbar - Test übersprungen")
        return
    
    client = EventKitCalendarClient()
    
    # Kalender abrufen
    calendars = client.list_calendars()
    print(f"📅 Gefundene Kalender: {calendars}")
    
    if calendars:
        # Events aus erstem Kalender laden
        test_calendar = calendars[0]
        events = client.get_events(test_calendar, SyncMode.FUTURE)
        print(f"🎯 Events in '{test_calendar}': {len(events)}")
        
        # Erste paar Events anzeigen
        for i, event in enumerate(events[:3]):
            print(f"  {i+1}. {event['title']} - {event['start_date']}")
    
    print("✅ EventKit-Test abgeschlossen")


if __name__ == "__main__":
    test_eventkit_client() 