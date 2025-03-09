import pandas as pd
import numpy as np
import itertools
import argparse
import time
import os
import shutil
from plattform_model import PlattformModel
from strategie_cluster import (
    # Einzelne Maßnahmen
    sem, social_media_marketing, affiliate_marketing,
    reduzierte_gebuehren, freemium_modell,
    eigenes_forum, treuepunkte,
    personalisierte_empfehlungen, nachhaltige_werte, co2_transparenz, 
    nachhaltige_produktfilter, regionale_kooperationen,
    
    # Cluster
    sichtbarkeit_cluster, monetarisierung_cluster, 
    community_cluster, nachhaltigkeit_cluster,
    
    # Alle Cluster
    alle_cluster
)

def run_simulation(anbieter=110, nachfrager=7788, aktive_cluster=None, schritte=365, 
                  seed=None, output_file="simulation_ergebnisse.csv"):
    """
    Führt die Plattform-Simulation mit den angegebenen Parametern aus.
    
    Args:
        anbieter (int): Anzahl der Anbieter zu Beginn
        nachfrager (int): Anzahl der Nachfrager zu Beginn
        aktive_cluster (list): Liste der aktiven Strategie-Cluster
        schritte (int): Anzahl der Simulationsschritte (Tage)
        seed (int, optional): Seed für den Zufallszahlengenerator zur Reproduzierbarkeit
        output_file (str): Name der Ausgabedatei für die Ergebnisse
    
    Returns:
        dict: Die letzten Werte der Simulationsdaten als Dictionary
    """
    if aktive_cluster is None:
        aktive_cluster = [sichtbarkeit_cluster]
        
    # Strategie-Namen für Logging
    strategie_namen = [c.name for c in aktive_cluster]
    
    print(f"Starte Simulation mit {len(aktive_cluster)} aktiven Strategien: {strategie_namen}")
    print(f"Anfangsbestand: {anbieter} Anbieter, {nachfrager} Nachfrager")
    if seed is not None:
        print(f"Verwende Random-Seed: {seed}")
    
    # Debug-Ausgabe der Cluster-Effekte
    for cluster in aktive_cluster:
        print(f"Cluster: {cluster.name}, Effekt: {cluster.effekt}")
    
    model = PlattformModel(anbieter, nachfrager, aktive_cluster, seed=seed)
    
    for i in range(schritte):
        model.step()
        if i % 30 == 0:  # Fortschrittsanzeige alle 30 Tage
            print(f"Simulationstag {i+1} von {schritte}")
    
    data = model.datacollector.get_model_vars_dataframe()
    if output_file:
        data.to_csv(output_file, index=True)
        print(f"Simulation abgeschlossen. Ergebnisse in '{output_file}' gespeichert.")
    
    # Füge Metadaten zur Simulation hinzu für spätere Analyse
    letzte_werte = data.iloc[-1].to_dict()
    letzte_werte['Strategien'] = ', '.join(strategie_namen)
    letzte_werte['Seed'] = seed
    letzte_werte['Dateiname'] = output_file
    
    return letzte_werte

