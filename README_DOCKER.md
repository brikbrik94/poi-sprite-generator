# 🎯 POI Sprite Builder - Docker Edition

Automatischer Sprite-Generator für PMTiles POI-Layer, integriert in deine bestehende Geodata Pipeline mit Docker-basiertem spreet.

## 🚀 Quick Start

```bash
# Kopiere die Scripts nach /srv/scripts
sudo cp build_poi_sprites.sh map_poi_icons.py build_poi_sprites.py /srv/scripts/

# Mache ausführbar
sudo chmod +x /srv/scripts/build_poi_sprites.sh

# Führe aus
cd /srv/scripts
./build_poi_sprites.sh
```

Das Mapping-Script wird dich **interaktiv** nach fehlenden Icon-Zuordnungen fragen.

## 📁 Verzeichnisstruktur

Passt sich automatisch in deine `/srv`-Struktur ein:

```
/srv/
├── build/
│   └── poi-sprites/          # Build-Verzeichnis
│       ├── svgs/             # Extrahierte Font Awesome SVGs
│       ├── fontawesome/      # Font Awesome Download
│       ├── tmp/              # Temporäre Dateien
│       └── poi_mapping.json  # Dein Icon-Mapping
│
└── assets/
    └── sprites/
        └── poi/              # 🎯 AUSGABE - Fertige Sprites
            ├── poi.png
            ├── poi.json
            ├── poi@2x.png
            ├── poi@2x.json
            └── README.md
```

## 🔧 Wie es funktioniert

### 1. Docker-Image

Verwendet dein bestehendes `local-spreet-builder` Image:

```bash
# Falls nicht vorhanden, wird es automatisch gebaut:
docker build -t local-spreet-builder https://github.com/flother/spreet.git
```

### 2. POI-Mapping

Mappt automatisch **~150 von 154** POI-Typen zu Font Awesome Icons:

```json
{
  "restaurant": "utensils",
  "cafe": "coffee",
  "parking": "square-parking",
  ...
}
```

### 3. Interaktive Eingabe

Für nicht-automatisch gemappte POIs fragt das Script:

```
Icon für 'special_poi': _
```

- Suche auf https://fontawesome.com/search?o=r&m=free
- Gib nur den Namen ein (z.B. `bicycle`, nicht `fa-bicycle`)
- ENTER zum Überspringen

### 4. Sprite-Generierung

Verwendet Docker-Volumes wie dein `build_sprites.sh`:

```bash
docker run --rm \
  -v /srv/build/poi-sprites/svgs:/sources \
  -v /srv/assets/sprites/poi:/output \
  local-spreet-builder /sources /output/poi
```

## 🗺️ MapLibre Integration

### Style-Konfiguration

```json
{
  "version": 8,
  "sprite": "https://tiles.oe5ith.at/assets/sprites/poi/poi",
  "sources": {
    "pmtiles": {
      "type": "vector",
      "url": "pmtiles://https://tiles.oe5ith.at/at-plus.pmtiles"
    }
  },
  "layers": [
    {
      "id": "poi-icons",
      "type": "symbol",
      "source": "pmtiles",
      "source-layer": "poi",
      "minzoom": 12,
      "layout": {
        "icon-image": ["get", "class"],
        "icon-size": [
          "interpolate", ["linear"], ["zoom"],
          12, 0.5,
          16, 0.8,
          20, 1.0
        ],
        "text-field": ["get", "name"],
        "text-font": ["Noto Sans Regular"],
        "text-size": 11,
        "text-anchor": "top",
        "text-offset": [0, 1]
      },
      "paint": {
        "text-color": "#333333",
        "text-halo-color": "#ffffff",
        "text-halo-width": 1.5
      }
    }
  ]
}
```

### Layer-Beispiele

**Nur Icons:**
```json
{
  "layout": {
    "icon-image": ["get", "class"],
    "icon-size": 0.8
  }
}
```

**Icons mit Labels:**
```json
{
  "layout": {
    "icon-image": ["get", "class"],
    "icon-size": 0.8,
    "text-field": ["get", "name"],
    "text-offset": [0, 1]
  }
}
```

**Zoom-abhängige Größe:**
```json
{
  "layout": {
    "icon-image": ["get", "class"],
    "icon-size": [
      "interpolate", ["linear"], ["zoom"],
      10, 0.3,
      14, 0.6,
      18, 1.0
    ]
  }
}
```

## 🔄 Workflow-Integration

### In deine start.sh einbinden

```bash
#!/bin/bash
# ... deine anderen Prozesse ...

# POI-Sprites erstellen (einmalig oder bei Updates)
if [ ! -f "/srv/assets/sprites/poi/poi.png" ]; then
    echo "Erstelle POI-Sprites..."
    /srv/scripts/build_poi_sprites.sh
fi

# ... weiter mit deinem normalen Workflow ...
```

### Automatisches Update

Füge zu deinem Cron oder Systemd-Timer hinzu:

```bash
# Täglich POI-Sprites neu bauen (falls Mapping sich ändert)
0 2 * * * /srv/scripts/build_poi_sprites.sh
```

## 📊 Unterstützte POI-Kategorien

