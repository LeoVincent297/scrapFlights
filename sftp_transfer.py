"""
Module de transfert SFTP pour envoyer les données vers l'ordinateur principal
"""

import os
import logging
import paramiko
from datetime import datetime
from typing import Optional

from config import SFTP_CONFIG, DOSSIER_DONNEES, FICHIER_CSV

class SFTPTransfer:
    """Gestionnaire de transfert SFTP"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.ssh_client = None
        self.sftp_client = None
        
    def _setup_logger(self):
        """Configuration du système de logs"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'{DOSSIER_DONNEES}/sftp_transfer.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def connect(self) -> bool:
        """Connexion au serveur SFTP"""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connexion avec les paramètres configurés
            self.ssh_client.connect(
                hostname=SFTP_CONFIG["hostname"],
                username=SFTP_CONFIG["username"],
                password=SFTP_CONFIG["password"],
                port=SFTP_CONFIG["port"],
                timeout=30
            )
            
            self.sftp_client = self.ssh_client.open_sftp()
            self.logger.info("Connexion SFTP établie avec succès")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur de connexion SFTP: {e}")
            return False
    
    def disconnect(self):
        """Déconnexion du serveur SFTP"""
        try:
            if self.sftp_client:
                self.sftp_client.close()
            if self.ssh_client:
                self.ssh_client.close()
            self.logger.info("Connexion SFTP fermée")
        except Exception as e:
            self.logger.warning(f"Erreur lors de la fermeture de la connexion: {e}")
    
    def upload_file(self, local_file: str, remote_file: str) -> bool:
        """Upload d'un fichier vers le serveur distant"""
        try:
            if not os.path.exists(local_file):
                self.logger.error(f"Fichier local introuvable: {local_file}")
                return False
            
            # Créer le répertoire distant s'il n'existe pas
            remote_dir = os.path.dirname(remote_file)
            try:
                self.sftp_client.mkdir(remote_dir)
            except:
                pass  # Le répertoire existe déjà
            
            # Upload du fichier
            self.sftp_client.put(local_file, remote_file)
            self.logger.info(f"Fichier uploadé: {local_file} → {remote_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'upload: {e}")
            return False
    
    def upload_csv_data(self) -> bool:
        """Upload du fichier CSV de données"""
        local_file = f"{DOSSIER_DONNEES}/{FICHIER_CSV}"
        remote_file = f"{SFTP_CONFIG['remote_path']}/{FICHIER_CSV}"
        
        if not os.path.exists(local_file):
            self.logger.warning("Aucun fichier CSV à transférer")
            return False
        
        return self.upload_file(local_file, remote_file)
    
    def upload_logs(self) -> bool:
        """Upload des fichiers de logs"""
        log_files = [
            f"{DOSSIER_DONNEES}/scraping.log",
            f"{DOSSIER_DONNEES}/scheduler.log",
            f"{DOSSIER_DONNEES}/sftp_transfer.log"
        ]
        
        success_count = 0
        for log_file in log_files:
            if os.path.exists(log_file):
                remote_file = f"{SFTP_CONFIG['remote_path']}/logs/{os.path.basename(log_file)}"
                if self.upload_file(log_file, remote_file):
                    success_count += 1
        
        self.logger.info(f"Upload de {success_count}/{len(log_files)} fichiers de logs")
        return success_count > 0
    
    def transfer_all_data(self) -> bool:
        """Transfert de toutes les données"""
        self.logger.info("Début du transfert SFTP")
        
        if not self.connect():
            return False
        
        try:
            # Upload du fichier CSV principal
            csv_success = self.upload_csv_data()
            
            # Upload des logs
            logs_success = self.upload_logs()
            
            if csv_success or logs_success:
                self.logger.info("Transfert SFTP terminé avec succès")
                return True
            else:
                self.logger.warning("Aucun fichier transféré")
                return False
                
        finally:
            self.disconnect()
    
    def create_backup(self) -> str:
        """Création d'une sauvegarde du fichier CSV avant transfert"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{DOSSIER_DONNEES}/backup_{FICHIER_CSV.replace('.csv', '')}_{timestamp}.csv"
            
            if os.path.exists(f"{DOSSIER_DONNEES}/{FICHIER_CSV}"):
                import shutil
                shutil.copy2(f"{DOSSIER_DONNEES}/{FICHIER_CSV}", backup_file)
                self.logger.info(f"Sauvegarde créée: {backup_file}")
                return backup_file
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la création de la sauvegarde: {e}")
        
        return ""

def main():
    """Fonction principale pour test du transfert"""
    transfer = SFTPTransfer()
    success = transfer.transfer_all_data()
    
    if success:
        print("Transfert réussi!")
    else:
        print("Échec du transfert")

if __name__ == "__main__":
    main() 