def run_multiple_simulations(anbieter=110, nachfrager=7788, aktive_cluster=None, 
                           schritte=365, anzahl_simulationen=3, seed_start=42):
    """
    Führt mehrere Simulationen mit den gleichen Parametern aber unterschiedlichen Seeds durch.
    
    Args:
        anbieter (int): Anzahl der Anbieter zu Beginn
        nachfrager (int): Anzahl der Nachfrager zu Beginn
        aktive_cluster (list): Liste der aktiven Strategie-Cluster
        schritte (int): Anzahl der Simulationsschritte (Tage)
        anzahl_simulationen (int): Anzahl der durchzuführenden Simulationen
        seed_start (int): Startwert für die Random-Seeds
    
    Returns:
        pandas.DataFrame: Zusammenfassung der Simulationsergebnisse mit Mittelwerten und Standardabweichungen
    """
    if aktive_cluster is None:
        aktive_cluster = [sichtbarkeit_cluster]
        
    strategie_string = '_'.join([c.name.replace(' & ', '_').replace(' ', '_').lower() for c in aktive_cluster])
    
    ergebnisse = []
    for sim_nr in range(anzahl_simulationen):
        seed = seed_start + sim_nr
        output_file = f"simulation_{strategie_string}_run{sim_nr+1}_seed{seed}.csv"
        
        print(f"\nSimulation {sim_nr+1} von {anzahl_simulationen} mit Seed {seed}")
        resultat = run_simulation(
            anbieter=anbieter, 
            nachfrager=nachfrager, 
            aktive_cluster=aktive_cluster,
            schritte=schritte,
            seed=seed,
            output_file=output_file
        )
        ergebnisse.append(resultat)
    
    # Erstelle ein DataFrame mit allen Simulationsergebnissen
    ergebnisse_df = pd.DataFrame(ergebnisse)
    
    # Berechne Mittelwerte und Standardabweichungen für numerische Spalten
    numerische_spalten = ergebnisse_df.select_dtypes(include=[np.number]).columns
    zusammenfassung = pd.DataFrame({
        'Mittelwert': ergebnisse_df[numerische_spalten].mean(),
        'Std.Abw.': ergebnisse_df[numerische_spalten].std(),
        'Min': ergebnisse_df[numerische_spalten].min(),
        'Max': ergebnisse_df[numerische_spalten].max()
    })
    
    # Speichere die Detailergebnisse und die Zusammenfassung
    ergebnisse_df.to_csv(f"ergebnisse_detail_{strategie_string}.csv", index=False)
    zusammenfassung.to_csv(f"ergebnisse_zusammenfassung_{strategie_string}.csv")
    
    print(f"\nZusammenfassung für Strategie(n): {', '.join([c.name for c in aktive_cluster])}")
    print(f"Durchschnittliche Netzwerkeffekte: {ergebnisse_df['Netzwerkeffekte'].mean():.2f} (±{ergebnisse_df['Netzwerkeffekte'].std():.2f})")
    
    return zusammenfassung

def simuliere_einzelmassnahmen(anzahl_simulationen=3, seed_start=42):
    """
    Simuliert jede einzelne Maßnahme separat mit mehrfachen Simulationsläufen.
    
    Args:
        anzahl_simulationen (int): Anzahl der Simulationen pro Maßnahme
        seed_start (int): Startwert für die Random-Seeds
    
    Returns:
        pandas.DataFrame: Zusammenfassung der Simulationsergebnisse
    """
    print("\n=== SIMULATION EINZELNER MAßNAHMEN ===")
    
    einzelmassnahmen = [
        # S&N
        sem, social_media_marketing, affiliate_marketing,
        # Monetarisierung
        reduzierte_gebuehren, freemium_modell,
        # C&N
        eigenes_forum, treuepunkte,
        # N&L
        personalisierte_empfehlungen, nachhaltige_werte, co2_transparenz, 
        nachhaltige_produktfilter, regionale_kooperationen
    ]
    
    ergebnisse = []
    for massnahme in einzelmassnahmen:
        print(f"\nSimuliere Maßnahme: {massnahme.name}")
        zusammenfassung = run_multiple_simulations(
            aktive_cluster=[massnahme],
            anzahl_simulationen=anzahl_simulationen,
            seed_start=seed_start
        )
        
        # Extrahiere den Mittelwert der Netzwerkeffekte
        netzwerkeffekt = zusammenfassung.loc['Netzwerkeffekte', 'Mittelwert']
        std_abw = zusammenfassung.loc['Netzwerkeffekte', 'Std.Abw.']
        
        ergebnisse.append({
            'Strategie': massnahme.name,
            'Netzwerkeffekte': netzwerkeffekt,
            'Standardabweichung': std_abw,
            'Cluster-Effekt': massnahme.effekt
        })
    
    # Erstelle Zusammenfassung
    zusammenfassung_df = pd.DataFrame(ergebnisse)
    zusammenfassung_df = zusammenfassung_df.sort_values(by='Netzwerkeffekte', ascending=False)
    zusammenfassung_df.to_csv("zusammenfassung_einzelmassnahmen.csv", index=False)
    
    print("\nZusammenfassung der Einzelmaßnahmen nach Netzwerkeffekten:")
    for idx, row in zusammenfassung_df.iterrows():
        print(f"{row['Strategie']}: {row['Netzwerkeffekte']:.2f} (±{row['Standardabweichung']:.2f})")
    
    return zusammenfassung_df

