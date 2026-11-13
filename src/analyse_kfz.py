"""Explorative Auswertung: KBA-Bestände × Typklassen anhand von HSN/TSN.

Dies ist eine auf ein verständliches Kernbeispiel reduzierte Fassung des
ursprünglichen Notebooks. Keine Aussage über individuelles Fahrverhalten,
Schadenhäufigkeit oder Versicherungsprämien.
"""

from __future__ import annotations

import argparse
import csv
from io import StringIO
from pathlib import Path
from zipfile import ZipFile

import matplotlib
matplotlib.use("Agg")  # Auch ohne Notebook / Desktop nutzbar
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

KBA_COLS = ["HSN", "Hersteller_KBA", "TSN", "Modell_KBA", "Bestand"]
AMS_COLS = [
    "HSN", "TSN", "Modell_AMS", "Hersteller_AMS", "Hubraum",
    "LeistungKW", "HP", "TK", "VK", "GueltigBis",
]


def normalize_keys(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    for field, width in [("HSN", 4), ("TSN", 3)]:
        frame[field] = frame[field].astype("string").str.strip().str.upper().str.zfill(width)
        if frame[field].isna().any():
            raise ValueError(f"Fehlende Schlüsselwerte: {field}")
    if frame.duplicated(["HSN", "TSN"]).any():
        example = frame.loc[frame.duplicated(["HSN", "TSN"], keep=False), ["HSN", "TSN"]].head()
        raise ValueError(f"Doppelte HSN/TSN-Schlüssel:\n{example}")
    return frame


def load_kba(path: Path) -> pd.DataFrame:
    df = pd.read_csv(
        path, header=None, names=KBA_COLS, encoding="latin1",
        dtype={"HSN": "string", "TSN": "string"}, thousands=".",
    )
    df = normalize_keys(df)
    df["Bestand"] = pd.to_numeric(df["Bestand"], errors="coerce")
    if df["Bestand"].isna().any() or (df["Bestand"] < 0).any():
        raise ValueError("KBA-Datei enthält fehlende oder negative Bestandszahlen.")
    df["Bestand"] = df["Bestand"].astype("int64")
    return df


def load_ams(path: Path) -> tuple[pd.DataFrame, int]:
    rows: list[list[str]] = []
    skipped = 0
    with ZipFile(path) as archive:
        raw = archive.read("KfzTypen.dat").decode("latin1")
    for line in raw.splitlines()[1:]:  # Erste Zeile ist Dateikopf
        line = line.strip()
        if not line:
            continue
        if not (line.startswith("(") and line.endswith(")")):
            skipped += 1
            continue
        try:
            fields = next(csv.reader(StringIO(line[1:-1]), delimiter=",", quotechar="'"))
        except csv.Error:
            skipped += 1
            continue
        if len(fields) != len(AMS_COLS):
            skipped += 1
            continue
        rows.append(fields)
    if not rows:
        raise ValueError("Keine AMS-Daten eingelesen: Dateiformat prüfen.")
    df = normalize_keys(pd.DataFrame(rows, columns=AMS_COLS))
    for col in ("Hubraum", "LeistungKW", "HP", "TK", "VK"):
        df[col] = pd.to_numeric(df[col], errors="coerce")  # Fehlende Werte NICHT zu 0 umdeuten
    return df, skipped


def joined_data(kba: pd.DataFrame, ams: pd.DataFrame) -> pd.DataFrame:
    # Ausgangspunkt KBA: Abdeckungsquote im zugelassenen Bestand sichtbar machen.
    df = kba.merge(ams, on=["HSN", "TSN"], how="left", validate="one_to_one", indicator=True)
    matched = df["_merge"].eq("both")
    valid_hp = df["HP"].between(10, 25)
    matched_stock = df.loc[matched, "Bestand"].sum()
    valid_stock = df.loc[matched & valid_hp, "Bestand"].sum()
    total_stock = df["Bestand"].sum()
    print(f"KBA-Zeilen: {len(kba):,}; AMS-Zeilen: {len(ams):,}")
    print(f"KBA-Schlüssel mit AMS-Treffer: {matched.sum():,} / {len(kba):,}")
    print(f"KBA-Bestand gesamt: {total_stock:,}")
    print(f"Mit AMS-Treffer: {matched_stock:,} ({matched_stock / total_stock:.1%})" if total_stock else "KBA-Bestand: 0")
    print(f"Mit gültiger HP-Typklasse 10–25: {valid_stock:,} ({valid_stock / total_stock:.1%})" if total_stock else "Keine gültigen Bestände")
    print(f"Ohne verwertbare HP-Typklasse: {(total_stock-valid_stock):,}")
    result = df.loc[matched & valid_hp & df["Bestand"].gt(0)].copy()
    if result.empty:
        raise ValueError("Keine gematchten Datensätze mit gültiger HP-Typklasse und Bestand > 0.")
    return result.drop(columns=["_merge"])


def weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    valid = values.notna() & weights.notna() & weights.gt(0)
    if not valid.any():
        return float("nan")
    return float(np.average(values.loc[valid], weights=weights.loc[valid]))


def hsn_report(df: pd.DataFrame, folder: Path, minimum_stock: int) -> pd.DataFrame:
    d = df.copy()
    d["weighted_hp"] = d["HP"] * d["Bestand"]
    grouped = d.groupby("HSN", as_index=False).agg(
        hersteller=("Hersteller_KBA", "first"),
        bestand=("Bestand", "sum"),
        hp_summe=("weighted_hp", "sum"),
    )
    grouped["hp_mittel"] = grouped["hp_summe"] / grouped["bestand"]
    eligible = grouped[grouped["bestand"].ge(minimum_stock)].sort_values("hp_mittel")
    if eligible.empty:
        print(f"Keine HSN mit mindestens {minimum_stock:,} Fahrzeugen; HSN-Grafik entfällt.")
        return grouped

    # Maximal 16 Kategorien, damit die Grafik als Bewerbungsauszug lesbar bleibt.
    view = pd.concat([eligible.head(8), eligible.tail(8)]).drop_duplicates("HSN")
    view = view.sort_values("hp_mittel")
    y = np.arange(len(view))
    fig, ax = plt.subplots(figsize=(11.5, max(5.5, len(view) * .43 + 1.5)))
    ax.barh(y, view["hp_mittel"] - 10, left=10, color="steelblue", height=.75)
    ax.set_yticks(y, [f"{hsn} · {str(name)[:27]}" for hsn, name in zip(view["HSN"], view["hersteller"])])
    ax.invert_yaxis()
    ax.set_xlim(10, max(25.5, float(view["hp_mittel"].max()) + 1))
    ax.set_xlabel("Bestandsgewichtete mittlere Haftpflicht-Typklasse")
    ax.set_title(f"HSN-Vergleich (jeweils mindestens {minimum_stock:,} Fahrzeuge)")
    for idx, (score, stock) in enumerate(zip(view["hp_mittel"], view["bestand"])):
        ax.text(score + .10, idx, f"{score:.2f} · n={stock:,}", va="center", fontsize=8)
    ax.grid(axis="x", alpha=.25)
    ax.set_axisbelow(True)
    fig.text(.02, .01, "Deskriptive HSN-Aggregation; keine Aussage zu Fahrer- oder Schadenrisiken.", fontsize=8)
    fig.tight_layout(rect=[0,.03,1,1])
    fig.savefig(folder / "hsn_auswahl.png", dpi=175)
    plt.close(fig)
    return grouped


def class_distribution(df: pd.DataFrame, folder: Path) -> None:
    agg = df.groupby("HP")["Bestand"].sum().reindex(range(10, 26), fill_value=0)
    fig, ax = plt.subplots(figsize=(10.5, 5.5))
    ax.bar(agg.index, agg.values / 1e6, color="steelblue")
    ax.axvline(weighted_mean(df["HP"], df["Bestand"]), color="black", linestyle="--", label="Gewichteter Mittelwert")
    ax.set_xticks(range(10, 26))
    ax.set_ylabel("Erfasste Fahrzeuge (Millionen)")
    ax.set_xlabel("Haftpflicht-Typklasse")
    ax.set_title("Bestandsverteilung nach Haftpflicht-Typklasse")
    ax.legend()
    ax.grid(axis="y", alpha=.25)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(folder / "bestand_je_typklasse.png", dpi=175)
    plt.close(fig)


def power_report(df: pd.DataFrame, folder: Path) -> None:
    d = df.loc[df["LeistungKW"].gt(0)].copy()
    if d.empty:
        return
    cuts = list(range(0, 301, 20)) + [np.inf]
    labels = [f"{lower+1}–{upper}" for lower, upper in zip(range(0, 300, 20), range(20, 301, 20))] + [">300"]
    d["power_bin"] = pd.cut(d["LeistungKW"], bins=cuts, labels=labels)
    agg = d.groupby("power_bin", observed=True).apply(
        lambda g: pd.Series({"hp_mittel": weighted_mean(g["HP"], g["Bestand"]),
                             "bestand": g["Bestand"].sum()}), include_groups=False)
    if agg.empty:
        return
    fig, ax = plt.subplots(figsize=(12, 6))
    xs = np.arange(len(agg))
    ax.bar(xs, agg["hp_mittel"], color="steelblue")
    ax.set_xticks(xs, list(agg.index), rotation=40, ha="right")
    ax.set_ylim(10, 25)
    ax.set_xlabel("Motorleistung in kW")
    ax.set_ylabel("Bestandsgewichtete Haftpflicht-Typklasse")
    ax.set_title("Typklasse nach Motorleistung (deskriptiver Vergleich)")
    ax.grid(axis="y", alpha=.25)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(folder / "leistung_und_typklasse.png", dpi=175)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kba", type=Path, default=Path("data/typen.csv"))
    parser.add_argument("--ams", type=Path, default=Path("data/kfzTypen.ams"))
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    parser.add_argument("--minimum-stock", type=int, default=100_000)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    kba = load_kba(args.kba)
    ams, skipped = load_ams(args.ams)
    print(f"Übersprungene fehlerhafte AMS-Zeilen: {skipped}")
    df = joined_data(kba, ams)
    print(f"Gewichtete HP-Typklasse im gematchten Bestand: {weighted_mean(df['HP'], df['Bestand']):.3f}")
    df.to_csv(args.output_dir / "gematchte_typklassen.csv", sep=";", index=False)
    hsn_report(df, args.output_dir, args.minimum_stock).to_csv(
        args.output_dir / "hsn_statistik.csv", sep=";", index=False)
    class_distribution(df, args.output_dir)
    power_report(df, args.output_dir)
    print(f"Ergebnisse gespeichert in: {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
