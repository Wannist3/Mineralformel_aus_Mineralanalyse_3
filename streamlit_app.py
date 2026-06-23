import streamlit as st

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
import streamlit as st
import pandas as pd
import numpy as np
import re

# Titel der App
st.title("Mineralformel-Rechner")
st.markdown("""
Diese App berechnet Mineralformeln aus chemischen Analysen (Gewichtsprozent der Oxide).
Wählen Sie die Mineralgruppe und geben Sie die chemische Zusammensetzung ein.
""")

# Seitenleiste für Mineralgruppen-Auswahl
mineral_group = st.sidebar.selectbox(
    "Mineralgruppe auswählen",
    ["Olivin", "Pyroxen", "Granat", "Amphibol", "Glimmer", "Feldspat", "Spinell", "Epidot", "Allgemein"]
)

# Erklärungen für jede Mineralgruppe
if mineral_group == "Olivin":
    st.sidebar.markdown("""
    **Olivin-Normalisierung:**
    - Basis: 4 Sauerstoffatome
    - Kationen: Si, Mg, Fe, Mn, Ca, Ni
    """)
elif mineral_group == "Pyroxen":
    st.sidebar.markdown("""
    **Pyroxen-Normalisierung:**
    - Basis: 6 Sauerstoffatome
    - Kationen: Si, Al, Ti, Fe³⁺, Fe²⁺, Mg, Mn, Ca, Na, Cr
    - Option für Ca-Na-Pyroxene verfügbar
    """)
elif mineral_group == "Granat":
    st.sidebar.markdown("""
    **Granat-Normalisierung:**
    - Basis: 12 Sauerstoffatome
    - Kationen: Si, Al, Fe³⁺, Cr³⁺, Fe²⁺, Mg, Mn, Ca
    """)
elif mineral_group == "Amphibol":
    st.sidebar.markdown("""
    **Amphibol-Normalisierung:**
    - Basis: 23 Sauerstoffatome
    - Kationen: Si, Al, Ti, Fe³⁺, Fe²⁺, Mg, Mn, Ca, Na, K
    - Berücksichtigung von OH⁻-Gruppen möglich
    """)
elif mineral_group == "Glimmer":
    st.sidebar.markdown("""
    **Glimmer-Normalisierung:**
    - Basis: 11 Sauerstoffatome + 2(OH,F,Cl)
    - Kationen: Si, Al, Ti, Fe³⁺, Fe²⁺, Mg, Mn, Li, Na, K
    """)
elif mineral_group == "Feldspat":
    st.sidebar.markdown("""
    **Feldspat-Normalisierung:**
    - Basis: 8 Sauerstoffatome
    - Kationen: Si, Al, Fe³⁺, Ca, Na, K
    """)
elif mineral_group == "Spinell":
    st.sidebar.markdown("""
    **Spinell-Normalisierung:**
    - Basis: 4 Sauerstoffatome
    - Kationen: Al, Cr, Fe³⁺, Fe²⁺, Mg, Mn, Zn, Ti
    """)
elif mineral_group == "Epidot":
    st.sidebar.markdown("""
    **Epidot-Normalisierung:**
    - Basis: 12.5 Sauerstoffatome
    - Kationen: Si, Al, Fe³⁺, Mn³⁺, Ca, Ce, La, Y
    """)
else:  # Allgemein
    st.sidebar.markdown("""
    **Allgemeine Normalisierung:**
    Basis-Sauerstoffatome können frei gewählt werden.
    """)

# Default-Oxide basierend auf Mineralgruppe
default_oxides = {
    "Olivin": ["SiO2", "MgO", "FeO", "MnO", "CaO", "NiO"],
    "Pyroxen": ["SiO2", "Al2O3", "TiO2", "Fe2O3", "FeO", "MgO", "MnO", "CaO", "Na2O", "Cr2O3"],
    "Granat": ["SiO2", "Al2O3", "Fe2O3", "Cr2O3", "FeO", "MgO", "MnO", "CaO"],
    "Amphibol": ["SiO2", "Al2O3", "TiO2", "Fe2O3", "FeO", "MgO", "MnO", "CaO", "Na2O", "K2O", "H2O"],
    "Glimmer": ["SiO2", "Al2O3", "TiO2", "Fe2O3", "FeO", "MgO", "MnO", "Li2O", "Na2O", "K2O", "F", "Cl"],
    "Feldspat": ["SiO2", "Al2O3", "Fe2O3", "CaO", "Na2O", "K2O"],
    "Spinell": ["Al2O3", "Cr2O3", "Fe2O3", "FeO", "MgO", "MnO", "ZnO", "TiO2"],
    "Epidot": ["SiO2", "Al2O3", "Fe2O3", "Mn2O3", "CaO", "Ce2O3", "La2O3", "Y2O3"],
    "Allgemein": ["SiO2", "Al2O3", "Fe2O3", "FeO", "MgO", "CaO", "Na2O", "K2O", "TiO2", "MnO", "Cr2O3", "NiO", "ZnO"]
}

