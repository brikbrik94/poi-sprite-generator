#!/bin/bash

# ==========================================
# POI SPRITE BUILDER - Docker Edition
# Integriert in bestehende Geodata Pipeline
# ==========================================

set -euo pipefail

# ==========================================
# KONFIGURATION
# ==========================================
DOCKER_IMAGE="${DOCKER_IMAGE:-local-spreet-builder}"
BUILD_DIR="${BUILD_DIR:-/srv/build/poi-sprites}"
OUTPUT_DIR="${OUTPUT_DIR:-/srv/assets/sprites/poi}"
SPRITE_NAME="${SPRITE_NAME:-poi}"
SPREET_REPO="https://github.com/flother/spreet.git"

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "  POI Sprite Builder (Docker Edition)"
echo "=========================================="
echo ""

# ==========================================
# 0. VORAUSSETZUNGEN PRÜFEN
# ==========================================
echo -e "${BLUE}--- Prüfe Voraussetzungen... ---${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker nicht gefunden!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker gefunden${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python3 nicht gefunden!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python3 gefunden${NC}"

# Docker läuft?
if ! docker ps &> /dev/null; then
    echo -e "${RED}✗ Docker läuft nicht!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker läuft${NC}"

# ==========================================
# 1. DOCKER IMAGE BAUEN (falls nötig)
# ==========================================
echo ""
echo -e "${BLUE}--- Prüfe spreet Docker-Image... ---${NC}"

if [[ "$(docker images -q $DOCKER_IMAGE 2> /dev/null)" == "" ]]; then
    echo -e "${YELLOW}⚠ Image nicht gefunden, baue '$DOCKER_IMAGE'...${NC}"
    if ! docker build -t "$DOCKER_IMAGE" "$SPREET_REPO"; then
        echo -e "${RED}✗ Docker-Build fehlgeschlagen!${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker-Image gebaut${NC}"
else
    echo -e "${GREEN}✓ Docker-Image '$DOCKER_IMAGE' vorhanden${NC}"
fi

# ==========================================
# 2. VERZEICHNISSE ERSTELLEN
# ==========================================
echo ""
echo -e "${BLUE}--- Erstelle Verzeichnisse... ---${NC}"

mkdir -p "$BUILD_DIR"/{svgs,tmp,fontawesome}
mkdir -p "$OUTPUT_DIR"

echo -e "${GREEN}✓ Build-Dir: $BUILD_DIR${NC}"
echo -e "${GREEN}✓ Output-Dir: $OUTPUT_DIR${NC}"

# ==========================================
# 3. PYTHON-SCRIPT AUSFÜHREN
# ==========================================
echo ""
echo -e "${BLUE}--- Starte POI Sprite Builder... ---${NC}"
echo ""

# Finde das Python-Script (sollte im gleichen Verzeichnis sein)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/build_poi_sprites.py"
MAPPER_SCRIPT="$SCRIPT_DIR/map_poi_icons.py"
MAPPING_FILE="$BUILD_DIR/poi_mapping.json"

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}✗ Python-Script nicht gefunden: $PYTHON_SCRIPT${NC}"
    exit 1
fi
if [ ! -f "$MAPPER_SCRIPT" ]; then
    echo -e "${RED}✗ Mapper-Script nicht gefunden: $MAPPER_SCRIPT${NC}"
    exit 1
fi

# Mapping nur erstellen, wenn noch nicht vorhanden
if [ ! -f "$MAPPING_FILE" ]; then
    echo -e "${BLUE}--- Erstelle POI → Font Awesome Mapping... ---${NC}"
    python3 "$MAPPER_SCRIPT" --build-dir "$BUILD_DIR"
fi

# Führe Sprite-Builder aus
python3 "$PYTHON_SCRIPT" \
    --build-dir "$BUILD_DIR" \
    --output-dir "$OUTPUT_DIR" \
    --docker-image "$DOCKER_IMAGE" \
    --sprite-name "$SPRITE_NAME"

exit_code=$?

# ==========================================
# 4. ABSCHLUSS
# ==========================================
echo ""

if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}  ✨ POI-Sprites erfolgreich erstellt! ✨${NC}"
    echo -e "${GREEN}=========================================${NC}"
    echo ""
    echo "Ausgabe-Verzeichnis:"
    echo "  $OUTPUT_DIR"
    echo ""
    echo "Erstelle Dateien:"
    find "$OUTPUT_DIR" -type f \( -name "*.json" -o -name "*.png" \) -exec ls -lh {} \;
    echo ""
    echo "MapLibre Sprite-URL:"
    echo "  https://tiles.oe5ith.at/assets/sprites/poi/$SPRITE_NAME"
    echo ""
    echo "Nächste Schritte:"
    echo "  1. Sprites sind bereits unter /srv/assets/sprites/poi/"
    echo "  2. Konfiguriere in deiner style.json:"
    echo "     \"sprite\": \"https://tiles.oe5ith.at/assets/sprites/poi/$SPRITE_NAME\""
    echo "  3. Verwende in Layers: \"icon-image\": [\"get\", \"class\"]"
    echo ""
else
    echo -e "${RED}=========================================${NC}"
    echo -e "${RED}  ✗ Fehler beim Erstellen der Sprites${NC}"
    echo -e "${RED}=========================================${NC}"
    echo ""
    echo "Prüfe die Ausgabe oben für Details."
    echo "Fortschritt wurde in $BUILD_DIR/poi_mapping.json gespeichert."
fi

exit $exit_code
