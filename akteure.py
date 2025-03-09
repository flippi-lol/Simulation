import random

class Anbieter:
    """
    Repräsentiert einen Anbieter auf der Plattform.
    
    Ein Anbieter stellt Produkte oder Dienstleistungen auf der Plattform zur Verfügung
    und kann basierend auf erhaltenen Bewertungen und dem Zustand der Netzwerkeffekte
    entscheiden, ob er auf der Plattform bleibt oder abwandert.
    
    Attributes:
        unique_id (int): Eindeutige ID des Anbieters
        model (PlattformModel): Referenz zum übergeordneten Modell
        bewertungen (list): Liste mit erhaltenen Bewertungen (1-5 Sterne)
    """
    
    def __init__(self, unique_id, model):
        """
        Initialisiert einen neuen Anbieter.
        
        Args:
            unique_id (int): Eindeutige ID des Anbieters
            model (PlattformModel): Referenz zum übergeordneten Modell
        """
        self.unique_id = unique_id
        self.model = model
        self.bewertungen = []

    def step(self):
        """
        Führt einen Simulationsschritt für den Anbieter durch.
        
        In jedem Schritt prüft der Anbieter, ob er die Plattform verlassen will,
        basierend auf seinen erhaltenen Bewertungen und dem Zustand der Plattform.
        """
        if self.pruefe_abwanderung():
            self.model.abgewanderte_anbieter += 1  # Anbieter-Abwanderung zählt hoch
            self.model.schedule.remove(self)  # Anbieter wird entfernt

    def erhalte_bewertung(self, bewertung):
        """
        Nimmt eine Bewertung von einem Nachfrager entgegen und speichert sie.
        
        Args:
            bewertung (int): Bewertung des Anbieters (1-5 Sterne)
        """
        self.bewertungen.append(bewertung)

    def pruefe_abwanderung(self):
        """
        Prüft, ob der Anbieter die Plattform verlassen soll.
        
        Die Entscheidung basiert auf zwei Faktoren:
        1. Die durchschnittliche Bewertung (schlechte Bewertungen erhöhen die Abwanderungswahrscheinlichkeit)
        2. Der Zustand der Netzwerkeffekte (sinkende Netzwerkeffekte erhöhen die Abwanderungswahrscheinlichkeit)
        
        Returns:
            bool: True, wenn der Anbieter abwandern soll, sonst False
        """
        # Abwanderungslogik basierend auf Bewertungen
        if len(self.bewertungen) > 0:
            durchschnitt = sum(self.bewertungen) / len(self.bewertungen)
            if durchschnitt <= 2.5:
                # Je schlechter die Bewertungen, desto höher die Abwanderungswahrscheinlichkeit
                abwanderungswahrscheinlichkeit = min(0.1 + (2.5 - durchschnitt) * 0.2, 0.9)
                if random.random() < abwanderungswahrscheinlichkeit:
                    return True

        # Abwanderungslogik basierend auf Netzwerkeffekten
        if self.model.sinkt_netzwerkeffekt():
            # Stärkerer Rückgang der Netzwerkeffekte führt zu höherer Abwanderungswahrscheinlichkeit
            abwanderungswahrscheinlichkeit = max(0.05, min(0.2, abs(self.model.N_p_history[-1] - self.model.N_p_history[0]) / 1000))
            if random.random() < abwanderungswahrscheinlichkeit:
                return True

        return False


class Nachfrager:
    """
    Repräsentiert einen Nachfrager auf der Plattform.
    
    Ein Nachfrager kauft Produkte oder Dienstleistungen von Anbietern, bewertet diese
    und kann die Plattform verlassen, wenn die Netzwerkeffekte sinken.
    
    Attributes:
        unique_id (int): Eindeutige ID des Nachfragers
        model (PlattformModel): Referenz zum übergeordneten Modell
        cooldown (int): Sperrzeit zwischen Käufen in Tagen
    """
    
    def __init__(self, unique_id, model):
        """
        Initialisiert einen neuen Nachfrager.
        
        Args:
            unique_id (int): Eindeutige ID des Nachfragers
            model (PlattformModel): Referenz zum übergeordneten Modell
        """
        self.unique_id = unique_id
        self.model = model
        self.cooldown = 0  # Sperrzeit zwischen Käufen

    def step(self):
        """
        Führt einen Simulationsschritt für den Nachfrager durch.
        
        In jedem Schritt entscheidet der Nachfrager, ob er einen Kauf tätigt
        (abhängig von der Wahrscheinlichkeit und Cooldown-Zeit) und prüft,
        ob er die Plattform verlassen will.
        """
        iteration = self.model.schedule.steps
        angebotstag = iteration % 60 == 0  # Alle 60 Tage ist ein Angebotstag

        # Wenn der Nachfrager im Cooldown ist und es kein Angebotstag ist, warten
        if not angebotstag and self.cooldown > 0:
            self.cooldown -= 1  
            return  

        # Basis-Kaufwahrscheinlichkeit an normalen Tagen
        kaufwahrscheinlichkeit = 0.3
        if angebotstag:
            kaufwahrscheinlichkeit *= 2  # Doppelte Kaufwahrscheinlichkeit an Angebotstagen
            
        # Entscheidung zum Kauf basierend auf Wahrscheinlichkeit
        if angebotstag or random.random() < kaufwahrscheinlichkeit:
            self.kaufen()
            if not angebotstag:
                self.cooldown = 7  # 7 Tage Cooldown nach einem Kauf (außer an Angebotstagen)

        # Prüfen, ob der Nachfrager abwandern soll
        if self.model.sinkt_netzwerkeffekt():
            # Abwanderungswahrscheinlichkeit basierend auf der Stärke des Netzwerkeffektrückgangs
            abwanderungswahrscheinlichkeit = max(0.02, min(0.15, abs(self.model.N_p_history[-1] - self.model.N_p_history[0]) / 1500))
            if random.random() < abwanderungswahrscheinlichkeit:
                self.model.abgewanderte_nachfrager += 1
                self.model.schedule.remove(self)  # Nachfrager wird entfernt

    def kaufen(self):
        """
        Führt einen Kaufvorgang durch.
        
        Der Nachfrager wählt zufällig einen Anbieter aus und bewertet ihn.
        """
        anbieter_liste = [a for a in self.model.schedule.agents if isinstance(a, Anbieter)]
        if anbieter_liste:
            anbieter = random.choice(anbieter_liste)
            bewertung = self.bewerten()
            anbieter.erhalte_bewertung(bewertung)

    def bewerten(self):
        """
        Generiert eine Bewertung für einen Anbieter.
        
        Die Verteilung der Bewertungen ist leicht nach oben verschoben,
        mit höherer Wahrscheinlichkeit für 3-5 Sterne als für 1-2 Sterne.
        
        Returns:
            int: Bewertung zwischen 1 und 5 Sternen
        """
        # Gewichte für die Wahrscheinlichkeiten der verschiedenen Bewertungen
        # [5%, 10%, 30%, 30%, 25%] für [1, 2, 3, 4, 5] Sterne
        gewichte = [0.05, 0.1, 0.3, 0.3, 0.25]
        return random.choices([1, 2, 3, 4, 5], weights=gewichte, k=1)[0]