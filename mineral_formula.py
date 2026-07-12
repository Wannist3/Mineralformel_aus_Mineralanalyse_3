from __future__ import annotations

from pathlib import Path


def find_data_file(filename: str, search_dirs=None) -> Path | None:
    """Suche nach einer Daten-Datei im aktuellen Arbeitsverzeichnis oder bekannten Ordnern."""
    if search_dirs is None:
        search_dirs = [Path.cwd(), Path(__file__).resolve().parent, Path("/content")]

    candidates = []
    for base_dir in search_dirs:
        if base_dir is None:
            continue
        path = Path(base_dir)
        if not path.exists():
            continue
        if path.is_file():
            candidates.append(path)
            continue

        direct_path = path / filename
        if direct_path.exists():
            return direct_path

        for match in path.rglob(filename):
            if match.is_file():
                return match

    return None


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
    "Mn2O3": 157.87,
}

elements_per_oxide = {
    "SiO2": {"Si": 1, "O": 2},
    "Al2O3": {"Al": 2, "O": 3},
    "Fe2O3": {"Fe3+": 2, "O": 3},
    "FeO": {"Fe2+": 1, "O": 1},
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
    "Mn2O3": {"Mn": 2, "O": 3},
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
    "Allgemein": ["SiO2", "Al2O3", "Fe2O3", "FeO", "MgO", "CaO", "Na2O", "K2O", "TiO2", "MnO", "Cr2O3", "NiO", "ZnO"],
}

basis_oxygen_map = {
    "Olivin": 4,
    "Pyroxen": 6,
    "Granat": 12,
    "Amphibol": 23,
    "Glimmer": 11,
    "Feldspat": 8,
    "Spinell": 4,
    "Epidot": 12.5,
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
    "default": ["Si", "Al", "Ti", "Fe3+", "Cr", "Fe2+", "Mg", "Mn", "Ca", "Na", "K", "Ni", "Zn", "Li"],
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
    "Allgemein": {"SiO2": 50.0, "Al2O3": 20.0, "Fe2O3": 5.0, "FeO": 5.0, "MgO": 10.0, "CaO": 5.0, "Na2O": 3.0, "K2O": 2.0},
}


def _format_coefficient(value: float) -> str:
    rounded = round(float(value), 2)
    if abs(rounded - 1.0) < 0.001:
        return ""
    text = f"{rounded:.2f}".rstrip("0").rstrip(".")
    if text == "":
        return ""
    return text.translate(str.maketrans("0123456789.", "₀₁₂₃₄₅₆₇₈₉."))


