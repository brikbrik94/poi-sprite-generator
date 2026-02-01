#!/usr/bin/env python3
"""
POI Sprite Builder - Docker Edition
Angepasst für bestehende Geodata Pipeline mit Docker-basiertem spreet
"""

import json
import os
import sys
import subprocess
import shutil
from pathlib import Path
import urllib.request
import zipfile

# Farben für Terminal-Output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓{Colors.ENDC} {text}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠{Colors.ENDC} {text}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ{Colors.ENDC} {text}")

# Automatisches Mapping: POI-Typ -> Font Awesome Icon-Name (ohne fa- Präfix)
AUTO_MAPPINGS = {
    # UNTERKUNFT & GASTRO
    "lodging": "bed",
    "restaurant": "utensils",
    "cafe": "coffee",
    "bar": "wine-glass",
    "beer": "beer-mug-empty",
    "biergarten": "beer-mug-empty",
    "fast_food": "burger",
    "ice_cream": "ice-cream",
    "pub": "beer-mug-empty",
    
    # EINZELHANDEL & SERVICES
    "shop": "store",
    "grocery": "basket-shopping",
    "bakery": "bread-slice",
    "butcher": "meat",
    "alcohol_shop": "wine-bottle",
    "clothing_store": "shirt",
    "hairdresser": "scissors",
    "laundry": "soap",
    
    # GESUNDHEIT
    "hospital": "hospital",
    "doctors": "user-doctor",
    "pharmacy": "prescription-bottle",
    "dentist": "tooth",
    "veterinary": "paw",
    
    # BILDUNG
    "school": "school",
    "college": "graduation-cap",
    "library": "book",
    "kindergarten": "child",
    
    # ÖFFENTLICHE EINRICHTUNGEN
    "town_hall": "landmark",
    "post": "envelope",
    "police": "shield",
    "fire_station": "fire-extinguisher",
    "prison": "lock",
    "office": "building",
    "community_centre": "users",
    "public_building": "building-columns",
    
    # KULTUR & FREIZEIT
    "museum": "building-columns",
    "art_gallery": "palette",
    "theatre": "masks-theater",
    "cinema": "film",
    "castle": "chess-rook",
    "monument": "monument",
    "attraction": "star",
    "theme_park": "ferris-wheel",
    "zoo": "hippo",
    "aquarium": "fish",
    "music": "music",
    "hackerspace": "laptop-code",
    
    # RELIGIÖS
    "place_of_worship": "place-of-worship",
    
    # VERKEHR & INFRASTRUKTUR
    "parking": "square-parking",
    "bicycle_parking": "bicycle",
    "motorcycle_parking": "motorcycle",
    "fuel": "gas-pump",
    "bus": "bus",
    "railway": "train",
    "aerialway": "cable-car",
    "ferry_terminal": "ferry",
    "gate": "door-open",
    "lift_gate": "bars",
    "bollard": "road-barrier",
    "cycle_barrier": "bars",
    "stile": "stairs",
    "sally_port": "door-closed",
    "toll_booth": "money-bill",
    "border_control": "passport",
    "entrance": "door-open",
    "harbor": "anchor",
    
    # SPORT & RECREATION - Ball-Sportarten
    "pitch": "futbol",
    "stadium": "building",
    "sports_centre": "dumbbell",
    "athletics": "person-running",
    "football": "futbol",
    "soccer": "futbol",
    "basketball": "basketball",
    "volleyball": "volleyball",
    "beachvolleyball": "volleyball",
    "tennis": "table-tennis-paddle-ball",
    "table_tennis": "table-tennis-paddle-ball",
    "handball": "hand",
    "team_handball": "hand",
    "baseball": "baseball",
    "field_hockey": "hockey-puck",
    "hockey": "hockey-puck",
    "rugby_union": "football",
    "badminton": "shuttle-space",
    
    # SPORT - Wasser
    "swimming": "person-swimming",
    "swimming_pool": "person-swimming",
    "water_park": "water",
    "scuba_diving": "water",
    "water_ski": "person-skiing-nordic",
    "sailing": "sailboat",
    "rowing": "water",
    "canoe": "water",
    "surfing": "water",
    "diving": "water",
    
    # SPORT - Winter
    "winter_sports": "snowflake",
    "ice_hockey": "hockey-puck",
    "ice_rink": "snowflake",
    "ice_stock": "snowflake",
    "curling": "snowflake",
    "skiing": "person-skiing",
    "skating": "snowflake",
    "toboggan": "sleigh",
    
    # SPORT - Andere
    "golf": "golf-ball-tee",
    "disc_golf": "compact-disc",
    "cycling": "bicycle",
    "bicycle": "bicycle",
    "running": "person-running",
    "climbing": "mountain",
    "climbing_adventure": "mountain",
    "archery": "bullseye",
    "shooting": "bullseye",
    "shooting_range": "bullseye",
    "gymnastics": "person-walking",
    "yoga": "spa",
    "judo": "hand-fist",
    "boxing": "hand-fist",
    "wrestling": "hand-fist",
    "equestrian": "horse",
    "horse_racing": "horse",
    "dog_racing": "dog",
    "motor": "car",
    "motocross": "motorcycle",
    "rc_car": "car",
    "karting": "car",
    "skateboard": "person-skateboarding",
    "bmx": "bicycle",
    "paragliding": "plane",
    "free_flying": "plane",
    "model_aerodrome": "plane",
    "orienteering": "compass",
    "paintball": "bullseye",
    "billiards": "circle",
    "table_soccer": "futbol",
    "chess": "chess",
    "bowls": "bowling-ball",
    "boules": "circle",
    "horseshoes": "horse",
    "racquet": "table-tennis-paddle-ball",
    "paddle_tennis": "table-tennis-paddle-ball",
    "long_jump": "person-running",
    
    # NATUR & PARKS
    "park": "tree",
    "garden": "leaf",
    "playground": "child",
    "picnic_site": "utensils",
    "dog_park": "dog",
    "campsite": "campground",
    "basin": "water",
    "reservoir": "water",
    
    # UTILITIES & SERVICES
    "atm": "money-bill",
    "toilets": "restroom",
    "drinking_water": "faucet-drip",
    "fountain": "fountain",
    "waste_basket": "trash-can",
    "recycling": "recycle",
    "information": "circle-info",
    "shelter": "house",
    "bench": "chair",
    "telephone": "phone",
    "car": "car",
    "multi": "circle",
}