# Eingabefelder für Oxidgehalte
st.subheader("Geben Sie die chemische Zusammensetzung ein (Gewichts%)")

# Dynamische Erstellung der Eingabefelder
with st.expander("Eingabefelder"):
    oxides = default_oxides.get(mineral_group, default_oxides["Allgemein"])
    oxide_values = {}

    for oxide in oxides:
        key = f"input_{oxide}"
        value = st.number_input(
            f"{oxide} (Gew.%)",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=0.01,
            key=key
        )
        oxide_values[oxide] = value

# Zusätzliche Optionen für bestimmte Mineralgruppen
if mineral_group == "Pyroxen":
    pyroxen_type = st.selectbox("Pyroxen-Typ", ["Quadrilaterale Pyroxene", "Ca-Na-Pyroxene"])
else:
    pyroxen_type = None

if mineral_group == "Allgemein":
    basis_oxygen = st.number_input("Basis-Sauerstoffatome", min_value=1, value=3, step=1)
else:
    # Standard-Basis-Sauerstoffatome
    basis_oxygen_map = {
        "Olivin": 4,
        "Pyroxen": 6,
        "Granat": 12,
        "Amphibol": 23,
        "Glimmer": 11,
        "Feldspat": 8,
        "Spinell": 4,
        "Epidot": 12.5
    }
    basis_oxygen = basis_oxygen_map.get(mineral_group, 3)

