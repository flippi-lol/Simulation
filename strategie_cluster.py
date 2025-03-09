class StrategieCluster:
    """
    Repräsentiert einen Strategie-Cluster oder eine einzelne Maßnahme mit dazugehörigem Effekt.
    
    Ein StrategieCluster kann entweder eine einzelne Maßnahme darstellen oder einen 
    Zusammenschluss mehrerer Maßnahmen zu einem Cluster, bei dem Synergieeffekte 
    berücksichtigt werden können.
    
    Attributes:
        name (str): Name des Strategie-Clusters oder der Maßnahme
        effekt (float): Numerischer Effektwert, der den Einfluss auf die Netzwerkeffekte angibt
    """
    
    def __init__(self, name, effekt):
        """
        Initialisiert einen neuen StrategieCluster.
        
        Args:
            name (str): Name des Strategie-Clusters oder der Maßnahme
            effekt (float): Numerischer Effektwert, der den Einfluss auf die Netzwerkeffekte angibt
        """
        self.name = name
        self.effekt = effekt

# Einzelne Maßnahmen Sichtbarkeit & Nutzergewinnung mit Netzwerkeffekten
sem = StrategieCluster("SEM", 5.16)
social_media_marketing = StrategieCluster("Social-Media-Marketing", 2)
affiliate_marketing = StrategieCluster("Affiliate-Marketing", 16)

# Cluster: Sichtbarkeit & Nutzergewinnung mit Synergiebonus (10 %)
sichtbarkeit_cluster = StrategieCluster("Sichtbarkeit & Nutzergewinnung", 
    (sem.effekt + social_media_marketing.effekt + affiliate_marketing.effekt) * 1.1)  


# Einzelne Maßnahmen Monetarisierung mit Netzwerkeffekten
reduzierte_gebuehren = StrategieCluster("Reduzierte Gebühren", 4)
freemium_modell = StrategieCluster("Freemium Modell", 25)

# Cluster: Monetarisierung mit Synergiebonus (10 %)
monetarisierung_cluster = StrategieCluster("Monetarisierung", 
    (reduzierte_gebuehren.effekt + freemium_modell.effekt) * 1.1)  


# Einzelne Maßnahmen Community & Nutzerbindung mit Netzwerkeffekten
eigenes_forum = StrategieCluster("Eigenes Forum", 2)
treuepunkte = StrategieCluster("Treuepunkte", 20)

# Cluster: Community & Nutzerbindung mit Synergiebonus (10 %)
community_cluster = StrategieCluster("Community & Nutzerbindung", 
    (eigenes_forum.effekt + treuepunkte.effekt) * 1.1)  


# Einzelne Maßnahmen Nachhaltigkeit & Lokalität mit Netzwerkeffekten
personalisierte_empfehlungen = StrategieCluster("Personalisierte Empfehlungen", 17.5)
nachhaltige_werte = StrategieCluster("Nachhaltige Werte", 10)
co2_transparenz = StrategieCluster("CO2-Transparenz", 5)
nachhaltige_produktfilter = StrategieCluster("Nachhaltige Produktfilter", 5)
regionale_kooperationen = StrategieCluster("Regionale Kooperationen", 10)

# Cluster: Nachhaltigkeit & Lokalität mit Synergiebonus (10 %)
nachhaltigkeit_cluster = StrategieCluster("Nachhaltigkeit & Lokalität", 
    (nachhaltige_werte.effekt + co2_transparenz.effekt + 
     nachhaltige_produktfilter.effekt + regionale_kooperationen.effekt) * 1.1)

# Debug-Ausgabe der Cluster-Effekte
print("\nKonfigurierte Strategie-Cluster und deren Effekte:")
print(f"Sichtbarkeit & Nutzergewinnung: {sichtbarkeit_cluster.effekt:.2f}")
print(f"Monetarisierung: {monetarisierung_cluster.effekt:.2f}")
print(f"Community & Nutzerbindung: {community_cluster.effekt:.2f}")
print(f"Nachhaltigkeit & Lokalität: {nachhaltigkeit_cluster.effekt:.2f}")

# Liste aller Cluster zur einfachen Referenz
alle_cluster = [
    sichtbarkeit_cluster,
    monetarisierung_cluster,
    community_cluster,
    nachhaltigkeit_cluster
]