# Alle POI-Typen aus der Referenz
ALL_POI_TYPES = [
    "lodging", "restaurant", "cafe", "bar", "beer", "biergarten", "fast_food", 
    "ice_cream", "pub", "shop", "grocery", "bakery", "butcher", "alcohol_shop", 
    "clothing_store", "hairdresser", "laundry", "hospital", "doctors", "pharmacy", 
    "dentist", "veterinary", "school", "college", "library", "kindergarten",
    "town_hall", "post", "police", "fire_station", "prison", "office", 
    "community_centre", "public_building", "museum", "art_gallery", "theatre", 
    "cinema", "castle", "monument", "attraction", "theme_park", "zoo", "aquarium", 
    "music", "hackerspace", "place_of_worship", "parking", "bicycle_parking", 
    "motorcycle_parking", "fuel", "bus", "railway", "aerialway", "ferry_terminal", 
    "gate", "lift_gate", "bollard", "cycle_barrier", "stile", "sally_port", 
    "toll_booth", "border_control", "entrance", "harbor", "pitch", "stadium", 
    "sports_centre", "athletics", "football", "soccer", "basketball", "volleyball", 
    "beachvolleyball", "tennis", "table_tennis", "handball", "team_handball", 
    "baseball", "field_hockey", "hockey", "rugby_union", "badminton", "swimming", 
    "swimming_pool", "water_park", "scuba_diving", "water_ski", "sailing", "rowing", 
    "canoe", "surfing", "diving", "winter_sports", "ice_hockey", "ice_rink", 
    "ice_stock", "curling", "skiing", "skating", "toboggan", "golf", "disc_golf", 
    "cycling", "bicycle", "running", "climbing", "climbing_adventure", "archery", 
    "shooting", "shooting_range", "gymnastics", "yoga", "judo", "boxing", 
    "wrestling", "equestrian", "horse_racing", "dog_racing", "motor", "motocross", 
    "rc_car", "karting", "skateboard", "bmx", "paragliding", "free_flying", 
    "model_aerodrome", "orienteering", "paintball", "billiards", "table_soccer", 
    "chess", "bowls", "boules", "horseshoes", "racquet", "paddle_tennis", 
    "long_jump", "park", "garden", "playground", "picnic_site", "dog_park", 
    "campsite", "basin", "reservoir", "atm", "toilets", "drinking_water", 
    "fountain", "waste_basket", "recycling", "information", "shelter", "bench", 
    "telephone", "car", "multi",
]


