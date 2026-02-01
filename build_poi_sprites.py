#!/usr/bin/env python3
"""
POI Sprite Builder - Docker Edition
Angepasst für bestehende Geodata Pipeline mit Docker-basiertem spreet
"""

import argparse
import json
import os
import sys
import subprocess
import shutil
from pathlib import Path
import urllib.request
import zipfile

from poi_mapping import ALL_POI_TYPES

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
    
    def load_existing_mapping(self, required=True):
        """Lade existierendes Mapping"""
        if self.mapping_file.exists():
            with open(self.mapping_file, 'r') as f:
                self.mapping = json.load(f)
            print_success(f"Existierendes Mapping geladen: {len(self.mapping)} Einträge")
            return True

        if required:
            print_warning("Kein Mapping gefunden. Bitte zuerst map_poi_icons.py ausführen.")
            return False

        print_info("Kein existierendes Mapping gefunden, starte neu")
        return True
    
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
            if not self.load_existing_mapping(required=True):
                sys.exit(1)
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
    parser = argparse.ArgumentParser(description="Build POI sprites from a saved mapping.")
    parser.add_argument("--build-dir", default=os.getenv("BUILD_DIR", "/srv/build/poi-sprites"))
    parser.add_argument("--output-dir", default=os.getenv("OUTPUT_DIR", "/srv/assets/sprites/poi"))
    parser.add_argument("--docker-image", default=os.getenv("DOCKER_IMAGE", "local-spreet-builder"))
    parser.add_argument("--sprite-name", default=os.getenv("SPRITE_NAME", "poi"))
    args = parser.parse_args()

    builder = POISpriteBuilder(
        build_dir=args.build_dir,
        output_dir=args.output_dir,
        docker_image=args.docker_image,
        sprite_name=args.sprite_name,
    )
    builder.run()
