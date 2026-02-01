# poi-sprite-generator

Automatischer Sprite-Generator für POI-Icons auf Basis von Font Awesome Free. Das Repository liefert ein Python-Backend und ein Shell-Wrapper-Script, die zusammen ein Icon-Mapping erstellen, SVGs sammeln und über Docker/spreet Sprite-Sheets für MapLibre erzeugen.

## Überblick

* `build_poi_sprites.py` übernimmt das komplette Build-Processing:
  * erstellt/verwendet ein persistiertes POI→Icon-Mapping (`/srv/build/poi-sprites/poi_mapping.json`).【F:build_poi_sprites.py†L236-L361】
  * lädt Font Awesome Free, kopiert die gemappten SVGs und erzeugt Sprites via Docker/spreet.【F:build_poi_sprites.py†L363-L552】
  * schreibt eine README und Build-Metadaten in die Output- und Build-Verzeichnisse.【F:build_poi_sprites.py†L554-L643】
* `build_poi_sprites.sh` prüft Abhängigkeiten, baut bei Bedarf das Docker-Image und startet das Python-Script.【F:build_poi_sprites.sh†L1-L126】

## Voraussetzungen

* Docker (für `spreet`)
* Python 3
* Schreibrechte auf `/srv/build` und `/srv/assets` (Default-Pfade)

Die Standardpfade können über Umgebungsvariablen im Shell-Script angepasst werden (`BUILD_DIR`, `OUTPUT_DIR`, `DOCKER_IMAGE`, `SPRITE_NAME`).【F:build_poi_sprites.sh†L12-L18】

## Quick Start

```bash
./build_poi_sprites.sh
```

Das Script erstellt die Sprites unter `/srv/assets/sprites/poi/` und speichert das Mapping in `/srv/build/poi-sprites/poi_mapping.json`. Bei fehlenden Zuordnungen fragt das Python-Script interaktiv nach Icon-Namen. 【F:build_poi_sprites.py†L301-L361】

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
