# 🚀 Installation & Integration - Quick Guide

## 📦 Was du bekommst

- **build_poi_sprites.sh** - Shell-Script (Docker-kompatibel)
- **build_poi_sprites.py** - Python-Backend
- **README_DOCKER.md** - Vollständige Dokumentation
- **example_integration.sh** - Beispiel-Integration in start.sh

## ⚡ Schnellinstallation

### 1. Scripts installieren

```bash
# Kopiere auf deinen Server
scp build_poi_sprites.* user@server:/tmp/

# Auf dem Server:
sudo cp /tmp/build_poi_sprites.sh /srv/scripts/
sudo cp /tmp/build_poi_sprites.py /srv/scripts/
sudo chmod +x /srv/scripts/build_poi_sprites.sh
sudo chmod +x /srv/scripts/build_poi_sprites.py
```

### 2. Ausführen

```bash
cd /srv/scripts
./build_poi_sprites.sh
```

Das war's! 🎉

## 🔄 Integration in deine Pipeline

### Option A: Manuell bei Bedarf

```bash
# Führe aus wenn du POI-Sprites brauchst
/srv/scripts/build_poi_sprites.sh
```

### Option B: In start.sh einbinden

Füge zu deiner `start.sh` hinzu:

```bash
# POI-Sprites erstellen (falls nicht vorhanden)
if [ ! -f "/srv/assets/sprites/poi/poi.png" ]; then
    /srv/scripts/build_poi_sprites.sh
fi
```

Siehe `example_integration.sh` für ein vollständiges Beispiel.

### Option C: Automatisch aktualisieren

Cron-Job für regelmäßige Updates:

```bash
# Täglich um 2 Uhr morgens
0 2 * * * /srv/scripts/build_poi_sprites.sh
```

## 📁 Wo liegen die Dateien?

Nach dem Ausführen findest du:

```
/srv/assets/sprites/poi/
├── poi.png          # Sprite-Sheet 1x
├── poi.json         # Metadaten 1x
├── poi@2x.png       # Sprite-Sheet 2x (Retina)
├── poi@2x.json      # Metadaten 2x
└── README.md        # Dokumentation

/srv/build/poi-sprites/
├── svgs/            # Extrahierte SVG-Icons
├── fontawesome/     # Font Awesome Download
└── poi_mapping.json # Dein Icon-Mapping (wichtig!)
```

## 🗺️ MapLibre Konfiguration

In deiner `style.json`:

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
        "icon-image": ["get", "class"],
        "icon-size": 0.8
      }
    }
  ]
}
```

## 🎯 Unterschiede zu deinem Maki/Temaki Setup

| Aspekt | Maki/Temaki | POI-Sprites |
|--------|-------------|-------------|
| Icons | Mapbox Maki/Temaki | Font Awesome Free |
| Anzahl | ~400 Icons | 154 POI-spezifisch |
| Mapping | Vordefiniert | Anpassbar |
| Update | Git Clone | Icon-Mapping |
| Verwendung | Generische Icons | PMTiles POI-Layer |

## 💡 Tipps

### Icons anpassen

Bearbeite `/srv/build/poi-sprites/poi_mapping.json`:

```json
{
  "restaurant": "utensils",
  "cafe": "coffee",
  "my_custom_poi": "star"
}
```

Dann erneut ausführen:

```bash
./build_poi_sprites.sh
```

### Fortschritt wird gespeichert

Wenn du das Script abbrichst (Ctrl+C), wird dein Fortschritt in `poi_mapping.json` gespeichert. Beim nächsten Ausführen macht es dort weiter!

### Keine redundanten Downloads

- Font Awesome wird nur einmal heruntergeladen
- Docker-Image wird nur einmal gebaut
- Bereits gemappte Icons werden nicht erneut gefragt

## 🔧 Voraussetzungen

Alles was du brauchst ist bereits in deinem Setup:

- ✅ Docker (hast du bereits)
- ✅ Python3 (hast du bereits)
- ✅ `local-spreet-builder` Image (wird automatisch gebaut)

## ❓ Häufige Fragen

### "Wo finde ich Font Awesome Icons?"

https://fontawesome.com/search?o=r&m=free

Verwende nur **Free** Icons!

### "Kann ich eigene SVGs verwenden?"

Ja! Lege sie in `/srv/build/poi-sprites/svgs/` und benenne sie nach deinem POI-Typ (z.B. `restaurant.svg`).

### "Wie viele POIs werden automatisch gemappt?"

~150 von 154. Nur wenige benötigen manuelle Eingabe.

### "Funktioniert es mit meinem bestehenden Setup?"

Ja! Es ist speziell für deine `/srv`-Struktur und Docker-Setup entwickelt.

## 🆘 Probleme?

1. **Lies README_DOCKER.md** für Details
2. **Prüfe Logs** im Script-Output
3. **Prüfe Berechtigungen** auf `/srv/build` und `/srv/assets`

## 📝 Checkliste

- [ ] Scripts nach `/srv/scripts/` kopiert
- [ ] Scripts ausführbar gemacht (`chmod +x`)
- [ ] Script ausgeführt (`./build_poi_sprites.sh`)
- [ ] Sprites in `/srv/assets/sprites/poi/` vorhanden
- [ ] `style.json` mit Sprite-URL aktualisiert
- [ ] In MapLibre getestet

## 🎉 Das war's!

Deine POI-Sprites sind jetzt Teil deiner Geodata Pipeline!

**Sprite-URL:**
```
https://tiles.oe5ith.at/assets/sprites/poi/poi
```

---

Bei Fragen oder Problemen siehe **README_DOCKER.md** für Details.
