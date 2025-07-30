# Scraping Google Flights - Projet Automatisé

## 📋 Description

Ce projet permet de scraper automatiquement les prix de vols sur Google Flights pour analyser les tendances de prix sur plusieurs destinations. Le système fonctionne 24h/24 sur un Raspberry Pi et transfère automatiquement les données vers votre ordinateur principal.

## 🎯 Fonctionnalités

- **Scraping automatique** : Collecte des données 3 fois par jour (8h, 14h, 20h)
- **Multiples destinations** : 16 destinations préconfigurées (Europe, Amérique, Asie, Afrique)
- **Données complètes** : Prix, horaires, durée, escales, compagnies
- **Stockage CSV** : Sauvegarde automatique en format CSV
- **Transfert SFTP** : Envoi automatique vers votre ordinateur
- **Logs détaillés** : Suivi complet des opérations
- **Maintenance automatique** : Nettoyage des logs et mise à jour des dates

## 🏗️ Architecture

```
scrapFlights/
├── main.py              # Script principal
├── scraper.py           # Module de scraping
├── scheduler.py         # Planification automatique
├── sftp_transfer.py     # Transfert SFTP
├── config.py            # Configuration
├── requirements.txt     # Dépendances
└── donnees/            # Dossier des données
    ├── vols_data.csv   # Données collectées
    ├── scraping.log    # Logs de scraping
    ├── scheduler.log   # Logs de planification
    └── sftp_transfer.log # Logs de transfert
```

## 🚀 Installation

### 1. Prérequis sur Raspberry Pi (Debian)

```bash
# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation de Python et pip
sudo apt install python3 python3-pip python3-venv -y

# Installation de Chrome (nécessaire pour Selenium)
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install google-chrome-stable -y

# Installation des dépendances système
sudo apt install chromium-chromedriver -y
```

### 2. Configuration du projet

```bash
# Cloner ou télécharger le projet
cd /home/pi/
git clone <votre-repo> scrapFlights
cd scrapFlights

# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances Python
pip install -r requirements.txt
```

### 3. Configuration

Éditez le fichier `config.py` pour personnaliser :

```python
# Modifier les destinations selon vos besoins
DESTINATIONS = [
    {"depart": "Paris", "arrivee": "Londres", "code_depart": "CDG", "code_arrivee": "LHR"},
    # Ajouter vos destinations...
]

# Configuration SFTP (votre ordinateur)
SFTP_CONFIG = {
    "hostname": "192.168.1.100",  # IP de votre ordinateur
    "username": "votre_username",
    "password": "votre_password",
    "port": 22,
    "remote_path": "/home/user/flights_data"
}
```

## 📊 Utilisation

### Test initial

```bash
# Test d'une seule session de scraping
python main.py --once
```

### Démarrage du système complet

```bash
# Démarrer le scheduler automatique
python main.py --scheduler
```

### Arrêt du système

```bash
# Utiliser Ctrl+C pour arrêter proprement
```

## 🔧 Configuration SFTP sur votre ordinateur

### Windows

1. **Installer un serveur SFTP** (WinSCP, FileZilla Server)
2. **Ou utiliser WSL** avec OpenSSH :

```bash
# Dans WSL
sudo apt install openssh-server
sudo systemctl start ssh
sudo systemctl enable ssh
```

### Linux/Mac

```bash
# Installer OpenSSH
sudo apt install openssh-server  # Ubuntu/Debian
sudo systemctl start ssh
sudo systemctl enable ssh
```

## 📈 Analyse des données

Les données sont sauvegardées dans `vols_data.csv` avec les colonnes :

- `date_collecte` : Date et heure de la collecte
- `depart` : Ville de départ
- `arrivee` : Ville d'arrivée
- `date_depart` : Date du vol
- `prix` : Prix en euros
- `compagnie` : Compagnie aérienne
- `heure_depart` : Heure de départ
- `heure_arrivee` : Heure d'arrivée
- `duree_vol` : Durée du vol
- `escales` : Nombre d'escales
- `url_source` : URL source

## 🔍 Surveillance et logs

### Logs disponibles

- `donnees/scraping.log` : Logs du scraping
- `donnees/scheduler.log` : Logs de planification
- `donnees/sftp_transfer.log` : Logs de transfert
- `donnees/main.log` : Logs principaux

### Surveillance en temps réel

```bash
# Suivre les logs en temps réel
tail -f donnees/main.log

# Vérifier l'état du système
ps aux | grep python
```

## 🛠️ Dépannage

### Problèmes courants

1. **Chrome ne démarre pas** :
   ```bash
   sudo apt install --reinstall google-chrome-stable
   ```

2. **Erreur de connexion SFTP** :
   - Vérifier l'IP et les credentials dans `config.py`
   - Tester la connexion SSH manuellement

3. **Pas de données récupérées** :
   - Vérifier la connexion internet
   - Consulter les logs pour les erreurs
   - Google peut bloquer temporairement

### Maintenance

```bash
# Nettoyer les anciens logs
find donnees/ -name "*.log" -mtime +30 -delete

# Vérifier l'espace disque
df -h

# Redémarrer le service
pkill -f main.py
python main.py --scheduler
```

## 📊 Exemple d'analyse des données

```python
import pandas as pd
import matplotlib.pyplot as plt

# Charger les données
df = pd.read_csv('donnees/vols_data.csv')

# Analyser les prix moyens par destination
prix_moyens = df.groupby('arrivee')['prix'].mean().sort_values(ascending=False)
print(prix_moyens)

# Tendance des prix dans le temps
df['date_collecte'] = pd.to_datetime(df['date_collecte'])
prix_temps = df.groupby(df['date_collecte'].dt.date)['prix'].mean()
prix_temps.plot()
plt.show()
```

## 🔒 Sécurité

- Utilisez des mots de passe forts pour SFTP
- Considérez l'utilisation de clés SSH
- Limitez l'accès réseau au Raspberry Pi
- Surveillez régulièrement les logs

## 📞 Support

En cas de problème :
1. Consultez les logs dans le dossier `donnees/`
2. Vérifiez la configuration dans `config.py`
3. Testez avec `python main.py --once` pour isoler le problème

## 📝 Notes importantes

- Le scraping respecte les délais entre les requêtes
- Les données sont sauvegardées automatiquement
- Le système redémarre automatiquement en cas d'erreur
- Surveillez l'espace disque sur le Raspberry Pi 