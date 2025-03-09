import random
from collections import deque
from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from akteure import Anbieter, Nachfrager

class PlattformModel(Model):
    """
    Agent-basiertes Modell einer digitalen Plattform mit Anbietern und Nachfragern.
    
    Simuliert die Dynamik eines Plattformökosystems unter Berücksichtigung verschiedener
    Strategien zur Steigerung der Netzwerkeffekte. Das Modell erfasst Zu- und Abwanderung
    von Akteuren sowie die Entwicklung von Netzwerkeffekten über Zeit.
    
    Attributes:
        schedule (RandomActivation): Aktivierungsschema für die Agenten
        aktive_cluster (list): Liste der aktiven Strategiecluster
        N_anbieter (int): Initiale Anzahl der Anbieter
        N_nachfrager (int): Initiale Anzahl der Nachfrager
        next_id (int): Nächste verfügbare ID für neue Agenten
        N_p_history (deque): Speichert die letzten 60 Netzwerkeffektwerte
        seed (int): Seed für den Zufallszahlengenerator zur Reproduzierbarkeit
    """
    
    def __init__(self, N_anbieter, N_nachfrager, aktive_cluster, seed=None):
        """
        Initialisiert das Plattformmodell mit gegebenen Parametern.
        
        Args:
            N_anbieter (int): Anfängliche Anzahl der Anbieter
            N_nachfrager (int): Anfängliche Anzahl der Nachfrager
            aktive_cluster (list): Liste der aktiven Strategiecluster
            seed (int, optional): Seed für den Zufallszahlengenerator zur Reproduzierbarkeit
        """
        # Setzen des Random-Seeds für Reproduzierbarkeit
        self.seed = seed
        if seed is not None:
            random.seed(seed)
            
        self.schedule = RandomActivation(self)
        self.aktive_cluster = aktive_cluster
        self.N_anbieter = N_anbieter
        self.N_nachfrager = N_nachfrager
        self.next_id = N_anbieter + N_nachfrager
        self.N_p_history = deque(maxlen=60)  # Speichert Werte für 60 Tage
        
        # Basis-Wahrscheinlichkeiten für Beitritte
        self.basis_wahrscheinlichkeit_anbieter = 0.015
        self.basis_wahrscheinlichkeit_nachfrager = 0.02
        
        # Maximale Wahrscheinlichkeiten für Beitritte
        self.max_wahrscheinlichkeit_anbieter = 0.2
        self.max_wahrscheinlichkeit_nachfrager = 0.3

        # Zähler für neue und abgewanderte Akteure
        self.neue_anbieter = 0
        self.neue_nachfrager = 0
        self.abgewanderte_anbieter = 0
        self.abgewanderte_nachfrager = 0

        # Erstellen und Hinzufügen der initialen Anbieter
        for i in range(self.N_anbieter):
            anbieter = Anbieter(i, self)
            self.schedule.add(anbieter)

        # Erstellen und Hinzufügen der initialen Nachfrager
        for j in range(self.N_nachfrager):
            nachfrager = Nachfrager(self.N_anbieter + j, self)
            self.schedule.add(nachfrager)

        # Konfiguration des DataCollectors für die Erfassung von Modellvariablen
        self.datacollector = DataCollector(
            model_reporters={
                "Anbieter": lambda m: sum(1 for a in m.schedule.agents if isinstance(a, Anbieter)),
                "Nachfrager": lambda m: sum(1 for a in m.schedule.agents if isinstance(a, Nachfrager)),
                "Netzwerkeffekte": self.berechne_netzwerkeffekte,
                "Neue Anbieter": lambda m: m.neue_anbieter,
                "Neue Nachfrager": lambda m: m.neue_nachfrager,
                "Abgewanderte Anbieter": lambda m: m.abgewanderte_anbieter,
                "Abgewanderte Nachfrager": lambda m: m.abgewanderte_nachfrager,
                "Beitrittsrate Anbieter": lambda m: m.berechne_beitrittsrate_anbieter(),
                "Beitrittsrate Nachfrager": lambda m: m.berechne_beitrittsrate_nachfrager(),
            }
        )
        
        # Initial einen Netzwerkeffekt berechnen, um die History zu starten
        self.berechne_netzwerkeffekte()

    def berechne_netzwerkeffekte(self):
        """
        Berechnet die aktuellen Netzwerkeffekte basierend auf der Anzahl der Anbieter und Nachfrager
        sowie den Effekten der aktiven Strategiecluster.
        
        Die Formel gewichtet Nachfrager stärker als Anbieter und bezieht die Effekte
        der aktiven Strategien mit ein.
        
        Returns:
            float: Durchschnittlicher Netzwerkeffekt über die letzten Zeitschritte
        """
        anbieterzahl = sum(1 for a in self.schedule.agents if isinstance(a, Anbieter))
        nachfragerzahl = sum(1 for a in self.schedule.agents if isinstance(a, Nachfrager))
        cluster_effekt = sum(cluster.effekt for cluster in self.aktive_cluster)

        # Berechnung des momentanen Netzwerkeffekts
        # Gewichtung: 40% Anbieter, 60% Nachfrager, zusätzlich 30% der Cluster-Effekte
        N_p = (0.4 * anbieterzahl) + (0.6 * nachfragerzahl) + (0.3 * cluster_effekt)
        self.N_p_history.append(N_p)
        
        # Rückgabe des Durchschnitts über die gespeicherten Werte
        return sum(self.N_p_history) / len(self.N_p_history)

    def sinkt_netzwerkeffekt(self):
        """
        Überprüft, ob der Netzwerkeffekt im Vergleich zu einem früheren Zeitpunkt gesunken ist.
        
        Vergleicht den aktuellen Netzwerkeffekt mit dem Wert von vor 30 Tagen (falls verfügbar).
        Diese Methode wird für die Abwanderungsentscheidung der Agenten verwendet.
        
        Returns:
            bool: True, wenn der Netzwerkeffekt gesunken ist, sonst False
        """
        if len(self.N_p_history) < 30:  # Vergleich erst ab 30 Datenpunkten aussagekräftig
            return False  
        # Vergleiche mit einem Wert von vor 30 Tagen statt mit dem ältesten Wert
        vergleichsindex = max(0, len(self.N_p_history) - 30)
        return self.N_p_history[-1] < self.N_p_history[vergleichsindex]
    
    def berechne_beitrittsrate_anbieter(self):
        """
        Berechnet die dynamische Beitrittswahrscheinlichkeit für Anbieter.
        
        Die Berechnung basiert auf der Veränderung der Netzwerkeffekte mit progressiver
        Skalierung (Exponent 0.7). Bei positiver Entwicklung der Netzwerkeffekte steigt 
        die Beitrittswahrscheinlichkeit überproportional an.
        
        Returns:
            float: Beitrittswahrscheinlichkeit für Anbieter zwischen Basis- und Maximalwert
        """
        if len(self.N_p_history) < 2:
            return self.basis_wahrscheinlichkeit_anbieter
        
        # Veränderung der Netzwerkeffekte über die letzten Perioden
        vergleichsindex = max(0, len(self.N_p_history) - 30)
        netzwerk_veraenderung = self.N_p_history[-1] - self.N_p_history[vergleichsindex]
        
        # Bei Stagnation oder Rückgang nur minimale Beitrittsrate
        if netzwerk_veraenderung <= 0:
            return self.basis_wahrscheinlichkeit_anbieter
        
        # Progressive Skalierung mit Exponent 0.7 und Normalisierungsfaktor 800
        normalisierte_veraenderung = min(1.0, (netzwerk_veraenderung / 800) ** 0.7)
        
        # Rate basierend auf der Veränderung zwischen Basis und Maximum
        return self.basis_wahrscheinlichkeit_anbieter + (
            (self.max_wahrscheinlichkeit_anbieter - self.basis_wahrscheinlichkeit_anbieter) * normalisierte_veraenderung
        )
    
    def berechne_beitrittsrate_nachfrager(self):
        """
        Berechnet die dynamische Beitrittswahrscheinlichkeit für Nachfrager.
        
        Ähnlich wie für Anbieter, aber mit anderen Parametern. Der Normalisierungsfaktor
        für Nachfrager ist niedriger (600), was zu einer schnelleren Steigerung der 
        Beitrittswahrscheinlichkeit führt.
        
        Returns:
            float: Beitrittswahrscheinlichkeit für Nachfrager zwischen Basis- und Maximalwert
        """
        if len(self.N_p_history) < 2:
            return self.basis_wahrscheinlichkeit_nachfrager
        
        # Veränderung der Netzwerkeffekte über die letzten Perioden
        vergleichsindex = max(0, len(self.N_p_history) - 30)
        netzwerk_veraenderung = self.N_p_history[-1] - self.N_p_history[vergleichsindex]
        
        # Bei Stagnation oder Rückgang nur minimale Beitrittsrate
        if netzwerk_veraenderung <= 0:
            return self.basis_wahrscheinlichkeit_nachfrager
        
        # Progressive Skalierung mit Exponent 0.7 und Normalisierungsfaktor 600
        normalisierte_veraenderung = min(1.0, (netzwerk_veraenderung / 600) ** 0.7)
        
        # Rate basierend auf der Veränderung
        return self.basis_wahrscheinlichkeit_nachfrager + (
            (self.max_wahrscheinlichkeit_nachfrager - self.basis_wahrscheinlichkeit_nachfrager) * normalisierte_veraenderung
        )

    def step(self):
        """
        Führt einen Simulationsschritt durch, der einen Tag im Modell repräsentiert.
        
        In jedem Schritt werden:
        1. Aktuelle Daten gespeichert
        2. Zähler zurückgesetzt
        3. Alle Agenten aktiviert
        4. Neue Anbieter und Nachfrager mit dynamischen Wahrscheinlichkeiten hinzugefügt
        
        Die Methode steuert das Wachstum der Plattform basierend auf den aktuellen
        Netzwerkeffekten und dem Erfolg der implementierten Strategien.
        """
        self.datacollector.collect(self)  # Speichern der aktuellen Werte, bevor die Zähler zurückgesetzt werden

        self.neue_anbieter = 0
        self.neue_nachfrager = 0
        self.abgewanderte_anbieter = 0
        self.abgewanderte_nachfrager = 0

        self.schedule.step()

        # Dynamische Beitrittswahrscheinlichkeiten basierend auf Netzwerkeffekten
        beitrittsrate_nachfrager = self.berechne_beitrittsrate_nachfrager()
        beitrittsrate_anbieter = self.berechne_beitrittsrate_anbieter()
        
        # Aktuelle Plattformgröße für dynamischen Zuwachs
        aktuelle_anbieter = sum(1 for a in self.schedule.agents if isinstance(a, Anbieter))
        aktuelle_nachfrager = sum(1 for a in self.schedule.agents if isinstance(a, Nachfrager))
        
        # Dynamisches Wachstumspotenzial basierend auf aktueller Größe
        max_neue_anbieter = max(5, int(aktuelle_anbieter * 0.03))  # Maximum 3% der aktuellen Anzahl, mindestens 5
        max_neue_nachfrager = max(10, int(aktuelle_nachfrager * 0.01))  # Maximum 1% der aktuellen Anzahl, mindestens 10

        # Neue Anbieter mit dynamischer Wahrscheinlichkeit
        neue_anbieter_heute = 0
        for _ in range(max_neue_anbieter):
            if random.random() < beitrittsrate_anbieter:
                neuer_anbieter = Anbieter(self.next_id, self)
                self.schedule.add(neuer_anbieter)
                self.next_id += 1
                neue_anbieter_heute += 1
        
        self.neue_anbieter = neue_anbieter_heute

        # Neue Nachfrager mit dynamischer Wahrscheinlichkeit
        neue_nachfrager_heute = 0
        for _ in range(max_neue_nachfrager):
            if random.random() < beitrittsrate_nachfrager:
                neuer_nachfrager = Nachfrager(self.next_id, self)
                self.schedule.add(neuer_nachfrager)
                self.next_id += 1
                neue_nachfrager_heute += 1
                
        self.neue_nachfrager = neue_nachfrager_heute

        # Debugging-Info
        if self.schedule.steps % 30 == 0:  # Nur jeden 30. Schritt anzeigen
            print(f"Tag {self.schedule.steps}: Neue Anbieter: {neue_anbieter_heute}, Neue Nachfrager: {neue_nachfrager_heute}")
            print(f"Aktuelle Beitrittsraten: Anbieter {beitrittsrate_anbieter:.3f}, Nachfrager {beitrittsrate_nachfrager:.3f}")
            print(f"Aktueller Netzwerkeffekt: {self.N_p_history[-1]:.2f}")
            print(f"Möglicher täglicher Zuwachs: Anbieter {max_neue_anbieter}, Nachfrager {max_neue_nachfrager}")