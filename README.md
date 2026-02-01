# poi-sprite-generator

Automatischer Sprite-Generator für POI-Icons auf Basis von Font Awesome Free. Das Repository liefert ein Mapping-Script und einen Sprite-Builder, die zusammen ein Icon-Mapping erstellen, SVGs sammeln und über Docker/spreet Sprite-Sheets für MapLibre erzeugen.

## Überblick

* `map_poi_icons.py` erstellt (interaktiv) das POI→Icon-Mapping und speichert es unter `/srv/build/poi-sprites/poi_mapping.json`.【F:map_poi_icons.py†L1-L140】
* `build_poi_sprites.py` lädt das Mapping, sammelt die SVGs und erzeugt Sprites via Docker/spreet.【F:build_poi_sprites.py†L236-L560】
* `build_poi_sprites.sh` prüft Abhängigkeiten, führt ggf. das Mapping aus und startet den Builder.【F:build_poi_sprites.sh†L1-L138】

## Voraussetzungen

* Docker (für `spreet`)
* Python 3
* Schreibrechte auf `/srv/build` und `/srv/assets` (Default-Pfade)

Die Standardpfade können über Umgebungsvariablen im Shell-Script angepasst werden (`BUILD_DIR`, `OUTPUT_DIR`, `DOCKER_IMAGE`, `SPRITE_NAME`).【F:build_poi_sprites.sh†L12-L18】

## Quick Start

```bash
./build_poi_sprites.sh
```

Das Script erstellt zuerst das Mapping (falls noch nicht vorhanden) und erzeugt danach die Sprites unter `/srv/assets/sprites/poi/`. Fehlende Zuordnungen werden im Mapping-Schritt interaktiv abgefragt. 【F:build_poi_sprites.sh†L1-L138】

## MapLibre Integration

Beispiel in einer `style.json`:

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

Weitere Details und Integrationsbeispiele findest du in `README_DOCKER.md` und `INSTALL.md`.【F:README_DOCKER.md†L1-L200】【F:INSTALL.md†L1-L200】