def simuliere_cluster(anzahl_simulationen=3, seed_start=100):
    """
    Simuliert jeden Cluster separat mit mehrfachen Simulationsläufen.
    
    Args:
        anzahl_simulationen (int): Anzahl der Simulationen pro Cluster
        seed_start (int): Startwert für die Random-Seeds
    
    Returns:
        pandas.DataFrame: Zusammenfassung der Simulationsergebnisse
    """
    print("\n=== SIMULATION EINZELNER CLUSTER ===")
    
    ergebnisse = []
    for cluster in alle_cluster:
        print(f"\nSimuliere Cluster: {cluster.name}")
        zusammenfassung = run_multiple_simulations(
            aktive_cluster=[cluster],
            anzahl_simulationen=anzahl_simulationen,
            seed_start=seed_start
        )
        
        # Extrahiere den Mittelwert der Netzwerkeffekte
        netzwerkeffekt = zusammenfassung.loc['Netzwerkeffekte', 'Mittelwert']
        std_abw = zusammenfassung.loc['Netzwerkeffekte', 'Std.Abw.']
        
        ergebnisse.append({
            'Strategie': cluster.name,
            'Netzwerkeffekte': netzwerkeffekt,
            'Standardabweichung': std_abw,
            'Cluster-Effekt': cluster.effekt
        })
    
    # Erstelle Zusammenfassung
    zusammenfassung_df = pd.DataFrame(ergebnisse)
    zusammenfassung_df = zusammenfassung_df.sort_values(by='Netzwerkeffekte', ascending=False)
    zusammenfassung_df.to_csv("zusammenfassung_cluster.csv", index=False)
    
    print("\nZusammenfassung der Cluster nach Netzwerkeffekten:")
    for idx, row in zusammenfassung_df.iterrows():
        print(f"{row['Strategie']}: {row['Netzwerkeffekte']:.2f} (±{row['Standardabweichung']:.2f})")
    
    return zusammenfassung_df

