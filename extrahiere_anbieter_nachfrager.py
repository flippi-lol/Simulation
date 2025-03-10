import os
import pandas as pd
import numpy as np
import glob
from pathlib import Path

def extrahiere_anbieter_nachfrager_daten(basis_verzeichnis):
    """
    Extrahiert die Anbieter- und Nachfragerdaten aus allen Simulationsdateien
    mit statistischen Kennwerten.
    
    Args:
        basis_verzeichnis (str): Pfad zum Hauptverzeichnis der Simulationsläufe
    """
    print(f"Suche in: {basis_verzeichnis}")
    
    # Suche nach allen Iterationsverzeichnissen
    iteration_dirs = sorted(glob.glob(os.path.join(basis_verzeichnis, "iteration_*")))
    
    if not iteration_dirs:
        print(f"Keine Iterationsverzeichnisse gefunden in {basis_verzeichnis}")
        return None
    
    # Dictionary zur Speicherung der Ergebnisse
    strategie_daten = {}
    
    # Durchlaufe alle Iterationsverzeichnisse
    for iteration_dir in iteration_dirs:
        iteration_nummer = int(Path(iteration_dir).name.split('_')[1])
        print(f"Verarbeite Iteration {iteration_nummer} aus {iteration_dir}")
        
        # Suche nach allen CSV-Dateien, die Simulationsergebnisse enthalten
        simulation_files = glob.glob(os.path.join(iteration_dir, "simulation_*.csv"))
        
        for sim_file in simulation_files:
            # Extrahiere den Strategienamen aus dem Dateinamen
            file_name = os.path.basename(sim_file)
            strategie_teile = file_name.split('_run')[0].split('simulation_')[1]
            
            # Normalisiere den Strategienamen (ersetze Unterstriche durch Leerzeichen und Kommas)
            strategie = strategie_teile.replace('_und_', ' & ').replace('_', ' ')
            
            # Bestimme die Kategorie (Einzelmaßnahme, Cluster, Kombination)
            if strategie in ["SEM", "Social Media Marketing", "Affiliate Marketing", 
                           "Reduzierte Gebühren", "Freemium Modell", "Eigenes Forum", 
                           "Treuepunkte", "Personalisierte Empfehlungen", "Nachhaltige Werte", 
                           "CO2 Transparenz", "Nachhaltige Produktfilter", "Regionale Kooperationen"]:
                kategorie = "Einzelmaßnahme"
            elif strategie in ["Sichtbarkeit & Nutzergewinnung", "Monetarisierung", 
                             "Community & Nutzerbindung", "Nachhaltigkeit & Lokalität"]:
                kategorie = "Cluster"
            else:
                kategorie = "Kombination"
            
            # Lese die CSV-Datei
            try:
                df = pd.read_csv(sim_file)
                
                # Extrahiere die letzten Werte für Anbieter und Nachfrager
                letzte_werte = df.iloc[-1]
                anbieter = letzte_werte.get('Anbieter', 0)
                nachfrager = letzte_werte.get('Nachfrager', 0)
                netzwerkeffekte = letzte_werte.get('Netzwerkeffekte', 0)
                
                # Speichere die Werte im Dictionary
                if strategie not in strategie_daten:
                    strategie_daten[strategie] = {
                        'Kategorie': kategorie,
                        'Anbieter': [],
                        'Nachfrager': [],
                        'Netzwerkeffekte': []
                    }
                
                strategie_daten[strategie]['Anbieter'].append(anbieter)
                strategie_daten[strategie]['Nachfrager'].append(nachfrager)
                strategie_daten[strategie]['Netzwerkeffekte'].append(netzwerkeffekte)
                
            except Exception as e:
                print(f"Fehler beim Verarbeiten von {sim_file}: {str(e)}")
    
    # Berechne Mittelwerte, Standardabweichungen, Min und Max und erstelle Ergebnistabelle
    ergebnis_daten = []
    for strategie, daten in strategie_daten.items():
        anbieter_mean = sum(daten['Anbieter']) / len(daten['Anbieter']) if daten['Anbieter'] else 0
        anbieter_std = np.std(daten['Anbieter']) if daten['Anbieter'] else 0
        anbieter_min = min(daten['Anbieter']) if daten['Anbieter'] else 0
        anbieter_max = max(daten['Anbieter']) if daten['Anbieter'] else 0
        
        nachfrager_mean = sum(daten['Nachfrager']) / len(daten['Nachfrager']) if daten['Nachfrager'] else 0
        nachfrager_std = np.std(daten['Nachfrager']) if daten['Nachfrager'] else 0
        nachfrager_min = min(daten['Nachfrager']) if daten['Nachfrager'] else 0
        nachfrager_max = max(daten['Nachfrager']) if daten['Nachfrager'] else 0
        
        netzwerkeffekte_mean = sum(daten['Netzwerkeffekte']) / len(daten['Netzwerkeffekte']) if daten['Netzwerkeffekte'] else 0
        netzwerkeffekte_std = np.std(daten['Netzwerkeffekte']) if daten['Netzwerkeffekte'] else 0
        netzwerkeffekte_min = min(daten['Netzwerkeffekte']) if daten['Netzwerkeffekte'] else 0
        netzwerkeffekte_max = max(daten['Netzwerkeffekte']) if daten['Netzwerkeffekte'] else 0
        
        ergebnis_daten.append({
            'Strategie': strategie,
            'Kategorie': daten['Kategorie'],
            'Anbieter_mean': anbieter_mean,
            'Anbieter_std': anbieter_std,
            'Anbieter_min': anbieter_min,
            'Anbieter_max': anbieter_max,
            'Nachfrager_mean': nachfrager_mean,
            'Nachfrager_std': nachfrager_std,
            'Nachfrager_min': nachfrager_min,
            'Nachfrager_max': nachfrager_max,
            'Netzwerkeffekte_mean': netzwerkeffekte_mean,
            'Netzwerkeffekte_std': netzwerkeffekte_std,
            'Netzwerkeffekte_min': netzwerkeffekte_min,
            'Netzwerkeffekte_max': netzwerkeffekte_max
        })
    
    # Erstelle DataFrame und sortiere nach Netzwerkeffekten
    ergebnis_df = pd.DataFrame(ergebnis_daten)
    ergebnis_df = ergebnis_df.sort_values(by='Netzwerkeffekte_mean', ascending=False)
    
    # Speichere die Ergebnisse
    ausgabe_verzeichnis = os.path.join(basis_verzeichnis, "zusammenfassung")
    os.makedirs(ausgabe_verzeichnis, exist_ok=True)
    
    # Speichere vollständige Ergebnisse mit allen statistischen Kennwerten
    ergebnis_df.to_csv(os.path.join(ausgabe_verzeichnis, "anbieter_nachfrager_statistik.csv"), index=False)
    
    # Erstelle eine vereinfachte Tabelle nur mit Mittelwerten für den Hauptteil
    einfache_tabelle = ergebnis_df[['Strategie', 'Kategorie', 'Anbieter_mean', 'Nachfrager_mean', 'Netzwerkeffekte_mean']]
    einfache_tabelle.to_csv(os.path.join(ausgabe_verzeichnis, "anbieter_nachfrager_mittelwerte.csv"), index=False)
    
    print(f"\nTop 10 Strategien mit Anbieter- und Nachfragerzahlen:")
    for idx, row in ergebnis_df.head(10).iterrows():
        print(f"{idx+1}. {row['Strategie']} ({row['Kategorie']}): " +
              f"Netzwerkeffekte: {row['Netzwerkeffekte_mean']:.2f} (±{row['Netzwerkeffekte_std']:.2f}), " +
              f"Anbieter: {row['Anbieter_mean']:.2f} (±{row['Anbieter_std']:.2f}), " +
              f"Nachfrager: {row['Nachfrager_mean']:.2f} (±{row['Nachfrager_std']:.2f})")
    
    print(f"\nErgebnisse wurden gespeichert:")
    print(f"- Vollständige Statistik: '{os.path.join(ausgabe_verzeichnis, 'anbieter_nachfrager_statistik.csv')}'")
    print(f"- Vereinfachte Tabelle: '{os.path.join(ausgabe_verzeichnis, 'anbieter_nachfrager_mittelwerte.csv')}'")
    
    return ergebnis_df

# Beispielaufruf
if __name__ == "__main__":
    # Passe diesen Pfad an das Verzeichnis mit deinen Simulationsergebnissen an
    basis_verzeichnis = "./results"
    ergebnis_df = extrahiere_anbieter_nachfrager_daten(basis_verzeichnis)