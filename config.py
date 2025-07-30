"""
Configuration du projet de scraping Google Flights
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Tuple

# Configuration des destinations
DESTINATIONS = [
    # Europe
    {"depart": "Paris", "arrivee": "Londres", "code_depart": "CDG", "code_arrivee": "LHR"},
    {"depart": "Paris", "arrivee": "Berlin", "code_depart": "CDG", "code_arrivee": "BER"},
    {"depart": "Paris", "arrivee": "Rome", "code_depart": "CDG", "code_arrivee": "FCO"},
    {"depart": "Paris", "arrivee": "Madrid", "code_depart": "CDG", "code_arrivee": "MAD"},
    {"depart": "Paris", "arrivee": "Amsterdam", "code_depart": "CDG", "code_arrivee": "AMS"},
    
    # Amérique du Nord
    {"depart": "Paris", "arrivee": "New York", "code_depart": "CDG", "code_arrivee": "JFK"},
    {"depart": "Paris", "arrivee": "Los Angeles", "code_depart": "CDG", "code_arrivee": "LAX"},
    {"depart": "Paris", "arrivee": "Montreal", "code_depart": "CDG", "code_arrivee": "YUL"},
    {"depart": "Paris", "arrivee": "Toronto", "code_depart": "CDG", "code_arrivee": "YYZ"},
    
    # Asie
    {"depart": "Paris", "arrivee": "Tokyo", "code_depart": "CDG", "code_arrivee": "NRT"},
    {"depart": "Paris", "arrivee": "Bangkok", "code_depart": "CDG", "code_arrivee": "BKK"},
    {"depart": "Paris", "arrivee": "Singapour", "code_depart": "CDG", "code_arrivee": "SIN"},
    {"depart": "Paris", "arrivee": "Dubai", "code_depart": "CDG", "code_arrivee": "DXB"},
    
    # Afrique
    {"depart": "Paris", "arrivee": "Casablanca", "code_depart": "CDG", "code_arrivee": "CMN"},
    {"depart": "Paris", "arrivee": "Tunis", "code_depart": "CDG", "code_arrivee": "TUN"},
    {"depart": "Paris", "arrivee": "Alger", "code_depart": "CDG", "code_arrivee": "ALG"},
]

# Configuration des dates de recherche
def get_dates_recherche():
    """Génère les dates de recherche pour les 12 prochains mois"""
    dates = []
    date_actuelle = datetime.now()
    
    # Recherche pour les 12 prochains mois
    for mois in range(1, 13):
        date_recherche = date_actuelle + timedelta(days=30*mois)
        dates.append(date_recherche.strftime("%Y-%m-%d"))
    
    return dates

# Configuration des horaires de collecte (3 fois par jour)
HORAIRES_COLLECTE = [
    "08:00",  # Matin
    "14:00",  # Après-midi
    "20:00",  # Soir
]

# Configuration des fichiers
DOSSIER_DONNEES = "donnees"
FICHIER_CSV = "vols_data.csv"
FICHIER_LOG = "scraping.log"



# Configuration du scraping
SCRAPING_CONFIG = {
    "delai_entre_requetes": 5,  # secondes
    "timeout_page": 30,  # secondes
    "max_tentatives": 3,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Création du dossier de données s'il n'existe pas
if not os.path.exists(DOSSIER_DONNEES):
    os.makedirs(DOSSIER_DONNEES) 