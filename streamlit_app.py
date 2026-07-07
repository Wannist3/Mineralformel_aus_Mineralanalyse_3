import streamlit as st
import pandas as pd
import re
import PyPDF2
import pdfplumber
import mag4 # Importieren Sie das mag4 Paket

# Ihre benutzerdefinierte Logik für Mineralformeln
from mineral_formula import calculate_mineral_formula, format_mineral_formula, default_oxides, molar_masses, elements_per_oxide, basis_oxygen_map, element_order, example_data

# Titel der App
st.title("Mineralformel-Rechner")
st.markdown(
    """
Diese App berechnet Mineralformeln aus chemischen Analysen (Gewichtsprozent der Oxide).
Wählen Sie eine Mineralgruppe aus und laden Sie Ihre Daten im passenden Format hoch.
"""
)

# --- Hilfsfunktionen für Dateiverarbeitung (wie zuvor) ---
def normalize_oxide_name(value):
    """Normalisiert Oxid-Namen für Vergleich."""
    value = str(value).strip().lower().replace(" ", "").replace("_", "").replace("-", "")
    return re.sub(r'(\d+)', r'\1', value)

def extract_text_from_pdf(pdf_file):
    """Extrahiert Text aus einer PDF-Datei."""
    try:
        pdf_file.seek(0)
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() if page.extract_text() else ""
        return text if text.strip() else None
    except Exception:
        return None

def extract_tables_from_pdf(pdf_file):
    """Extrahiert Tabellen aus einer PDF-Datei."""
    try:
        pdf_file.seek(0)
        with pdfplumber.open(pdf_file) as pdf:
            tables = []
            for page in pdf.pages:
                try:
                    page_tables = page.extract_tables()
                    if page_tables:
                        tables.extend(page_tables)
                except Exception:
                    continue
            return tables if tables else None
    except Exception:
        return None

def parse_pdf_text(text, mineral_group):
    """Sucht nach Oxid-Werten im extrahierten PDF-Text."""
    expected_oxides = set(default_oxides[mineral_group]) | set(molar_masses.keys())
    parsed_values = {}

    for oxide in expected_oxides:
        pattern = re.compile(rf"{oxide}\s*[:=]?\s*(\d+\.?\d*)", re.IGNORECASE)
        match = pattern.search(text)
        if match:
            try:
                parsed_values[oxide] = float(match.group(1))
            except ValueError:
                continue

    return parsed_values if parsed_values else None

def parse_pdf_tables(tables, mineral_group):
    """Verarbeitet extrahierte Tabellen aus PDF-Dateien."""
    expected_oxides = set(default_oxides[mineral_group]) | set(molar_masses.keys())
    normalized_oxide_map = {normalize_oxide_name(oxide): oxide for oxide in expected_oxides}

    for table in tables:
        try:
            if len(table) <= 1:
                continue

            df = pd.DataFrame(table[1:], columns=table[0])
            if df.empty:
                continue

            parsed_values = {}

            # Spalten als Oxide
            for column in df.columns:
                normalized_name = normalize_oxide_name(str(column))
                if normalized_name in normalized_oxide_map and pd.api.types.is_numeric_dtype(df[column]):
                    try:
                        parsed_values[normalized_oxide_map[normalized_name]] = float(df[column].iloc[0])
                    except (ValueError, TypeError):
                        continue

            if parsed_values:
                return parsed_values

            # Zwei Spalten (Oxid | Wert)
            if len(df.columns) >= 2:
                for oxide_col in [0, 1]:
                    try:
                        col_data = df.iloc[:, oxide_col]
                        if any(normalize_oxide_name(str(val)) in normalized_oxide_map for val in col_data):
                            value_col = 1 if oxide_col == 0 else 0
                            for _, row in df.iterrows():
                                oxide = str(row.iloc[oxide_col]).strip()
                                normalized_name = normalize_oxide_name(oxide)
                                if normalized_name in normalized_oxide_map:
                                    try:
                                        value = float(row.iloc[value_col])
                                        parsed_values[normalized_oxide_map[normalized_name]] = value
                                    except (ValueError, TypeError):
                                        continue
                            if parsed_values:
                                return parsed_values
                    except Exception:
                        continue

        except Exception:
            continue

    return None

