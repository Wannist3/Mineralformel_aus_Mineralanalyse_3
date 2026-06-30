import streamlit as st
import pandas as pd
import numpy as np

from mineral_formula import calculate_mineral_formula, format_mineral_formula

# Titel der App
st.title("Mineralformel-Rechner")
st.markdown(
    """
Diese App berechnet Mineralformeln aus chemischen Analysen (Gewichtsprozent der Oxide).
Wählen Sie eine Mineralgruppe aus und klicken Sie auf **"Beispieldaten anzeigen und berechnen"**, um typische Werte zu laden.
    """
)

# --- Definitionen ---
molar_masses = {
    "SiO2": 60.084, "Al2O3": 101.96, "Fe2O3": 159.69, "FeO": 71.844,
    "MgO": 40.304, "CaO": 56.077, "Na2O": 61.979, "K2O": 94.196,
    "TiO2": 79.866, "MnO": 70.937, "Cr2O3": 151.99, "NiO": 74.693,
    "ZnO": 81.38, "Li2O": 29.88, "H2O": 18.015, "F": 18.998,
    "Cl": 35.45, "Ce2O3": 328.23, "La2O3": 325.81, "Y2O3": 225.81,
    "Mn2O3": 157.87
}

elements_per_oxide = {
    "SiO2": {"Si": 1, "O": 2}, "Al2O3": {"Al": 2, "O": 3},
    "Fe2O3": {"Fe3+": 2, "O": 3},
    "FeO": {"Fe2+": 1, "O": 1},
    "MgO": {"Mg": 1, "O": 1}, "CaO": {"Ca": 1, "O": 1},
    "Na2O": {"Na": 2, "O": 1}, "K2O": {"K": 2, "O": 1},
    "TiO2": {"Ti": 1, "O": 2}, "MnO": {"Mn": 1, "O": 1},
    "Cr2O3": {"Cr": 2, "O": 3}, "NiO": {"Ni": 1, "O": 1},
    "ZnO": {"Zn": 1, "O": 1}, "Li2O": {"Li": 2, "O": 1},
    "H2O": {"H": 2, "O": 1}, "F": {"F": 1}, "Cl": {"Cl": 1},
    "Ce2O3": {"Ce": 2, "O": 3}, "La2O3": {"La": 2, "O": 3},
    "Y2O3": {"Y": 2, "O": 3},
    "Mn2O3": {"Mn": 2, "O": 3}
}

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

basis_oxygen_map = {
    "Olivin": 4, "Pyroxen": 6, "Granat": 12, "Amphibol": 23,
    "Glimmer": 11, "Feldspat": 8, "Spinell": 4, "Epidot": 12.5
}

# Mineralgruppenspezifische Element-Reihenfolgen (korrigiert)
element_order = {
    "Olivin": ["Si", "Mg", "Fe2+", "Mn", "Ca", "Ni"],
    "Pyroxen": ["Si", "Al", "Ti", "Fe3+", "Cr", "Fe2+", "Mg", "Mn", "Ca", "Na"],
    "Granat": ["Si", "Al", "Fe3+", "Cr", "Fe2+", "Mg", "Mn", "Ca"],
    "Amphibol": ["Si", "Al", "Ti", "Fe3+", "Cr", "Fe2+", "Mg", "Mn", "Ca", "Na", "K"],
    "Glimmer": ["Si", "Al", "Ti", "Fe3+", "Fe2+", "Mg", "Mn", "Li", "Na", "K"],
    "Feldspat": ["Si", "Al", "Fe3+", "Ca", "Na", "K"],
    "Spinell": ["Al", "Fe3+", "Cr", "Fe2+", "Mg", "Mn", "Zn", "Ti"],
    "Epidot": ["Si", "Al", "Fe3+", "Mn", "Ca", "Ce", "La", "Y"],
    "default": ["Si", "Al", "Ti", "Fe3+", "Cr", "Fe2+", "Mg", "Mn", "Ca", "Na", "K", "Ni", "Zn", "Li"]
}

