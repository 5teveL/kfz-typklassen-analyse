# Review des bereitgestellten Notebooks `vibe2.ipynb`

**Kontext:** Bewerbung auf aktuarielle/data-orientierte Rollen in der
Kfz-Versicherung. Die vorliegende Datei enthält Code und gespeicherte Ausgaben,
aber **nicht** `typen.csv` und `kfzTypen.ams`. Daher sind die Zahlen des
Originalnotebooks nicht unabhängig neu berechnet worden.

## Was im Original tatsächlich gemacht wird

- KBA-Bestands-CSV mit 61.294 Zeilen einlesen.
- 33.661 Datensätze aus `KfzTypen.dat` innerhalb `kfzTypen.ams` einlesen.
- Eindeutigkeit der Kombination HSN/TSN auf beiden Seiten prüfen.
- Per HSN/TSN verknüpfen und laut gespeicherter Ausgabe 28.007
  Datensätze mit positivem Bestand und insgesamt 47.446.751 Fahrzeugen
  in der gewählten *AMS-basierten* Auswertung erfassen.
- Bestandsgewichtete Haftpflicht-Typklassen, Haftpflicht-/Kasko-Vergleiche,
  Motorleistungsgruppen und Modellrankings berechnen und visualisieren.

Diese Zahlen sind **gespeicherte Notebook-Ausgaben**, keine hier
reproduzierten Ergebnisse. Die Summe 47.446.751 bezeichnet nicht automatisch
sämtliche zugelassenen Pkw in Deutschland; die Abdeckungsquote ist noch zu
prüfen.

## Priorität 1 – vor Veröffentlichung beheben

1. **Frischer Notebook-Lauf:** Am Ende der ersten Codezelle werden `df`
   und `np` verwendet, bevor sie in dieser Zelle definiert bzw. importiert
   werden. Das Notebook hängt damit von einem zuvor verwendeten Kernel ab.
   Eine leere Codezelle speichert außerdem einen `NameError` zu
   `fmt_bestand`. Das schwächt die Reproduzierbarkeit.
2. **Rankingfilter:** Die erste Marken-Ranking-Grafik behauptet im Text
   "nur Marken >= 100.000 Pkw". Tatsächlich filtert die Zeile
   `agg = agg[agg["bestand"] >= 1]...` aber ab **einem** Fahrzeug, was zu
   122 Balken und extremen Kleinstgruppen führt. Die HSN-Zusatzgrafik
   hat dagegen schon die Grenze 100.000.
3. **Merge-Abdeckung:** Die Verbindung wird von AMS (`how="left"`) aus
   gerechnet und nicht systematisch gegen den *gesamten* KBA-Bestand
   validiert. Fehlende oder nicht gematchte HSN/TSN können die
   Mittelwerte verzerren. Anzahl *und Bestandsvolumen* der nicht
   gematchten Fahrzeuge sollten dokumentiert werden.
4. **Validierung:** Typklassen und Leistungswerte werden teils mit
   `.fillna(0)` aus fehlenden/unlesbaren Einträgen erzeugt. Ungültige
   Typklassen nicht als numerische Typklasse 0 behandeln; filtern oder
   separat ausweisen.
5. **Datenjahr/Urheberrecht:** Stichtag und Herkunft beider Datenquellen
   sowie Nutzungsbedingungen dokumentieren. Nicht automatisch die
   Rohdaten mitsamt Repository veröffentlichen.

## Priorität 2 – wissenschaftliche und fachliche Präzision

6. Herstellerzuordnung ist nicht eindeutig: Bei den `kurzname`-Regeln wird
   z. B. `PSA` einmal als eigene Sammelkategorie und einmal als `OPEL`
   eingeordnet. Ein HSN ist außerdem nicht immer einer einzelnen Marke
   gleichzusetzen. Für die Bewerbung lieber das nachvollziehbare
   **HSN-Ranking** zeigen, nicht vermeintlich exakte Markenrisiken.
7. Typklasse ist **nicht** die beobachtete Schadenhäufigkeit eines
   bestimmten Fahrers und **nicht** der individuelle Versicherungsbeitrag.
   Titel wie "welche Fahrer richten mehr Unheil an?" oder "brav" sind
   für einen Versicherung-Arbeitsnachweis zu grob und teilweise irreführend.
8. Absolute Bestandszahlen und einzelne Modell-Highlights sind in manchen
   Diagrammbeschriftungen fest einprogrammiert. Das muss nach Datenupdate
   automatisch berechnet oder aus der Bewerbungsgrafik entfernt werden.
9. Der Zusammenhang zwischen Motorleistung und Haftpflicht-Typklasse ist
   **deskriptiv, nicht kausal**. Modellmix, Fahrleistungen und
   Nutzerstruktur werden nicht kontrolliert.
10. Notebook hat eine große Anzahl eingebetteter Grafiken, alte
    Fehlerausgaben und leere Zellen. GitHub-Version sollte diese
    bereinigen und einen klaren Startpunkt bieten.

## Für die HUK-Bewerbung geeignet

- Gut: konkrete HSN/TSN-Verknüpfung, selbst entworfene gewichtete Kennzahlen,
  Plausibilitäts- und Schlüsselprüfung, Visualisierungen, unabhängige
  Auseinandersetzung mit Kfz-Typklassen.
- Nicht behaupten: aktuarielle Reservierung, beobachtete Schadensquoten,
  Unfallwahrscheinlichkeiten je Marke, statistische Kausalanalyse.
- Eine Grafik mit höchstens ~15 HSN-Gruppen und jeweiligem Bestand ist
  wesentlich besser als ein Plot mit 100+ Marken.

Die neue Datei `src/analyse_kfz.py` ist eine **bewusst reduzierte
Beispielimplementierung**. Sie ersetzt nicht sämtliche sieben Originalplots
und wurde ohne echte Rohdaten **nur mit synthetischen Testeingaben** geprüft.
