"""
Setup-Skript für die vereinfachte EventKit-App
"""

from setuptools import setup
import plistlib

APP = ['src/simple_gui.py']
DATA_FILES = []

OPTIONS = {
    'argv_emulation': False,
    'includes': [
        # Python Standard-Module
        'datetime', 
        'logging', 
        'os', 
        'sys',
        'traceback',
        'typing',
        
        # PyQt6 Core-Module  
        'PyQt6.QtWidgets',
        'PyQt6.QtCore', 
        'PyQt6.QtGui',
        
        # PyObjC und EventKit (kritisch!)
        'objc',
        'Foundation',
        'EventKit',
        
        # Unsere vereinfachten Module
        'src.simple_calendar_client',
        'src.calendar_client_eventkit',
        'src.duplicate_cleanup_tab',
    ],
    'packages': [
        'PyQt6', 
        'objc',
    ],
    'excludes': [
        # Nicht benötigte Module ausschließen
        'PIL', 
        'numpy', 
        'matplotlib',
        'tkinter',
        'test',
        'unittest',
        'distutils',
        'setuptools',
        'pip',
        'appscript',  # Nicht mehr benötigt (nur EventKit)
        'sqlite3',   # Nicht mehr benötigt (kein Caching)
        
        # Alte komplexe Module ausschließen
        'src.calendar_client',
        'src.batch_cache_logger',
        'src.sync_manager',
        'src.gui_threaded',
        'src.gui',
    ],
    'resources': [],
    'optimize': 2,  # Optimierung für kleinere App
    'debug_modulegraph': False,
    'debug_skip_macholib': False,
    'site_packages': True,
    'strip': True,  # Strip für kleinere App-Größe
    'iconfile': None,
    'plist': {
        'CFBundleName': 'Kalender Sync Ultra',
        'CFBundleDisplayName': 'Kalender Sync Ultra',
        'CFBundleIdentifier': 'com.kalendersync.ultra',
        'CFBundleVersion': '2.0.0',
        'CFBundleShortVersionString': '2.0.0',
        'NSCalendarsUsageDescription': 'Diese App synchronisiert Kalender-Ereignisse ultraschnell mit EventKit.',
        'NSAppleEventsUsageDescription': 'Diese App verwendet EventKit für direkten Kalenderzugriff.',
        'LSApplicationCategoryType': 'public.app-category.productivity',
        'LSBackgroundOnly': False,
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.15',  # Mindest macOS-Version für EventKit
        'NSRequiresAquaSystemAppearance': False,
    }
}

setup(
    name='Kalender Sync Ultra',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
) 