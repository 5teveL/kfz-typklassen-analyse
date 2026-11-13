# Kfz-Haftpflicht-Typklassen und Fahrzeugbestand

Exploratives Python-Projekt: Verknüpfung von Fahrzeugbestandsdaten mit
Typklassen über **Herstellerschlüsselnummer (HSN)** und
**Typschlüsselnummer (TSN)**.

Das Projekt untersucht u. a. die Verteilung der Haftpflicht-Typklassen sowie
bestandsgewichtete Mittelwerte nach Herstellerschlüssel und Motorleistung.
Es basiert auf einem umfangreicheren selbstständig erstellten Notebook.

## Daten und Methode

1. HSN/TSN in beiden Quelldateien als Zeichenketten einlesen und normalisieren.
2. Eindeutigkeit der Schlüssel kontrollieren.
3. Bestandsdaten mit Typklassen verknüpfen und **Abdeckungsquote** ausgeben.
4. Nur Datensätze mit Bestand > 0 und gültiger Haftpflicht-Typklasse (10–25)
   für die Hauptauswertungen verwenden.
5. Gewichteter Mittelwert:

   `Summe(Typklasse_i * Bestand_i) / Summe(Bestand_i)`.

6. Ergebnisse als CSV und PNG-Grafiken speichern.

## Ausführen

Python 3.10+:

```bash
python -m pip install -r requirements.txt
python src/analyse_kfz.py --kba data/typen.csv --ams data/kfzTypen.ams
```

Optionale Auswahlgrenze für HSN-Diagramm:

```bash
python src/analyse_kfz.py --minimum-stock 100000
```

## Dateien

- `src/analyse_kfz.py`: nachvollziehbarer Analyseablauf, in Funktionen gegliedert
- `data/README.md`: erwartete Inputstruktur
- `results/`: nach der Ausführung generierte Tabellen und Grafiken

Die Original-Rohdaten wurden **nicht** mit dem Projekt hochgeladen. Ihre
Verwendung und mögliche Weitergabe sind anhand der jeweiligen
Nutzungsbedingungen zu prüfen.

## Interpretation / Grenzen

- Die Typklasse ist eine **Tarifierungs-Klassifikation**, keine individuelle
  Unfallwahrscheinlichkeit, keine gemessene Schadenquote des Herstellers und
  kein direkt vergleichbarer Versicherungsbeitrag.
- Aggregationen auf HSN-Ebene sind **keine sauberen Markenvergleiche**. Eine
  Marke kann mehrere Herstellerschlüssel besitzen; umgekehrt repräsentieren
  Herstellerschlüssel nicht zwingend genau eine Marke.
- Fehlende Typklassen-/Bestandszuordnungen können die Ergebnisse verzerren.
  Daher wird der Anteil des gematchten Fahrzeugbestands explizit ausgegeben.
- Der Zeitraum der Bestandsdatei und der Gültigkeitsstand der Typklassen
  müssen fachlich zusammenpassen. **Bitte Datenjahre hier ergänzen:**
  KBA-Bestand: `[Jahr/Stichtag]`, Typklassen: `[Jahr/Stand]`.
- Motorleistung korreliert nicht automatisch kausal mit Versicherungsschäden.
  Modellmix, Nutzungsprofile und weitere Variablen werden nicht kontrolliert.
- Diese Analyse ist deskriptiv und **keine** versicherungsmathematische
  Schadenreservierung oder Prognose.

## Stand

Die neue, kompakte Skriptfassung wurde aus dem vom Autor bereitgestellten
Notebook abgeleitet und mit synthetischen Testdaten auf Ausführbarkeit geprüft.
Mangels originaler Rohdaten wurden die ausgegebenen Fachkennzahlen nicht erneut
nachgerechnet oder gegen amtliche Datenbestände abgeglichen.
