from pathlib import Path

import streamlit as st
import pandas as pd
import re
import PyPDF2
import pdfplumber
# import mag4 # 'mag4' was imported but not used in the provided code, consider removing if not needed.

# Ihre benutzerdefinierte Logik für Mineralformeln
from mineral_formula import (
    calculate_mineral_formula,
    format_mineral_formula,
    molar_masses,
    elements_per_oxide,
    basis_oxygen_map,
    element_order,
    find_data_file,
)

GROUP_NAME_CANONICAL = {
    "olivine group": "Olivin",
    "olivine": "Olivin",
    "olivin": "Olivin",
    "pyroxene group": "Pyroxen",
    "pyroxen": "Pyroxen",
    "pyroxene": "Pyroxen",
    "garnet group": "Granat",
    "garnet": "Granat",
    "granat": "Granat",
    "amphibole group": "Amphibol",
    "amphibol": "Amphibol",
    "mica group": "Glimmer",
    "phyllosilicate": "Glimmer",
    "glimmer": "Glimmer",
    "feldspar group": "Feldspat",
    "feldspat": "Feldspat",
    "spinel group": "Spinell",
    "spinel": "Spinell",
    "epidote group": "Epidot",
    "epidote": "Epidot",
    "allgemein": "Allgemein",
    "general": "Allgemein",
}