def format_mineral_formula(cations, basis_oxygen, mineral_group):
    subscripts = str.maketrans("0123456789.", "₀₁₂₃₄₅₆₇₈₉.")
    
    if mineral_group == "Granat":
        # Granat: X₃Y₂[SiO₄]₃
        # X-Plätze (dodecahedral): Ca, Mg, Fe2+, Mn
        # Y-Plätze (octahedral): Al, Fe3+, Cr
        x_elements = {e: cations.get(e, 0) for e in ["Ca", "Mg", "Fe2+", "Mn"]}
        y_elements = {e: cations.get(e, 0) for e in ["Al", "Fe3+", "Cr"]}
        si = cations.get("Si", 0)
        
        x_total = sum(x_elements.values())
        y_total = sum(y_elements.values())
        si_coeff = round(si / 3, 2) if si > 0 else 0
        
        # Normalisiere auf Si = 1
        if si > 0:
            factor = 1 / (si / 3)
            x_total *= factor
            y_total *= factor
        
        x_str = _format_cation_group(x_elements, subscripts)
        y_str = _format_cation_group(y_elements, subscripts)
        
        x_coeff = _format_coefficient(x_total / 3) if x_total > 0 else ""
        y_coeff = _format_coefficient(y_total / 2) if y_total > 0 else ""
        
        formula = f"{x_str}{x_coeff}{y_str}{y_coeff}[SiO₄]₃"
        return formula
    
    elif mineral_group == "Olivin":
        # Olivin: Mg₁.₈₃Fe²⁺₀.₂₁SiO4
        cation_elements = {e: cations.get(e, 0) for e in ["Mg", "Fe2+", "Mn", "Ca", "Ni"]}
        si = cations.get("Si", 0)

        if si > 0:
            parts = []
            for element in ["Mg", "Fe2+", "Mn", "Ca", "Ni"]:
                value = cation_elements.get(element, 0)
                if value > 0.01:
                    coeff = _format_coefficient(value / si)
                    if coeff:
                        parts.append(f"{element.replace('2+', '²⁺')}{coeff}")
                    else:
                        parts.append(element.replace("2+", "²⁺"))
            return "".join(parts) + "SiO4"

        return "SiO4"
    
    elif mineral_group == "Pyroxen":
        # Pyroxen: (Ca,Mg,Fe)₂(Si,Al)₂O₆ oder X(Y,Z)O₃ mit X=Ca,Mg,Fe und Y,Z=Si,Al
        x_elements = {e: cations.get(e, 0) for e in ["Ca", "Mg", "Fe2+", "Mn"]}
        yz_elements = {e: cations.get(e, 0) for e in ["Si", "Al", "Ti"]}
        
        x_str = _format_cation_group(x_elements, subscripts)
        yz_str = _format_cation_group(yz_elements, subscripts)
        
        formula = f"{x_str}({yz_str})O₆"
        return formula
    
    elif mineral_group == "Amphibol":
        # Amphibol: Ca₂(Mg,Fe)₅[Si₈O₂₂](OH)₂
        ca = cations.get("Ca", 0)
        mg_fe = {e: cations.get(e, 0) for e in ["Mg", "Fe2+", "Mn"]}
        si = cations.get("Si", 0)
        h = cations.get("H", 0)
        
        ca_coeff = _format_coefficient(ca / 2) if ca > 0 else ""
        mg_fe_str = _format_cation_group(mg_fe, subscripts)
        mg_fe_coeff = _format_coefficient(sum(mg_fe.values()) / 5) if sum(mg_fe.values()) > 0 else ""
        si_coeff = _format_coefficient(si / 8) if si > 0 else ""
        h_coeff = _format_coefficient(h / 2) if h > 0 else ""
        
        formula = f"Ca{ca_coeff}({mg_fe_str}){mg_fe_coeff}[Si{si_coeff}O₂₂](OH){h_coeff}"
        return formula
    
    elif mineral_group == "Spinell":
        # Spinell: (Mg,Fe)2+(Al,Fe3+,Cr)₂O₄
        divalent = {e: cations.get(e, 0) for e in ["Mg", "Fe2+", "Zn", "Mn"]}
        trivalent = {e: cations.get(e, 0) for e in ["Al", "Fe3+", "Cr", "Ti"]}
        
        div_str = _format_cation_group(divalent, subscripts)
        triv_str = _format_cation_group(trivalent, subscripts)
        
        formula = f"({div_str})({triv_str})₂O₄"
        return formula
    
    elif mineral_group == "Feldspat":
        # Feldspat: (Ca,Na,K)[Si,Al]₄O₈
        a_site = {e: cations.get(e, 0) for e in ["Ca", "Na", "K"]}
        t_site = {e: cations.get(e, 0) for e in ["Si", "Al"]}
        
        a_str = _format_cation_group(a_site, subscripts)
        t_str = _format_cation_group(t_site, subscripts)
        
        formula = f"({a_str})({t_str})₄O₈"
        return formula
    
    elif mineral_group == "Glimmer":
        # Glimmer: K(Al,Mg,Fe)₂[AlSi₃O₁₀](OH,F)₂
        k = cations.get("K", 0)
        oct = {e: cations.get(e, 0) for e in ["Al", "Mg", "Fe2+", "Li", "Mn"]}
        si = cations.get("Si", 0)
        oh_f = cations.get("H", 0) + cations.get("F", 0) + cations.get("Cl", 0)
        
        k_coeff = _format_coefficient(k)
        oct_str = _format_cation_group(oct, subscripts)
        oct_coeff = _format_coefficient(sum(oct.values()) / 2) if sum(oct.values()) > 0 else ""
        si_coeff = _format_coefficient(si / 3) if si > 0 else ""
        oh_f_coeff = _format_coefficient(oh_f / 2) if oh_f > 0 else ""
        
        formula = f"K{k_coeff}({oct_str}){oct_coeff}[AlSi{si_coeff}O₁₀](OH,F){oh_f_coeff}"
        return formula
    
    elif mineral_group == "Epidot":
        # Epidot: Ca₂(Al,Fe3+)₃[SiO₄][Si₂O₇](OH)
        ca = cations.get("Ca", 0)
        al_fe = {e: cations.get(e, 0) for e in ["Al", "Fe3+", "Mn"]}
        
        ca_coeff = _format_coefficient(ca / 2) if ca > 0 else ""
        al_fe_str = _format_cation_group(al_fe, subscripts)
        al_fe_coeff = _format_coefficient(sum(al_fe.values()) / 3) if sum(al_fe.values()) > 0 else ""
        
        formula = f"Ca{ca_coeff}({al_fe_str}){al_fe_coeff}[SiO₄][Si₂O₇](OH)"
        return formula
    
    else:
        # Allgemein oder unbekannt - einfache Darstellung
        cation_order = element_order.get(mineral_group, element_order["default"])
        visible_cations = {element: value for element, value in cations.items() if value > 0.001}
        if not visible_cations:
            oxygen_str = "O"
            if isinstance(basis_oxygen, float):
                if basis_oxygen.is_integer():
                    oxygen_str += str(int(basis_oxygen)).translate(subscripts)
                else:
                    oxygen_str += f"{basis_oxygen:.1f}".rstrip("0").rstrip(".").translate(subscripts)
            else:
                oxygen_str += str(basis_oxygen).translate(subscripts)
            return oxygen_str
        
        ordered_elements = [element for element in cation_order if element in visible_cations]
        ordered_elements.extend(element for element in visible_cations if element not in ordered_elements)
        
        formula_parts = []
        for element in ordered_elements:
            value = visible_cations[element]
            if value < 0.01:
                continue
            part = element.replace("2+", "²⁺").replace("3+", "³⁺")
            coeff = _format_coefficient(value)
            if coeff:
                part += coeff
            formula_parts.append(part)
        
        oxygen_str = "O"
        if isinstance(basis_oxygen, float):
            if basis_oxygen.is_integer():
                oxygen_str += str(int(basis_oxygen)).translate(subscripts)
            else:
                oxygen_str += f"{basis_oxygen:.1f}".rstrip("0").rstrip(".").translate(subscripts)
        else:
            oxygen_str += str(basis_oxygen).translate(subscripts)
        
        formula_parts.append(oxygen_str)
        return "".join(formula_parts)