- 🏨 **Unterkunft & Gastro** (15): restaurant, cafe, bar, hotel, ...
- 🛍️ **Einzelhandel & Services** (12): shop, grocery, bakery, ...
- 🏥 **Gesundheit** (5): hospital, doctors, pharmacy, ...
- 🎓 **Bildung** (4): school, college, library, ...
- 🏛️ **Öffentliche Einrichtungen** (8): town_hall, police, ...
- 🎨 **Kultur & Freizeit** (12): museum, cinema, theatre, ...
- ⛪ **Religiös** (1): place_of_worship
- 🅿️ **Verkehr & Infrastruktur** (20): parking, fuel, bus, ...
- ⚽ **Sport & Recreation** (50+): football, swimming, tennis, ...
- 🏞️ **Natur & Parks** (10): park, garden, playground, ...
- 🔧 **Utilities & Services** (12): atm, toilets, information, ...

**Gesamt: 154 POI-Typen**

## 🔧 Erweiterte Konfiguration

### Eigene Icons hinzufügen

1. Bearbeite `/srv/build/poi-sprites/poi_mapping.json`:
   ```json
   {
     "restaurant": "utensils",
     "my_custom_poi": "star"
   }
   ```

2. Führe Script erneut aus:
   ```bash
   ./build_poi_sprites.sh
   ```

### Sprite-Name ändern

```bash
SPRITE_NAME=my-pois ./build_poi_sprites.sh
```

Ausgabe: `/srv/assets/sprites/poi/my-pois.png`

### Verschiedene Output-Verzeichnisse

```bash
OUTPUT_DIR=/srv/assets/sprites/custom ./build_poi_sprites.sh
```

## 🐛 Troubleshooting

### "Docker läuft nicht"

```bash
# Starte Docker
sudo systemctl start docker

# Prüfe Status
sudo systemctl status docker
```

### "Docker-Image nicht gefunden"

```bash
# Baue Image manuell
docker build -t local-spreet-builder https://github.com/flother/spreet.git
```

### "Keine SVGs gefunden"

Font Awesome Download fehlgeschlagen. Manuell herunterladen:

```bash
cd /srv/build/poi-sprites
wget https://github.com/FortAwesome/Font-Awesome/releases/download/6.5.1/fontawesome-free-6.5.1-web.zip
unzip fontawesome-free-6.5.1-web.zip -d fontawesome/
```

### Berechtigungen

```bash
# Falls Berechtigungsprobleme auftreten
sudo chown -R $USER:$USER /srv/build/poi-sprites
sudo chown -R $USER:$USER /srv/assets/sprites/poi
```

## 📝 Beispiel-Session

```bash
$ ./build_poi_sprites.sh

==========================================
  POI Sprite Builder (Docker Edition)
==========================================

--- Prüfe Voraussetzungen... ---
✓ Docker gefunden
✓ Python3 gefunden
✓ Docker läuft

--- Prüfe spreet Docker-Image... ---
✓ Docker-Image 'local-spreet-builder' vorhanden

--- Erstelle Verzeichnisse... ---
✓ Build-Dir: /srv/build/poi-sprites
✓ Output-Dir: /srv/assets/sprites/poi

--- Starte POI Sprite Builder... ---

============================================================
Erstelle POI → Font Awesome Mapping
============================================================

ℹ Insgesamt 154 POI-Typen zu mappen
ℹ Automatisch gemappt: 150
ℹ Manuelle Eingabe nötig: 4

✓ restaurant                   → utensils
✓ cafe                         → coffee
...

⚠ 4 POI-Typen benötigen manuelle Zuordnung
ℹ Suche Icons auf: https://fontawesome.com/search?o=r&m=free

Icon für 'special_poi': star
✓ Gespeichert: special_poi → star

...

=========================================
  ✨ POI-Sprites erfolgreich erstellt! ✨
=========================================

Ausgabe-Verzeichnis:
  /srv/assets/sprites/poi

MapLibre Sprite-URL:
  https://tiles.oe5ith.at/assets/sprites/poi/poi
```

## 🎨 Verwendete Icons

Basiert auf **Font Awesome Free 6.5.1**:
- Icons: CC BY 4.0 License
- Fonts: SIL OFL 1.1 License
- Code: MIT License

https://fontawesome.com/license/free

## 🤝 Integration mit deinem Setup

Dieses Tool ist speziell für deine bestehende Pipeline entwickelt:

✅ Verwendet dein `local-spreet-builder` Docker-Image  
✅ Folgt deiner `/srv`-Verzeichnisstruktur  
✅ Kompatibel mit deinem `build_sprites.sh` Workflow  
✅ Berücksichtigt deine User/Gruppen-Konfiguration  
✅ Passt zu deinem Maki/Temaki Sprite-Setup  

## 📚 Weitere Ressourcen

- Font Awesome Icons: https://fontawesome.com/search?o=r&m=free
- MapLibre Sprites Docs: https://maplibre.org/maplibre-style-spec/sprite/
- spreet GitHub: https://github.com/flother/spreet
- Deine PMTiles: https://tiles.oe5ith.at/at-plus.pmtiles

---

**Viel Erfolg mit den POI-Sprites!** 🗺️✨
