#!/bin/bash
# Beispiel: Integration von POI-Sprites in deine start.sh
# Zeigt wie du den POI Sprite Builder in deinen bestehenden Workflow einbindest

set -euo pipefail

# Deine bestehenden Variablen
INSTALL_DIR="${INSTALL_DIR:-/srv/scripts}"
BUILD_DIR="${BUILD_DIR:-/srv/build}"
TILES_DIR="${TILES_DIR:-/srv/tiles}"
ASSETS_DIR="${ASSETS_DIR:-/srv/assets}"

echo "=== OSM Geodata Pipeline Start ==="

# ... deine bestehenden Downloads und Prozesse ...

# ==========================================
# POI-SPRITES ERSTELLEN (NEU)
# ==========================================
echo ""
echo "--- Erstelle POI-Sprites... ---"

POI_SPRITE_DIR="$ASSETS_DIR/sprites/poi"

# Prüfe ob POI-Sprites bereits existieren
if [ -f "$POI_SPRITE_DIR/poi.png" ] && [ -f "$POI_SPRITE_DIR/poi.json" ]; then
    echo "✓ POI-Sprites bereits vorhanden, überspringe..."
    
    # Optional: Prüfe Alter der Sprites (z.B. älter als 7 Tage?)
    if [ -n "$(find "$POI_SPRITE_DIR/poi.png" -mtime +7 2>/dev/null)" ]; then
        echo "⚠ Sprites sind älter als 7 Tage, aktualisiere..."
        "$INSTALL_DIR/build_poi_sprites.sh" || {
            echo "⚠ POI-Sprite Update fehlgeschlagen, verwende alte Version"
        }
    fi
else
    echo "→ Erstelle POI-Sprites zum ersten Mal..."
    
    # Führe POI Sprite Builder aus
    if [ -x "$INSTALL_DIR/build_poi_sprites.sh" ]; then
        "$INSTALL_DIR/build_poi_sprites.sh" || {
            echo "✗ POI-Sprite Erstellung fehlgeschlagen"
            echo "  Fahre fort ohne POI-Sprites..."
        }
    else
        echo "⚠ build_poi_sprites.sh nicht gefunden oder nicht ausführbar"
        echo "  Installiere zuerst: cp build_poi_sprites.sh /srv/scripts/"
    fi
fi

# ==========================================
# ANDERE SPRITES (BESTEHEND)
# ==========================================
echo ""
echo "--- Erstelle Maki & Temaki Sprites... ---"
"$INSTALL_DIR/build_sprites.sh"

# ... rest deines bestehenden Workflows ...

echo ""
echo "=== Alle Sprites erstellt ==="
echo ""
echo "Verfügbare Sprite-Sets:"
find "$ASSETS_DIR/sprites" -name "sprite.png" -o -name "poi.png" | while read sprite; do
    dir=$(dirname "$sprite")
    name=$(basename "$dir")
    echo "  - $name: $(basename "$sprite")"
done

# ==========================================
# STYLE.JSON AKTUALISIEREN
# ==========================================
echo ""
echo "--- Aktualisiere style.json mit POI-Sprites... ---"

STYLE_FILE="$TILES_DIR/osm/styles/at-plus/style.json"

if [ -f "$STYLE_FILE" ]; then
    # Backup erstellen
    cp "$STYLE_FILE" "${STYLE_FILE}.bak"
    
    # Sprite-URL in style.json setzen (falls noch nicht vorhanden)
    # Hinweis: Hier würdest du dein bevorzugtes JSON-Editing-Tool verwenden
    # z.B. jq, python, sed, etc.
    
    # Beispiel mit jq (wenn installiert):
    if command -v jq &> /dev/null; then
        jq '.sprite = "https://tiles.oe5ith.at/assets/sprites/poi/poi"' \
            "$STYLE_FILE" > "${STYLE_FILE}.tmp" && \
            mv "${STYLE_FILE}.tmp" "$STYLE_FILE"
        echo "✓ style.json aktualisiert"
    else
        echo "⚠ jq nicht installiert, style.json muss manuell angepasst werden"
        echo "  Setze: \"sprite\": \"https://tiles.oe5ith.at/assets/sprites/poi/poi\""
    fi
fi

echo ""
echo "=== Pipeline komplett! ==="