def canonical_mineral_group(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return value
    normalized = str(value).strip().lower()
    return GROUP_NAME_CANONICAL.get(normalized, str(value).strip())

# --- Load and process MRMinerals.csv for mineral identification ---
try:
    csv_path = find_data_file('MRMinerals.csv', search_dirs=[Path.cwd(), Path(__file__).resolve().parent, Path('/content')])
    if csv_path is None:
        raise FileNotFoundError("MRMinerals.csv")

    df_minerals_data = pd.read_csv(csv_path)
    # Flexible handling: accept alternative column names for the mineral group
    import ast

    # Find a suitable group column and prioritize structural group fields over mineral names.
    group_col = None
    for col in df_minerals_data.columns:
        if col.strip().lower() in ('mineralgruppe', 'subgroup', 'group'):
            group_col = col
            break
    if group_col:
        df_minerals_data = df_minerals_data.rename(columns={group_col: 'Mineralgruppe'})
    else:
        st.error("❌ Die Datei 'MRMinerals.csv' muss eine Spalte für Mineralgruppen enthalten (z. B. 'Subgroup' oder 'Group').")
        st.stop()

    # Normalize subgroup names into canonical categories used by the formula logic
    df_minerals_data['Mineralgruppe'] = df_minerals_data['Mineralgruppe'].apply(canonical_mineral_group)

    # If oxide values are provided as a dict-string in a single column (e.g. 'Oxide wt%' or 'Elemental wt%'),
    # try to expand them into separate columns so the rest of the app can process them.
    oxide_dict_col = None
    oxide_preferred = ['oxide wt%', 'oxid wt%', 'oxide wt', 'oxides wt%', ' oxide wt%', 'elemental wt%', 'elemental wt', 'elemental wt%']
    for preferred in oxide_preferred:
        for col in df_minerals_data.columns:
            if col.strip().lower() == preferred:
                oxide_dict_col = col
                break
        if oxide_dict_col:
            break
    if oxide_dict_col is None:
        for col in df_minerals_data.columns:
            lower = col.strip().lower()
            if 'oxide' in lower and ('wt' in lower or '%' in lower):
                oxide_dict_col = col
                break
            if 'elemental' in lower and ('wt' in lower or '%' in lower):
                oxide_dict_col = col
                break

    if oxide_dict_col:
        def _parse_dict_cell(cell):
            if pd.isna(cell):
                return {}
            if isinstance(cell, dict):
                return cell
            try:
                return ast.literal_eval(cell)
            except Exception:
                return {}

        parsed = df_minerals_data[oxide_dict_col].apply(_parse_dict_cell)
        # Determine all keys used in the dicts
        all_keys = set()
        for d in parsed:
            if isinstance(d, dict):
                all_keys.update(d.keys())

        # Add each key as a separate column (fill missing with 0)
        for key in sorted(all_keys):
            try:
                df_minerals_data[key] = parsed.apply(lambda d: float(d.get(key, 0)) if isinstance(d, dict) else 0.0)
            except Exception:
                df_minerals_data[key] = 0.0
    # Assuming 'Mineralgruppe' is the column that defines the mineral group
    if 'Mineralgruppe' not in df_minerals_data.columns:
        st.error("❌ Die Datei 'MRMinerals.csv' muss eine Spalte 'Mineralgruppe' enthalten.")
        st.stop()

    initial_mineral_groups_from_csv = sorted(df_minerals_data['Mineralgruppe'].unique().tolist())
    DEFAULT_OXIDES_MAP = {}
    EXAMPLE_DATA_MAP = {}

    for group in initial_mineral_groups_from_csv:
        group_df = df_minerals_data[df_minerals_data['Mineralgruppe'] == group]
        # Identify oxide columns - assume all columns except 'Mineralgruppe' are oxides
        # Exclude other non-oxide columns if any are identified
        oxide_columns = [col for col in group_df.columns if col != 'Mineralgruppe']

        # Filter out columns that are not in molar_masses (i.e., not recognized oxides)
        # This makes sure we only consider valid oxides for calculations
        valid_oxides_for_group = [oxide for oxide in oxide_columns if oxide in molar_masses]

        if not valid_oxides_for_group:
            st.warning(f"⚠️ Keine gültigen Oxid-Spalten für Mineralgruppe '{group}' in 'MRMinerals.csv' gefunden. Diese Gruppe wird ignoriert.")
            continue

        # Sort oxides for consistent display, using element_order if available
        DEFAULT_OXIDES_MAP[group] = sorted(valid_oxides_for_group, key=lambda x: element_order.get(x, 999))

        # Get example data (first row for this group)
        example_row = group_df[valid_oxides_for_group].iloc[0]
        EXAMPLE_DATA_MAP[group] = example_row.fillna(0).to_dict() # Fill NaN with 0 for example data

    # If no mineral groups with valid oxides were found after processing the CSV
    if not DEFAULT_OXIDES_MAP: # This would be true if all groups were ignored
        st.error("❌ Keine Mineralgruppen in 'MRMinerals.csv' gefunden oder keine gültigen Oxide zugeordnet. Bitte überprüfen Sie die Datei.")
        st.stop()

    # Now, construct the final MINERAL_GROUPS list for the selectbox
    # It should include all groups from DEFAULT_OXIDES_MAP keys.
    MINERAL_GROUPS_FOR_SELECTBOX = sorted(list(DEFAULT_OXIDES_MAP.keys()))

    # Add a general option if it's missing
    if "Allgemein" not in MINERAL_GROUPS_FOR_SELECTBOX:
        MINERAL_GROUPS_FOR_SELECTBOX.append("Allgemein")
        # For 'Allgemein', list all known oxides from molar_masses
        DEFAULT_OXIDES_MAP["Allgemein"] = sorted(list(molar_masses.keys()), key=lambda x: element_order.get(x, 999))
        EXAMPLE_DATA_MAP["Allgemein"] = {oxide: 0.0 for oxide in DEFAULT_OXIDES_MAP["Allgemein"]}

    # Re-sort MINERAL_GROUPS to ensure 'Allgemein' is included and sorted alphabetically, or put 'Allgemein' at top if desired.
    MINERAL_GROUPS = sorted(MINERAL_GROUPS_FOR_SELECTBOX)
    # --- End Debugging outputs ---

except FileNotFoundError:
    st.error("❌ Die Datei 'MRMinerals.csv' wurde nicht gefunden. Bitte stellen Sie sicher, dass sie im Verzeichnis '/content/' liegt.")
    st.stop()
except Exception as e:
    st.error(f"❌ Fehler beim Laden oder Verarbeiten von 'MRMinerals.csv': {str(e)}")
    st.stop()

# Titel der App
st.title("Mineralformel-Rechner")
st.markdown(
    """
Diese App berechnet Mineralformeln aus chemischen Analysen (Gewichtsprozent der Oxide).
Wählen Sie eine Mineralgruppe aus und laden Sie Ihre Daten im passenden Format hoch.
"""
)

# --- Hilfsfunktionen für Dateiverarbeitung ---
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
    # Use DEFAULT_OXIDES_MAP here
    expected_oxides_for_group = DEFAULT_OXIDES_MAP.get(mineral_group, [])
    # Combine with all known molar_masses keys to recognize any valid oxide, even if not explicitly in the current group's DEFAULT_OXIDES_MAP
    expected_oxides = set(expected_oxides_for_group) | set(molar_masses.keys())
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
    # Use DEFAULT_OXIDES_MAP here
    expected_oxides_for_group = DEFAULT_OXIDES_MAP.get(mineral_group, [])
    expected_oxides = set(expected_oxides_for_group) | set(molar_masses.keys())
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

        # Use DEFAULT_OXIDES_MAP here
        expected_oxides_for_group = DEFAULT_OXIDES_MAP.get(mineral_group, [])
        expected_oxides = set(expected_oxides_for_group) | set(molar_masses.keys())
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


def find_mineral_matches(parsed_values, df, top_n=5):
    """Vergleicht die hochgeladenen Oxid-Werte mit Einträgen in df (MRMinerals.csv) und liefert Top-N Kandidaten.

    Rückgabe: Liste von Diktaten mit Feldern: 'Mineral name', 'Chemical formula', 'Mineralgruppe', 'distance'
    """
    # Bestimme mögliche Oxid-Spalten in df (alles außer bekannte Metadaten)
    metadata_cols = set([c for c in df.columns if c.strip().lower() in (
        'mineral name', 'mineralname', 'mineralgruppe', 'group', 'subgroup', 'chemical formula',
        'machine readable formula', 'elemental wt%', 'oxide wt%')])
    oxide_cols = [c for c in df.columns if c not in metadata_cols]

    candidates = []
    # Normalisiere parsed_values
    pv = {k: float(v) for k, v in parsed_values.items()}
    sum_pv = sum(pv.values())
    pv_norm = {k: (v / sum_pv * 100.0) if sum_pv > 0 else 0.0 for k, v in pv.items()}

    for _, row in df.iterrows():
        # Baue Reihen-Oxid-Dict
        row_ox = {}
        for col in oxide_cols:
            try:
                val = row[col]
                if pd.isna(val):
                    continue
                row_ox[col] = float(val)
            except Exception:
                continue

        # Normiere Reihen-Oxide
        sum_row = sum(row_ox.values())
        row_norm = {k: (v / sum_row * 100.0) if sum_row > 0 else 0.0 for k, v in row_ox.items()}

        # Vereinigung der Keys
        keys = set(pv_norm.keys()) | set(row_norm.keys())
        if not keys:
            continue

        # Erzeuge Vektoren und berechne L2-Distanz
        diff_sq = 0.0
        for k in keys:
            a = pv_norm.get(k, 0.0)
            b = row_norm.get(k, 0.0)
            diff_sq += (a - b) ** 2
        distance = diff_sq ** 0.5

        candidates.append({
            'Mineral name': row.get('Mineral name') if 'Mineral name' in df.columns else row.get('Mineralname', ''),
            'Chemical formula': row.get('Chemical formula') if 'Chemical formula' in df.columns else '',
            'Mineralgruppe': row.get('Mineralgruppe') if 'Mineralgruppe' in df.columns else row.get('Group', ''),
            'distance': float(distance),
            'row_index': row.name,
            'row_ox': row_ox,
            'row_norm': row_norm,
        })

    # Sortiere und gebe Top-N zurück
    candidates = sorted(candidates, key=lambda x: x['distance'])[:top_n]
    return candidates

# --- Streamlit UI ---
def apply_candidate_selection():
    """Callback: setzt die Mineralgruppe basierend auf der ausgewählten Match-Kandidaten-Selectbox."""
    sel = st.session_state.get('candidate_select')
    opts = st.session_state.get('candidate_options')
    if not sel or not opts or 'match_candidates' not in st.session_state:
        return
    try:
        idx = opts.index(sel)
    except Exception:
        idx = 0
    try:
        cand = st.session_state['match_candidates'][idx]
    except Exception:
        return
    group = cand.get('Mineralgruppe') or cand.get('Mineral group') or cand.get('Group') or None
    if group and group in MINERAL_GROUPS:
        # Setze die selectbox value via session_state, der selectbox verwendet den key 'selected_mineral_group'
        st.session_state['selected_mineral_group'] = group
        # Aktualisiere aktuelle Gruppe (aber übernehme Referenzwerte erst nach Bestätigung)
        st.session_state['current_mineral_group'] = group
        # Lege einen Vorschlag (pending) mit Referenz-Oxidwerten an, zur Bestätigung durch den Benutzer
        row_ox = cand.get('row_ox') if isinstance(cand, dict) else None
        expected = DEFAULT_OXIDES_MAP.get(group, [])
        pending = {'group': group, 'row_ox': {}, 'expected': expected}
        if row_ox:
            for oxide in expected:
                if oxide in row_ox:
                    try:
                        pending['row_ox'][oxide] = float(row_ox[oxide])
                    except Exception:
                        pending['row_ox'][oxide] = 0.0
        # speichere den Vorschlag in session_state; Benutzer muss Übernehmen klicken
        st.session_state['pending_reference'] = pending
        # keine direkte Übernahme mehr; UI zeigt jetzt Vorschlag mit Buttons
        return



# Mineralgruppe-Auswahl (jetzt im Hauptbereich)
mineral_group = st.session_state.get('selected_mineral_group') if 'selected_mineral_group' in st.session_state else None
if mineral_group not in MINERAL_GROUPS:
    mineral_group = MINERAL_GROUPS[0]
    st.session_state['selected_mineral_group'] = mineral_group

# Session State initialisieren und bei Mineralgruppenwechsel zurücksetzen
if 'current_mineral_group' not in st.session_state or st.session_state.current_mineral_group != mineral_group:
    st.session_state.current_mineral_group = mineral_group
    # Reset oxide_values based on the newly selected mineral_group
    st.session_state.oxide_values = {oxide: 0.0 for oxide in DEFAULT_OXIDES_MAP.get(mineral_group, [])}
    # Also reset uploaded and calculated states when mineral group changes
    st.session_state.uploaded_values = {}
    st.session_state.uploaded_file_name = None
    st.session_state.calculate = False

# Fallback for initial state if not covered by the above logic (e.g., first load)
if 'oxide_values' not in st.session_state:
    st.session_state.oxide_values = {oxide: 0.0 for oxide in DEFAULT_OXIDES_MAP.get(mineral_group, [])}
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
        # Update session_state.oxide_values for the current mineral_group based on uploaded data
        for oxide in DEFAULT_OXIDES_MAP.get(mineral_group, []): # Use DEFAULT_OXIDES_MAP
            if oxide in parsed_values:
                st.session_state.oxide_values[oxide] = parsed_values[oxide]
        st.session_state.calculate = True
        st.session_state.uploaded_file_name = uploaded_file.name
        # Führe Matching gegen die MRMinerals-Daten durch und speichere Kandidaten
        try:
            st.session_state.match_candidates = find_mineral_matches(parsed_values, df_minerals_data, top_n=5)
            # Default Auswahl auf den besten Kandidaten
            if st.session_state.match_candidates:
                st.session_state.selected_candidate_index = 0
        except Exception:
            st.session_state.match_candidates = []
            st.session_state.selected_candidate_index = None
        st.success(f"✅ Daten aus '{uploaded_file.name}' erfolgreich übernommen.")
        st.rerun()
    else:
        st.session_state.uploaded_file_name = None

if st.session_state.uploaded_file_name:
    st.caption(f"📄 Letzte Datei: {st.session_state.uploaded_file_name}")

# Wenn Matching-Kandidaten vorhanden sind, zeige sie zur Auswahl
if 'match_candidates' in st.session_state and st.session_state.match_candidates:
    options = [f"{c.get('Mineral name','')} ({c.get('Chemical formula','')}) — Dist {c.get('distance',0):.2f}" for c in st.session_state.match_candidates]
    # Speichere options in session_state, damit der Callback sie verwenden kann
    st.session_state['candidate_options'] = options
    # Selectbox mit Callback, die beim Ändern die Mineralgruppe setzt
    sel = st.selectbox(
        "Erkannte Mineral-Kandidaten (höchste Ähnlichkeit oben)",
        options,
        index=st.session_state.get('selected_candidate_index', 0),
        key='candidate_select',
        on_change=apply_candidate_selection,
    )
    # Speichere den Index
    try:
        st.session_state.selected_candidate_index = options.index(sel)
    except Exception:
        st.session_state.selected_candidate_index = 0

    # Handler: Übernehme den pending_reference in die Eingabefelder
    def confirm_pending_reference():
        pending = st.session_state.get('pending_reference')
        if not pending:
            return
        group = pending.get('group')
        expected = pending.get('expected', [])
        row_ox = pending.get('row_ox', {})
        # Setze Mineralgruppe und oxide_values
        st.session_state['selected_mineral_group'] = group
        st.session_state['current_mineral_group'] = group
        new_vals = {oxide: float(row_ox.get(oxide, 0.0)) for oxide in expected}
        st.session_state['oxide_values'] = new_vals
        # entferne pending
        st.session_state.pop('pending_reference', None)
        st.experimental_rerun()

    def discard_pending_reference():
        st.session_state.pop('pending_reference', None)
        st.experimental_rerun()

    # Wenn ein Vorschlag existiert, zeige ihn zur Bestätigung an
    if 'pending_reference' in st.session_state and st.session_state['pending_reference']:
        pending = st.session_state['pending_reference']
        with st.expander("Referenzvorschlag anzeigen"):
            st.write(f"Vorgeschlagene Mineralgruppe: **{pending.get('group')}**")
            if pending.get('row_ox'):
                st.write("Vorgeschlagene Oxid-Werte:")
                for ox, val in pending['row_ox'].items():
                    st.write(f"- {ox}: {val}")
            else:
                st.write("Keine Referenz-Oxidwerte in der gewählten Zeile gefunden.")
            col1, col2 = st.columns(2)
            with col1:
                st.button("Übernehmen", on_click=confirm_pending_reference)
            with col2:
                st.button("Verwerfen", on_click=discard_pending_reference)

# Button zum Laden der Beispieldaten
if st.button("🔄 Beispieldaten laden"):
    # Use EXAMPLE_DATA_MAP here
    example = EXAMPLE_DATA_MAP.get(mineral_group, {})
    for oxide in DEFAULT_OXIDES_MAP.get(mineral_group, []): # Use DEFAULT_OXIDES_MAP
        st.session_state.oxide_values[oxide] = example.get(oxide, 0.0)
    st.session_state.calculate = True
    st.rerun()

# Eingabefelder für Oxide
st.subheader("Chemische Zusammensetzung (Gewichts%)")
with st.container():
    cols = st.columns(3)
    # Use DEFAULT_OXIDES_MAP here
    for i, oxide in enumerate(DEFAULT_OXIDES_MAP.get(mineral_group, [])):
        with cols[i % 3]:
            # Make key unique to mineral group to prevent state issues on group change
            st.session_state.oxide_values[oxide] = st.number_input(
                f"{oxide} (Gew.%)",
                min_value=0.0,
                max_value=100.0,
                value=st.session_state.oxide_values.get(oxide, 0.0), # Use .get() for safety
                step=0.01,
                key=f"input_{mineral_group}_{oxide}"
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
    # Ensure oxide_values are only for the current mineral group's expected oxides
    oxide_values = {oxide: st.session_state.oxide_values.get(oxide, 0.0) for oxide in DEFAULT_OXIDES_MAP.get(mineral_group, [])}

    total_weight = sum(oxide_values.values())
    if total_weight < 95 or total_weight > 105:
        st.warning(f"⚠️ Die Summe der Oxide ({total_weight:.1f}%) weicht stark von 100% ab. Ist das korrekt?")
    elif total_weight == 0 and any(DEFAULT_OXIDES_MAP.get(mineral_group, [])): # Only warn if there are expected oxides but all values are 0
        st.warning("⚠️ Alle Werte sind 0. Bitte geben Sie gültige Daten ein.")
    else:
        result = calculate_mineral_formula(oxide_values, basis_oxygen, mineral_group)

        if result:
            st.subheader("Ergebnis")
            # Zeige die Formel und daneben den Mineralnamen (falls aus der CSV verfügbar)
            col_formula, col_name = st.columns([3, 1])
            with col_formula:
                st.markdown(f"**Mineralformel:** `{result['formula']}`")
            with col_name:
                # Versuche zuerst, einen erkannten Kandidaten anzuzeigen
                cand = None
                mcands = st.session_state.get('match_candidates')
                sel_idx = st.session_state.get('selected_candidate_index', 0)
                if mcands:
                    try:
                        cand = mcands[sel_idx]
                    except Exception:
                        cand = mcands[0] if mcands else None

                # Falls kein Kandidat gewählt wurde, aber ein pending_reference existiert,
                # zeige die zugehörige Gruppe als Hinweis
                if not cand and 'pending_reference' in st.session_state:
                    pending = st.session_state['pending_reference']
                    st.markdown(f"**Vorgeschlagene Mineralgruppe:** `{pending.get('group')}`")

                # Wenn ein Kandidat vorhanden ist, hole den Mineralnamen möglichst verlässlich
                if cand:
                    mineral_name = cand.get('Mineral name') or cand.get('Mineralname') or ''
                    # Wenn der Kandidat keine Namen-Spalte enthält, versuche, über row_index aus df nachzusehen
                    if not mineral_name and 'row_index' in cand:
                        try:
                            row = df_minerals_data.loc[int(cand['row_index'])]
                            for col in ('Mineral name', 'Mineralname', 'mineralname'):
                                if col in row.index and pd.notna(row[col]):
                                    mineral_name = row[col]
                                    break
                        except Exception:
                            mineral_name = ''

                    if mineral_name:
                        st.markdown(f"**Mineralname (erkannt):** `{mineral_name}`")
                    else:
                        st.markdown("**Mineralname (erkannt):** (kein Name verfügbar)")

                    # Referenzformel und Abstand
                    ref_formula = cand.get('Chemical formula') or cand.get('chemical formula') or ''
                    if ref_formula:
                        st.markdown(f"**Referenzformel:** `{ref_formula}`")
                    try:
                        st.markdown(f"**Ähnlichkeitsabstand:** {float(cand.get('distance', 0.0)):.2f}")
                    except Exception:
                        pass
                else:
                    # Fallback: Gruppenname oder erster Mineralname der Gruppe aus der CSV
                    try:
                        names = []
                        for col in ('Mineral name', 'Mineralname'):
                            if col in df_minerals_data.columns:
                                names = df_minerals_data.loc[df_minerals_data['Mineralgruppe'] == mineral_group, col].dropna().unique().tolist()
                                if names:
                                    break
                    except Exception:
                        names = []
                    mineral_name_display = names[0] if names else mineral_group
                    st.markdown(f"**Mineralname:** `{mineral_name_display}`")

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