class POISpriteBuilder:
    def __init__(self, 
                 build_dir="/srv/build/poi-sprites",
                 output_dir="/srv/assets/sprites/poi",
                 docker_image="local-spreet-builder",
                 sprite_name="poi"):
        
        self.build_dir = Path(build_dir)
        self.output_dir = Path(output_dir)
        self.docker_image = docker_image
        self.sprite_name = sprite_name
        
        # Unterverzeichnisse im Build-Dir
        self.svg_dir = self.build_dir / "svgs"
        self.tmp_dir = self.build_dir / "tmp"
        self.fa_dir = self.build_dir / "fontawesome"
        self.mapping_file = self.build_dir / "poi_mapping.json"
        
        # Mapping speichern
        self.mapping = {}
        
    def setup_directories(self):
        """Erstelle Arbeitsverzeichnisse"""
        print_header("Setup Verzeichnisse")
        
        for directory in [self.build_dir, self.svg_dir, self.tmp_dir, self.fa_dir, self.output_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            print_success(f"Verzeichnis erstellt: {directory}")
    
    def load_existing_mapping(self):
        """Lade existierendes Mapping falls vorhanden"""
        if self.mapping_file.exists():
            with open(self.mapping_file, 'r') as f:
                self.mapping = json.load(f)
            print_success(f"Existierendes Mapping geladen: {len(self.mapping)} Einträge")
        else:
            print_info("Kein existierendes Mapping gefunden, starte neu")
    
    def save_mapping(self):
        """Speichere Mapping in JSON"""
        with open(self.mapping_file, 'w') as f:
            json.dump(self.mapping, f, indent=2, ensure_ascii=False)
        print_success(f"Mapping gespeichert: {self.mapping_file}")
    
    def create_mapping(self):
        """Erstelle interaktives Mapping"""
        print_header("Erstelle POI → Font Awesome Mapping")
        
        print_info(f"Insgesamt {len(ALL_POI_TYPES)} POI-Typen zu mappen")
        print_info(f"Automatisch gemappt: {len([p for p in ALL_POI_TYPES if p in AUTO_MAPPINGS])}")
        print_info(f"Manuelle Eingabe nötig: {len([p for p in ALL_POI_TYPES if p not in AUTO_MAPPINGS])}")
        print()
        
        unmapped = []
        
        for poi_type in ALL_POI_TYPES:
            # Überspringe wenn bereits gemappt
            if poi_type in self.mapping:
                continue
                
            # Versuche Auto-Mapping
            if poi_type in AUTO_MAPPINGS:
                self.mapping[poi_type] = AUTO_MAPPINGS[poi_type]
                print_success(f"{poi_type:30} → {AUTO_MAPPINGS[poi_type]}")
            else:
                unmapped.append(poi_type)
        
        # Interaktive Eingabe für unmapped POIs
        if unmapped:
            print()
            print_warning(f"{len(unmapped)} POI-Typen benötigen manuelle Zuordnung")
            print_info("Suche Icons auf: https://fontawesome.com/search?o=r&m=free")
            print_info("Gib nur den Icon-Namen ein (ohne 'fa-' Präfix)")
            print_info("Beispiel: Für 'fa-circle' gib nur 'circle' ein")
            print_info("Drücke ENTER ohne Eingabe um zu überspringen")
            print()
            
            for poi_type in unmapped:
                icon = input(f"{Colors.OKCYAN}Icon für '{poi_type}': {Colors.ENDC}").strip()
                if icon:
                    self.mapping[poi_type] = icon
                    print_success(f"Gespeichert: {poi_type} → {icon}")
                else:
                    print_warning(f"Übersprungen: {poi_type}")
        
        self.save_mapping()
        
        mapped_count = len([p for p in ALL_POI_TYPES if p in self.mapping])
        print()
        print_success(f"Mapping abgeschlossen: {mapped_count}/{len(ALL_POI_TYPES)} POI-Typen gemappt")
    
    def download_fontawesome(self):
        """Lade Font Awesome Free herunter"""
        print_header("Font Awesome Download")
        
        fa_zip = self.build_dir / "fontawesome.zip"
        
        if (self.fa_dir / "svgs").exists():
            print_info("Font Awesome bereits heruntergeladen, überspringe Download")
            return
        
        print_info("Lade Font Awesome Free von GitHub...")
        url = "https://github.com/FortAwesome/Font-Awesome/releases/download/6.5.1/fontawesome-free-6.5.1-web.zip"
        
        try:
            urllib.request.urlretrieve(url, fa_zip)
            print_success("Download abgeschlossen")
            
            print_info("Entpacke Font Awesome...")
            with zipfile.ZipFile(fa_zip, 'r') as zip_ref:
                zip_ref.extractall(self.fa_dir)
            
            print_success("Font Awesome entpackt")
            fa_zip.unlink()
            
        except Exception as e:
            print_warning(f"Automatischer Download fehlgeschlagen: {e}")
            print_info("Bitte lade Font Awesome manuell herunter:")
            print_info("1. Gehe zu: https://fontawesome.com/download")
            print_info("2. Lade 'Free For Web' herunter")
            print_info(f"3. Entpacke das Archiv nach: {self.fa_dir}")
            input("\nDrücke ENTER wenn bereit...")
    
    def copy_svgs(self):
        """Kopiere und benenne SVGs basierend auf Mapping"""
        print_header("Kopiere SVG Icons")
        
        # Finde Font Awesome SVG-Verzeichnisse
        fa_svgs_base = None
        for root, dirs, files in os.walk(self.fa_dir):
            if 'svgs' in dirs:
                fa_svgs_base = Path(root) / 'svgs'
                break
        
        if not fa_svgs_base or not fa_svgs_base.exists():
            print_warning("Font Awesome SVG-Verzeichnis nicht gefunden!")
            fa_svgs_base = self.fa_dir
        
        print_info(f"Font Awesome Basis: {fa_svgs_base}")
        
        copied = 0
        not_found = []
        
        for poi_type, icon_name in self.mapping.items():
            svg_found = False
            
            for category in ['solid', 'regular', 'brands']:
                svg_path = fa_svgs_base / category / f"{icon_name}.svg"
                
                if svg_path.exists():
                    dest = self.svg_dir / f"{poi_type}.svg"
                    shutil.copy2(svg_path, dest)
                    print_success(f"{poi_type:30} → {icon_name}.svg ({category})")
                    copied += 1
                    svg_found = True
                    break
            
            if not svg_found:
                for svg_file in fa_svgs_base.rglob(f"{icon_name}.svg"):
                    dest = self.svg_dir / f"{poi_type}.svg"
                    shutil.copy2(svg_file, dest)
                    print_success(f"{poi_type:30} → {icon_name}.svg (gefunden)")
                    copied += 1
                    svg_found = True
                    break
                
                if not svg_found:
                    not_found.append((poi_type, icon_name))
                    print_warning(f"Nicht gefunden: {icon_name}.svg für {poi_type}")
        
        print()
        print_success(f"{copied} SVGs erfolgreich kopiert")
        
        if not_found:
            print_warning(f"{len(not_found)} Icons nicht gefunden:")
            for poi, icon in not_found[:10]:
                print(f"  - {poi} → {icon}")
    
    def check_docker(self):
        """Prüfe ob Docker läuft"""
        print_header("Prüfe Docker")
        
        try:
            result = subprocess.run(['docker', 'ps'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print_success("Docker läuft")
                return True
            else:
                print_warning("Docker läuft nicht")
                return False
        except FileNotFoundError:
            print_warning("Docker nicht gefunden!")
            return False
    
    def build_docker_image(self):
        """Baue spreet Docker-Image falls nicht vorhanden"""
        print_header("Prüfe spreet Docker-Image")
        
        # Prüfe ob Image existiert
        result = subprocess.run(
            ['docker', 'images', '-q', self.docker_image],
            capture_output=True, text=True
        )
        
        if result.stdout.strip():
            print_success(f"Docker-Image '{self.docker_image}' bereits vorhanden")
            return True
        
        print_info(f"Baue Docker-Image '{self.docker_image}'...")
        
        spreet_repo = "https://github.com/flother/spreet.git"
        
        try:
            result = subprocess.run(
                ['docker', 'build', '-t', self.docker_image, spreet_repo],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                print_success(f"Docker-Image erfolgreich gebaut")
                return True
            else:
                print_warning(f"Fehler beim Bauen: {result.stderr}")
                return False
                
        except Exception as e:
            print_warning(f"Fehler: {e}")
            return False
    
    def build_sprites_with_docker(self):
        """Erstelle Sprites mit Docker-spreet"""
        print_header("Erstelle Sprites mit Docker")
        
        if not self.check_docker():
            print_warning("Docker nicht verfügbar")
            return False
        
        if not self.build_docker_image():
            print_warning("Docker-Image nicht verfügbar")
            return False
        
        svg_count = len(list(self.svg_dir.glob("*.svg")))
        if svg_count == 0:
            print_warning("Keine SVG-Dateien zum Verarbeiten gefunden!")
            return False
        
        print_info(f"Verarbeite {svg_count} SVG-Dateien...")
        
        # Erstelle Sprites in verschiedenen Auflösungen
        for retina in [False, True]:
            suffix = "@2x" if retina else ""
            output_name = f"{self.sprite_name}{suffix}"
            
            print_info(f"Erstelle {output_name}...")
            
            # Docker-Command zusammenbauen
            cmd = [
                'docker', 'run', '--rm',
                '--entrypoint', '/app/spreet',
                '-v', f"{self.svg_dir.absolute()}:/sources",
                '-v', f"{self.output_dir.absolute()}:/output",
                self.docker_image
            ]
            
            if retina:
                cmd.append('--retina')
            
            cmd.extend(['/sources', f'/output/{output_name}'])
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print_success(f"{output_name}.png erstellt")
                    print_success(f"{output_name}.json erstellt")
                else:
                    print_warning(f"Fehler: {result.stderr}")
                    
            except Exception as e:
                print_warning(f"Fehler beim Ausführen: {e}")
        
        return True
    
    def generate_docs(self):
        """Erstelle Dokumentation"""
        print_header("Erstelle Dokumentation")
        
        # README für output dir
        readme = self.output_dir / "README.md"
        with open(readme, 'w') as f:
            f.write(f"""# POI Sprites

Automatisch generierte Sprites für PMTiles POI-Layer.

## Dateien

- `{self.sprite_name}.png` - Sprite-Sheet (1x)
- `{self.sprite_name}.json` - Sprite-Metadaten (1x)
- `{self.sprite_name}@2x.png` - Sprite-Sheet (2x Retina)
- `{self.sprite_name}@2x.json` - Sprite-Metadaten (2x)

## MapLibre Verwendung

```json
{{
  "sprite": "https://tiles.oe5ith.at/assets/sprites/poi/{self.sprite_name}",
  "layers": [
    {{
      "id": "poi-icons",
      "type": "symbol",
      "source": "pmtiles",
      "source-layer": "poi",
      "layout": {{
        "icon-image": ["get", "class"],
        "icon-size": 0.8
      }}
    }}
  ]
}}
```

## Gemappte POI-Typen: {len(self.mapping)}

Basiert auf Font Awesome Free Icons.
""")
        
        print_success(f"README erstellt: {readme}")
        
        # Info in build dir
        info_file = self.build_dir / "build_info.json"
        with open(info_file, 'w') as f:
            json.dump({
                "sprite_name": self.sprite_name,
                "total_pois": len(ALL_POI_TYPES),
                "mapped_pois": len(self.mapping),
                "output_dir": str(self.output_dir),
                "files": [
                    f"{self.sprite_name}.png",
                    f"{self.sprite_name}.json",
                    f"{self.sprite_name}@2x.png",
                    f"{self.sprite_name}@2x.json"
                ]
            }, f, indent=2)
        
        print_success(f"Build-Info erstellt: {info_file}")
    
    def run(self):
        """Führe kompletten Build-Prozess aus"""
        try:
            self.setup_directories()
            self.load_existing_mapping()
            self.create_mapping()
            self.download_fontawesome()
            self.copy_svgs()
            
            if self.build_sprites_with_docker():
                self.generate_docs()
                
                print_header("✨ Fertig! ✨")
                print_success("POI-Sprites erfolgreich erstellt!")
                print_info(f"Ausgabe: {self.output_dir}")
                print()
                print_info("Sprite-URL für MapLibre:")
                print(f"  https://tiles.oe5ith.at/assets/sprites/poi/{self.sprite_name}")
            else:
                print_warning("Sprite-Generierung fehlgeschlagen")
            
        except KeyboardInterrupt:
            print()
            print_warning("Abgebrochen durch Benutzer")
            print_info(f"Fortschritt gespeichert in: {self.mapping_file}")
            sys.exit(1)
        except Exception as e:
            print()
            print_warning(f"Fehler: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    builder = POISpriteBuilder()
    builder.run()
