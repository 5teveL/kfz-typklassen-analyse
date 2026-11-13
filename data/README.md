# Eingabedaten

Für einen Lauf werden **lokal** zwei Dateien benötigt. Sie werden aus Rücksicht auf nicht abschließend geklärte Nutzungsrechte nicht im öffentlichen Repository bereitgestellt.

- `data/typen.csv`: KBA-Bestandsdatei ohne Kopfzeile, kommasepariert, Spalten: HSN, Herstellername, TSN, Handelsname, Anzahl. Schlüssel als Text, damit führende Nullen erhalten bleiben.
- `data/kfzTypen.ams`: ZIP-Archiv mit `KfzTypen.dat`; Einträge mit zehn Feldern (HSN, TSN, Modell, Hersteller, Hubraum, Leistung in kW, Haftpflicht-, Teilkasko- und Vollkasko-Typklasse, Gültigkeitsinformation).

Die Formate entsprechen dem ursprünglichen Notebook. Andere Datenstände oder Exportformate können Anpassungen erfordern. Quelle und Stichtag der tatsächlich verwendeten Dateien sowie deren Veröffentlichungsrechte müssen vor einer erneuten Weitergabe geprüft werden.
