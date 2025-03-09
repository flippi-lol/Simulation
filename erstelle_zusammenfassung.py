import os
import pandas as pd
import numpy as np
import glob
from pathlib import Path

def erstelle_gesamtzusammenfassung(basis_verzeichnis):
    """
    Erstellt eine Gesamtzusammenfassung der Simulationsergebnisse aus den einzelnen Iterationen.
    
    Args:
        basis_verzeichnis (str): Pfad zum Hauptverzeichnis der Simulationsläufe
    """
    # Finde alle Iterationsverzeichnisse
    print(f"Suche in: {basis_verzeichnis}")
    print(f"Existiert: {os.path.exists(basis_verzeichnis)}")
    
    # Zeige alle Dateien und Verzeichnisse im angegebenen Verzeichnis
    if os.path.exists(basis_verzeichnis):
        print("Inhalt des Verzeichnisses:")
        for item in os.listdir(basis_verzeichnis):
            print(f"  - {item}")
    
    # Suche direkt nach Iterationsordnern
    iteration_dirs = sorted(glob.glob(os.path.join(basis_verzeichnis, "iteration_*")))
    hauptlauf_verzeichnis = basis_verzeichnis
    
    if not iteration_dirs:
        print(f"Keine Iterationsverzeichnisse gefunden in {basis_verzeichnis}")
        return None
    
    # Listen zum Sammeln aller Ergebnisse
    alle_einzelmassnahmen = []
    alle_cluster = []
    alle_kombinationen = []
    alle_gesamtvergleiche = []
    
    # Durchlaufe alle gefundenen Iterationsverzeichnisse
    for iteration_dir in iteration_dirs:
        iteration_nummer = int(Path(iteration_dir).name.split('_')[1])
        print(f"Verarbeite Iteration {iteration_nummer} aus {iteration_dir}")
        
        # Suche nach den Zusammenfassungsdateien
        einzelmassnahmen_path = os.path.join(iteration_dir, "zusammenfassung_einzelmassnahmen.csv")
        cluster_path = os.path.join(iteration_dir, "zusammenfassung_cluster.csv")
        kombinationen_path = os.path.join(iteration_dir, "zusammenfassung_clusterkombinationen.csv")
        
        # Suche nach dem Gesamtvergleich (kann einen Zeitstempel im Namen haben)
        gesamtvergleiche = glob.glob(os.path.join(iteration_dir, "gesamtvergleich_aller_simulationen_*.csv"))
        gesamtvergleich_path = gesamtvergleiche[0] if gesamtvergleiche else None
        
        # Lade die Daten, wenn die Dateien existieren
        if os.path.exists(einzelmassnahmen_path):
            df = pd.read_csv(einzelmassnahmen_path)
            df['Iteration'] = iteration_nummer
            # Kategoriespalte hinzufügen, falls nicht vorhanden
            if 'Kategorie' not in df.columns:
                df['Kategorie'] = 'Einzelmaßnahme'
            alle_einzelmassnahmen.append(df)
        else:
            print(f"Warnung: Keine Einzelmaßnahmen-Zusammenfassung gefunden in Iteration {iteration_nummer}")
        
        if os.path.exists(cluster_path):
            df = pd.read_csv(cluster_path)
            df['Iteration'] = iteration_nummer
            # Kategoriespalte hinzufügen, falls nicht vorhanden
            if 'Kategorie' not in df.columns:
                df['Kategorie'] = 'Cluster'
            alle_cluster.append(df)
        else:
            print(f"Warnung: Keine Cluster-Zusammenfassung gefunden in Iteration {iteration_nummer}")
        
        if os.path.exists(kombinationen_path):
            df = pd.read_csv(kombinationen_path)
            df['Iteration'] = iteration_nummer
            # Kategoriespalte hinzufügen, falls nicht vorhanden
            if 'Kategorie' not in df.columns:
                df['Kategorie'] = 'Kombination'
            alle_kombinationen.append(df)
        else:
            print(f"Warnung: Keine Kombinationen-Zusammenfassung gefunden in Iteration {iteration_nummer}")
        
        if gesamtvergleich_path and os.path.exists(gesamtvergleich_path):
            df = pd.read_csv(gesamtvergleich_path)
            df['Iteration'] = iteration_nummer
            alle_gesamtvergleiche.append(df)
        else:
            print(f"Warnung: Kein Gesamtvergleich gefunden in Iteration {iteration_nummer}")
    
    # Erstelle Ausgabeverzeichnis
    ausgabe_verzeichnis = os.path.join(basis_verzeichnis, "zusammenfassung")
    os.makedirs(ausgabe_verzeichnis, exist_ok=True)
    
    # Zusammenführen aller Daten
    ergebnisse = {}
    
    if alle_einzelmassnahmen:
        ergebnisse["einzelmassnahmen"] = pd.concat(alle_einzelmassnahmen, ignore_index=True)
    
    if alle_cluster:
        ergebnisse["cluster"] = pd.concat(alle_cluster, ignore_index=True)
    
    if alle_kombinationen:
        ergebnisse["kombinationen"] = pd.concat(alle_kombinationen, ignore_index=True)
    
    if alle_gesamtvergleiche:
        ergebnisse["gesamtvergleich"] = pd.concat(alle_gesamtvergleiche, ignore_index=True)
    
    # Erstelle Zusammenfassungen und speichere sie
    for name, df in ergebnisse.items():
        # Speichere die kombinierten Rohdaten
        df.to_csv(os.path.join(ausgabe_verzeichnis, f"alle_{name}.csv"), index=False)
        
        # Gruppieren nach Strategie und berechne Statistiken
        if "Strategie" in df.columns and "Netzwerkeffekte" in df.columns:
            agg_dict = {
                "Netzwerkeffekte": ["mean", "std", "min", "max"]
            }
            
            # Füge weitere Spalten hinzu, wenn sie existieren
            for col in ["Kategorie", "Cluster-Effekt", "Summe Cluster-Effekte", "Anzahl Cluster"]:
                if col in df.columns:
                    agg_dict[col] = "first"
            
            zusammenfassung = df.groupby("Strategie").agg(agg_dict)
            
            # Umbenenne für bessere Lesbarkeit
            zusammenfassung.columns = [f"{col[0]}_{col[1]}" if isinstance(col, tuple) else col for col in zusammenfassung.columns]
            
            # Sortiere nach Mittelwert der Netzwerkeffekte
            zusammenfassung = zusammenfassung.sort_values(by="Netzwerkeffekte_mean", ascending=False)
            
            # Speichere die Zusammenfassung
            zusammenfassung.to_csv(os.path.join(ausgabe_verzeichnis, f"zusammenfassung_{name}.csv"))
            
            # Drucke die Top-Ergebnisse aus
            print(f"\nTop 5 Strategien für {name}:")
            for idx, (strat, row) in enumerate(zusammenfassung.head(5).iterrows()):
                kategorie_info = ""
                if "Kategorie_first" in row:
                    kategorie_info = f"({row['Kategorie_first']})"
                
                print(f"{idx+1}. {strat} {kategorie_info}: " +
                      f"{row['Netzwerkeffekte_mean']:.2f} (±{row['Netzwerkeffekte_std']:.2f}, " +
                      f"Min: {row['Netzwerkeffekte_min']:.2f}, Max: {row['Netzwerkeffekte_max']:.2f})")
    
    # Erstelle einen übergreifenden Gesamtvergleich aller Strategien
    if "gesamtvergleich" in ergebnisse:
        gesamtvergleich_df = ergebnisse["gesamtvergleich"]
        
        # Gruppieren nach Strategie und berechne Statistiken
        agg_dict = {
            "Netzwerkeffekte": ["mean", "std", "min", "max"]
        }
        
        # Füge Kategorie hinzu, wenn sie existiert
        if "Kategorie" in gesamtvergleich_df.columns:
            agg_dict["Kategorie"] = "first"
        
        gesamt_zusammenfassung = gesamtvergleich_df.groupby("Strategie").agg(agg_dict)
        
        # Umbenenne für bessere Lesbarkeit
        gesamt_zusammenfassung.columns = [f"{col[0]}_{col[1]}" if isinstance(col, tuple) else col for col in gesamt_zusammenfassung.columns]
        
        # Sortiere nach Mittelwert der Netzwerkeffekte
        gesamt_zusammenfassung = gesamt_zusammenfassung.sort_values(by="Netzwerkeffekte_mean", ascending=False)
        
        # Speichere die Gesamtzusammenfassung
        gesamt_zusammenfassung.to_csv(os.path.join(ausgabe_verzeichnis, "gesamtzusammenfassung_aller_durchlaufe.csv"))
        
        # Speichere auch die Detailergebnisse
        gesamtvergleich_df.to_csv(os.path.join(ausgabe_verzeichnis, "alle_ergebnisse_aller_durchlaufe.csv"), index=False)
        
        print("\n" + "="*80)
        print("=== GESAMTZUSAMMENFASSUNG ÜBER ALLE DURCHLÄUFE ===")
        print("="*80 + "\n")
        print("Top 10 Strategien nach mittleren Netzwerkeffekten:")
        for idx, (strat, row) in enumerate(gesamt_zusammenfassung.head(10).iterrows()):
            kategorie_info = ""
            if "Kategorie_first" in row:
                kategorie_info = f"({row['Kategorie_first']})"
            
            print(f"{idx+1}. {strat} {kategorie_info}: {row['Netzwerkeffekte_mean']:.2f} " +
                  f"(±{row['Netzwerkeffekte_std']:.2f}, Min: {row['Netzwerkeffekte_min']:.2f}, Max: {row['Netzwerkeffekte_max']:.2f})")
    
    print(f"\nZusammenfassung abgeschlossen. Ergebnisse wurden in '{ausgabe_verzeichnis}' gespeichert.")
    
    return gesamt_zusammenfassung if "gesamtvergleich" in ergebnisse else None

# Beispielaufruf
if __name__ == "__main__":
    # Passe diesen Pfad an das Verzeichnis mit deinen Simulationsergebnissen an
    basis_verzeichnis = "./results"
    erstelle_gesamtzusammenfassung(basis_verzeichnis)