# Funktion zur Berechnung der Mineralformel
def calculate_mineral_formula(oxide_values, basis_oxygen, mineral_group, pyroxen_type=None):
    # Molare Massen der Oxide
    molar_masses = {
        "SiO2": 60.084,
        "Al2O3": 101.96,
        "Fe2O3": 159.69,
        "FeO": 71.844,
        "MgO": 40.304,
        "CaO": 56.077,
        "Na2O": 61.979,
        "K2O": 94.196,
        "TiO2": 79.866,
        "MnO": 70.937,
        "Cr2O3": 151.99,
        "NiO": 74.693,
        "ZnO": 81.38,
        "Li2O": 29.88,
        "H2O": 18.015,
        "F": 18.998,
        "Cl": 35.45,
        "Ce2O3": 328.23,
        "La2O3": 325.81,
        "Y2O3": 225.81,
        "Mn2O3": 157.87
    }

    # Elemente pro Oxid
    elements_per_oxide = {
        "SiO2": {"Si": 1, "O": 2},
        "Al2O3": {"Al": 2, "O": 3},
        "Fe2O3": {"Fe": 2, "O": 3},
        "FeO": {"Fe": 1, "O": 1},
        "MgO": {"Mg": 1, "O": 1},
        "CaO": {"Ca": 1, "O": 1},
        "Na2O": {"Na": 2, "O": 1},
        "K2O": {"K": 2, "O": 1},
        "TiO2": {"Ti": 1, "O": 2},
        "MnO": {"Mn": 1, "O": 1},
        "Cr2O3": {"Cr": 2, "O": 3},
        "NiO": {"Ni": 1, "O": 1},
        "ZnO": {"Zn": 1, "O": 1},
        "Li2O": {"Li": 2, "O": 1},
        "H2O": {"H": 2, "O": 1},
        "F": {"F": 1},
        "Cl": {"Cl": 1},
        "Ce2O3": {"Ce": 2, "O": 3},
        "La2O3": {"La": 2, "O": 3},
        "Y2O3": {"Y": 2, "O": 3},
        "Mn2O3": {"Mn": 2, "O": 3}
    }

    # Berechnung der Molmengen
    mol_numbers = {}
    total_oxygen = 0
    element_moles = {}

    for oxide, weight in oxide_values.items():
        if weight > 0 and oxide in molar_masses:
            mol_number = weight / molar_masses[oxide]
            mol_numbers[oxide] = mol_number

            # Elemente hinzufügen
            for element, count in elements_per_oxide[oxide].items():
                if element == "O":
                    total_oxygen += count * mol_number
                else:
                    if element in element_moles:
                        element_moles[element] += count * mol_number
                    else:
                        element_moles[element] = count * mol_number

    # Normalisierung auf Basis-Sauerstoffatome
    if total_oxygen == 0:
        return None

    normalization_factor = basis_oxygen / total_oxygen

    # Berechnung der Kationen pro Formel-Einheit
    cations = {}
    for element, moles in element_moles.items():
        cations[element] = moles * normalization_factor

    # Spezielle Behandlung für bestimmte Mineralgruppen
    if mineral_group == "Pyroxen" and pyroxen_type == "Ca-Na-Pyroxene":
        # Berücksichtigung von Fe³⁺/Fe²⁺-Verhältnis für Ca-Na-Pyroxene
        if "Fe" in cations:
            # Annahme: 50% des Eisens ist Fe³⁺ (kann angepasst werden)
            total_fe = cations["Fe"]
            fe3 = total_fe * 0.5
            fe2 = total_fe * 0.5
            del cations["Fe"]
            cations["Fe3+"] = fe3
            cations["Fe2+"] = fe2

    # Umwandlung in DataFrame für bessere Darstellung
    formula_df = pd.DataFrame.from_dict(cations, orient='index', columns=['Kationen'])

    # Berechnung der Summe der Kationen
    if mineral_group in ["Olivin", "Pyroxen", "Granat", "Spinell"]:
        cation_sum_key = "Tetraeder+Oktaeder"
        if mineral_group == "Pyroxen":
            if "Si" in cations and "Al" in cations:
                if (cations["Si"] + cations["Al"]) <= 2.0:
                    tetrahedral = cations["Si"] + cations["Al"]
                else:
                    tetrahedral = 2.0
                    # Überschüssiges Al kommt zu den oktaedrischen Positionen
                    if "Al" in cations:
                        cations["Al"] = max(0, cations["Al"] - (2.0 - cations["Si"]))
                    if "Si" in cations:
                        cations["Si"] = 2.0
                    # Neu berechnen
                    formula_df = pd.DataFrame.from_dict(cations, orient='index', columns=['Kationen'])
    else:
        cation_sum_key = "Gesamtkationen"

    total_cations = sum(cations.values())

    # Ergebnis zurückgeben
    return {
        "formula_df": formula_df,
        "basis_oxygen": basis_oxygen,
        "total_cations": total_cations,
        "normalization_factor": normalization_factor,
        "cation_sum_key": cation_sum_key
    }

