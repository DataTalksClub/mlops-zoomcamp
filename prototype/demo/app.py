"""Démo Streamlit de l'agent Coûts.

Lancer depuis `prototype/` :
    pip install streamlit
    python -m streamlit run demo/app.py
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Permet les imports des modules du prototype quand Streamlit lance ce fichier.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st

from agents.cost import recommender
from agents.cost.settings import CostConfig
from demo.sim import Simulation

st.set_page_config(page_title="Agent Coûts - démo", layout="wide")
st.title("Agent Coûts - démo locale")
st.caption("Tarifs fictifs. Aucune base de données ni Docker : tout est simulé en mémoire.")

defaults = CostConfig()


# ---------- configuration (barre latérale) ----------
def build_sim() -> Simulation:
    cfg = CostConfig(
        cost_per_cpu_second=st.session_state.get(
            "cfg_rate", defaults.cost_per_cpu_second
        ),
        spot_discount=st.session_state.get("cfg_spot", defaults.spot_discount),
        monthly_budget=st.session_state.get("cfg_budget", defaults.monthly_budget),
        default_cpu_seconds_per_month_of_data=st.session_state.get(
            "cfg_default", defaults.default_cpu_seconds_per_month_of_data
        ),
    )
    return Simulation(cfg)


with st.sidebar:
    st.header("Configuration")
    st.number_input("Tarif par seconde de CPU", min_value=0.0,
                    value=defaults.cost_per_cpu_second,
                    step=0.001, format="%.4f", key="cfg_rate")
    st.slider("Remise du serveur spot", 0.0, 0.9,
              defaults.spot_discount, 0.05, key="cfg_spot")
    st.number_input("Budget mensuel", min_value=1.0,
                    value=defaults.monthly_budget, step=5.0, key="cfg_budget")
    st.number_input("CPU par défaut (s par mois de données)", min_value=1.0,
                    value=defaults.default_cpu_seconds_per_month_of_data,
                    step=50.0, key="cfg_default")
    if st.button("Appliquer et réinitialiser la démo"):
        st.session_state.sim = build_sim()
        st.rerun()

if "sim" not in st.session_state:
    st.session_state.sim = build_sim()
sim: Simulation = st.session_state.sim
cfg = sim.config

# ---------- budget ----------
total = sim.month_total()
c1, c2, c3 = st.columns(3)
c1.metric("Dépensé ce mois", f"{total:.2f}")
c2.metric("Budget", f"{cfg.monthly_budget:.2f}")
c3.metric("Reste", f"{cfg.monthly_budget - total:.2f}")
st.progress(sim.budget_ratio(), text=f"{sim.budget_ratio() * 100:.0f} % du budget")

tab_chat, tab_cost, tab_reco, tab_logs = st.tabs(
    ["Scénario 3 : demande de retrain", "Coûts par modèle", "Recommandations", "Événements et journal"]
)

# ---------- scénario 3 ----------
with tab_chat:
    st.subheader("Un data scientist demande un réentraînement")
    with st.form("retrain_form"):
        a, b, c = st.columns(3)
        model = a.text_input("Modèle", "taxi")
        months = b.number_input("Période (mois de données)", 1, 12, 3)
        who = c.text_input("Demandé par", "data scientist")
        submitted = st.form_submit_button("Demander le retrain")
    if submitted:
        sim.request_retrain(model, int(months), who)
        st.rerun()

    # dernière estimation
    estimates = [e for e in sim.bus.events if e["type"] == "cost_estimated"]
    if estimates:
        last = estimates[-1]["payload"]
        st.markdown("**Dernière estimation**")
        x, y, z = st.columns(3)
        x.metric("CPU estimé (s)", f"{last['estimated_cpu_seconds']:.0f}")
        y.metric("Serveur standard", f"{last['options']['standard']['cost']:.2f}")
        z.metric("Serveur spot", f"{last['options']['spot']['cost']:.2f}",
                 delta=f"-{last['options']['spot']['saving']:.2f}")

    if sim.pending:
        p = sim.pending
        st.error(
            f"Budget dépassé : dépensé {p['month_total']:.2f} + estimation "
            f"{p['options']['standard']['cost']:.2f} > budget {p['budget']:.2f}"
        )
        st.write(f"Demande de validation : réentraîner **{p['model']}** sur "
                 f"**{p['months']}** mois, demandé par **{p['requested_by']}**.")
        ok, no = st.columns(2)
        if ok.button("Approuver", type="primary"):
            sim.approve()
            st.rerun()
        if no.button("Refuser"):
            sim.refuse()
            st.rerun()
    elif estimates:
        st.success("Aucune validation en attente.")

    st.divider()
    st.markdown("**Remplir le budget pour la démo**")
    d, e, f = st.columns(3)
    t_model = d.text_input("Modèle", "taxi", key="t_model")
    t_cpu = e.number_input("CPU consommé (s)", 1.0, 100000.0, 500.0, step=100.0)
    t_months = f.number_input("Mois de données", 1, 12, 1, key="t_months")
    if st.button("Enregistrer un entraînement terminé"):
        sim.add_training(t_model, float(t_cpu), int(t_months))
        st.rerun()
    g, h = st.columns(2)
    api_cpu = g.number_input("CPU de l'API à ajouter (s)", 1.0, 100000.0, 60.0, step=10.0)
    if h.button("Facturer le CPU de l'API"):
        sim.advance_api_cpu(t_model, float(api_cpu))
        st.rerun()

# ---------- coût par modèle ----------
with tab_cost:
    by_model = sim.store.by_model(sim.month())
    if by_model:
        df = pd.DataFrame({"modèle": list(by_model), "coût": list(by_model.values())})
        st.bar_chart(df, x="modèle", y="coût")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Aucun coût enregistré pour l'instant.")

# ---------- recommandations ----------
with tab_reco:
    st.subheader("Taille de serveur")
    names = [s.name for s in cfg.sizes]
    r1, r2, r3 = st.columns(3)
    cur = r1.selectbox("Taille actuelle", names, index=len(names) - 1)
    used = r2.slider("vCPU réellement utilisés", 0.0, 4.0, 0.5, 0.1)
    r_model = r3.text_input("Modèle", "taxi", key="r_model")
    if st.button("Recommander une taille"):
        sim.agent.recommend_server_size(r_model, used, cur)
        st.rerun()

    st.subheader("Inactivité (scale-to-zero)")
    i1, i2 = st.columns(2)
    minutes = i1.number_input("Minutes depuis la dernière requête", 0, 1440, 45)
    hours = i2.number_input("Heures d'inactivité à chiffrer", 0.0, 24.0, 8.0, step=1.0)
    if st.button("Vérifier l'inactivité"):
        last_req = datetime.now() - timedelta(minutes=int(minutes))
        res = sim.agent.check_idle(r_model, last_req, cur, float(hours))
        if res is None:
            st.info(f"API active (moins de {cfg.idle_minutes:.0f} min) : rien à recommander.")
        else:
            st.rerun()

    recs = [e["payload"] for e in sim.bus.events if e["type"] == "cost_recommendation"]
    if recs:
        st.dataframe(pd.DataFrame(recs), use_container_width=True)

# ---------- journaux ----------
with tab_logs:
    left, right = st.columns(2)
    with left:
        st.markdown("**Événements publiés**")
        if sim.bus.events:
            st.dataframe(
                pd.DataFrame([{"type": e["type"], "détails": str(e["payload"])}
                              for e in sim.bus.events]),
                use_container_width=True)
        else:
            st.info("Aucun événement.")
    with right:
        st.markdown("**Journal d'actions**")
        if sim.log.rows:
            st.dataframe(
                pd.DataFrame([{"agent": r["agent"], "action": r["action"],
                               "détails": str(r["details"])} for r in sim.log.rows]),
                use_container_width=True)
        else:
            st.info("Journal vide.")
