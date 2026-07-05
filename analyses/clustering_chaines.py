"""
Clustering des chaînes TV par profil thématique.

Méthode :
  1. Construire un vecteur "profil" par chaîne-année = parts des 14 rubriques JT
  2. Réduction de dimension par ACP (2 composantes, visualisable)
  3. Clustering k-means (k=3) : positionne chaque chaîne dans un "archétype"

Permet de montrer par exemple :
  - Cluster 1 : "info généraliste équilibrée" (France 2, France 3)
  - Cluster 2 : "populaire / faits divers" (TF1, M6)
  - Cluster 3 : "culturel / international" (Arte)

Sortie :
  analyses/outputs/clusters_chaines.csv      — chaque chaîne-année + son cluster
  analyses/outputs/clusters_chaines.png      — scatter ACP 2D coloré par cluster
  analyses/outputs/clusters_centroides.csv   — profil moyen de chaque cluster
"""

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent.parent
GOLD = ROOT / "data" / "gold" / "tv_theme_parite.csv"
OUT  = ROOT / "analyses" / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

N_CLUSTERS = 3
RANDOM_STATE = 42


def main() -> None:
    df = pd.read_csv(GOLD)

    # On ne garde que les colonnes 'part_*' (profil thématique)
    part_cols = [c for c in df.columns if c.startswith("part_")]
    X = df[part_cols].to_numpy()

    # Standardisation (chaque rubrique a des échelles différentes)
    X_scaled = StandardScaler().fit_transform(X)

    # ACP 2D
    pca = PCA(n_components=2, random_state=RANDOM_STATE)
    X_pca = pca.fit_transform(X_scaled)
    var_explained = pca.explained_variance_ratio_
    print(f"Variance expliquée ACP : PC1={var_explained[0]:.1%}, PC2={var_explained[1]:.1%}")

    # K-means
    km = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_STATE, n_init=10)
    clusters = km.fit_predict(X_scaled)

    # Enrichir le dataframe
    df["pc1"] = X_pca[:, 0]
    df["pc2"] = X_pca[:, 1]
    df["cluster"] = clusters

    df[["annee", "chaine", "cluster", "pc1", "pc2"] + part_cols].to_csv(
        OUT / "clusters_chaines.csv", index=False
    )

    # Profil moyen des clusters (quelles rubriques dominent chaque groupe)
    centroides = df.groupby("cluster")[part_cols].mean().round(3)
    centroides["nb_obs"] = df.groupby("cluster").size()
    centroides["chaines_principales"] = df.groupby("cluster")["chaine"] \
        .agg(lambda s: ", ".join(s.value_counts().head(3).index))
    centroides.to_csv(OUT / "clusters_centroides.csv")

    # Scatter plot ACP
    fig, ax = plt.subplots(figsize=(10, 7))
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
    for c in range(N_CLUSTERS):
        sub = df[df["cluster"] == c]
        ax.scatter(sub["pc1"], sub["pc2"], c=colors[c], label=f"Cluster {c}",
                   alpha=0.7, s=80, edgecolors="white")
    # Annoter chaque point (chaîne + année abrégée)
    for _, row in df.iterrows():
        ax.annotate(f"{row['chaine']}·{str(row['annee'])[2:]}",
                    (row["pc1"], row["pc2"]), fontsize=7, alpha=0.7)

    ax.set_xlabel(f"PC1 ({var_explained[0]:.1%})")
    ax.set_ylabel(f"PC2 ({var_explained[1]:.1%})")
    ax.set_title("Clustering des chaînes TV par profil thématique JT (2010-2019)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "clusters_chaines.png", dpi=120)
    plt.close(fig)

    print(f"\n→ Cluster centroides :\n{centroides[['nb_obs', 'chaines_principales']]}")
    print(f"\n→ Fichiers produits dans {OUT}")


if __name__ == "__main__":
    main()
