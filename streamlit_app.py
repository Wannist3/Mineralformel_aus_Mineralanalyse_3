import streamlit as st
import pandas as pd
import numpy as np
import re
import PyPDF2
from mineral_formula import calculate_mineral_formula, format_mineral_formula

# Titel der App
st.title("Mineralformel-Rechner")
st.markdown(
    """
Diese App berechnet Mineralformeln aus chemischen Analysen (Gewichtsprozent der Oxide).
Wählen Sie eine Mineralgruppe aus und laden Sie Ihre Daten im passenden Format hoch.
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
    "Fe2O3": {"Fe3+": 2, "O": 3}, "FeO": {"Fe2+": 1, "O": 1},
    "MgO": {"Mg": 1, "O": 1}, "CaO": {"Ca": 1, "O": 1},
    "Na2O": {"Na": 2, "O": 1}, "K2O": {"K": 2, "O": 1},
    "TiO2": {"Ti": 1, "O": 2}, "MnO": {"Mn": 1, "O": 1},
    "Cr2O3": {"Cr": 2, "O": 3}, "NiO": {"Ni": 1, "O": 1},
    "ZnO": {"Zn": 1, "O": 1}, "Li2O": {"Li": 2, "O": 1},
    "H2O": {"H": 2, "O": 1}, "F": {"F": 1}, "Cl": {"Cl": 1},
    "Ce2O3": {"Ce": 2, "O": 3}, "La2O3": {"La": 2, "O": 3},
    "Y2O3": {"Y": 2, "O": 3}, "Mn2O3": {"Mn": 2, "O": 3}
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

# --- Hilfsfunktionen ---
def normalize_oxide_name(value):
    """Normalisiert Oxid-Namen für Vergleich (z.B. 'SiO2', 'sio2', 'SiO-2' → 'SiO2')."""
    value = str(value).strip().lower().replace(" ", "").replace("_", "").replace("-", "")
    return re.sub(r'(\d+)', r'\1', value)

def extract_text_from_pdf(pdf_file):
    """Extrahiert Text aus einer PDF-Datei mit PyPDF2."""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text if text.strip() else None
    except Exception as e:
        st.error(f"❌ Fehler beim Lesen der PDF: {str(e)}")
        return None

def parse_pdf_text(text, mineral_group):
    """Sucht nach Oxid-Werten im extrahierten PDF-Text."""
    expected_oxides = set(default_oxides[mineral_group]) | set(molar_masses.keys())
    parsed_values = {}

    for oxide in expected_oxides:
        # Suche nach Mustern wie "SiO2 40.5" oder "SiO2: 40.5"
        pattern = re.compile(rf"{oxide}\s*[:=]?\s*(\d+\.?\d*)", re.IGNORECASE)
        match = pattern.search(text)
        if match:
            parsed_values[oxide] = float(match.group(1))

    return parsed_values if parsed_values else None

def parse_uploaded_data(uploaded_file, mineral_group):
    """Verarbeitet hochgeladene Dateien (CSV, XLSX, PDF) und extrahiert Oxid-Daten."""
    if uploaded_file is None:
        return None

    file_type = uploaded_file.name.split('.')[-1].lower()

    try:
        if file_type == 'csv':
            df = pd.read_csv(uploaded_file)
        elif file_type == 'xlsx':
            df = pd.read_excel(uploaded_file)
        elif file_type == 'pdf':
            text = extract_text_from_pdf(uploaded_file)
            if text:
                return parse_pdf_text(text, mineral_group)
            else:
                st.error("❌ Kein Text in der PDF gefunden oder die PDF enthält keine maschinenlesbaren Daten.")
                return None
        else:
            st.error(f"❌ Ununterstützter Dateityp: {file_type}")
            return None

        if df.empty:
            st.error("❌ Die hochgeladene Datei enthält keine Daten.")
            return None

        # Erwartete Oxide für diese Mineralgruppe
        expected_oxides = set(default_oxides[mineral_group]) | set(molar_masses.keys())
        normalized_oxide_map = {normalize_oxide_name(oxide): oxide for oxide in expected_oxides}

        # 1. Versuch: Spalten als Oxide (z.B. erste Zeile mit SiO2, MgO, etc.)
        if df.shape[1] > 1:
            parsed_values = {}
            for column in df.columns:
                normalized_name = normalize_oxide_name(column)
                if normalized_name in normalized_oxide_map and pd.api.types.is_numeric_dtype(df[column]):
                    parsed_values[normalized_oxide_map[normalized_name]] = float(df[column].iloc[0])
            if parsed_values:
                return parsed_values

        # 2. Versuch: Zwei Spalten (Oxid | Wert)
        if df.shape[1] >= 2:
            for oxide_col in [0, 1]:  # Prüfe beide Spalten als Oxid-Spalte
                if df.iloc[:, oxide_col].apply(lambda x: normalize_oxide_name(str(x)) in normalized_oxide_map).any():
                    value_col = 1 - oxide_col  # Andere Spalte als Wert
                    parsed_values = {}
                    for _, row in df.iterrows():
                        oxide = str(row.iloc[oxide_col]).strip()
                        normalized_name = normalize_oxide_name(oxide)
                        if normalized_name in normalized_oxide_map and pd.api.types.is_numeric_dtype(row.iloc[value_col]):
                            parsed_values[normalized_oxide_map[normalized_name]] = float(row.iloc[value_col])
                    if parsed_values:
                        return parsed_values

        st.error("❌ Keine gültigen Oxid-Daten in der Datei gefunden. Bitte überprüfen Sie das Format.")
        return None

    except Exception as e:
        st.error(f"❌ Fehler beim Lesen der Datei: {str(e)}")
        return None

# --- Streamlit UI ---
mineral_group = st.sidebar.selectbox(
    "Mineralgruppe auswählen",
    list(default_oxides.keys())
)

# Session State initialisieren
if 'oxide_values' not in st.session_state:
    st.session_state.oxide_values = {oxide: 0.0 for oxide in default_oxides[mineral_group]}
if 'calculate' not in st.session_state:
    st.session_state.calculate = False
if 'uploaded_values' not in st.session_state:
    st.session_state.uploaded_values = {}
if 'uploaded_file_name' not in st.session_state:
    st.session_state.uploaded_file_name = None

# Datei-Upload mit ausführlichen Format-Hinweisen
st.sidebar.markdown("### 📁 Eigene Daten hochladen")

# Aufklappbare Hilfe-Box mit Format-Informationen
with st.sidebar.expander("ℹ️ Format-Hinweise anzeigen"):
    st.markdown("""
    **Unterstützte Dateiformate und Beispiele**:

    1. **CSV / Excel (XLSX)**
       - **Format 1**: Spalten mit Oxid-Namen (pro Zeile ein Datensatz)
         ```csv
         SiO2, Al2O3, FeO, MgO
         40.5,  12.3, 15.2, 8.1
         ```
       - **Format 2**: Zwei Spalten (Oxid | Wert)
         ```csv
         Oxid,   Wert
         SiO2,   40.5
         Al2O3,  12.3
         FeO,    15.2
         ```

    2. **PDF** *(nur Text-Extraktion, keine Tabellen!)*
       - Der Text muss Oxid-Werte im Format enthalten:
         ```
         SiO2 40.5
         Al2O3: 12.3
         FeO = 15.2
         MgO 8.1
         ```
       - ❗ **Wichtig**: Die PDF muss **maschinenlesbaren Text** enthalten
         (keine gescannten Bilder oder Tabellen ohne Textlayer).

    **Beispiel-Downloads**:
    - [CSV-Vorlage herunterladen](https://example.com/template.csv)
    - [Excel-Vorlage herunterladen](https://example.com/template.xlsx)
    """)

# Datei-Uploader
uploaded_file = st.sidebar.file_uploader(
    "Datei auswählen (CSV, XLSX, PDF)",
    type=["csv", "xlsx", "pdf"],
    help="Klicken Sie oben auf 'ℹ️ Format-Hinweise anzeigen' für Details zu den erwarteten Formaten."
)

# Dynamische Hinweise nach Upload
if uploaded_file:
    file_type = uploaded_file.name.split('.')[-1].lower()
    if file_type == 'pdf':
        st.sidebar.warning(
            "⚠️ **Hinweis zu PDFs**: \n"
            "Die App extrahiert nur **Text** (nicht Tabellen). \n"
            "Stellen Sie sicher, dass Ihre PDF Werte wie folgt enthält:\n"
            "`SiO2 40.5` oder `Al2O3: 12.3`\n\n"
            "Falls Ihre PDF eine Tabelle enthält, nutzen Sie stattdessen CSV/Excel."
        )
    else:
        st.sidebar.success(
            f"✅ {file_type.upper()}-Datei erfolgreich hochgeladen.\n"
            "Erwartetes Format: "
            "**Spalten mit Oxid-Namen** (z.B. `SiO2`, `Al2O3`) oder "
            "**zwei Spalten** (`Oxid` | `Wert`)."
        )

# Dateiverarbeitung
if uploaded_file is not None and st.session_state.uploaded_file_name != uploaded_file.name:
    parsed_values = parse_uploaded_data(uploaded_file, mineral_group)
    if parsed_values is not None:
        st.session_state.uploaded_values = parsed_values
        for oxide in default_oxides[mineral_group]:
            if oxide in parsed_values:
                st.session_state.oxide_values[oxide] = parsed_values[oxide]
        st.session_state.calculate = True
        st.session_state.uploaded_file_name = uploaded_file.name
        st.success(f"✅ Daten aus '{uploaded_file.name}' erfolgreich übernommen.")
        st.rerun()
    else:
        st.session_state.uploaded_file_name = None

if st.session_state.uploaded_file_name:
    st.sidebar.caption(f"📄 Letzte Datei: {st.session_state.uploaded_file_name}")

# Button zum Laden der Beispieldaten
if st.sidebar.button("🔄 Beispieldaten laden"):
    example = example_data[mineral_group]
    for oxide in default_oxides[mineral_group]:
        st.session_state.oxide_values[oxide] = example.get(oxide, 0.0)
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
    basis_oxygen = st.number_input(
        "Basis-Sauerstoffatome",
        min_value=1,
        value=3,
        step=1,
        help="Anzahl der Sauerstoffatome, auf die normalisiert wird (z.B. 4 für Olivin, 8 für Feldspat)."
    )

# Berechnung durchführen
if st.button("🔢 Mineralformel berechnen") or st.session_state.calculate:
    st.session_state.calculate = False
    oxide_values = {oxide: st.session_state.oxide_values[oxide] for oxide in default_oxides[mineral_group]}

    total_weight = sum(oxide_values.values())
    if total_weight == 0:
        st.warning("⚠️ Alle Werte sind 0. Bitte geben Sie gültige Daten ein.")
    else:
        result = calculate_mineral_formula(oxide_values, basis_oxygen, mineral_group)

        if result:
            st.subheader("Ergebnis")
            st.markdown(f"**Mineralformel:** `{result['formula']}`")

            # Tabelle aller Kationen
            cations_df = pd.DataFrame.from_dict(result["cations"], orient="index", columns=["Kationen"])
            st.dataframe(cations_df.style.format("{:.4f}"))

            st.markdown(f"**Summe der Kationen:** {result['total_cations']:.4f}")
            st.markdown(f"**Normalisierungsfaktor:** {result['normalization_factor']:.4f}")
            st.markdown(f"**Summe der Oxide:** {total_weight:.2f}%")
        else:
            st.error("❌ Berechnung fehlgeschlagen. Bitte überprüfen Sie Ihre Eingaben.")