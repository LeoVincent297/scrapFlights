"""
Module de planification pour exécuter le scraping automatiquement
"""

import schedule
import time
import logging
from datetime import datetime, timedelta
from typing import List

from scraper import GoogleFlightsScraper
from config import HORAIRES_COLLECTE, get_dates_recherche, DOSSIER_DONNEES

class ScrapingScheduler:
    """Gestionnaire de planification du scraping"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.scraper = GoogleFlightsScraper()
        self.dates_recherche = get_dates_recherche()
        
    def _setup_logger(self):
        """Configuration du système de logs pour le scheduler"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'{DOSSIER_DONNEES}/scheduler.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def run_scraping_job(self):
        """Tâche de scraping planifiée"""
        self.logger.info("=== DÉBUT DE LA TÂCHE DE SCRAPING PLANIFIÉE ===")
        
        try:
            # Exécuter le scraping
            data = self.scraper.run_scraping_session(self.dates_recherche)
            
            self.logger.info(f"Tâche terminée avec succès: {len(data)} vols récupérés")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'exécution de la tâche: {e}")
            
        self.logger.info("=== FIN DE LA TÂCHE DE SCRAPING ===")
    
    def setup_schedule(self):
        """Configuration de la planification"""
        self.logger.info("Configuration de la planification...")
        
        # Planifier les tâches aux horaires définis
        for horaire in HORAIRES_COLLECTE:
            schedule.every().day.at(horaire).do(self.run_scraping_job)
            self.logger.info(f"Tâche planifiée à {horaire}")
        
        # Planifier une tâche de maintenance quotidienne
        schedule.every().day.at("02:00").do(self.maintenance_task)
        
        self.logger.info("Planification configurée avec succès")
    
    def maintenance_task(self):
        """Tâche de maintenance quotidienne"""
        self.logger.info("=== DÉBUT DE LA TÂCHE DE MAINTENANCE ===")
        
        try:
            # Mettre à jour les dates de recherche
            self.dates_recherche = get_dates_recherche()
            self.logger.info("Dates de recherche mises à jour")
            
            # Nettoyer les logs anciens (garder 30 jours)
            self.cleanup_old_logs()
            
            self.logger.info("Maintenance terminée avec succès")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la maintenance: {e}")
            
        self.logger.info("=== FIN DE LA TÂCHE DE MAINTENANCE ===")
    
    def cleanup_old_logs(self):
        """Nettoyage des anciens logs"""
        try:
            import os
            from datetime import datetime, timedelta
            
            # Supprimer les logs de plus de 30 jours
            cutoff_date = datetime.now() - timedelta(days=30)
            
            log_files = [
                f'{DOSSIER_DONNEES}/scraping.log',
                f'{DOSSIER_DONNEES}/scheduler.log'
            ]
            
            for log_file in log_files:
                if os.path.exists(log_file):
                    file_time = datetime.fromtimestamp(os.path.getmtime(log_file))
                    if file_time < cutoff_date:
                        os.remove(log_file)
                        self.logger.info(f"Ancien log supprimé: {log_file}")
                        
        except Exception as e:
            self.logger.warning(f"Erreur lors du nettoyage des logs: {e}")
    
    def run_scheduler(self):
        """Exécution du scheduler en continu"""
        self.logger.info("Démarrage du scheduler de scraping")
        self.logger.info(f"Horaires de collecte: {HORAIRES_COLLECTE}")
        
        # Configuration de la planification
        self.setup_schedule()
        
        # Exécuter une première collecte immédiatement
        self.logger.info("Exécution de la première collecte...")
        self.run_scraping_job()
        
        # Boucle principale du scheduler
        self.logger.info("Scheduler en cours d'exécution...")
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Vérifier toutes les minutes
                
            except KeyboardInterrupt:
                self.logger.info("Arrêt du scheduler demandé par l'utilisateur")
                break
            except Exception as e:
                self.logger.error(f"Erreur dans la boucle du scheduler: {e}")
                time.sleep(300)  # Attendre 5 minutes en cas d'erreur
    
    def run_once(self):
        """Exécution d'une seule fois (pour les tests)"""
        self.logger.info("Exécution d'une seule session de scraping")
        self.run_scraping_job()

def main():
    """Fonction principale"""
    scheduler = ScrapingScheduler()
    
    # Vérifier si on veut exécuter une seule fois ou en continu
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        scheduler.run_once()
    else:
        scheduler.run_scheduler()

if __name__ == "__main__":
    main() 