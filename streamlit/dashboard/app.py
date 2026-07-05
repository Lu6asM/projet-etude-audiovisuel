"""
Dashboard Streamlit - Les Français face à l'info (2000-2020).

5 pages :
    1. Accueil
    2. Agenda médiatique (volumes, thèmes, saisonnalité, événements)
    3. Parité H/F (évolution, classement, prime time)
    4. Thèmes × Parité (corrélations, cœur du projet)
    5. Analyses avancées (clustering ACP, ruptures PELT)

Lancement : python -m streamlit run dashboard/app.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st
from streamlit_extras.chart_container import chart_container
from streamlit_extras.metric_cards import style_metric_cards

ROOT = Path(__file__).resolve().parent.parent
SILVER = ROOT / "data" / "silver"
GOLD = ROOT / "data" / "gold"
ANALYSES = ROOT / "analyses" / "outputs"

# ─────────────────────────────────────────────
# CONFIG STREAMLIT
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Les Français face à l'info",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Projet M1 Big Data & IA - JT et parité H/F 2000-2020."},
)

# ─────────────────────────────────────────────
# PALETTE
# ─────────────────────────────────────────────
PRIMARY = "#6366f1"
SECONDARY = "#f59e0b"
ACCENT = "#10b981"
DANGER = "#ef4444"
MUTED = "#94a3b8"
PALETTE = ["#6366f1", "#f59e0b", "#10b981", "#06b6d4", "#8b5cf6", "#ec4899", "#84cc16", "#f97316"]

# ─────────────────────────────────────────────
# TEMPLATE PLOTLY
# ─────────────────────────────────────────────
pio.templates["projet"] = go.layout.Template(
    layout=dict(
        font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif", size=13, color="#1f2937"),
        title=dict(font=dict(size=15, color="#0f172a", family="-apple-system, sans-serif"),
                   x=0.0, xanchor="left", y=0.97, yanchor="top", pad=dict(b=18)),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        colorway=PALETTE,
        xaxis=dict(gridcolor="#f1f5f9", zerolinecolor="#e5e7eb", linecolor="#e5e7eb",
                   ticks="outside", tickcolor="#e5e7eb", ticklen=4),
        yaxis=dict(gridcolor="#f1f5f9", zerolinecolor="#e5e7eb", linecolor="#e5e7eb",
                   ticks="outside", tickcolor="#e5e7eb", ticklen=4),
        legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="left", x=0,
                    title="", bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=70, b=70),
        hoverlabel=dict(bgcolor="white", font_size=12, bordercolor="#e5e7eb"),
    )
)
pio.templates.default = "projet"


# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
      .block-container {padding-top: 2rem; padding-bottom: 3rem; max-width: 1400px;}

      h1 {font-weight: 700; letter-spacing: -0.025em; color: #0f172a;}
      h2 {font-weight: 600; letter-spacing: -0.015em; color: #1e293b;}
      h3 {font-weight: 600; color: #334155;}

      /* Hero accueil - compact */
      .hero {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        padding: 1.75rem 2rem;
        border-radius: 14px;
        color: white;
        margin-bottom: 1.5rem;
      }
      .hero h1 {color: white; font-size: 1.9rem; margin-bottom: 0.4rem;}
      .hero p {color: rgba(255,255,255,0.95); font-size: 1rem; max-width: 760px; margin: 0;}

      /* Cartes KPI (style typographique seulement, le reste vient de style_metric_cards) */
      [data-testid="stMetricValue"] {font-size: 1.6rem; font-weight: 700; color: #0f172a;}
      [data-testid="stMetricLabel"] {
        font-size: 0.75rem; font-weight: 600; color: #64748b;
        text-transform: uppercase; letter-spacing: 0.04em;
      }
      [data-testid="stMetricDelta"] {font-size: 0.82rem; font-weight: 500;}

      /* Tabs */
      .stTabs [data-baseweb="tab-list"] {gap: 2px; border-bottom: 1px solid #e2e8f0;}
      .stTabs [data-baseweb="tab"] {
        padding: 0.55rem 1rem; font-weight: 500; font-size: 0.9rem;
        border-radius: 6px 6px 0 0; color: #64748b;
      }
      .stTabs [aria-selected="true"] {color: #6366f1; font-weight: 600;}

      /* Sidebar */
      [data-testid="stSidebar"] {background: #fafbfc; border-right: 1px solid #e5e7eb;}
      [data-testid="stSidebar"] .stRadio label {font-size: 0.9rem;}

      /* Cache footer & menu hamburger custom */
      footer {visibility: hidden;}

      /* Widgets labels */
      .stSelectbox label, .stRadio label, .stSlider label, .stMultiSelect label {
        font-weight: 500; color: #475569; font-size: 0.88rem;
      }

      /* Caption */
      [data-testid="stCaptionContainer"] {color: #64748b;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# UTILS
# ─────────────────────────────────────────────
@st.cache_data(show_spinner="Chargement des données…")
def load(name: str, layer: str = "gold") -> pd.DataFrame:
    base = {"gold": GOLD, "silver": SILVER, "analyses": ANALYSES}[layer]
    return pd.read_csv(base / f"{name}.csv")


def has(name: str, layer: str = "analyses") -> bool:
    base = {"gold": GOLD, "silver": SILVER, "analyses": ANALYSES}[layer]
    return (base / f"{name}.csv").exists()


def style_fig(fig, height: int = 420):
    fig.update_layout(height=height)
    return fig


def styled_metrics():
    """Applique le style aux st.metric précédents sur la page."""
    style_metric_cards(
        background_color="#ffffff",
        border_left_color=PRIMARY,
        border_color="#e2e8f0",
        border_radius_px=10,
        box_shadow=True,
    )


def empty_state(msg: str):
    st.info(f"👉 {msg}")


def explain(text: str, label: str = "💡 Comment lire ce graphique ?"):
    """Bloc dépliable avec une explication accessible aux non-techniciens.
    On utilise st.expander natif (stoggle n'interprète ni HTML ni markdown).
    """
    with st.expander(label):
        st.markdown(text, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📺 Les Français face à l'info")
    st.caption("M1 Big Data & IA · INA 2000-2020")

    st.markdown("")
    PAGES = {
        "🏠  Accueil": "home",
        "📊  Agenda médiatique": "agenda",
        "👩  Parité H/F": "parite",
        "🔀  Thèmes × Parité": "cross",
        "🔬  Analyses avancées": "advanced",
    }
    page_label = st.radio("Navigation", list(PAGES.keys()), label_visibility="collapsed")
    page = PAGES[page_label]

    st.markdown("---")
    st.markdown("**Période**")

    preset = st.selectbox(
        "Preset", ["Tout (2000-2020)", "Années 2000", "Années 2010", "Période COVID (2018-2020)", "Personnalisé"],
        label_visibility="collapsed", index=0,
    )
    presets = {
        "Tout (2000-2020)": (2000, 2020),
        "Années 2000": (2000, 2009),
        "Années 2010": (2010, 2019),
        "Période COVID (2018-2020)": (2018, 2020),
    }
    if preset == "Personnalisé":
        year_min, year_max = st.slider("Personnalisée", 1995, 2020, (2000, 2020), label_visibility="collapsed")
    else:
        year_min, year_max = presets[preset]
    st.caption(f"📅 {year_min} → {year_max}")

    st.divider()
    st.caption("**Sources**  ·  INA Baromètre JT  ·  INA Égalité H/F")
    st.caption("**Stack**  ·  Bronze → Silver → Gold  ·  pandera  ·  ruptures  ·  k-means")
    st.caption("M1 Big Data & IA  ·  2025-2026")


# ─────────────────────────────────────────────
# PAGE 1 - ACCUEIL
# ─────────────────────────────────────────────
if page == "home":
    st.markdown(
        """
        <div class="hero">
          <h1>Les Français face à l'information</h1>
          <p>20 ans de JT et de parité H/F dans l'audiovisuel français.
          On croise <strong>l'agenda médiatique</strong> avec <strong>la place des femmes</strong>
          à l'antenne pour voir si les deux se parlent.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    ina = load("ina_jt", "silver")
    pu = load("parite_unifiee")
    ev = load("themes_evenements")

    c1, c2, c3, c4 = st.columns(4, gap="medium")
    c1.metric("Sujets JT", f"{int(ina['nb_sujets'].sum()):,}".replace(",", " "))
    c2.metric("Heures de JT", f"{ina['duree_totale'].sum() / 3600:,.0f}".replace(",", " "))
    c3.metric("Médias suivis", pu["media_name"].nunique())
    c4.metric("Événements analysés", ev["evenement"].nunique())
    styled_metrics()

    st.subheader("Trois trouvailles majeures", divider="violet")

    trouvailles = st.columns(3, gap="medium")

    trouvailles[0].markdown(
        """
        <div style="border:1px solid #e2e8f0;border-radius:10px;padding:1.25rem;background:white;height:100%;">
          <div style="font-size:2.8rem;font-weight:800;color:#ef4444;line-height:1;">−0,60</div>
          <div style="margin-top:0.5rem;font-weight:600;">International ↔ Parité</div>
          <div style="color:#64748b;font-size:0.82rem;margin:0.25rem 0 0.6rem;">Indicateur de lien (-1 à +1)</div>
          <div style="font-size:0.92rem;color:#334155;">Les chaînes très tournées vers l'international donnent moins la parole aux femmes.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    trouvailles[1].markdown(
        """
        <div style="border:1px solid #e2e8f0;border-radius:10px;padding:1.25rem;background:white;height:100%;">
          <div style="font-size:2.8rem;font-weight:800;color:#10b981;line-height:1;">+0,58</div>
          <div style="margin-top:0.5rem;font-weight:600;">Faits divers / Société ↔ Parité</div>
          <div style="color:#64748b;font-size:0.82rem;margin:0.25rem 0 0.6rem;">Indicateur de lien (-1 à +1)</div>
          <div style="font-size:0.92rem;color:#334155;">Les rubriques de proximité accueillent plus de voix féminines.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    trouvailles[2].markdown(
        """
        <div style="border:1px solid #e2e8f0;border-radius:10px;padding:1.25rem;background:white;height:100%;">
          <div style="font-size:2.8rem;font-weight:800;color:#6366f1;line-height:1;">3</div>
          <div style="margin-top:0.5rem;font-weight:600;">Archétypes de chaînes</div>
          <div style="color:#64748b;font-size:0.82rem;margin:0.25rem 0 0.6rem;">Familles dégagées par l'analyse</div>
          <div style="font-size:0.92rem;color:#334155;">Généralistes grand public · chaînes internationales · newsrooms politiques.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Sources & données", divider="violet")
    src1, src2, src3 = st.columns(3, gap="medium")
    with src1:
        st.markdown("##### 📺 INA Baromètre JT")
        st.caption("Sujets quotidiens 2000-2020, 5 chaînes, 14 rubriques.")
    with src2:
        st.markdown("##### 👥 INA Égalité H/F")
        st.caption("Temps de parole par chaîne/station, 1995-2020.")
    with src3:
        st.markdown("##### 🧱 Pipeline médaillon")
        st.caption("Bronze → Silver → Gold validé pandera, 6 tables analytiques.")

    with st.expander("📚 Méthodologie complète"):
        st.markdown(
            """
            - **Pipeline médaillon** Bronze → Silver → Gold avec validation pandera
            - **Sources INA** : Baromètre JT (5 chaînes, 14 rubriques, ~3M sujets) + Égalité H/F (TV + radio)
            - **Analyses avancées** : détection de ruptures PELT (`ruptures`), clustering ACP + k-means (`scikit-learn`), corrélations Pearson
            - **Période** : 2000-2020 pour les JT, 1995-2020 pour la parité
            - **Limites** : la parité est mesurée en temps de parole, pas en nombre de personnes ; les rubriques INA sont déclaratives
            """
        )


# ─────────────────────────────────────────────
# PAGE 2 - AGENDA MEDIATIQUE
# ─────────────────────────────────────────────
elif page == "agenda":
    st.title("📊 Agenda médiatique", anchor=False)
    st.caption("Ce que racontent les JT français, comment ça évolue, et ce qui les fait basculer.")
    st.divider()

    ina = load("ina_jt", "silver")
    ina["annee"] = ina["annee"].astype(int)
    ina_f = ina[(ina["annee"] >= year_min) & (ina["annee"] <= year_max)]

    if ina_f.empty:
        empty_state("Aucune donnée sur la période sélectionnée. Élargis le filtre.")
        st.stop()

    t_vol, t_themes, t_season, t_events = st.tabs(
        ["Volumes", "Thèmes", "Saisonnalité", "Événements"]
    )

    # ─── Volumes
    with t_vol:
        c1, c2, c3 = st.columns(3, gap="medium")
        c1.metric("Sujets", f"{int(ina_f['nb_sujets'].sum()):,}".replace(",", " "))
        c2.metric("Heures", f"{ina_f['duree_totale'].sum() / 3600:,.0f}".replace(",", " "))
        c3.metric("Chaînes", ina_f["chaine"].nunique())
        styled_metrics()

        by_chaine = ina_f.groupby(["annee", "chaine"], as_index=False)["nb_sujets"].sum()
        with chart_container(by_chaine):
            fig = px.line(by_chaine, x="annee", y="nb_sujets", color="chaine", markers=True,
                          labels={"nb_sujets": "Sujets JT", "annee": ""})
            fig.update_layout(title="Sujets JT par chaîne", hovermode="x unified")
            fig.update_traces(hovertemplate="%{y:,.0f} sujets<extra>%{fullData.name}</extra>")
            st.plotly_chart(style_fig(fig, 440), width="stretch")

        explain(
            "Chaque ligne représente une chaîne de télévision. La hauteur indique "
            "<b>combien de reportages</b> elle a diffusés cette année-là dans ses journaux télévisés. "
            "Plus une ligne est haute, plus la chaîne a couvert d'événements."
        )

        st.info(
            "💡 **TF1 et France 2** dominent en volume. "
            "La baisse 2013-2014 reflète des réformes éditoriales sur le service public."
        )

    # ─── Thèmes
    with t_themes:
        rubriques = sorted(ina_f["rubrique"].unique())
        default = [r for r in ["Politique France", "International", "Santé", "Faits divers"] if r in rubriques]

        c1, c2 = st.columns([3, 1], gap="medium")
        with c1:
            sel = st.multiselect("Rubriques à afficher", rubriques, default=default)
        with c2:
            metric = st.radio("Mesure", ["Heures", "% du temps"], horizontal=True)

        if not sel:
            empty_state("Sélectionne au moins une rubrique pour afficher la courbe.")
        else:
            by_rub = ina_f[ina_f["rubrique"].isin(sel)].groupby(
                ["annee", "rubrique"], as_index=False
            )["duree_totale"].sum()

            if metric == "Heures":
                by_rub["valeur"] = by_rub["duree_totale"] / 3600
                ylabel, suffix = "Heures cumulées", " h"
            else:
                tot = ina_f.groupby("annee", as_index=False)["duree_totale"].sum().rename(
                    columns={"duree_totale": "tot"}
                )
                by_rub = by_rub.merge(tot, on="annee")
                by_rub["valeur"] = by_rub["duree_totale"] / by_rub["tot"] * 100
                ylabel, suffix = "% du temps JT", " %"

            with chart_container(by_rub):
                fig = px.area(by_rub, x="annee", y="valeur", color="rubrique",
                              labels={"valeur": ylabel, "annee": ""})
                fig.update_layout(title="Évolution thématique", hovermode="x unified")
                fig.update_traces(hovertemplate="%{y:.1f}" + suffix + "<extra>%{fullData.name}</extra>")

                # Annotations événements
                if year_min <= 2020 <= year_max and "Santé" in sel:
                    fig.add_vline(x=2020, line_dash="dot", line_color=DANGER, opacity=0.5,
                                  annotation_text="COVID", annotation_position="top")
                if "Politique France" in sel:
                    for y in [2002, 2007, 2012, 2017]:
                        if year_min <= y <= year_max:
                            fig.add_vline(x=y, line_dash="dot", line_color=MUTED, opacity=0.3)

                st.plotly_chart(style_fig(fig, 480), width="stretch")

            explain(
                "Chaque couleur représente un grand thème (politique, santé, sport...). "
                "L'épaisseur de la zone montre <b>la place qu'a pris ce thème</b> à la télé "
                "cette année-là. Bascule sur '% du temps' pour voir la part relative plutôt que l'absolu."
            )

    # ─── Saisonnalité
    with t_season:
        st.markdown("**Indice = part du mois ÷ part annuelle.** Au-dessus de 1, la rubrique est sur-représentée ce mois-là.")
        s = load("saisonnalite")
        pivot = s.pivot(index="rubrique", columns="mois", values="indice_saisonnalite")
        pivot.columns = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]

        sort_mode = st.radio("Ordre", ["Alphabétique", "Par mois de pic"], horizontal=True)
        if sort_mode == "Par mois de pic":
            peak_month = pivot.idxmax(axis=1).map({m: i for i, m in enumerate(pivot.columns)})
            pivot = pivot.loc[peak_month.sort_values().index]

        with chart_container(s):
            fig = px.imshow(pivot, aspect="auto", color_continuous_scale="RdBu_r",
                            color_continuous_midpoint=1.0,
                            labels={"x": "", "y": "", "color": "Indice"})
            fig.update_layout(title="Heatmap mensuelle de saisonnalité",
                              coloraxis_colorbar=dict(thickness=12, len=0.7))
            fig.update_traces(hovertemplate="%{y}<br>%{x}<br>Indice : %{z:.2f}<extra></extra>")
            st.plotly_chart(style_fig(fig, 620), width="stretch")

        explain(
            "Chaque case = un thème (en lignes) un mois donné (en colonnes). "
            "<b>Rouge</b> = on en parle beaucoup ce mois-là par rapport au reste de l'année. "
            "<b>Bleu</b> = on en parle peu. <b>Blanc</b> = pas de saisonnalité. "
            "Exemple : la ligne Sport est rouge vif en juillet-août, parce que c'est la période des JO et du Tour de France."
        )

        st.info(
            "💡 **Sport** explose en juillet-août (JO, Tour de France). "
            "**Politique** culmine en septembre (rentrée parlementaire). "
            "**Catastrophes** sur-représentées en hiver."
        )

    # ─── Événements
    with t_events:
        st.markdown("**Delta % de durée médiatique** pendant l'événement vs 30 jours avant.")
        ev = load("themes_evenements")

        c1, c2 = st.columns([2, 1])
        with c1:
            seuil = st.slider("Seuil de variation (%)", 10, 200, 30, 5)
        ev_sig = ev[ev["delta_pct"].notna() & (abs(ev["delta_pct"]) > seuil)].copy()

        if ev_sig.empty:
            empty_state("Aucun événement au-dessus de ce seuil. Abaisse-le.")
        else:
            with chart_container(ev_sig):
                fig = px.bar(ev_sig.sort_values("delta_pct"), y="evenement", x="delta_pct",
                             color="rubrique", orientation="h",
                             labels={"delta_pct": "Variation %", "evenement": ""})
                fig.update_layout(title=f"Variations > {seuil}% sur la couverture médiatique")
                fig.update_traces(hovertemplate="%{y}<br>%{x:+.0f}%<extra>%{fullData.name}</extra>")
                st.plotly_chart(style_fig(fig, max(420, 22 * len(ev_sig))), width="stretch")

            explain(
                "Chaque barre = un événement historique. La longueur indique <b>de combien le sujet "
                "a été plus traité</b> pendant l'événement, comparé au mois précédent. "
                "Exemple : pendant le 11 septembre 2001, le thème International a explosé de +400 %. "
                "Barres à droite = beaucoup plus parlé ; à gauche = beaucoup moins."
            )

            with st.expander("📋 Détail brut"):
                st.dataframe(
                    ev.sort_values("delta_pct", ascending=False)[
                        ["evenement", "date_debut", "rubrique", "duree_moy_avant", "duree_moy_pendant", "delta_pct"]
                    ],
                    hide_index=True, width="stretch",
                )


# ─────────────────────────────────────────────
# PAGE 3 - PARITE H/F
# ─────────────────────────────────────────────
elif page == "parite":
    st.title("👩 Représentation des femmes dans l'audiovisuel", anchor=False)
    st.caption("Temps de parole des femmes par chaîne, par média, en prime time. 1995-2020.")
    st.divider()

    # Sélecteur média unique au niveau page
    media = st.segmented_control(
        "Média", ["tv", "radio", "compare"], default="tv",
        format_func=lambda x: {"tv": "📺 TV", "radio": "📻 Radio", "compare": "⚖️ Comparer"}[x],
    ) or "tv"
    media_local = "tv" if media == "compare" else media
    label_media = {"tv": "📺 TV", "radio": "📻 Radio"}[media_local]

    t_evo, t_rank, t_prime = st.tabs(["Évolution", "Classement", "Prime time"])

    # ─── Évolution
    with t_evo:
        pu = load("parite_unifiee")
        pu = pu[(pu["year"] >= year_min) & (pu["year"] <= year_max)]
        pu["Média"] = pu["media_type"].map({"tv": "📺 TV", "radio": "📻 Radio"})

        if media == "compare":
            avg_both = pu.groupby(["year", "Média"], as_index=False)["women_expression_rate"].mean()
            with chart_container(avg_both):
                fig = px.line(avg_both, x="year", y="women_expression_rate", color="Média",
                              markers=True,
                              color_discrete_map={"📺 TV": PRIMARY, "📻 Radio": SECONDARY},
                              labels={"women_expression_rate": "% temps femmes (moyenne)", "year": ""})
                fig.add_hline(y=50, line_dash="dot", line_color=DANGER,
                              annotation_text="Parité 50 %", annotation_position="right")
                fig.update_layout(title="TV vs Radio : moyenne tous médias confondus",
                                  hovermode="x unified")
                fig.update_traces(hovertemplate="%{y:.1f} %<extra>%{fullData.name}</extra>")
                st.plotly_chart(style_fig(fig, 460), width="stretch")

            last = avg_both[avg_both["year"] == avg_both["year"].max()]
            if len(last) == 2:
                tv = last[last["Média"] == "📺 TV"]["women_expression_rate"].iloc[0]
                rd = last[last["Média"] == "📻 Radio"]["women_expression_rate"].iloc[0]
                c1, c2, c3 = st.columns(3, gap="medium")
                c1.metric("📺 TV", f"{tv:.1f} %")
                c2.metric("📻 Radio", f"{rd:.1f} %")
                c3.metric("Écart TV − Radio", f"{tv - rd:+.1f} pts", delta_color="off")
                styled_metrics()
            st.info("💡 La radio est historiquement en avance sur la parité ; la TV rattrape.")

        else:
            sub = pu[pu["media_type"] == media]
            if sub.empty:
                empty_state("Pas de données pour ce média sur cette période.")
            else:
                avg = sub.groupby("year", as_index=False)["women_expression_rate"].mean()
                c1, c2, c3 = st.columns(3, gap="medium")
                last_val = avg["women_expression_rate"].iloc[-1]
                first_val = avg["women_expression_rate"].iloc[0]
                c1.metric(f"Moyenne {label_media} en {int(avg['year'].max())}",
                          f"{last_val:.1f} %",
                          delta=f"{last_val - first_val:+.1f} pts vs {int(avg['year'].min())}")
                c2.metric("Écart à la parité (50 %)", f"{50 - last_val:+.1f} pts",
                          delta_color="inverse")
                c3.metric("Médias suivis", sub["media_name"].nunique())
                styled_metrics()

                top = (sub.groupby("media_name")["women_expression_rate"].mean()
                          .sort_values(ascending=False).head(15).index.tolist())
                sel = st.multiselect("Chaînes / stations", sorted(sub["media_name"].unique()),
                                     default=top[:6])

                if not sel:
                    empty_state("Sélectionne au moins un média pour afficher la courbe.")
                else:
                    plot_df = sub[sub["media_name"].isin(sel)]
                    with chart_container(plot_df):
                        fig = px.line(plot_df, x="year",
                                      y="women_expression_rate", color="media_name", markers=True,
                                      labels={"women_expression_rate": "% temps de parole femmes",
                                              "year": "", "media_name": ""})
                        fig.add_hline(y=50, line_dash="dot", line_color=DANGER,
                                      annotation_text="Parité 50 %", annotation_position="right")
                        fig.update_layout(title=f"Évolution {label_media}", hovermode="x unified")
                        fig.update_traces(hovertemplate="%{y:.1f} %<extra>%{fullData.name}</extra>")
                        st.plotly_chart(style_fig(fig, 460), width="stretch")
                    explain(
                        "Chaque ligne représente une chaîne ou une station. "
                        "L'axe vertical montre <b>le pourcentage du temps de parole occupé par des femmes</b>. "
                        "La ligne pointillée rouge à 50 % est l'objectif parité parfaite. "
                        "Plus une courbe est proche de cette ligne, plus la chaîne donne une place équilibrée aux femmes."
                    )

    # ─── Classement
    with t_rank:
        if media == "compare":
            st.caption("ℹ️ Le classement n'est dispo que par média. Affichage TV par défaut.")
        pr = load("parite_ranking")
        pr = pr[(pr["year"] >= year_min) & (pr["year"] <= year_max)]
        sub = pr[pr["media_type"] == media_local]

        if sub.empty:
            empty_state("Pas de données pour ce média sur cette période.")
        else:
            year_sel = st.slider("Année du classement",
                                 int(sub["year"].min()), int(sub["year"].max()),
                                 int(sub["year"].max()))
            snap = sub[sub["year"] == year_sel].sort_values("women_expression_rate")

            with chart_container(snap):
                fig = px.bar(snap, x="women_expression_rate", y="media_name", orientation="h",
                             color="women_expression_rate", color_continuous_scale="RdYlGn",
                             range_color=[20, 60],
                             labels={"women_expression_rate": "% temps femmes", "media_name": ""})
                fig.add_vline(x=50, line_dash="dot", line_color="#0f172a",
                              annotation_text="Parité", annotation_position="top")
                fig.update_layout(title=f"Classement {label_media} en {year_sel}",
                                  coloraxis_showscale=False)
                fig.update_traces(hovertemplate="%{y}<br>%{x:.1f} %<extra></extra>")
                st.plotly_chart(style_fig(fig, max(420, 28 * len(snap))), width="stretch")
            explain(
                "Classement de tous les médias par leur taux de parole féminine pour l'année choisie. "
                "Les barres <b>vertes</b> dépassent 50 % (parité atteinte ou dépassée), "
                "les <b>rouges</b> sont loin du compte. Trie automatique du moins paritaire au plus paritaire."
            )

            st.markdown("##### Trajectoire d'un média")
            name = st.selectbox("Média", sorted(sub["media_name"].unique()),
                                label_visibility="collapsed")
            traj = sub[sub["media_name"] == name]
            fig2 = px.line(traj, x="year", y="rang", markers=True,
                           color_discrete_sequence=[PRIMARY],
                           labels={"rang": "Rang (1 = meilleur)", "year": ""})
            fig2.update_yaxes(autorange="reversed")
            fig2.update_layout(title=f"Évolution du rang : {name}")
            fig2.update_traces(hovertemplate="%{x} : rang %{y}<extra></extra>")
            st.plotly_chart(style_fig(fig2, 360), width="stretch")

    # ─── Prime time
    with t_prime:
        st.markdown("**La parité diffère-t-elle aux heures de grande écoute ?**")
        pt = load("stats_prime_time")
        pt = pt[(pt["year"] >= year_min) & (pt["year"] <= year_max)]
        pt["pct_femmes"] = pt["female_speech_rate"] * 100
        pt["créneau"] = pt["is_prime_time"].map({True: "Prime time", False: "Hors prime time"})
        sub = pt[pt["media_type"] == media_local]
        grouped = sub.groupby(["year", "créneau"], as_index=False)["pct_femmes"].mean()

        if grouped.empty:
            empty_state("Pas de données prime time pour ce média sur cette période.")
        else:
            with chart_container(grouped):
                fig = px.line(grouped, x="year", y="pct_femmes", color="créneau", markers=True,
                              color_discrete_sequence=[PRIMARY, SECONDARY],
                              labels={"pct_femmes": "% femmes", "year": ""})
                fig.add_hline(y=50, line_dash="dot", line_color=DANGER,
                              annotation_text="Parité 50 %", annotation_position="right")
                fig.update_layout(title=f"Prime time vs hors prime time {label_media}",
                                  hovermode="x unified")
                fig.update_traces(hovertemplate="%{y:.1f} %<extra>%{fullData.name}</extra>")
                st.plotly_chart(style_fig(fig, 440), width="stretch")
            explain(
                "On compare les heures de grande écoute (prime time, ~20h-23h) au reste de la journée. "
                "Si la courbe Prime time est <b>en dessous</b> de l'autre, ça veut dire qu'il y a "
                "moins de femmes à l'antenne aux heures où le plus de gens regardent."
            )

            last = grouped[grouped["year"] == grouped["year"].max()]
            if len(last) == 2:
                p = last[last["créneau"] == "Prime time"]["pct_femmes"].iloc[0]
                h = last[last["créneau"] == "Hors prime time"]["pct_femmes"].iloc[0]
                c1, c2, c3 = st.columns(3, gap="medium")
                c1.metric("Prime time", f"{p:.1f} %")
                c2.metric("Hors prime time", f"{h:.1f} %")
                c3.metric("Écart", f"{p - h:+.1f} pts",
                          delta_color="normal" if p >= h else "inverse")
                styled_metrics()


# ─────────────────────────────────────────────
# PAGE 4 - THEMES × PARITE
# ─────────────────────────────────────────────
elif page == "cross":
    st.title("🔀 Thèmes JT × Parité H/F", anchor=False)
    st.caption("La composition thématique d'une chaîne est-elle liée à sa parité ? C'est le cœur du projet.")
    st.divider()

    df = load("tv_theme_parite")
    df = df[(df["annee"] >= year_min) & (df["annee"] <= year_max)]

    if df.empty:
        empty_state("Pas de données sur cette période (table dispo 2010-2019).")
        st.stop()

    part_cols = [c for c in df.columns if c.startswith("part_")]

    t_scatter, t_matrix = st.tabs(["Scatter par rubrique", "Matrice complète"])

    # ─── Scatter
    with t_scatter:
        rubs = [c.replace("part_", "") for c in part_cols]
        default_idx = rubs.index("international") if "international" in rubs else 0
        rubrique = st.selectbox("Rubrique à corréler avec la parité", rubs, index=default_idx)
        col = f"part_{rubrique}"

        with chart_container(df[[col, "women_expression_rate", "chaine", "annee", "nb_hours_analyzed"]]):
            fig = px.scatter(df, x=col, y="women_expression_rate",
                             color="chaine", size="nb_hours_analyzed",
                             hover_data=["annee"], trendline="ols",
                             labels={col: f"Part du temps consacré à {rubrique}",
                                     "women_expression_rate": "% femmes"})
            fig.update_layout(title=f"« {rubrique} » vs expression des femmes")
            st.plotly_chart(style_fig(fig, 500), width="stretch")
        explain(
            "Chaque <b>point</b> représente une chaîne sur une année. "
            "Plus on va à droite, plus la chaîne consacre du temps à la rubrique sélectionnée. "
            "Plus on monte, plus elle donne la parole aux femmes. "
            "La <b>ligne de tendance</b> montre s'il y a un lien : qui monte = lien positif, "
            "qui descend = les deux s'opposent."
        )

        corr_val = df[[col, "women_expression_rate"]].corr().iloc[0, 1]
        c1, c2, c3 = st.columns(3, gap="medium")
        c1.metric("Indicateur de lien", f"{corr_val:+.2f}")
        c2.metric("Observations", len(df))
        intensity = "forte" if abs(corr_val) >= 0.6 else ("notable" if abs(corr_val) >= 0.4 else "faible")
        c3.metric("Intensité", intensity)
        styled_metrics()

        st.info(
            f"💡 Indicateur de lien : **{corr_val:+.2f}** pour **{rubrique}**. "
            "Entre -1 (s'opposent totalement) et +1 (vont parfaitement ensemble). "
            "À partir de ±0,4 le lien est notable ; ±0,6 c'est fort ; 0 = sans rapport."
        )

    # ─── Matrice
    with t_matrix:
        focus = st.toggle("Focaliser sur la ligne « parité »", value=True)
        mat = df[part_cols + ["women_expression_rate"]].corr()
        mat.index = [c.replace("part_", "") for c in mat.index]
        mat.columns = [c.replace("part_", "") for c in mat.columns]

        if focus:
            row_df = mat.loc[["women_expression_rate"]].drop(columns=["women_expression_rate"])
            row_df = row_df.sort_values(by="women_expression_rate", axis=1)
            fig = px.imshow(row_df, color_continuous_scale="RdBu_r",
                            color_continuous_midpoint=0, aspect="auto", text_auto=".2f",
                            labels={"x": "Rubrique", "y": "", "color": "Pearson"})
            fig.update_layout(title="Corrélation de chaque rubrique avec la parité",
                              coloraxis_colorbar=dict(thickness=12, len=0.7),
                              yaxis=dict(showticklabels=False))
            st.plotly_chart(style_fig(fig, 220), width="stretch")
            explain(
                "Chaque case = un lien entre une rubrique et la parité H/F. "
                "<b>Rouge foncé</b> = quand la chaîne parle beaucoup de ce sujet, elle donne plus la parole aux femmes. "
                "<b>Bleu foncé</b> = c'est l'inverse, moins de femmes. "
                "<b>Pâle</b> = pas de lien. Les rubriques sont triées du plus négatif au plus positif."
            )
        else:
            fig = px.imshow(mat, color_continuous_scale="RdBu_r",
                            color_continuous_midpoint=0, aspect="auto", text_auto=".2f")
            fig.update_layout(title="Matrice complète de corrélation (Pearson)",
                              coloraxis_colorbar=dict(thickness=12, len=0.7))
            st.plotly_chart(style_fig(fig, 620), width="stretch")
            explain(
                "Tableau croisé : chaque ligne et chaque colonne est une rubrique (ou la parité). "
                "Une case rouge dit que <b>les deux vont ensemble</b> ; bleue qu'elles <b>s'opposent</b> ; "
                "blanche qu'<b>elles n'ont rien à voir</b>. La diagonale est toujours rouge vif (une rubrique est toujours liée à elle-même)."
            )

        if has("correlation_themes_parite"):
            st.markdown("##### Corrélations avec la parité (vert = significatif à 5 %)")
            sig = load("correlation_themes_parite", "analyses").sort_values("pearson_r")
            fig2 = px.bar(sig, x="pearson_r", y="rubrique", orientation="h",
                          color="significatif_5pct",
                          color_discrete_map={True: ACCENT, False: MUTED},
                          hover_data={"p_value": ":.3f", "significatif_5pct": False},
                          labels={"pearson_r": "Corrélation Pearson", "rubrique": ""})
            fig2.update_layout(showlegend=False)
            st.plotly_chart(style_fig(fig2, 420), width="stretch")


# ─────────────────────────────────────────────
# PAGE 5 - ANALYSES AVANCEES
# ─────────────────────────────────────────────
elif page == "advanced":
    st.title("🔬 Analyses avancées", anchor=False)
    st.caption("Au-delà du descriptif : clustering non supervisé et détection automatique de ruptures.")
    st.divider()

    t_clust, t_rupt = st.tabs(["Clustering chaînes", "Ruptures temporelles"])

    # ─── Clustering
    with t_clust:
        if not has("clusters_chaines"):
            st.warning("Lance `python -m analyses.clustering_chaines` pour générer les clusters.")
        else:
            cl = load("clusters_chaines", "analyses")
            cen = load("clusters_centroides", "analyses")
            cl["cluster"] = "Cluster " + cl["cluster"].astype(str)
            cl_f = cl[(cl["annee"] >= year_min) & (cl["annee"] <= year_max)]

            st.markdown("**ACP + k-means** sur les profils thématiques. Trois archétypes émergent.")

            chaines_dispo = sorted(cl_f["chaine"].unique())
            preferred = [c for c in ["TF1", "France 2", "Arte"] if c in chaines_dispo]
            default_chaines = preferred[:2] if preferred else chaines_dispo[:2]
            chaines_sel = st.multiselect(
                "Tracer la trajectoire temporelle de ces chaînes",
                chaines_dispo, default=default_chaines,
            )

            fig = px.scatter(cl_f, x="pc1", y="pc2", color="cluster",
                             hover_data=["chaine", "annee"], opacity=0.40,
                             labels={"pc1": "Composante principale 1",
                                     "pc2": "Composante principale 2"})
            fig.update_traces(marker=dict(size=11, line=dict(width=1, color="white")))

            # Trajectoires : labels seulement pour 1ère, dernière et années rondes (multiples de 5)
            traj_palette = ["#0f172a", "#ef4444", "#f59e0b", "#10b981", "#8b5cf6"]
            for i, ch in enumerate(chaines_sel):
                tr = cl_f[cl_f["chaine"] == ch].sort_values("annee").reset_index(drop=True)
                if tr.empty:
                    continue
                color = traj_palette[i % len(traj_palette)]
                # On garde le label seulement pour début, fin et années multiples de 5
                labels_show = [
                    str(int(y)) if (
                        idx == 0 or idx == len(tr) - 1 or int(y) % 5 == 0
                    ) else ""
                    for idx, y in enumerate(tr["annee"])
                ]
                fig.add_trace(go.Scatter(
                    x=tr["pc1"], y=tr["pc2"], mode="lines+markers+text",
                    text=labels_show, textposition="top center",
                    textfont=dict(size=10, color=color),
                    line=dict(color=color, width=2.5),
                    marker=dict(size=9, color=color, line=dict(width=2, color="white")),
                    name=f"→ {ch}", showlegend=True,
                    customdata=tr["annee"],
                    hovertemplate="<b>" + ch + "</b><br>%{customdata}<extra></extra>",
                ))

            fig.update_layout(title="Projection ACP : points = (chaîne, année), lignes = trajectoires")
            st.plotly_chart(style_fig(fig, 560), width="stretch")
            explain(
                "On a demandé à l'ordinateur de <b>regrouper les chaînes par profil thématique</b> "
                "(celles qui parlent des mêmes sujets se ressemblent). Trois familles ressortent, "
                "chacune en couleur différente. <b>Chaque point</b> = une chaîne sur une année. "
                "Deux points proches = profils similaires. Les <b>lignes</b> que tu choisis montrent comment "
                "une chaîne a évolué d'une année à l'autre."
            )

            st.markdown("##### Profil thématique de chaque cluster")
            st.caption("Part moyenne du temps consacré à chaque rubrique, par cluster.")
            part_cols = [c for c in cen.columns if c.startswith("part_")]
            long = cen.melt(id_vars=["cluster", "chaines_principales"],
                            value_vars=part_cols,
                            var_name="rubrique", value_name="part")
            long["rubrique"] = long["rubrique"].str.replace("part_", "")
            long["cluster"] = "Cluster " + long["cluster"].astype(str) + " (" + long["chaines_principales"] + ")"

            fig_c = px.bar(long, x="rubrique", y="part", color="cluster", barmode="group",
                           labels={"part": "Part du temps", "rubrique": ""})
            fig_c.update_layout(title="Part du temps par rubrique et par cluster",
                                yaxis_tickformat=".0%")
            fig_c.update_traces(hovertemplate="%{x}<br>%{y:.1%}<extra>%{fullData.name}</extra>")
            st.plotly_chart(style_fig(fig_c, 420), width="stretch")

    # ─── Ruptures
    with t_rupt:
        if not has("ruptures_points"):
            st.warning("Lance `python -m analyses.ruptures_detection` pour générer les ruptures.")
        else:
            rp = load("ruptures_points", "analyses")
            rp["date_rupture"] = pd.to_datetime(rp["date_rupture"])
            rp["annee"] = rp["date_rupture"].dt.year
            rp_f = rp[(rp["annee"] >= year_min) & (rp["annee"] <= year_max)]

            st.markdown(
                "**Algorithme PELT** (`ruptures`) sur les séries mensuelles. "
                "Lignes rouges = points de bascule détectés."
            )

            rubs = sorted(rp["rubrique"].unique())
            rub = st.selectbox("Rubrique", rubs)

            ina = load("ina_jt", "silver")
            ina["date"] = pd.to_datetime(ina["date"])
            ina["mois"] = ina["date"].dt.to_period("M").dt.to_timestamp()

            serie = (ina[ina["rubrique"] == rub]
                     .groupby("mois", as_index=False)["duree_totale"].sum())
            serie["heures"] = serie["duree_totale"] / 3600

            ruptures_rub = rp_f[rp_f["rubrique"] == rub]["date_rupture"].sort_values().tolist()

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=serie["mois"], y=serie["heures"], mode="lines", name=rub,
                line=dict(color=PRIMARY, width=2),
                fill="tozeroy", fillcolor="rgba(99,102,241,0.10)",
                hovertemplate="%{x|%b %Y}<br>%{y:.0f} h<extra></extra>",
            ))
            # Lignes verticales pour chaque rupture
            for d in ruptures_rub:
                fig.add_vline(x=d, line_dash="dash", line_color=DANGER, opacity=0.5)
            # Markers cliquables sur les ruptures
            if ruptures_rub:
                rupture_heights = []
                for d in ruptures_rub:
                    nearest = serie.iloc[(serie["mois"] - d).abs().argsort()[:1]]
                    rupture_heights.append(nearest["heures"].iloc[0] if not nearest.empty else 0)
                fig.add_trace(go.Scatter(
                    x=ruptures_rub, y=rupture_heights, mode="markers", name="Ruptures",
                    marker=dict(size=12, color=DANGER, symbol="diamond",
                                line=dict(width=2, color="white")),
                    hovertemplate="<b>Rupture détectée</b><br>%{x|%b %Y}<extra></extra>",
                ))
            fig.update_layout(title=f"Série mensuelle « {rub} » : {len(ruptures_rub)} ruptures",
                              yaxis_title="Heures par mois", xaxis_title="")
            with chart_container(serie[["mois", "heures"]]):
                st.plotly_chart(style_fig(fig, 480), width="stretch")
            explain(
                "La <b>courbe bleue</b> montre combien d'heures les JT ont consacré à ce sujet, mois par mois. "
                "Un algorithme détecte automatiquement les <b>moments où l'intensité change durablement</b> "
                "(plus de couverture, ou moins). Les <b>diamants rouges</b> sont ces points de bascule. "
                "Exemple : sur la Santé, on voit un saut brutal en mars 2020 avec l'arrivée du COVID."
            )

            with st.expander(f"📋 Dates des ruptures détectées ({rub})"):
                rdf = rp_f[rp_f["rubrique"] == rub][["date_rupture"]].copy()
                rdf["date_rupture"] = rdf["date_rupture"].dt.strftime("%Y-%m")
                st.dataframe(rdf, hide_index=True, width="stretch")


# ─────────────────────────────────────────────
# FOOTER STICKY
# ─────────────────────────────────────────────
with st.bottom:
    st.caption(
        "Projet M1 Big Data & IA — 2025-2026  ·  "
        "Données INA  ·  Construit avec Streamlit, Plotly, scikit-learn, ruptures, pandera"
    )
