# 🎯 POI Sprite Builder - Docker Edition

**Angepasst für deine bestehende Geodata Pipeline mit Docker-spreet**

## 📦 Paket-Inhalt

### 🚀 Haupt-Scripts

1. **build_poi_sprites.sh** (Shell-Script)
   - Haupt-Einstiegspunkt
   - Prüft Docker und Voraussetzungen
   - Baut spreet Docker-Image falls nötig
   - Ruft Python-Script auf
   - Zeigt Ergebnisse an

2. **build_poi_sprites.py** (Python-Backend)
   - POI → Font Awesome Mapping
   - Interaktive Icon-Auswahl
   - Font Awesome Download
   - SVG-Extraktion
   - Docker-spreet Integration

### 📚 Dokumentation

3. **INSTALL.md** (Schnellstart)
   - Installation in 3 Schritten
   - Integration in deine Pipeline
   - Checkliste

4. **README_DOCKER.md** (Vollständige Docs)
   - Ausführliche Anleitung
   - MapLibre Integration
   - Troubleshooting
   - Beispiele

5. **example_integration.sh** (Beispiel)
   - Zeigt Integration in start.sh
   - Automatisches Update-Handling
   - Style.json Aktualisierung

## 🎯 Hauptunterschiede zur Standalone-Version

| Aspekt | Standalone | Docker-Edition |
|--------|------------|----------------|
| spreet | Lokal installiert | Docker-Container |
| Pfade | `./poi_sprites/` | `/srv/build/poi-sprites/` |
| Output | `./output/` | `/srv/assets/sprites/poi/` |
| Integration | Eigenständig | Teil der Pipeline |
| Image | Muss installiert sein | Wird automatisch gebaut |

## 🚀 Schnellstart

```bash
# 1. Auf Server kopieren
scp build_poi_sprites.* user@server:/tmp/

# 2. Installieren
sudo cp /tmp/build_poi_sprites.* /srv/scripts/
sudo chmod +x /srv/scripts/build_poi_sprites.*

# 3. Ausführen
cd /srv/scripts
./build_poi_sprites.sh
```

## 📁 Verzeichnisstruktur

### Build-Verzeichnis

```
/srv/build/poi-sprites/
├── svgs/                # Extrahierte SVG-Icons (154 Dateien)
├── fontawesome/         # Font Awesome Download (einmalig)
├── tmp/                 # Temporäre Dateien
└── poi_mapping.json     # Dein Icon-Mapping (wichtig!)
```

### Output-Verzeichnis

```
/srv/assets/sprites/poi/
├── poi.png             # Sprite-Sheet 1x
├── poi.json            # Metadaten 1x
├── poi@2x.png          # Sprite-Sheet 2x (Retina)
├── poi@2x.json         # Metadaten 2x
└── README.md           # Info
```

## 🔧 Docker-Integration

### Verwendet dein bestehendes Image

```bash
# Dein build_sprites.sh baut bereits:
DOCKER_IMAGE="local-spreet-builder"

# POI Sprite Builder verwendet das gleiche Image
docker run --rm \
  -v /srv/build/poi-sprites/svgs:/sources \
  -v /srv/assets/sprites/poi:/output \
  local-spreet-builder /sources /output/poi
```

### Docker-Volumes wie in deiner Pipeline

Genau wie dein `build_sprites.sh` für Maki/Temaki:
- Input: Lokales Verzeichnis mit SVGs
- Output: Direkt nach `/srv/assets/sprites/`
- Keine temporären Container-Dateien

## 🗺️ MapLibre Integration

### Sprite-URL

```
https://tiles.oe5ith.at/assets/sprites/poi/poi
```

### In style.json

```json
{
  "sprite": "https://tiles.oe5ith.at/assets/sprites/poi/poi",
  "layers": [
    {
      "id": "poi-icons",
      "type": "symbol",
      "source": "pmtiles",
      "source-layer": "poi",
      "layout": {
        "icon-image": ["get", "class"]
      }
    }
  ]
}
```

## 📊 Features

