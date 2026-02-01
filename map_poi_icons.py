#!/usr/bin/env python3
"""
POI Icon Mapper
Erstellt oder aktualisiert das POI → Font Awesome Mapping.
"""

import argparse
import json
import os
from pathlib import Path

from poi_mapping import AUTO_MAPPINGS, ALL_POI_TYPES


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
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")


def print_success(text):
    print(f"{Colors.OKGREEN}✓{Colors.ENDC} {text}")


def print_warning(text):
    print(f"{Colors.WARNING}⚠{Colors.ENDC} {text}")


def print_info(text):
    print(f"{Colors.OKCYAN}ℹ{Colors.ENDC} {text}")


class POIIconMapper:
    def __init__(self, build_dir="/srv/build/poi-sprites"):
        self.build_dir = Path(build_dir)
        self.mapping_file = self.build_dir / "poi_mapping.json"
        self.mapping = {}

    def setup_directory(self):
        self.build_dir.mkdir(parents=True, exist_ok=True)
        print_success(f"Build-Verzeichnis bereit: {self.build_dir}")

    def load_existing_mapping(self):
        if self.mapping_file.exists():
            with open(self.mapping_file, "r") as f:
                self.mapping = json.load(f)
            print_success(f"Existierendes Mapping geladen: {len(self.mapping)} Einträge")
        else:
            print_info("Kein existierendes Mapping gefunden, starte neu")

    def save_mapping(self):
        with open(self.mapping_file, "w") as f:
            json.dump(self.mapping, f, indent=2, ensure_ascii=False)
        print_success(f"Mapping gespeichert: {self.mapping_file}")

    def create_mapping(self):
        print_header("Erstelle POI → Font Awesome Mapping")

        print_info(f"Insgesamt {len(ALL_POI_TYPES)} POI-Typen zu mappen")
        print_info(f"Automatisch gemappt: {len([p for p in ALL_POI_TYPES if p in AUTO_MAPPINGS])}")
        print_info(f"Manuelle Eingabe nötig: {len([p for p in ALL_POI_TYPES if p not in AUTO_MAPPINGS])}")
        print()

        unmapped = []

        for poi_type in ALL_POI_TYPES:
            if poi_type in self.mapping:
                continue

            if poi_type in AUTO_MAPPINGS:
                self.mapping[poi_type] = AUTO_MAPPINGS[poi_type]
                print_success(f"{poi_type:30} → {AUTO_MAPPINGS[poi_type]}")
            else:
                unmapped.append(poi_type)

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

    def run(self):
        self.setup_directory()
        self.load_existing_mapping()
        self.create_mapping()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create or update POI → Font Awesome mapping.")
    parser.add_argument("--build-dir", default=os.getenv("BUILD_DIR", "/srv/build/poi-sprites"))
    args = parser.parse_args()

    mapper = POIIconMapper(build_dir=args.build_dir)
    mapper.run()