# Beispiel-Datensätze
example_data = {
    "Olivin": {"SiO2": 40.0, "MgO": 49.0, "FeO": 10.0, "MnO": 0.1, "CaO": 0.1, "NiO": 0.3},
    "Pyroxen": {"SiO2": 55.0, "Al2O3": 0.5, "TiO2": 0.1, "Fe2O3": 0.5, "FeO": 1.5, "MgO": 18.0, "MnO": 0.1, "CaO": 25.0, "Na2O": 0.2, "Cr2O3": 0.1},
    "Granat": {"SiO2": 38.0, "Al2O3": 20.0, "Fe2O3": 1.5, "Cr2O3": 0.1, "FeO": 30.0, "MgO": 5.0, "MnO": 2.0, "CaO": 5.0},
    "Amphibol": {"SiO2": 44.0, "Al2O3": 12.0, "TiO2": 1.5, "Fe2O3": 2.5, "FeO": 12.0, "MgO": 13.0, "MnO": 0.2, "CaO": 11.5, "Na2O": 1.5, "K2O": 0.5, "H2O": 1.5},
    "Glimmer": {"SiO2": 36.0, "Al2O3": 18.0, "TiO2": 3.0, "Fe2O3": 2.0, "FeO": 15.0, "MgO": 14.0, "MnO": 0.1, "Li2O": 0.5, "Na2O": 1.0, "K2O": 9.0, "F": 1.0, "Cl": 0.1},
    "Feldspat": {"SiO2": 65.0, "Al2O3": 20.0, "Fe2O3": 0.5, "CaO": 2.0, "Na2O": 10.0, "K2O": 2.0},
    "Spinell": {"Al2O3": 60.0, "Cr2O3": 10.0, "Fe2O3": 5.0, "FeO": 5.0, "MgO": 18.0, "MnO": 0.5, "ZnO": 1.0, "TiO2": 0.5},
    "Epidot": {"SiO2": 38.0, "Al2O3": 25.0, "Fe2O3": 10.0, "Mn2O3": 0.1, "CaO": 23.0, "Ce2O3": 0.5, "La2O3": 0.2, "Y2O3": 0.1},
    "Allgemein": {"SiO2": 50.0, "Al2O3": 20.0, "Fe2O3": 5.0, "FeO": 5.0, "MgO": 10.0, "CaO": 5.0, "Na2O": 3.0, "K2O": 2.0}
}

# --- Streamlit UI ---
def normalize_oxide_name(value):
    return str(value).strip().lower().replace(" ", "").replace("_", "").replace("-", "")


def parse_uploaded_oxide_data(uploaded_file, mineral_group):
    if uploaded_file is None:
        return None

    if not uploaded_file.name.lower().endswith(".csv"):
        st.error("❌ Bitte eine CSV-Datei hochladen.")
        return None

    try:
        df = pd.read_csv(uploaded_file)
    except Exception as exc:
        st.error(f"❌ Die Datei konnte nicht gelesen werden: {exc}")
        return None

    if df.empty:
        st.error("❌ Die hochgeladene Datei ist leer.")
        return None

    expected_oxides = set(default_oxides[mineral_group]) | set(molar_masses.keys())
    normalized_oxide_map = {normalize_oxide_name(oxide): oxide for oxide in expected_oxides}

    if df.shape[0] >= 1:
        first_row = df.iloc[0]
        parsed_values = {}
        for column in df.columns:
            normalized_name = normalize_oxide_name(column)
            if normalized_name in normalized_oxide_map and pd.api.types.is_numeric_dtype(df[column]):
                parsed_values[normalized_oxide_map[normalized_name]] = float(first_row[column])
        if parsed_values:
            return parsed_values

    if df.shape[1] >= 2:
        for oxide_column in df.columns:
            if normalize_oxide_name(oxide_column) in {"oxide", "oxides", "compound", "component", "komponente"}:
                for value_column in df.columns:
                    if value_column != oxide_column and pd.api.types.is_numeric_dtype(df[value_column]):
                        parsed_values = {}
                        for _, row in df.iterrows():
                            oxide_name = str(row[oxide_column]).strip()
                            normalized_name = normalize_oxide_name(oxide_name)
                            if normalized_name in normalized_oxide_map:
                                parsed_values[normalized_oxide_map[normalized_name]] = float(row[value_column])
                        if parsed_values:
                            return parsed_values

    st.error("❌ Die CSV-Datei konnte nicht erkannt werden. Bitte eine Datei mit Oxidspalten oder zwei Spalten (Oxid + Wert) verwenden.")
    return None