def _format_cation_group(elements, subscripts):
    """Formatiert eine Gruppe von Kationen für die strukturelle Formel."""
    parts = []
    for element, value in elements.items():
        if value > 0.01:
            el_str = element.replace("2+", "²⁺").replace("3+", "³⁺")
            parts.append(el_str)
    return ",".join(parts)


def calculate_mineral_formula(oxide_values, basis_oxygen, mineral_group):
    element_moles = {}
    total_oxygen = 0.0

    for oxide, weight in oxide_values.items():
        if weight > 0 and oxide in molar_masses:
            mol_number = weight / molar_masses[oxide]
            for element, count in elements_per_oxide[oxide].items():
                if element == "O":
                    total_oxygen += count * mol_number
                else:
                    element_moles[element] = element_moles.get(element, 0.0) + count * mol_number

    if total_oxygen == 0:
        return None

    normalization_factor = basis_oxygen / total_oxygen
    cations = {element: moles * normalization_factor for element, moles in element_moles.items()}

    if mineral_group == "Pyroxen":
        total_fe_initial = cations.get("Fe2+", 0.0) + cations.get("Fe3+", 0.0)
        if "Fe2+" in cations:
            del cations["Fe2+"]
        if "Fe3+" in cations:
            del cations["Fe3+"]
        if total_fe_initial > 0:
            cations["Fe3+"] = total_fe_initial * 0.1
            cations["Fe2+"] = total_fe_initial * 0.9

    return {
        "cations": cations,
        "formula": format_mineral_formula(cations, basis_oxygen, mineral_group),
        "basis_oxygen": basis_oxygen,
        "total_cations": sum(cations.values()),
        "normalization_factor": normalization_factor,
    }
