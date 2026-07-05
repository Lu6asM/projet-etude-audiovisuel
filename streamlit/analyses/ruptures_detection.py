"""
Détection de ruptures temporelles dans l'intensité médiatique des rubriques JT.

Utilise l'algorithme PELT (Pruned Exact Linear Time) de la librairie `ruptures`
pour identifier automatiquement les dates où la série change significativement
de régime (ex : explosion du thème 'Santé' en mars 2020).

Sortie :
  analyses/outputs/ruptures_points.csv   — liste des ruptures détectées
  analyses/outputs/ruptures_{rubrique}.png — graphe par rubrique
"""

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import matplotlib
matplotlib.use("Agg")  # backend headless, pas besoin de GUI
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import ruptures as rpt

ROOT = Path(__file__).resolve().parent.parent
SILVER = ROOT / "data" / "silver" / "ina_jt.csv"
OUT    = ROOT / "analyses" / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

# Rubriques ciblées : celles où on attend des ruptures socio-historiques
RUBRIQUES_CIBLES = ["Santé", "Politique France", "International", "Faits divers", "Economie"]

# Pénalité PELT — plus haut = moins de ruptures (moins sensible au bruit)
# Valeur calibrée empiriquement sur les rubriques INA (≈ 3-5 ruptures/série)
PELT_PENALTY = 3


def main() -> None:
    df = pd.read_csv(SILVER, parse_dates=["date"])

    # Série mensuelle de durée totale par rubrique (toutes chaînes confondues)
    monthly = (
        df.assign(mois=df["date"].dt.to_period("M").dt.to_timestamp())
          .groupby(["mois", "rubrique"], as_index=False)["duree_totale"]
          .sum()
    )

    all_points = []

    for rub in RUBRIQUES_CIBLES:
        serie = monthly[monthly["rubrique"] == rub].sort_values("mois")
        signal = serie["duree_totale"].to_numpy()

        # PELT sur un modèle RBF — bon pour détecter changements de moyenne ET variance
        algo = rpt.Pelt(model="rbf").fit(signal)
        bkps = algo.predict(pen=PELT_PENALTY)

        # bkps = indices ; on en retire les dates
        rupture_dates = [serie["mois"].iloc[i - 1] for i in bkps if i <= len(serie)]
        for d in rupture_dates[:-1]:  # le dernier est la fin de série, pas une vraie rupture
            all_points.append({
                "rubrique": rub,
                "date_rupture": d.strftime("%Y-%m"),
                "nb_mois_serie": len(serie),
            })

        # Graphe
        fig, ax = plt.subplots(figsize=(12, 3))
        ax.plot(serie["mois"], signal, linewidth=1.2, color="#1f77b4")
        for d in rupture_dates[:-1]:
            ax.axvline(d, color="red", linestyle="--", alpha=0.6)
        ax.set_title(f"Ruptures détectées — {rub}")
        ax.set_ylabel("Durée totale (sec)")
        ax.grid(alpha=0.3)
        fig.tight_layout()
        fig.savefig(OUT / f"ruptures_{rub.replace(' ', '_').replace('é', 'e')}.png", dpi=100)
        plt.close(fig)
        print(f"  {rub:20s} → {len(rupture_dates)-1} rupture(s)")

    pd.DataFrame(all_points).to_csv(OUT / "ruptures_points.csv", index=False)
    print(f"\n→ {OUT / 'ruptures_points.csv'} ({len(all_points)} ruptures au total)")


if __name__ == "__main__":
    main()