mineral_group = st.sidebar.selectbox(
    "Mineralgruppe auswählen",
    list(default_oxides.keys())
)

# Session State initialisieren
if 'oxide_values' not in st.session_state or not isinstance(st.session_state.oxide_values, dict):
    st.session_state.oxide_values = {}
for oxide in default_oxides[mineral_group]:
    st.session_state.oxide_values.setdefault(oxide, 0.0)
if 'calculate' not in st.session_state:
    st.session_state.calculate = False
if 'uploaded_values' not in st.session_state:
    st.session_state.uploaded_values = {}
if 'uploaded_file_name' not in st.session_state:
    st.session_state.uploaded_file_name = None

uploaded_file = st.sidebar.file_uploader(
    "Eigene Daten hochladen (.csv)",
    type=["csv"],
    help="Erwartet eine CSV-Datei mit Oxidspalten wie SiO2, MgO, FeO oder zwei Spalten: Oxid und Wert."
)

if uploaded_file is not None and st.session_state.uploaded_file_name != uploaded_file.name:
    parsed_values = parse_uploaded_oxide_data(uploaded_file, mineral_group)
    if parsed_values is not None:
        st.session_state.uploaded_values = parsed_values
        for oxide in default_oxides[mineral_group]:
            if oxide in parsed_values:
                st.session_state.oxide_values[oxide] = parsed_values[oxide]
        st.session_state.calculate = True
        st.session_state.uploaded_file_name = uploaded_file.name
        st.success(f"✅ Daten aus '{uploaded_file.name}' übernommen.")
        st.rerun()
    else:
        st.session_state.uploaded_file_name = None

if st.session_state.uploaded_file_name:
    st.sidebar.caption(f"Letzte Datei: {st.session_state.uploaded_file_name}")

# Button zum Laden der Beispieldaten
if st.sidebar.button("Beispieldaten anzeigen und berechnen"):
    # Werte setzen
    example = example_data[mineral_group]
    for oxide in default_oxides[mineral_group]:
        st.session_state.oxide_values[oxide] = example.get(oxide, 0.0)
    # Berechnung erzwingen
    st.session_state.calculate = True
    st.rerun()

# Eingabefelder für Oxide
st.subheader("Chemische Zusammensetzung (Gewichts%)")
with st.container():
    for oxide in default_oxides[mineral_group]:
        st.session_state.oxide_values[oxide] = st.number_input(
            f"{oxide} (Gew.%)",
            min_value=0.0,
            max_value=100.0,
            value=st.session_state.oxide_values[oxide],
            step=0.01,
            key=f"input_{oxide}"
        )

# Basis-Sauerstoffatome
basis_oxygen = basis_oxygen_map.get(mineral_group, 3)
if mineral_group == "Allgemein":
    basis_oxygen = st.number_input("Basis-Sauerstoffatome", min_value=1, value=3, step=1)

# Die Formelausgabe wird über die zentrale Stoichiometrie-Logik aus mineral_formula.py erzeugt.

# Berechnung durchführen
if st.button("Mineralformel berechnen") or st.session_state.calculate:
    st.session_state.calculate = False
    oxide_values = {oxide: st.session_state.oxide_values[oxide] for oxide in default_oxides[mineral_group]}

    total_weight = sum(oxide_values.values())
    result = calculate_mineral_formula(oxide_values, basis_oxygen, mineral_group)

    if result:
        st.subheader("Ergebnis")
        st.markdown(f"**Mineralformel:** `{result['formula']}`")

        # Tabelle aller Kationen (inkl. Spurenelemente)
        cations_df = pd.DataFrame.from_dict(result["cations"], orient="index", columns=["Kationen"])
        st.dataframe(cations_df.style.format("{:.4f}"))

        st.markdown(f"**Summe der Kationen:** {result['total_cations']:.4f}")
        st.markdown(f"**Normalisierungsfaktor:** {result['normalization_factor']:.4f}")
        st.markdown(f"**Summe der Oxide:** {total_weight:.2f}%")
    else:
        st.error("❌ Berechnung fehlgeschlagen. Bitte Eingaben prüfen.")