"""
Module principal de scraping Google Flights
"""

import time
import logging
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

from config import DESTINATIONS, SCRAPING_CONFIG, DOSSIER_DONNEES, FICHIER_CSV

class GoogleFlightsScraper:
    """Classe principale pour le scraping de Google Flights"""
    
    def __init__(self):
        self.driver = None
        self.logger = self._setup_logger()
        self.data = []
        
    def _setup_logger(self):
        """Configuration du système de logs"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'{DOSSIER_DONNEES}/scraping.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def _setup_driver(self):
        """Configuration du driver Chrome avec Selenium standard pour ARM64"""
        try:
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--headless')  # Mode headless pour ARM64
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Utilisation d'un user agent aléatoire
            ua = UserAgent()
            options.add_argument(f'--user-agent={ua.random}')
            
            # Utiliser ChromeDriver système pour ARM64
            options.binary_location = "/usr/bin/chromium-browser"
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.logger.info("Driver Chrome configuré avec succès")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la configuration du driver: {e}")
            return False
    
    def _construct_google_flights_url(self, depart: str, arrivee: str, date_depart: str, 
                                    code_depart: str, code_arrivee: str) -> str:
        """Construction de l'URL Google Flights"""
        base_url = "https://www.google.com/travel/flights"
        
        # Format de l'URL Google Flights
        url = f"{base_url}?hl=fr&tfs={code_depart}_{code_arrivee}_{date_depart}&curr=EUR"
        
        return url
    
    def _extract_flight_data(self, depart: str, arrivee: str, date_depart: str) -> List[Dict]:
        """Extraction des données de vol depuis la page Google Flights"""
        flights_data = []
        
        try:
            # Attendre que les résultats se chargent
            WebDriverWait(self.driver, SCRAPING_CONFIG["timeout_page"]).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='flight-card']"))
            )
            
            # Récupérer tous les vols
            flight_cards = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='flight-card']")
            
            for card in flight_cards[:10]:  # Limiter à 10 premiers résultats
                try:
                    flight_info = self._parse_flight_card(card, depart, arrivee, date_depart)
                    if flight_info:
                        flights_data.append(flight_info)
                        
                except Exception as e:
                    self.logger.warning(f"Erreur lors du parsing d'une carte de vol: {e}")
                    continue
                    
        except TimeoutException:
            self.logger.warning(f"Timeout lors du chargement des résultats pour {depart}-{arrivee}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'extraction des données: {e}")
            
        return flights_data
    
    def _parse_flight_card(self, card, depart: str, arrivee: str, date_depart: str) -> Optional[Dict]:
        """Parsing d'une carte de vol individuelle"""
        try:
            # Extraction du prix
            price_element = card.find_element(By.CSS_SELECTOR, "[data-testid='price']")
            price_text = price_element.text.replace('€', '').replace(',', '').strip()
            price = float(price_text) if price_text.replace('.', '').isdigit() else None
            
            # Extraction des horaires
            time_elements = card.find_elements(By.CSS_SELECTOR, "[data-testid='departure-time'], [data-testid='arrival-time']")
            departure_time = time_elements[0].text if len(time_elements) > 0 else None
            arrival_time = time_elements[1].text if len(time_elements) > 1 else None
            
            # Extraction de la durée
            duration_element = card.find_element(By.CSS_SELECTOR, "[data-testid='duration']")
            duration = duration_element.text if duration_element else None
            
            # Extraction de la compagnie
            airline_element = card.find_element(By.CSS_SELECTOR, "[data-testid='airline']")
            airline = airline_element.text if airline_element else None
            
            # Vérification des escales
            stops_element = card.find_element(By.CSS_SELECTOR, "[data-testid='stops']")
            stops = stops_element.text if stops_element else "Direct"
            
            return {
                'date_collecte': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'depart': depart,
                'arrivee': arrivee,
                'date_depart': date_depart,
                'prix': price,
                'compagnie': airline,
                'heure_depart': departure_time,
                'heure_arrivee': arrival_time,
                'duree_vol': duration,
                'escales': stops,
                'url_source': self.driver.current_url
            }
            
        except Exception as e:
            self.logger.warning(f"Erreur lors du parsing d'une carte: {e}")
            return None
    
    def scrape_destination(self, destination: Dict, date_depart: str) -> List[Dict]:
        """Scraping d'une destination spécifique"""
        depart = destination['depart']
        arrivee = destination['arrivee']
        code_depart = destination['code_depart']
        code_arrivee = destination['code_arrivee']
        
        self.logger.info(f"Scraping: {depart} → {arrivee} le {date_depart}")
        
        url = self._construct_google_flights_url(depart, arrivee, date_depart, code_depart, code_arrivee)
        
        try:
            self.driver.get(url)
            time.sleep(SCRAPING_CONFIG["delai_entre_requetes"])
            
            flights_data = self._extract_flight_data(depart, arrivee, date_depart)
            
            self.logger.info(f"Récupéré {len(flights_data)} vols pour {depart}-{arrivee}")
            return flights_data
            
        except Exception as e:
            self.logger.error(f"Erreur lors du scraping de {depart}-{arrivee}: {e}")
            return []
    
    def scrape_all_destinations(self, dates_recherche: List[str]) -> List[Dict]:
        """Scraping de toutes les destinations pour toutes les dates"""
        all_data = []
        
        if not self._setup_driver():
            return all_data
        
        try:
            for date_depart in dates_recherche:
                for destination in DESTINATIONS:
                    flights = self.scrape_destination(destination, date_depart)
                    all_data.extend(flights)
                    
                    # Pause entre les requêtes
                    time.sleep(SCRAPING_CONFIG["delai_entre_requetes"])
                    
        finally:
            if self.driver:
                self.driver.quit()
                
        return all_data
    
    def save_to_csv(self, data: List[Dict]):
        """Sauvegarde des données en CSV"""
        if not data:
            self.logger.warning("Aucune donnée à sauvegarder")
            return
            
        df = pd.DataFrame(data)
        
        # Ajouter les nouvelles données au fichier existant
        try:
            existing_df = pd.read_csv(f'{DOSSIER_DONNEES}/{FICHIER_CSV}')
            df = pd.concat([existing_df, df], ignore_index=True)
        except FileNotFoundError:
            pass  # Premier fichier
        
        # Sauvegarder
        df.to_csv(f'{DOSSIER_DONNEES}/{FICHIER_CSV}', index=False)
        self.logger.info(f"Données sauvegardées: {len(data)} nouveaux vols")
    
    def run_scraping_session(self, dates_recherche: List[str]):
        """Exécution d'une session de scraping complète"""
        self.logger.info("Début de la session de scraping")
        
        start_time = datetime.now()
        data = self.scrape_all_destinations(dates_recherche)
        
        if data:
            self.save_to_csv(data)
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        self.logger.info(f"Session terminée en {duration}")
        self.logger.info(f"Total: {len(data)} vols récupérés")
        
        return data 