# Berechnung durchführen
if st.button("Mineralformel berechnen"):
    # Summe der Oxide überprüfen
    total_weight = sum(oxide_values.values())

    if total_weight > 101.0:
        st.warning("Achtung: Die Summe der Oxide überschreitet 101%. Bitte überprüfen Sie die Eingaben.")
    elif total_weight < 98.0:
        st.warning("Achtung: Die Summe der Oxide liegt unter 98%. Möglicherweise fehlen Oxide in der Analyse.")

    # Berechnung starten
    result = calculate_mineral_formula(oxide_values, basis_oxygen, mineral_group, pyroxen_type)

    if result:
        formula_df = result["formula_df"]
        basis_oxygen = result["basis_oxygen"]
        total_cations = result["total_cations"]
        normalization_factor = result["normalization_factor"]
        cation_sum_key = result["cation_sum_key"]

        st.subheader("Ergebnis")

        # Anzeige der berechneten Formel
        st.markdown(f"**Mineralformel (bezogen auf {basis_oxygen} O-Atome):**")
        st.dataframe(formula_df.style.format("{:.4f}"))

        # Summen anzeigen
        st.markdown(f"**{cation_sum_key}-Summe:** {total_cations:.4f}")
        st.markdown(f"**Normalisierungsfaktor:** {normalization_factor:.4f}")

        # Spezifische Mineralgruppen-Hinweise
        if mineral_group == "Olivin":
            if "Si" in formula_df.index:
                si = formula_df.loc["Si", "Kationen"]
                st.write(f"**Si-Position:** {si:.4f} von 1.0000")
            else:
                st.write("Kein Si in der Analyse - möglicherweise kein Olivin")

        elif mineral_group == "Pyroxen":
            if "Si" in formula_df.index and "Al" in formula_df.index:
                si_al_sum = formula_df.loc["Si", "Kationen"] + formula_df.loc["Al", "Kationen"]
                if si_al_sum <= 2.0:
                    st.write("Tetraederpositionen sind vollständig besetzt")
                else:
                    st.write(f"Achtung: Überschuss in Tetraederpositionen ({si_al_sum:.4f}/2.0000)")

        # Option zur Anzeige der kompletten Berechnung
        with st.expander("Details der Berechnung anzeigen"):
            st.markdown("### Molmengen der Oxide:")
            mol_df = pd.DataFrame.from_dict({k: v for k, v in mol_numbers.items() if v > 0},
                                          orient='index', columns=['Molmenge'])
            st.dataframe(mol_df.style.format("{:.6f}"))

            st.markdown("### Sauerstoffbeitrag pro Oxid:")
            oxygen_contribution = {}
            for oxide, mol_number in mol_numbers.items():
                if oxide in elements_per_oxide and "O" in elements_per_oxide[oxide]:
                    oxygen_contribution[oxide] = mol_number * elements_per_oxide[oxide]["O"]

            oxygen_df = pd.DataFrame.from_dict(oxygen_contribution, orient='index', columns=['O-Atome'])
            st.dataframe(oxygen_df.style.format("{:.6f}"))

            st.markdown(f"### Summe Sauerstoffatome: {total_oxygen:.6f}")
            st.markdown(f"### Normalisierungsfaktor: {normalization_factor:.6f}")
    else:
        st.error("Die Berechnung ist fehlgeschlagen. Bitte überprüfen Sie die Eingaben.")

# Beispiel-Datensätze
st.sidebar.header("Beispieldatensätze")
example_data = {
    "Olivin": {"SiO2": 40.0, "MgO": 49.0, "FeO": 10.0, "MnO": 0.1, "CaO": 0.1, "NiO": 0.3},
    "Diopsid (Pyroxen)": {"SiO2": 55.0, "Al2O3": 0.5, "MgO": 18.0, "CaO": 25.0, "FeO": 1.5},
    "Almandin (Granat)": {"SiO2": 38.0, "Al2O3": 20.0, "FeO": 30.0, "MgO": 5.0, "MnO": 2.0, "CaO": 5.0},
    "Hornblende (Amphibol)": {
        "SiO2": 44.0, "Al2O3": 12.0, "FeO": 12.0, "MgO": 13.0,
        "CaO": 11.5, "Na2O": 1.5, "K2O": 0.5, "TiO2": 1.5
    },
    "Biotit (Glimmer)": {
        "SiO2": 36.0, "Al2O3": 18.0, "FeO": 15.0, "MgO": 14.0,
        "K2O": 9.0, "TiO2": 3.0, "H2O": 4.0
    }
}

if st.sidebar.button("Beispieldaten laden"):
    example = example_data.get(mineral_group, example_data["Olivin"])
    for oxide, value in example.items():
        if oxide in oxides:
            st.session_state[f"input_{oxide}"] = value
    st.experimental_rerun()

# Anleitung
with st.expander("Anleitung"):
    st.markdown("""
    **Schritt-für-Schritt Anleitung:**

    1. Wählen Sie die Mineralgruppe aus der Seitenleiste.
    2. Geben Sie die Gewichtsprozente der Oxide ein.
       - Nicht vorhandene Oxide auf 0 setzen.
    3. Klicken Sie auf "Mineralformel berechnen".
    4. Die berechnete Mineralformel wird mit Kationen pro Formel-Einheit angezeigt.
    5. Die Summe der Kationen wird basierend auf der Mineralgruppe angezeigt.
    6. Optional können Sie die Details der Berechnung einsehen.

    **Hinweise:**
    - Die Analyse sollte möglichst vollständig sein (Summe ~100%).
    - Für Pyroxene können Sie den Typ auswählen.
    - Für allgemeine Mineralien können Sie die Basis-Sauerstoffatome selbst festlegen.
    - Die Berechnung berücksichtigt nicht alle möglichen Ladungsausgleiche.
    """)