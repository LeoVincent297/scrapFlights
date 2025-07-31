"""
Script principal du projet de scraping Google Flights
Orchestre le scraping, la planification et le transfert SFTP
"""

import sys
import logging
from datetime import datetime

from scraper import GoogleFlightsScraper
from scheduler import ScrapingScheduler
from config import DOSSIER_DONNEES, get_dates_recherche

def setup_logging():
    """Configuration du système de logs principal"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'{DOSSIER_DONNEES}/main.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def run_single_scraping():
    """Exécution d'une seule session de scraping"""
    logger = setup_logging()
    logger.info("=== DÉBUT DE LA SESSION DE SCRAPING UNIQUE ===")

    try:
        # Exécuter le scraping
        scraper = GoogleFlightsScraper()
        dates_recherche = get_dates_recherche()
        data = scraper.run_scraping_session(dates_recherche)

        if data:
            logger.info(f"Scraping terminé: {len(data)} vols récupérés")
        else:
            logger.warning("Aucune donnée récupérée")

    except Exception as e:
        logger.error(f"Erreur lors de la session: {e}")

    logger.info("=== FIN DE LA SESSION ===")

def run_scheduler_with_transfer():
    """Exécution du scheduler avec transfert automatique"""
    logger = setup_logging()
    logger.info("=== DÉMARRAGE DU SYSTÈME COMPLET ===")

    try:
        # Créer le scheduler avec transfert intégré
        scheduler = ScrapingSchedulerWithTransfer()
        scheduler.run_scheduler()

    except KeyboardInterrupt:
        logger.info("Arrêt demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur dans le système principal: {e}")

class ScrapingSchedulerWithTransfer(ScrapingScheduler):
    """Scheduler étendu pour le scraping automatique"""

    def __init__(self):
        super().__init__()

    def run_scraping_job(self):
        """Tâche de scraping automatique"""
        self.logger.info("=== DÉBUT DE LA TÂCHE DE SCRAPING ===")

        try:
            # Exécuter le scraping
            data = self.scraper.run_scraping_session(self.dates_recherche)

            if data:
                self.logger.info(f"Scraping terminé: {len(data)} vols récupérés")
            else:
                self.logger.warning("Aucune donnée récupérée")

        except Exception as e:
            self.logger.error(f"Erreur lors de la tâche: {e}")

        self.logger.info("=== FIN DE LA TÂCHE ===")

def show_help():
    """Affichage de l'aide"""
    print("""
Script de scraping Google Flights

Usage:
    python main.py [option]

Options:
    --once          Exécuter une seule session de scraping
    --scheduler     Démarrer le scheduler automatique (par défaut)
    --help          Afficher cette aide

Exemples:
    python main.py --once          # Une seule collecte
    python main.py --scheduler     # Collecte automatique 3x/jour
    python main.py                 # Même que --scheduler
    """)

def main():
    """Fonction principale"""
    if len(sys.argv) > 1:
        option = sys.argv[1]

        if option == "--once":
            run_single_scraping()
        elif option == "--scheduler":
            run_scheduler_with_transfer()
        elif option == "--help":
            show_help()
        else:
            print(f"Option inconnue: {option}")
            show_help()
    else:
        # Par défaut, démarrer le scheduler
        run_scheduler_with_transfer()

if __name__ == "__main__":
    main()
