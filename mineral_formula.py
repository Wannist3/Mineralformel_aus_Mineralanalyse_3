from __future__ import annotations

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

    cation_order = element_order.get(mineral_group, element_order["default"])
    visible_cations = {element: value for element, value in cations.items() if value > 0.001}
    if not visible_cations:
        return f"O{basis_oxygen}"

    reference_element = "Si" if "Si" in visible_cations else next((element for element in cation_order if element in visible_cations), None)
    if reference_element is None:
        reference_element = max(visible_cations, key=visible_cations.get)

    reference_value = visible_cations[reference_element]
    normalized_cations = {
        element: value / reference_value
        for element, value in visible_cations.items()
    }

    ordered_elements = [element for element in cation_order if element in normalized_cations and element != reference_element]
    ordered_elements.extend(element for element in normalized_cations if element not in ordered_elements and element != reference_element)
    if reference_element in normalized_cations:
        ordered_elements.append(reference_element)

    formula_parts = []
    for element in ordered_elements:
        value = normalized_cations[element]
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
            oxygen_str += str(int(basis_oxygen))
        else:
            oxygen_str += f"{basis_oxygen:.1f}".rstrip("0").rstrip(".").translate(subscripts)
    else:
        oxygen_str += str(basis_oxygen)

    formula_parts.append(oxygen_str)
    return "".join(formula_parts)


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
