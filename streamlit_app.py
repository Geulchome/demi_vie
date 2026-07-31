import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px


def simulate_population(cl, vd, c0, variability_pct, n_patients=50, seed=42):
    """1-compartment elimination: C(t)=C0*exp(-k t)

    Interindividual variability modeled as log-normal around individual k values.
    Variability_pct is the coefficient of variation (approx, for small values).
    """
    if cl <= 0 or vd <= 0:
        raise ValueError("Cl et Vd doivent être strictement positifs.")

    k = cl / vd  # 1/h
    if variability_pct < 0:
        raise ValueError("Variabilité doit être >= 0.")

    rng = np.random.default_rng(seed)

    # Convert CV-ish percentage to lognormal sigma; guard variability_pct=0
    cv = variability_pct / 100.0
    if cv == 0:
        k_i = np.full(n_patients, k)
    else:
        # For lognormal: CV^2 = exp(sigma^2) - 1
        sigma = np.sqrt(np.log(1 + cv**2))
        mu = np.log(k) - 0.5 * sigma**2
        k_i = rng.lognormal(mean=mu, sigma=sigma, size=n_patients)

    # Population distribution snapshot at time t_snapshot is handled outside.
    return k, k_i


def half_life_hours(k):
    return np.log(2) / k


def concentration_curve(t_hours, c0, k):
    return c0 * np.exp(-k * t_hours)


def main():
    st.set_page_config(page_title="Simulateur PK - Décroissance", layout="wide")

    with st.sidebar:
        st.title("Paramètres")

        cl = st.slider("Cl (L/h)", min_value=0.01, max_value=200.0, value=10.0, step=0.01)
        vd = st.slider("Vd (L)", min_value=0.01, max_value=500.0, value=50.0, step=0.01)

        c0 = st.slider("Dose initiale (mg/L) ou C0", min_value=0.0, max_value=500.0, value=100.0, step=1.0)

        variability_pct = st.slider(
            "Variabilité interindividuelle (%)",
            min_value=0.0,
            max_value=100.0,
            value=20.0,
            step=1.0,
        )

        n_patients = st.number_input("Nombre de patients fictifs", min_value=10, max_value=200, value=50, step=5)
        seed = st.number_input("Seed (reproductibilité)", min_value=0, max_value=10_000, value=42, step=1)

    error = None
    try:
        k, k_i = simulate_population(cl=cl, vd=vd, c0=c0, variability_pct=variability_pct, n_patients=int(n_patients), seed=int(seed))
        t_half = half_life_hours(k)

        # 5*t1/2 horizon
        t_max = 5.0 * t_half
        if not np.isfinite(t_max) or t_max <= 0:
            raise ValueError("Fenêtre de simulation invalide.")

        t = np.linspace(0, t_max, 300)
        c_ind = concentration_curve(t, c0, k)

        # population curves at each t for mono curve population summary (median)
        c_pop = c0 * np.exp(-np.outer(k_i, t))  # shape (n_patients, len(t))
        c_median = np.median(c_pop, axis=0)
        c_p10 = np.percentile(c_pop, 10, axis=0)
        c_p90 = np.percentile(c_pop, 90, axis=0)

        # Steps at 100%, 50%, 25%, ... (halve concentration)
        # concentration fraction after m half-lives: 1/2^m
        m_vals = np.arange(0, 6)  # up to ~1/32
        t_steps = m_vals * t_half
        c_steps = c0 / (2.0 ** m_vals)
        fractions = (c_steps / c0) * 100 if c0 > 0 else np.zeros_like(c_steps)

        t_snapshot = st.slider(
            "Instant t (pour la vue populationnelle)",
            min_value=0.0,
            max_value=float(t_max),
            value=float(min(t_half, t_max)),
            step=float(t_max / 200) if t_max > 0 else 0.01,
        )
        c_snapshot = c0 * np.exp(-k_i * t_snapshot)

    except Exception as e:
        error = str(e)

    if error:
        st.error(f"Erreur: {error}")
        return

    tab1, tab2 = st.tabs(["Vue Individuelle", "Vue Populationnelle"])

    with tab1:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Demi-vie", f"{t_half:.2f} heures")
            st.metric("Temps d'élimination totale", f"{t_max:.2f} heures")
            st.caption("Modèle 1-compartiment: C(t)=C0·e^(-k·t), k=Cl/Vd")

        with col2:
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(x=t, y=c_ind, mode="lines", name="Individuel (k=Cl/Vd)", line=dict(color="#1f77b4", width=3)))
            # mark half-lives
            for m in [1, 2, 3, 4, 5]:
                tt = m * t_half
                if tt <= t_max:
                    fig1.add_vline(x=tt, line_width=1, line_dash="dot", line_color="#2ca02c")
                    fig1.add_annotation(x=tt, y=float(np.interp(tt, t, c_ind)), text=f"{m}×t1/2", showarrow=False, yshift=10, font=dict(color="#2ca02c"))
            fig1.update_layout(
                template="plotly_white",
                margin=dict(l=10, r=10, t=30, b=10),
                xaxis_title="Temps (h)",
                yaxis_title="Concentration (mg/L)",
                legend=dict(orientation="h"),
                height=420,
            )
            st.plotly_chart(fig1, width="stretch")

        fig2 = go.Figure()
        fig2.add_trace(
            go.Bar(
                x=[f"{i}" for i in m_vals],
                y=fractions,
                marker_color=["#9467bd" if i % 2 == 0 else "#8c564b" for i in range(len(m_vals))],
            )
        )
        fig2.update_layout(
            template="plotly_white",
            margin=dict(l=10, r=10, t=30, b=10),
            xaxis_title="Nombre de demi-vies",
            yaxis_title="% restant",
            height=320,
        )
        # add labels 100%, 50%, 25%...
        st.subheader("Histogramme des fractions (100%, 50%, 25%…)")
        st.plotly_chart(fig2, width="stretch")

        st.caption("Les barres représentent C(t)/C0 pour t = n·t1/2.")

    with tab2:
        # Snapshot distribution by classes
        bins = st.slider("Nombre de classes (histogramme)", min_value=10, max_value=60, value=25, step=1)
        hist_data = np.array(c_snapshot)

        fig3 = px.histogram(
            hist_data,
            nbins=bins,
            labels={"value": "Concentration (mg/L)", "count": "Nombre de patients"},
            title=f"Répartition des concentrations à t = {t_snapshot:.2f} h",
        )
        fig3.update_traces(marker_color="#6f42c1", opacity=0.85)
        fig3.update_layout(template="plotly_white", height=360, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig3, width="stretch")

        # Box plot across patients at t_snapshot
        fig4 = go.Figure()
        fig4.add_trace(
            go.Box(
                y=hist_data,
                boxpoints="outliers",
                marker_color="#20c997",
                name="Concentration",
            )
        )
        fig4.update_layout(
            template="plotly_white",
            margin=dict(l=10, r=10, t=50, b=10),
            height=320,
            yaxis_title="Concentration (mg/L)",
            title=f"Boîte à moustaches (t = {t_snapshot:.2f} h)",
        )
        st.plotly_chart(fig4, width="stretch")

        st.caption("La boîte montre la médiane et les quartiles; les moustaches et points indiquent les extrêmes.")


if __name__ == "__main__":
    main()

