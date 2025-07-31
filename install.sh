#!/bin/bash

# Script d'installation automatique pour le projet de scraping Google Flights
# À exécuter sur Raspberry Pi (Debian)

echo "🚀 Installation du projet de scraping Google Flights"
echo "=================================================="

# Vérifier si on est sur un système Debian/Ubuntu
if ! command -v apt &> /dev/null; then
    echo "❌ Ce script nécessite un système Debian/Ubuntu"
    exit 1
fi

# Vérifier si on est root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Ne pas exécuter ce script en tant que root"
    exit 1
fi

echo "📦 Mise à jour du système..."
sudo apt update && sudo apt upgrade -y

echo "🐍 Installation de Python et pip..."
sudo apt install python3 python3-pip python3-venv -y

echo "🌐 Installation de Chrome..."
# Ajouter la clé Google
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -

# Ajouter le dépôt Chrome
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list

# Mettre à jour et installer Chrome
sudo apt update
sudo apt install google-chrome-stable -y

echo "🔧 Installation de ChromeDriver..."
sudo apt install chromium-chromedriver -y

echo "📁 Création de l'environnement virtuel..."
python3 -m venv venv
source venv/bin/activate

echo "📦 Installation des dépendances Python..."
pip install --upgrade pip
pip install -r requirements.txt

echo "📂 Création des dossiers nécessaires..."
mkdir -p donnees
mkdir -p logs

echo "🔐 Configuration des permissions..."
chmod +x main.py
chmod +x scheduler.py

echo "✅ Installation terminée !"
echo ""
echo "📋 Prochaines étapes :"
echo "1. Éditer config.py pour configurer vos destinations et SFTP"
echo "2. Tester avec : python main.py --once"
echo "3. Démarrer le système : python main.py --scheduler"
echo ""
echo "📖 Consultez le README.md pour plus d'informations" 