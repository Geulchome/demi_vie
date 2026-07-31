# 🎈 Blank app template

A simple Streamlit app template for you to modify!

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://blank-app-template.streamlit.app/)

### How to run it on your own machine

Prerequisite: install `uv` if you don't already have it.

```
$ curl -LsSf https://astral.sh/uv/install.sh | sh
```

1. Sync the dependencies

   ```
   $ uv sync
   ```

2. Run the app

   ```
   $ uv run streamlit run streamlit_app.py
   ```
# Guide d’utilisation — Simulateur de décroissance (PK) via Streamlit

## 1) Lancer l’application
Dans un terminal (au niveau du projet) :
```bash
streamlit run decroisance/app.py
```
Ensuite, ouvrez l’URL indiquée (souvent `http://localhost:8501`).

## 2) Comprendre l’interface
L’application comporte :
- **Panneau de configuration** (à gauche, via des sliders / champs numériques)
- **2 onglets** :
  1. **Vue Individuelle**
  2. **Vue Populationnelle**

Les graphiques se mettent à jour **automatiquement en temps réel** dès que vous modifiez un paramètre.

## 3) Paramètres à modifier (panneau de gauche)

### Molécule
1. **Cl (L/h)** : Clairance (doit être > 0)
   - Rôle : entre dans `k = Cl / Vd`
2. **Vd (L)** : Volume de distribution (doit être > 0)
   - Rôle : influence directement la constante d’élimination `k`

### Administration
3. **Dose initiale / C0 (mg/L)**
   - Interprétation dans l’app : concentration initiale **C0** au temps `t=0`
   - Si vous mettez `C0 = 0`, toutes les courbes seront à 0

### Population / Variabilité
4. **Variabilité interindividuelle (%)**
   - Rôle : simule une variabilité entre 50 patients fictifs
   - Une valeur plus élevée => une population plus étalée (plus de dispersion)

5. **Nombre de patients fictifs**
   - Nombre de trajectoires utilisées pour les distributions (par défaut 50)

6. **Seed**
   - Fixe le “hasard” pour que les résultats soient reproductibles

### Paramètre de temps pour la vue populationnelle
- **Instant t (pour la vue populationnelle)**
  - Sert aux Graphiques populationnels (histogramme + boxplot)

## 4) Résultats attendus (onglet par onglet)

## Onglet 1 — Vue Individuelle (Suivi Temporel)

### KPIs (indicateurs clés)
- **Demi-vie : X heures**
  - Calculée avec :
    - `k = Cl / Vd`
    - `t1/2 = ln(2) / k`
- **Temps d’élimination totale : Y heures**
  - Fenêtre de simulation : `5 × t1/2`

### Graphique 1 (Mono)
- **Courbe concentration vs temps** : `C(t) = C0 · exp(-k·t)`
- **Marqueurs/traits** aux multiples de la demi-vie (1×t1/2, 2×t1/2, …)

### Graphique 2 (Barres)
- **Histogramme des fractions** correspondant aux diminutions de concentration :
  - Après 0 demi-vies : 100%
  - Après 1 demi-vie : 50%
  - Après 2 demi-vies : 25%
  - etc.

## Onglet 2 — Vue Populationnelle (Variabilité)

À un instant **t** sélectionné, l’application génère une distribution des concentrations entre patients.

### Graphique 3 (Histogramme)
- **Répartition des concentrations** à l’instant `t`
- Vous pouvez régler le **nombre de classes** (bacs) avec le slider
- Attendu : si la variabilité interindividuelle (%) augmente, l’histogramme devient plus large.

### Graphique 4 (Boîte à moustaches)
- Donne la **médiane**, les **quartiles** et les **extrêmes** des concentrations à l’instant t.
- Attendu : plus la variabilité est forte, plus la boîte et les moustaches s’élargissent.

## 5) Sécurité / erreurs
L’application affiche un message d’erreur si :
- **Cl ≤ 0** ou **Vd ≤ 0**
- **Variabilité < 0**

## 6) Interprétation rapide (rappels)
- Plus **Cl** augmente => élimination plus rapide => demi-vie plus courte
- Plus **Vd** augmente => distribution plus grande => élimination plus lente => demi-vie plus longue

---
Fin du guide.
