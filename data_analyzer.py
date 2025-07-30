"""
Module d'analyse des données de vols
Fournit des fonctions pour analyser les tendances de prix
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

class FlightDataAnalyzer:
    """Analyseur de données de vols"""
    
    def __init__(self, csv_file: str = "donnees/vols_data.csv"):
        self.csv_file = csv_file
        self.df = None
        self.load_data()
    
    def load_data(self):
        """Chargement des données CSV"""
        try:
            self.df = pd.read_csv(self.csv_file)
            self.df['date_collecte'] = pd.to_datetime(self.df['date_collecte'])
            self.df['date_depart'] = pd.to_datetime(self.df['date_depart'])
            print(f"✅ Données chargées: {len(self.df)} vols")
        except FileNotFoundError:
            print(f"❌ Fichier {self.csv_file} introuvable")
            self.df = pd.DataFrame()
    
    def get_basic_stats(self) -> Dict:
        """Statistiques de base"""
        if self.df.empty:
            return {}
        
        stats = {
            'total_vols': len(self.df),
            'destinations_uniques': self.df['arrivee'].nunique(),
            'periode_collecte': f"{self.df['date_collecte'].min()} à {self.df['date_collecte'].max()}",
            'prix_moyen': self.df['prix'].mean(),
            'prix_min': self.df['prix'].min(),
            'prix_max': self.df['prix'].max(),
            'compagnies_uniques': self.df['compagnie'].nunique()
        }
        
        print("📊 Statistiques de base:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        return stats
    
    def analyze_destination_prices(self, top_n: int = 10) -> pd.DataFrame:
        """Analyse des prix par destination"""
        if self.df.empty:
            return pd.DataFrame()
        
        dest_stats = self.df.groupby('arrivee').agg({
            'prix': ['mean', 'min', 'max', 'count'],
            'compagnie': 'nunique'
        }).round(2)
        
        dest_stats.columns = ['prix_moyen', 'prix_min', 'prix_max', 'nb_vols', 'nb_compagnies']
        dest_stats = dest_stats.sort_values('prix_moyen', ascending=False)
        
        print(f"\n🏛️ Top {top_n} destinations les plus chères:")
        print(dest_stats.head(top_n))
        
        return dest_stats
    
    def analyze_price_trends(self, destination: str = None) -> pd.DataFrame:
        """Analyse des tendances de prix dans le temps"""
        if self.df.empty:
            return pd.DataFrame()
        
        df_filtered = self.df
        if destination:
            df_filtered = self.df[self.df['arrivee'] == destination]
        
        # Grouper par date de collecte
        trends = df_filtered.groupby(df_filtered['date_collecte'].dt.date).agg({
            'prix': ['mean', 'min', 'max', 'count']
        }).round(2)
        
        trends.columns = ['prix_moyen', 'prix_min', 'prix_max', 'nb_vols']
        trends = trends.reset_index()
        trends['date_collecte'] = pd.to_datetime(trends['date_collecte'])
        
        print(f"\n📈 Tendances de prix {'pour ' + destination if destination else 'globales'}:")
        print(trends.tail(10))
        
        return trends
    
    def find_best_days_to_book(self, destination: str = None) -> pd.DataFrame:
        """Trouver les meilleurs jours pour réserver"""
        if self.df.empty:
            return pd.DataFrame()
        
        df_filtered = self.df
        if destination:
            df_filtered = self.df[self.df['arrivee'] == destination]
        
        # Analyser par jour de la semaine
        df_filtered['jour_semaine'] = df_filtered['date_collecte'].dt.day_name()
        
        best_days = df_filtered.groupby('jour_semaine').agg({
            'prix': ['mean', 'count']
        }).round(2)
        
        best_days.columns = ['prix_moyen', 'nb_vols']
        best_days = best_days.sort_values('prix_moyen')
        
        print(f"\n📅 Meilleurs jours pour réserver {'pour ' + destination if destination else 'globalement'}:")
        print(best_days)
        
        return best_days
    
    def find_best_months_to_travel(self, destination: str = None) -> pd.DataFrame:
        """Trouver les meilleurs mois pour voyager"""
        if self.df.empty:
            return pd.DataFrame()
        
        df_filtered = self.df
        if destination:
            df_filtered = self.df[self.df['arrivee'] == destination]
        
        # Analyser par mois de départ
        df_filtered['mois_depart'] = df_filtered['date_depart'].dt.month_name()
        
        best_months = df_filtered.groupby('mois_depart').agg({
            'prix': ['mean', 'count']
        }).round(2)
        
        best_months.columns = ['prix_moyen', 'nb_vols']
        best_months = best_months.sort_values('prix_moyen')
        
        print(f"\n🗓️ Meilleurs mois pour voyager {'vers ' + destination if destination else 'globalement'}:")
        print(best_months)
        
        return best_months
    
    def analyze_airlines(self, destination: str = None) -> pd.DataFrame:
        """Analyse des compagnies aériennes"""
        if self.df.empty:
            return pd.DataFrame()
        
        df_filtered = self.df
        if destination:
            df_filtered = self.df[self.df['arrivee'] == destination]
        
        airlines = df_filtered.groupby('compagnie').agg({
            'prix': ['mean', 'min', 'max', 'count']
        }).round(2)
        
        airlines.columns = ['prix_moyen', 'prix_min', 'prix_max', 'nb_vols']
        airlines = airlines.sort_values('prix_moyen')
        
        print(f"\n✈️ Compagnies aériennes {'pour ' + destination if destination else 'globalement'}:")
        print(airlines.head(10))
        
        return airlines
    
    def plot_price_trends(self, destination: str = None, save_path: str = None):
        """Graphique des tendances de prix"""
        if self.df.empty:
            print("❌ Aucune donnée à visualiser")
            return
        
        trends = self.analyze_price_trends(destination)
        
        plt.figure(figsize=(12, 6))
        plt.plot(trends['date_collecte'], trends['prix_moyen'], marker='o')
        plt.title(f'Tendances de prix {"pour " + destination if destination else "globales"}')
        plt.xlabel('Date de collecte')
        plt.ylabel('Prix moyen (€)')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"📊 Graphique sauvegardé: {save_path}")
        
        plt.show()
    
    def plot_destination_comparison(self, save_path: str = None):
        """Graphique de comparaison des destinations"""
        if self.df.empty:
            print("❌ Aucune donnée à visualiser")
            return
        
        dest_stats = self.analyze_destination_prices()
        
        plt.figure(figsize=(12, 8))
        dest_stats['prix_moyen'].plot(kind='bar')
        plt.title('Prix moyens par destination')
        plt.xlabel('Destination')
        plt.ylabel('Prix moyen (€)')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"📊 Graphique sauvegardé: {save_path}")
        
        plt.show()
    
    def generate_report(self, destination: str = None, output_file: str = None):
        """Génération d'un rapport complet"""
        print("📋 Génération du rapport d'analyse...")
        print("=" * 50)
        
        # Statistiques de base
        self.get_basic_stats()
        
        # Analyses spécifiques
        self.analyze_destination_prices()
        self.analyze_price_trends(destination)
        self.find_best_days_to_book(destination)
        self.find_best_months_to_travel(destination)
        self.analyze_airlines(destination)
        
        print("\n✅ Rapport généré avec succès!")
        
        if output_file:
            # Sauvegarder le rapport en texte
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("RAPPORT D'ANALYSE DES VOLS\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Ajouter les statistiques
                stats = self.get_basic_stats()
                for key, value in stats.items():
                    f.write(f"{key}: {value}\n")
        
        print(f"📄 Rapport sauvegardé: {output_file}")

def main():
    """Fonction principale pour tester l'analyseur"""
    analyzer = FlightDataAnalyzer()
    
    if not analyzer.df.empty:
        # Générer un rapport complet
        analyzer.generate_report(output_file="donnees/rapport_analyse.txt")
        
        # Créer des graphiques
        analyzer.plot_price_trends(save_path="donnees/tendances_prix.png")
        analyzer.plot_destination_comparison(save_path="donnees/comparaison_destinations.png")
        
        print("\n🎉 Analyse terminée! Consultez les fichiers générés dans le dossier 'donnees/'")
    else:
        print("❌ Aucune donnée disponible pour l'analyse")

if __name__ == "__main__":
    main() 