def simuliere_clusterkombinationen(anzahl_simulationen=3, seed_start=200):
    """
    Simuliert verschiedene Kombinationen von Clustern mit mehrfachen Simulationsläufen.
    
    Args:
        anzahl_simulationen (int): Anzahl der Simulationen pro Kombination
        seed_start (int): Startwert für die Random-Seeds
    
    Returns:
        pandas.DataFrame: Zusammenfassung der Simulationsergebnisse
    """
    print("\n=== SIMULATION VON CLUSTER-KOMBINATIONEN ===")
    
    ergebnisse = []
    seed = seed_start
    
    # Generiere alle möglichen Kombinationen von 2 und 3 Clustern
    for r in range(2, 4):  # 2 und 3 Cluster kombinieren
        for kombination in itertools.combinations(alle_cluster, r):
            cluster_namen = [c.name for c in kombination]
            print(f"\nSimuliere Kombination: {', '.join(cluster_namen)}")
            
            zusammenfassung = run_multiple_simulations(
                aktive_cluster=list(kombination),
                anzahl_simulationen=anzahl_simulationen,
                seed_start=seed
            )
            seed += anzahl_simulationen
            
            # Extrahiere den Mittelwert der Netzwerkeffekte
            netzwerkeffekt = zusammenfassung.loc['Netzwerkeffekte', 'Mittelwert']
            std_abw = zusammenfassung.loc['Netzwerkeffekte', 'Std.Abw.']
            
            # Berechne Summe der Einzel-Cluster-Effekte
            summe_effekte = sum(c.effekt for c in kombination)
            
            ergebnisse.append({
                'Strategie': ', '.join(cluster_namen),
                'Netzwerkeffekte': netzwerkeffekt,
                'Standardabweichung': std_abw,
                'Summe Cluster-Effekte': summe_effekte,
                'Anzahl Cluster': len(kombination)
            })
    
    # Simulation mit allen Clustern
    print("\nSimuliere alle Cluster zusammen")
    zusammenfassung = run_multiple_simulations(
        aktive_cluster=alle_cluster,
        anzahl_simulationen=anzahl_simulationen,
        seed_start=seed
    )
    
    # Extrahiere den Mittelwert der Netzwerkeffekte
    netzwerkeffekt = zusammenfassung.loc['Netzwerkeffekte', 'Mittelwert']
    std_abw = zusammenfassung.loc['Netzwerkeffekte', 'Std.Abw.']
    
    # Berechne Summe der Einzel-Cluster-Effekte
    summe_effekte = sum(c.effekt for c in alle_cluster)
    
    ergebnisse.append({
        'Strategie': 'Alle Cluster',
        'Netzwerkeffekte': netzwerkeffekt,
        'Standardabweichung': std_abw,
        'Summe Cluster-Effekte': summe_effekte,
        'Anzahl Cluster': len(alle_cluster)
    })
    
    # Erstelle Zusammenfassung
    zusammenfassung_df = pd.DataFrame(ergebnisse)
    zusammenfassung_df = zusammenfassung_df.sort_values(by='Netzwerkeffekte', ascending=False)
    zusammenfassung_df.to_csv("zusammenfassung_clusterkombinationen.csv", index=False)
    
    print("\nZusammenfassung der Cluster-Kombinationen nach Netzwerkeffekten:")
    for idx, row in zusammenfassung_df.iterrows():
        print(f"{row['Strategie']}: {row['Netzwerkeffekte']:.2f} (±{row['Standardabweichung']:.2f})")
    
    return zusammenfassung_df

def erstelle_gesamtvergleich(einzeln_df, cluster_df, kombinationen_df):
    """
    Erstellt einen Gesamtvergleich aller Simulationen.
    
    Args:
        einzeln_df (pandas.DataFrame): Ergebnisse der Einzelmaßnahmen
        cluster_df (pandas.DataFrame): Ergebnisse der Cluster
        kombinationen_df (pandas.DataFrame): Ergebnisse der Cluster-Kombinationen
    
    Returns:
        pandas.DataFrame: Gesamtvergleich aller Simulationen
    """
    # Erstelle eine neue Spalte für die Kategorie
    einzeln_df['Kategorie'] = 'Einzelmaßnahme'
    cluster_df['Kategorie'] = 'Cluster'
    kombinationen_df['Kategorie'] = 'Kombination'
    
    # Zusammenführen aller Ergebnisse
    alle_ergebnisse = pd.concat([einzeln_df, cluster_df, kombinationen_df], ignore_index=True)
    
    # Sortieren nach Netzwerkeffekten absteigend
    gesamtvergleich = alle_ergebnisse.sort_values(by='Netzwerkeffekte', ascending=False)
    
    # Speichern des Gesamtvergleichs
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    gesamtvergleich.to_csv(f"gesamtvergleich_aller_simulationen_{timestamp}.csv", index=False)
    
    print("\n=== VOLLSTÄNDIGES RANKING ALLER STRATEGIEN NACH NETZWERKEFFEKTEN ===")
    for index, row in gesamtvergleich.iterrows():
        print(f"{row['Strategie']} ({row['Kategorie']}): {row['Netzwerkeffekte']:.2f} (±{row['Standardabweichung']:.2f})")
    
    return gesamtvergleich

