"""
Corrélation entre les thèmes JT et le taux d'expression des femmes.

Question data-driven : est-ce qu'il existe un lien statistique entre la
composition thématique d'une chaîne (% politique, % société, etc.) et la
part de parole donnée aux femmes ?

Méthode : corrélation de Pearson entre chaque 'part_rubrique' et
'women_expression_rate' sur l'ensemble des couples (année, chaîne).

Sortie :
  analyses/outputs/correlation_themes_parite.csv   — coefs Pearson + p-values
  analyses/outputs/correlation_heatmap.png         — heatmap visuelle
"""

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pearsonr

ROOT = Path(__file__).resolve().parent.parent
GOLD = ROOT / "data" / "gold" / "tv_theme_parite.csv"
OUT  = ROOT / "analyses" / "outputs"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    df = pd.read_csv(GOLD)
    part_cols = [c for c in df.columns if c.startswith("part_")]

    results = []
    for col in part_cols:
        r, p = pearsonr(df[col], df["women_expression_rate"])
        results.append({
            "rubrique": col.replace("part_", ""),
            "pearson_r": round(r, 3),
            "p_value":   round(p, 4),
            "significatif_5pct": p < 0.05,
        })

    res_df = pd.DataFrame(results).sort_values("pearson_r", ascending=False)
    res_df.to_csv(OUT / "correlation_themes_parite.csv", index=False)

    # Heatmap : matrice de corrélation complète parts × parité + speech_rate
    cols_all = part_cols + ["women_expression_rate", "speech_rate"]
    corr = df[cols_all].corr().round(2)

    fig, ax = plt.subplots(figsize=(12, 10))
    im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(cols_all)))
    ax.set_yticks(range(len(cols_all)))
    labels = [c.replace("part_", "") for c in cols_all]
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticklabels(labels)

    # Valeurs dans les cases
    for i in range(len(cols_all)):
        for j in range(len(cols_all)):
            val = corr.values[i, j]
            ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                    color="white" if abs(val) > 0.5 else "black", fontsize=8)

    fig.colorbar(im, ax=ax)
    ax.set_title("Corrélations : parts de rubriques JT × parité H/F\n(Pearson, 5 chaînes × 10 ans)")
    fig.tight_layout()
    fig.savefig(OUT / "correlation_heatmap.png", dpi=120)
    plt.close(fig)

    # Summary console
    print("Top 3 corrélations positives (rubriques + associées à la parité femmes) :")
    print(res_df.head(3).to_string(index=False))
    print("\nTop 3 corrélations négatives :")
    print(res_df.tail(3).to_string(index=False))
    print(f"\n→ Fichiers produits dans {OUT}")


if __name__ == "__main__":
    main()
