# analyse_emballage_app.py

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io



# Fonction pour définir la zone autorisée selon le poids
def zone_autorisee(poids):
    if poids <= 4:
        return (700, 1300, 400)
    elif 4 < poids <= 9:
        return (750, 1200, 300)
    elif 9 < poids <= 15:
        return (800, 1000, 300)
    else:
        return (0, 0, 0)


# Fonction principale d’analyse
def analyser_emballage(data):
    poids = data["poids_piece"]
    nb_lits = int(data["nb_lits"])
    pieces_par_lit = data["pieces_par_lit"]
    hmin = data["hauteur_sol_min"]
    hmax = data["hauteur_sol_max"]
    pmin = data["profondeur_min"]
    pmax = data["profondeur_max"]

    hmin_ok, hmax_ok, prof_ok = zone_autorisee(poids)

    fig, ax = plt.subplots(figsize=(7, 9))
    ax.set_title(f"Analyse ergonomique – {data['ref']}", fontsize=14)
    ax.set_xlim(0, max(pmax + 100, prof_ok + 100))
    ax.set_ylim(0, max(hmax + 100, hmax_ok + 100))

    # Zones
    rect_prise = patches.Rectangle((pmin, hmin), pmax - pmin, hmax - hmin,
                                   linewidth=2, edgecolor='red', facecolor='red', alpha=0.5, label='Zone de prise réelle')
    ax.add_patch(rect_prise)

    rect_zone_ok = patches.Rectangle((0, hmin_ok), prof_ok, hmax_ok - hmin_ok,
                                     linewidth=1, edgecolor='green', facecolor='green', alpha=0.3, label='Zone conforme')
    ax.add_patch(rect_zone_ok)

    # Calculs
    hauteur_totale = hmax - hmin
    hauteur_par_lit = hauteur_totale / nb_lits
    pieces_contraignantes = 0
    total_pieces = data.get("nb_total_pieces", pieces_par_lit * nb_lits)

    for i in range(nb_lits):
        lit_bas = hmin + i * hauteur_par_lit
        lit_haut = lit_bas + hauteur_par_lit
        conforme_hauteur = (lit_bas >= hmin_ok and lit_haut <= hmax_ok)

        if pmin < prof_ok < pmax:
            proportion_non_conforme_profondeur = (pmax - prof_ok) / (pmax - pmin)
        elif pmin >= prof_ok:
            proportion_non_conforme_profondeur = 1.0
        else:
            proportion_non_conforme_profondeur = 0.0

        if conforme_hauteur:
            pieces_contraignantes += pieces_par_lit * proportion_non_conforme_profondeur
        else:
            pieces_contraignantes += pieces_par_lit

    pourcentage_contraint = (pieces_contraignantes / total_pieces) * 100

    # Texte sur le graphique
    ax.text(0.05, 0.95,
            f"Total pièces : {total_pieces}\n"
            f"Contraignantes : {int(round(pieces_contraignantes))}\n"
            f"{pourcentage_contraint:.1f}% contraignantes",
            transform=ax.transAxes,
            fontsize=12,
            verticalalignment='top',
            bbox=dict(boxstyle="round", facecolor="white", edgecolor="gray", alpha=0.8)
    )

    ax.set_xlabel("Profondeur (mm)")
    ax.set_ylabel("Hauteur (mm)")
    ax.legend()
    ax.grid(True)
    plt.tight_layout()

    return fig, pourcentage_contraint, int(round(pieces_contraignantes)), total_pieces


# Interface Streamlit
st.set_page_config(page_title="Analyse Ergonomique d’un Emballage", layout="centered")
st.title("📦 Analyse Ergonomique d’un Emballage")

st.sidebar.title("📌 Informations générales")
departement = st.sidebar.selectbox("Département", ["Logistique", "Tôlerie", "Peinture", "Montage", "Qualité"])
uet = st.sidebar.text_input("UET")
poste = st.sidebar.text_input("Poste")
date = st.sidebar.date_input("Date de l’analyse")


with st.form("formulaire"):
    ref = st.text_input("Référence")
    poids_piece = st.number_input("Poids d’une pièce (kg)", min_value=0.0, step=0.1)
    pieces_par_lit = st.number_input("Nombre de pièces par lit", min_value=1, step=1)
    nb_total_pieces = st.number_input("Nombre total de pièces dans l’emballage", min_value=1, step=1)

    hauteur_sol_min = st.number_input("Hauteur de la pièce la plus basse (mm)", min_value=0)
    hauteur_sol_max = st.number_input("Hauteur de la pièce la plus haute (mm)", min_value=0)
    profondeur_min = st.number_input("Position de la pièce la plus proche (mm)", min_value=0)
    profondeur_max = st.number_input("Position de la pièce la plus éloignée (mm)", min_value=0)

    submit = st.form_submit_button("Analyser")

if submit:
    nb_lits = nb_total_pieces / pieces_par_lit

    data = {
        "ref": ref,
        "poids_piece": poids_piece,
        "nb_lits": nb_lits,
        "pieces_par_lit": pieces_par_lit,
        "nb_total_pieces": nb_total_pieces,
        "hauteur_sol_min": hauteur_sol_min,
        "hauteur_sol_max": hauteur_sol_max,
        "profondeur_min": profondeur_min,
        "profondeur_max": profondeur_max,
        "departement": departement,
        "uet": uet,
        "poste": poste,
        "date": str(date)
    }

    fig, pourcentage_contraint, nb_contraint, nb_total = analyser_emballage(data)
    st.pyplot(fig)

    # Résumé texte
    st.markdown(f"- 🔢 Nombre total de pièces : **{nb_total}**")
    st.markdown(f"- ❌ Pièces en prise contraignante : **{nb_contraint}**")
    st.markdown(f"- 📉 Pourcentage contraignant : **{pourcentage_contraint:.1f} %**")

    # Export PNG
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    st.download_button(
        label="📥 Télécharger le graphique",
        data=buf.getvalue(),
        file_name = f"{departement}_{uet}_{poste}_{date}.png".replace(" ", "_"),
        mime="image/png"
    )