def parse_uploaded_data(uploaded_file, mineral_group):
    """Verarbeitet hochgeladene Dateien."""
    if uploaded_file is None:
        return None

    file_type = uploaded_file.name.split('.')[-1].lower()

    try:
        if file_type == 'csv':
            df = pd.read_csv(uploaded_file)
        elif file_type == 'xlsx':
            df = pd.read_excel(uploaded_file)
        elif file_type == 'pdf':
            tables = extract_tables_from_pdf(uploaded_file)
            if tables:
                parsed_values = parse_pdf_tables(tables, mineral_group)
                if parsed_values:
                    return parsed_values

            text = extract_text_from_pdf(uploaded_file)
            if text:
                parsed_values = parse_pdf_text(text, mineral_group)
                if parsed_values:
                    return parsed_values

            st.error("❌ Keine verwertbaren Daten in der PDF gefunden.")
            return None
        else:
            st.error(f"❌ Ununterstützter Dateityp: {file_type}")
            return None

        if df.empty:
            st.error("❌ Die hochgeladene Datei enthält keine Daten.")
            return None

        expected_oxides = set(default_oxides[mineral_group]) | set(molar_masses.keys())
        normalized_oxide_map = {normalize_oxide_name(oxide): oxide for oxide in expected_oxides}

        # Spalten als Oxide
        if df.shape[1] > 1:
            parsed_values = {}
            for column in df.columns:
                normalized_name = normalize_oxide_name(str(column))
                if normalized_name in normalized_oxide_map and pd.api.types.is_numeric_dtype(df[column]):
                    try:
                        parsed_values[normalized_oxide_map[normalized_name]] = float(df[column].iloc[0])
                    except (ValueError, TypeError):
                        continue
            if parsed_values:
                return parsed_values

        # Zwei Spalten (Oxid | Wert)
        if df.shape[1] >= 2:
            for oxide_col in [0, 1]:
                try:
                    if df.iloc[:, oxide_col].apply(lambda x: normalize_oxide_name(str(x)) in normalized_oxide_map).any():
                        value_col = 1 if oxide_col == 0 else 0
                        parsed_values = {}
                        for _, row in df.iterrows():
                            oxide = str(row.iloc[oxide_col]).strip()
                            normalized_name = normalize_oxide_name(oxide)
                            if normalized_name in normalized_oxide_map:
                                try:
                                    value = float(row.iloc[value_col])
                                    parsed_values[normalized_oxide_map[normalized_name]] = value
                                except (ValueError, TypeError):
                                    continue
                        if parsed_values:
                            return parsed_values
                except Exception:
                    continue

        st.error("❌ Keine gültigen Oxid-Daten in der Datei gefunden.")
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

# Datei-Upload mit Format-Hinweisen
st.sidebar.markdown("### 📁 Eigene Daten hochladen")

with st.sidebar.expander("ℹ️ Format-Hinweise anzeigen"):
    st.markdown("""
    **Unterstützte Dateiformate und Beispiele**:

    **CSV / Excel (XLSX)**
    - Spalten mit Oxid-Namen (pro Zeile ein Datensatz):
      ```csv
      SiO2, Al2O3, FeO, MgO
      40.5, 12.3, 15.2, 8.1
      ```
    - Zwei Spalten (Oxid | Wert):
      ```csv
      Oxid,   Wert
      SiO2,   40.5
      Al2O3,  12.3
      FeO,    15.2
      ```

    **PDF**
    - Mit Tabellen: Oxid-Namen und Werte in Tabellenform
    - Mit Text: Oxid-Werte im Format:
      ```
      SiO2 40.5
      Al2O3: 12.3
      FeO = 15.2
      MgO 8.1
      ```
    ❗Wichtig: Die PDF muss maschinenlesbar sein (keine gescannten Bilder).
    """
)

# Datei-Uploader
uploaded_file = st.sidebar.file_uploader(
    "Datei auswählen (CSV, XLSX, PDF)",
    type=["csv", "xlsx", "pdf"],
    help="Klicken Sie auf 'ℹ️ Format-Hinweise anzeigen' für Details"
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
    cols = st.columns(3)
    for i, oxide in enumerate(default_oxides[mineral_group]):
        with cols[i % 3]:
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
        help="Anzahl der Sauerstoffatome, auf die normalisiert wird"
    )

# Berechnung durchführen
if st.button("🔢 Mineralformel berechnen") or st.session_state.calculate:
    st.session_state.calculate = False
    oxide_values = {oxide: st.session_state.oxide_values[oxide] for oxide in default_oxides[mineral_group]}

    total_weight = sum(oxide_values.values())
    if total_weight < 95 or total_weight > 105:
        st.warning(f"⚠️ Die Summe der Oxide ({total_weight:.1f}%) weicht stark von 100% ab. Ist das korrekt?")
    elif total_weight == 0:
        st.warning("⚠️ Alle Werte sind 0. Bitte geben Sie gültige Daten ein.")
    else:
        result = calculate_mineral_formula(oxide_values, basis_oxygen, mineral_group)

        if result:
            st.subheader("Ergebnis")
            st.markdown(f"**Mineralformel:** `{result['formula']}`")

            # Tabelle der Kationen
            cations_df = pd.DataFrame.from_dict(result["cations"], orient="index", columns=["Kationen"])
            st.dataframe(cations_df.style.format("{:.4f}"))

            st.markdown(f"**Summe der Kationen:** {result['total_cations']:.4f}")
            st.markdown(f"**Normalisierungsfaktor:** {result['normalization_factor']:.4f}")
            st.markdown(f"**Summe der Oxide:** {total_weight:.2f}%")

            # Debugging-Informationen
            with st.expander("Details zum Berechnungsergebnis"):
                st.json(result)

            st.info("💡 Die finale Mineralformel (`result['formula']`) wird von der Funktion `format_mineral_formula` in Ihrer `mineral_formula.py` Datei erstellt. Bitte überprüfen Sie die Logik dieser Funktion, um zu sehen, wie die Kationen zu der Formel zusammengesetzt werden.")

            if mineral_group == "Olivin" and (result['total_cations'] < 2.9 or result['total_cations'] > 3.1):
                st.warning("⚠️ Ungewöhnliche Kationen-Summe für Olivin (Erwartet ~3)")
            elif mineral_group == "Pyroxen" and (result['total_cations'] < 3.9 or result['total_cations'] > 4.1):
                st.warning("⚠️ Ungewöhnliche Kationen-Summe für Pyroxen (Erwartet ~4)")
            elif mineral_group == "Granat" and (result['total_cations'] < 7.9 or result['total_cations'] > 8.1):
                st.warning("⚠️ Ungewöhnliche Kationen-Summe für Granat (Erwartet ~8)")
        else:
            st.error("❌ Berechnung fehlgeschlagen. Bitte überprüfen Sie Ihre Eingaben.")