def run_multiple_iterations(iterations=4, sim_runs=3, seed_start=42, tage=365):
    """
    Führt mehrere Iterationen der Simulationen durch.
    
    Args:
        iterations (int): Anzahl der Gesamtiterationen
        sim_runs (int): Anzahl der Simulationsläufe pro Konfiguration
        seed_start (int): Basis-Seed für den ersten Durchlauf
        tage (int): Anzahl der simulierten Tage
    
    Returns:
        None
    """
    # Erstelle Verzeichnisstruktur für die Ergebnisse
    basis_verzeichnis = "results"
    if not os.path.exists(basis_verzeichnis):
        os.makedirs(basis_verzeichnis)
    
    # Führe die Iterationen durch
    for iteration in range(1, iterations + 1):
        iteration_verzeichnis = os.path.join(basis_verzeichnis, f"iteration_{iteration}")
        
        # Falls der Ordner bereits existiert, lösche ihn und erstelle ihn neu
        if os.path.exists(iteration_verzeichnis):
            shutil.rmtree(iteration_verzeichnis)
        os.makedirs(iteration_verzeichnis)
        
        # Wechsle ins Iterationsverzeichnis
        current_dir = os.getcwd()
        os.chdir(iteration_verzeichnis)
        
        iteration_seed = seed_start + (iteration - 1) * 10000
        
        print(f"\n\n{'='*80}")
        print(f"=== STARTE ITERATION {iteration} VON {iterations} ===")
        print(f"=== Basis-Seed: {iteration_seed}, Simulationen pro Konfiguration: {sim_runs} ===")
        print(f"{'='*80}\n")
        
        try:
            # Einzelne Maßnahmen simulieren
            print(f"Simuliere einzelne Maßnahmen...")
            einzeln_df = simuliere_einzelmassnahmen(
                anzahl_simulationen=sim_runs, 
                seed_start=iteration_seed
            )
            
            # Cluster simulieren
            print(f"\nSimuliere Cluster...")
            cluster_df = simuliere_cluster(
                anzahl_simulationen=sim_runs, 
                seed_start=iteration_seed + 1000
            )
            
            # Cluster-Kombinationen simulieren
            print(f"\nSimuliere Cluster-Kombinationen...")
            kombinationen_df = simuliere_clusterkombinationen(
                anzahl_simulationen=sim_runs, 
                seed_start=iteration_seed + 2000
            )
            
            # Gesamtvergleich erstellen
            print(f"\nErstelle Gesamtvergleich...")
            erstelle_gesamtvergleich(einzeln_df, cluster_df, kombinationen_df)
            
            print(f"\nIteration {iteration} abgeschlossen.")
            
        except Exception as e:
            print(f"\nFehler in Iteration {iteration}: {str(e)}")
        
        # Zurück zum Hauptverzeichnis
        os.chdir(current_dir)
    
    print("\nAlle Iterationen abgeschlossen. Verwende das Skript 'erstelle_zusammenfassung.py', um die Gesamtergebnisse zu aggregieren.")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Plattform-Modell Simulation mit mehrfachen Durchläufen')
    parser.add_argument('--iterations', type=int, default=4, help='Anzahl der Iterationen')
    parser.add_argument('--runs', type=int, default=3, help='Anzahl der Simulationen pro Konfiguration')
    parser.add_argument('--days', type=int, default=365, help='Anzahl der simulierten Tage')
    parser.add_argument('--seed', type=int, default=42, help='Basis-Seed für den ersten Durchlauf')
    
    args = parser.parse_args()
    
    # Führe die Simulationen durch
    run_multiple_iterations(
        iterations=args.iterations,
        sim_runs=args.runs,
        seed_start=args.seed,
        tage=args.days
    )