✅ **154 POI-Typen** automatisch gemappt  
✅ **Docker-basiert** - nutzt dein Setup  
✅ **Fortschritt speichern** - jederzeit fortsetzbar  
✅ **Pipeline-Integration** - passt zu deinem Workflow  
✅ **Multi-Resolution** - 1x und 2x Sprites  
✅ **Interaktive Eingabe** - für fehlende Icons  
✅ **Font Awesome Free** - 6.5.1  

## 🔄 Workflow

```
1. build_poi_sprites.sh ausführen
   ↓
2. Docker-Image prüfen/bauen
   ↓
3. Verzeichnisse erstellen
   ↓
4. Python-Script starten
   ↓
5. POI-Mapping erstellen (interaktiv)
   ↓
6. Font Awesome herunterladen
   ↓
7. SVGs extrahieren
   ↓
8. Docker-spreet für Sprites
   ↓
9. Output nach /srv/assets/sprites/poi/
   ↓
10. Fertig! ✨
```

## 💡 Tipps

### Mit deinem Maki/Temaki Setup kombinieren

```bash
# Erst POI-Sprites
/srv/scripts/build_poi_sprites.sh

# Dann Maki/Temaki
/srv/scripts/build_sprites.sh

# Jetzt hast du alle Sprites:
# - /srv/assets/sprites/poi/
# - /srv/assets/sprites/maki/
# - /srv/assets/sprites/temaki/
```

### Verschiedene Sprite-Sets nutzen

In style.json kannst du mehrere Sprite-Quellen angeben:

```json
{
  "sprite": [
    "https://tiles.oe5ith.at/assets/sprites/poi/poi",
    "https://tiles.oe5ith.at/assets/sprites/maki/sprite"
  ]
}
```

Oder verschiedene Layer verwenden unterschiedliche Sprites.

## 🔍 Was ist neu gegenüber Standalone?

1. **Docker statt lokales spreet**
   - Nutzt `local-spreet-builder` Container
   - Keine lokale spreet-Installation nötig

2. **/srv/-Pfade**
   - Build: `/srv/build/poi-sprites/`
   - Output: `/srv/assets/sprites/poi/`

3. **Pipeline-Integration**
   - Kann in start.sh eingebunden werden
   - Automatisches Update-Handling

4. **Konsistent mit deinem Setup**
   - Gleiche Docker-Befehle
   - Gleiche Verzeichnisstruktur
   - Gleiche Berechtigungen

## 📋 Voraussetzungen

Alles bereits in deinem Setup vorhanden:

- ✅ Docker (läuft)
- ✅ Python3 (installiert)
- ✅ `/srv/`-Struktur (vorhanden)
- ✅ spreet-Docker (wird gebaut)

## 🎨 Unterstützte POI-Kategorien

Siehe POI_REFERENCE.md für die komplette Liste von 154 POI-Typen.

Die wichtigsten:
- Restaurant, Cafe, Bar, Hotel, Pub
- Shop, Grocery, Bakery, Pharmacy
- Hospital, School, Library, Museum
- Parking, Fuel, Bus, Railway
- Park, Playground, Sports Centre
- und 130+ weitere...

## 📄 Lizenz

- **Tool**: Frei verwendbar
- **Font Awesome Icons**: CC BY 4.0
- **Font Awesome Fonts**: SIL OFL 1.1
- **Font Awesome Code**: MIT

## 🆘 Support

**Lies zuerst:**
1. INSTALL.md für Schnellstart
2. README_DOCKER.md für Details

**Bei Problemen:**
- Prüfe Docker: `docker ps`
- Prüfe Logs im Script-Output
- Prüfe Berechtigungen auf `/srv/`

## 🎯 Nächste Schritte

1. **Installiere** die Scripts
2. **Führe aus** `./build_poi_sprites.sh`
3. **Konfiguriere** deine style.json
4. **Teste** in MapLibre
5. **Integriere** in deine Pipeline (optional)

---

**Erstellt für:** https://tiles.oe5ith.at/  
**Kompatibel mit:** Deiner OSM Geodata Pipeline  
**Version:** Docker Edition (angepasst an dein Setup)

🗺️ **Viel Erfolg mit deinen POI-Sprites!** ✨
