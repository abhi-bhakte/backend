import json
import math
from pathlib import Path
from typing import Optional, Dict
from .transportation import TransportationEmissions


class LandfillEmissions:
    # Landfill operational condition factors (default values; could be moved to JSON later)
    _LANDFILL_PROPERTIES = {
        'sanitary_without_gas': {'mcf': 1.0, 'ox': 0.1},
        'sanitary_with_gas': {'mcf': 1.0, 'ox': 0.1},
        'managed_semi_aerobic': {'mcf': 0.5, 'ox': 0.0},
        'open_dumping_deep': {'mcf': 0.8, 'ox': 0.0},
        'open_dumping_shallow': {'mcf': 0.4, 'ox': 0.0},
        'uncategorized': {'mcf': 0.6, 'ox': 0.0},
    }

    # Waste properties with DOC fraction, composition (% of total), and first-order decay rate constant k
    _WASTE_PROPERTIES = {
        'food': {'doc': 0.152, 'composition': 40.30,'rate_constant': 0.4},
        'garden': {'doc': 0.196, 'composition': 0.0, 'rate_constant': 0.17},
        'plastic': {'doc': 0.0, 'composition': 6.4, 'rate_constant': 0.0},
        'paper': {'doc': 0.41, 'composition': 11.30, 'rate_constant': 0.07},
        'textile': {'doc': 0.32, 'composition': 2.5, 'rate_constant': 0.07},
        'rubber': {'doc': 0.45024, 'composition': 0.8, 'rate_constant': 0.035},
        'glass': {'doc': 0.0, 'composition': 3.5, 'rate_constant': 0.0},
        'metal': {'doc': 0.0, 'composition': 3.8, 'rate_constant': 0.0},
        'nappies': {'doc': 0.252, 'composition': 0.0, 'rate_constant': 0.17},
        'wood': {'doc': 0.425, 'composition': 7.9, 'rate_constant': 0.035},
        'hazardous': {'doc': 0.0, 'composition': 0.0, 'rate_constant': 0.0},
        'others': {'doc': 0.0, 'composition': 21.9, 'rate_constant': 0.0},
    }

    # Default constants
    _DOCF = 0.5  # Fraction of DOC decomposing under anaerobic conditions
    _F_CH4 = 0.5  # Fraction of CH4 in landfill gas

    def _gwp100(self, key: str) -> float:
        """Return GWP100 using the exact JSON key from transportation data."""
        gwp = self.data_trans.get("gwp_factors", {})
        return gwp.get(key, {}).get("gwp100", 0)
    """
    A class to calculate GHG emissions (CH₄, CO₂, N₂O, BC) from landfill operations.

    Attributes:
        waste_disposed (float): Amount of waste disposed at the site (tons).
        waste_disposed_fired (float): Percentage of waste disposed via open burning (tons).
        landfill_type (str): Type of landfill (e.g., "landfill", "open dump").
        start_year (int): Starting year of waste disposal.
        end_year (int): End year of waste disposal.
        current_year (int): Current year of disposal.
        annual_growth_rate (float): Estimated growth of annual disposal at the landfill (%).
        fossil_fuel_types (list[str]): Types of fossil fuels used for operation activities.
        fossil_fuel_consumed (list[float]): Consumption of fossil fuels used for operation activities (liters).
        electricity_kwh_per_day (float): Grid electricity used for operation activities (kWh).
        gas_collection_efficiency (float): Efficiency of gas collection (%).
        gas_treatment_method (str): Treatment method of collected landfill gas.
        lfg_utilization_efficiency (float): LFG utilization efficiency (e.g., electricity production, flare efficiency).
        gas_recovery_start_year (int): Starting year of gas recovery after commencing the landfill.
        gas_recovery_end_year (int): Closing year of gas recovery project.
        replaced_fossil_fuel_type (str): Type of fossil fuel replaced by recovered LFG.
    """

    def __init__(
        self,
        waste_disposed: float,
        waste_disposed_fired: float,
        landfill_type: str,
        start_year: int,
        end_year: int,
        current_year: int,
        annual_growth_rate: float,
        fossil_fuel_types: list,
        fossil_fuel_consumed: list,
        electricity_kwh_per_day: float,
        gas_collection_efficiency: float = 0.0,
        gas_treatment_method: str = None,
        lfg_utilization_efficiency: float = 0.0,
        gas_recovery_start_year: int = None,
        gas_recovery_end_year: int = None,
        replaced_fossil_fuel_type: str = None,
        mix_waste_composition: Optional[Dict[str, float]] = None,
    ):
        """
        Initialize the LandfillEmissions class and validate inputs.

        Args:
            waste_disposed (float): Amount of waste disposed at the site (tons).
            waste_disposed_fired (float): Percentage of waste disposed via open burning (tons).
            landfill_type (str): Type of landfill (e.g., "landfill", "open dump").
            start_year (int): Starting year of waste disposal.
            end_year (int): End year of waste disposal.
            current_year (int): Current year of disposal.
            annual_growth_rate (float): Estimated growth of annual disposal at the landfill (%).
            fossil_fuel_types (list[str]): Types of fossil fuels used for operation activities.
            fossil_fuel_consumed (list[float]): Consumption of fossil fuels used for operation activities (liters).
            electricity_kwh_per_day (float): Grid electricity used for operation activities (kWh).
            gas_collection_efficiency (float): Efficiency of gas collection (%).
            gas_treatment_method (str): Treatment method of collected landfill gas.
            lfg_utilization_efficiency (float): LFG utilization efficiency (e.g., electricity production, flare efficiency).
            gas_recovery_start_year (int): Starting year of gas recovery after commencing the landfill.
            gas_recovery_end_year (int): Closing year of gas recovery project.
            replaced_fossil_fuel_type (str): Type of fossil fuel replaced by recovered LFG.

        Raises:
            ValueError: If any numeric inputs are negative or invalid.
        """
        # Validate inputs
        if any(
            x < 0
            for x in [
                waste_disposed,
                annual_growth_rate,
                electricity_kwh_per_day,
                gas_collection_efficiency,
                lfg_utilization_efficiency,
            ]
        ):
            raise ValueError("Numeric values cannot be negative.")
        if any(x < 0 for x in fossil_fuel_consumed):
            raise ValueError("Fossil fuel consumption values cannot be negative.")
        if start_year > end_year or current_year < start_year or current_year > end_year:
            raise ValueError("Invalid year range for disposal or recovery.")

        # Initialize attributes
        self.waste_disposed = waste_disposed
        self.waste_disposed_fired = waste_disposed_fired
        self.landfill_type = landfill_type
        self.start_year = start_year
        self.end_year = end_year
        self.current_year = current_year
        self.annual_growth_rate = annual_growth_rate
        self.fossil_fuel_types = fossil_fuel_types
        self.fossil_fuel_consumed = fossil_fuel_consumed
        self.electricity_kwh_per_day = electricity_kwh_per_day
        self.gas_collection_efficiency = gas_collection_efficiency
        self.gas_treatment_method = gas_treatment_method
        self.lfg_utilization_efficiency = lfg_utilization_efficiency
        self.gas_recovery_start_year = gas_recovery_start_year
        self.gas_recovery_end_year = gas_recovery_end_year
        self.replaced_fossil_fuel_type = replaced_fossil_fuel_type
        self._composition_map = self._build_default_composition_map()
        if mix_waste_composition:
            self._apply_mix_composition(mix_waste_composition)

        # Load emission factor data
        self.trans_file = Path(__file__).parent.parent / "data" / "transportation.json"
        self.landfill_file = Path(__file__).parent.parent / "data" / "landfill.json"

        self.data_landfill = self._load_json_file(self.landfill_file)
        self.data_trans = self._load_json_file(self.trans_file)

    def _build_default_composition_map(self) -> dict:
        """Return a name->percentage map from default _WASTE_PROPERTIES."""
        return {k: v.get('composition', 0.0) for k, v in self._WASTE_PROPERTIES.items()}

    @staticmethod
    def _normalize_percentages(values: dict[str, float]) -> dict[str, float]:
        total = sum(max(0.0, float(v)) for v in values.values())
        if total <= 0:
            return {k: 0.0 for k in values}
        return {k: (max(0.0, float(v)) * 100.0 / total) for k, v in values.items()}

    def _apply_mix_composition(self, mix: dict):
        """
        Apply a frontend-provided mixed waste composition, supporting either percentages
        (sum≈100) or absolute masses which are normalized to percentages. Keys are matched
        to our known categories. Unspecified categories default to 0, and any remainder is
        assigned to 'others'.
        """
        # Accept common aliases
        alias_map = {
            'plastic': 'plastic',
            'rubber': 'rubber',
            'nappies': 'nappies',
            'hazardous': 'hazardous',
            'others': 'others',
        }
        cleaned: dict[str, float] = {}
        for k, v in (mix or {}).items():
            key = str(k).strip().lower()
            key = alias_map.get(key, key)
            cleaned[key] = max(0.0, float(v))

        # Only keep known categories
        known = {k: cleaned.get(k, 0.0) for k in self._WASTE_PROPERTIES.keys()}

        s = sum(known.values())
        # Heuristic: if numbers look like percentages (<=100 and sum<=100*len in extreme), treat as percentages
        looks_like_percent = s > 0 and all(v <= 100.0 for v in known.values()) and s <= 1000.0
        if not looks_like_percent:
            # Normalize masses to percentages
            known = self._normalize_percentages(known)

        # Ensure total is 100 by putting remainder to 'others'
        total_pct = sum(known.values())
        remainder = max(0.0, 100.0 - total_pct)
        if 'others' in known:
            known['others'] = known.get('others', 0.0) + remainder
        else:
            known['others'] = remainder

        # Clamp minor floats and assign
        self._composition_map = {k: float(known.get(k, 0.0)) for k in self._WASTE_PROPERTIES.keys()}

    @staticmethod
    def _load_json_file(file_path: Path) -> dict:
        """
        Load a JSON file and return its content.

        Args:
            file_path (Path): Path to the JSON file.

        Returns:
            dict: Parsed JSON data.

        Raises:
            FileNotFoundError: If the file is not found.
            ValueError: If the JSON file cannot be decoded.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {file_path} was not found.")
        except json.JSONDecodeError:
            raise ValueError(f"Error decoding JSON file: {file_path}")

    def _calculate_emissions(
        self, fuel_types: list, fuel_consumed: list, factor_key: str, per_waste: float
    ) -> float:
        """
        Calculate emissions for different gases based on fuel consumption.

        Args:
            fuel_types (list): List of fuel types used.
            fuel_consumed (list): Corresponding fuel consumption in liters per tonne waste treated.
            factor_key (str): Key for the emission factor in the JSON file (e.g., 'co2_kg_per_mj').
            per_waste (float): Amount of waste incinerated.

        Returns:
            float: Emissions per ton of waste.
        """
        if not isinstance(fuel_types, list):
            fuel_types = [fuel_types]
        if not isinstance(fuel_consumed, list):
            fuel_consumed = [fuel_consumed]

        total_emissions = 0
        fuel_data = self.data_landfill.get("fuel_data", [])

        for fuel, consumption in zip(fuel_types, fuel_consumed):
            fuel_entry = next((f for f in fuel_data if f.get("fuel_type") == fuel), None)
            if fuel_entry is not None:
                energy_content = fuel_entry.get("energy_content_mj_per_l", 0)
                emission_factors = fuel_entry.get("emission_factors", {})
                emission_factor = emission_factors.get(factor_key, 0)
                total_emissions += consumption * energy_content * emission_factor

        amount_deposited = self.waste_disposed * (100 - self.waste_disposed_fired) / 100

        return total_emissions / amount_deposited if amount_deposited > 0 else 0
    
    def _biogenic_ch4_mass_per_ton(self) -> float:
        """Return biogenic CH₄ mass (kg CH₄ per ton waste) using first-order decay.

        This mirrors prior biogenic computation but returns mass, leaving CO₂-eq
        conversion to the caller.
        """
        # Amount of waste actually landfilled (excluding open burning)
        waste_burned_pct = self.waste_disposed_fired  # treated as percent
        waste_deposited = self.waste_disposed
        landfill_waste_daily_gg = waste_deposited * (100 - waste_burned_pct) * 0.01 * 0.001  # Gg/day

        props = self._LANDFILL_PROPERTIES.get(
            self.landfill_type,
            self._LANDFILL_PROPERTIES['uncategorized'],
        )
        mcf = props['mcf']
        ox = props['ox']

        # Growth adjusted initial annual waste (Gg/year)
        w0 = (landfill_waste_daily_gg * 365) / (1 + 0.01 * self.annual_growth_rate) ** (
            self.current_year - self.start_year
        )
        initial_deposit = w0

        # Weighted average DOC from (possibly overridden) composition
        weighted_doc = 0.0
        for name, vals in self._WASTE_PROPERTIES.items():
            comp_pct = self._composition_map.get(name, vals.get('composition', 0.0))
            weighted_doc += (comp_pct / 100.0) * vals['doc']

        # Weighted decay rate constant k
        k_weighted = 0.0
        for name, vals in self._WASTE_PROPERTIES.items():
            comp_pct = self._composition_map.get(name, vals.get('composition', 0.0))
            k_weighted += (comp_pct / 100.0) * vals['rate_constant']

        exp_decay = math.exp(-k_weighted)

        # Initialize tracking variables
        total_waste_deposited = 0.0
        total_ch4_generated = 0.0
        h_last = w0 * weighted_doc * self._DOCF * mcf  # initial DDOCm accumulated

        for i in range(1, 101):  # 100-year horizon
            year = self.start_year + i
            if year > self.end_year:
                w = 0.0
            elif year == self.current_year:
                w = 365 * landfill_waste_daily_gg
            else:
                w = w0 * (1 + 0.01 * self.annual_growth_rate)
            w0 = w

            # Decomposable DOC deposited (DDOCm)
            d = w * weighted_doc * self._DOCF * mcf
            # Assume immediate fraction reacting (simplified: all new deposit subject to future decay)
            # Accumulated at end of year
            h = (d) + h_last * exp_decay
            # DDOCm decomposed during year
            e = (h_last * (1 - exp_decay))
            # CH4 generated (Gg CH4)
            ch4_year = e * self._F_CH4 * 16 / 12
            total_ch4_generated += ch4_year
            total_waste_deposited += w
            h_last = h

        total_waste_deposited += initial_deposit

        # Oxidation adjustment (fugitive share)
        ch4_fugitive = total_ch4_generated * (1 - ox)  # Gg CH4
        # Convert Gg CH4 to kg CH4 per ton waste: 1 Gg = 1e9 g = 1e6 kg
        kg_ch4_total = ch4_fugitive * 1_000_000.0
        # total waste deposited (w) was in Gg/year, convert to tonnes: 1 Gg = 1e6 kg = 1000 tonnes
        tonnes_waste = total_waste_deposited * 1000.0
        kg_ch4_per_ton = kg_ch4_total / tonnes_waste if tonnes_waste > 0 else 0.0

        return kg_ch4_per_ton

    def ch4_emit_landfill(self) -> float:
        """Calculate total CH₄ emissions (kg CO₂-eq) per ton of waste landfilled.

        Combines fossil CH₄ from fuel combustion and biogenic CH₄ from waste
        degradation. Each component is converted to CO₂-eq with its respective
        GWP100 factor, then summed.

        Returns:
            float: Total CH₄ emissions (CO₂-eq) per ton of waste.
        """
        # Fossil CH4 from fuel combustion (kg CH4 per ton converted to CO2-eq)
        ch4_fossil_mass = self._calculate_emissions(
            self.fossil_fuel_types,
            self.fossil_fuel_consumed,
            "ch4_kg_per_mj",
            self.waste_disposed,
        )
        gwp_100_fossil = self._gwp100("ch4_fossil")
        ch4_fossil_co2e = ch4_fossil_mass * gwp_100_fossil

        # Biogenic CH4 (already returned as kg CH4 per ton); convert using biogenic GWP
        ch4_biogenic_mass = self._biogenic_ch4_mass_per_ton()
        gwp_100_biogenic = self._gwp100("ch4_biogenic")
        ch4_biogenic_co2e = ch4_biogenic_mass * gwp_100_biogenic

        # Store breakdown for later reporting
        self._last_ch4_fossil = ch4_fossil_co2e
        self._last_ch4_biogenic = ch4_biogenic_co2e

        return ch4_fossil_co2e + ch4_biogenic_co2e


    def ch4_avoid_landfill(self):
        """
        Calculate CH₄ emissions avoided per ton of waste landfilled.

        Returns:
            float: Avoided CH₄ emissions (to be implemented).
        """
        return 0.0  # Placeholder for avoided CH₄ emissions calculation

    def co2_emit_landfill(self) -> float:
        """
        Calculate CO₂ emissions (kg CO₂-eq) per ton of waste landfilled.

        Returns:
            float: CO₂ emissions from electricity and fuel combustion.
        """
        grid_emission_factor = self.data_trans.get("electricity_grid_factor", {})
        co2_per_kwh = grid_emission_factor.get("co2_kg_per_kwh", 0)

        amount_deposited = self.waste_disposed * (100 - self.waste_disposed_fired) / 100

        total_co2_electricity = self.electricity_kwh_per_day * co2_per_kwh / amount_deposited if amount_deposited > 0 else 0

        co2_fuel_combustion = self._calculate_emissions(
            self.fossil_fuel_types,
            self.fossil_fuel_consumed,
            "co2_kg_per_mj",
            self.waste_disposed,
        )
        return co2_fuel_combustion + total_co2_electricity

    def co2_avoid_landfill(self):
        """
        Calculate avoided CO₂ emissions (kg CO₂-eq) per ton of waste landfilled.

        Returns:
            float: Avoided CO₂ emissions (to be implemented).
        """
        return 0.0

    def n2o_emit_landfill(self) -> float:
        """
        Calculate N₂O emissions (kg CO₂-eq) per ton of waste landfilled, applying GWP100.

        Returns:
            float: N₂O emissions from fuel combustion, as CO₂-eq.
        """
        n2o_fuel_combustion = self._calculate_emissions(
            self.fossil_fuel_types,
            self.fossil_fuel_consumed,
            "n2o_kg_per_mj",
            self.waste_disposed,
        )
        gwp_100_n2o = self._gwp100("n2o")
        return n2o_fuel_combustion * gwp_100_n2o

    def n2o_avoid_landfill(self):
        """
        Calculate avoided N₂O emissions (kg CO₂-eq) per ton of waste landfilled.

        Returns:
            float: Avoided N₂O emissions (to be implemented).
        """
        return 0.0

    def bc_emit_landfill(self) -> float:
        """
        Calculate black carbon (BC) emissions (kg CO₂-eq) per ton of waste landfilled.

        Returns:
            float: BC emissions from fuel combustion.
        """
        bc_fuel_combustion = self._calculate_emissions(
            self.fossil_fuel_types,
            self.fossil_fuel_consumed,
            "bc_kg_per_mj",
            self.waste_disposed,
        )
        return bc_fuel_combustion

    def bc_avoid_landfill(self):
        """
        Calculate avoided black carbon (BC) emissions (kg CO₂-eq) per ton of waste landfilled.

        Returns:
            float: Avoided BC emissions (to be implemented).
        """
        return 0.0  # Placeholder for avoided BC emissions calculation

    def overall_emissions(self) -> dict:
        """
        Calculate kgCO2e emissions and BC mass per ton of waste treated, and also total (kgCO2e) outputs.

        Returns:
            dict: Dictionary containing all emissions, avoided emissions, total emissions,
                  total avoided emissions, and net emissions. BC is reported as mass (kg/ton and kg).
        """
        ch4_total = self.ch4_emit_landfill()
        ch4_a = self.ch4_avoid_landfill()
        # Retrieve breakdown from last calculation (fallback to 0 if missing)
        ch4_fossil = getattr(self, "_last_ch4_fossil", 0.0)
        ch4_biogenic = getattr(self, "_last_ch4_biogenic", 0.0)
        co2_e = self.co2_emit_landfill()
        co2_a = self.co2_avoid_landfill()
        n2o_e = self.n2o_emit_landfill()
        n2o_a = self.n2o_avoid_landfill()
        bc_e = self.bc_emit_landfill()
        bc_a = self.bc_avoid_landfill()

        total_emissions = ch4_total + co2_e + n2o_e
        total_emissions_avoid = ch4_a + co2_a + n2o_a
        net_emissions = total_emissions - total_emissions_avoid
        net_emissions_bc = bc_e - bc_a

        multiplier = self.waste_disposed if self.waste_disposed > 0 else 1

        return {
            "ch4_emissions": ch4_total,
            "ch4_emissions_avoid": ch4_a,
            "co2_emissions": co2_e,
            "co2_emissions_avoid": co2_a,
            "n2o_emissions": n2o_e,
            "n2o_emissions_avoid": n2o_a,
            "bc_emissions": bc_e,           # kg BC/ton
            "bc_emissions_avoid": bc_a,     # kg BC/ton
            "total_emissions": total_emissions,
            "total_emissions_avoid": total_emissions_avoid,
            "net_emissions": net_emissions,
            "net_emissions_bc": net_emissions_bc, # kg BC/ton

            # New total outputs (kgCO2e, not per tonne)
            "ch4_emissions_total": ch4_total * multiplier,
            "ch4_emissions_avoid_total": ch4_a * multiplier,
            "co2_emissions_total": co2_e * multiplier,
            "co2_emissions_avoid_total": co2_a * multiplier,
            "n2o_emissions_total": n2o_e * multiplier,
            "n2o_emissions_avoid_total": n2o_a * multiplier,
            "bc_emissions_total": bc_e * multiplier,
            "bc_emissions_avoid_total": bc_a * multiplier,
            "total_emissions_total": total_emissions * multiplier,
            "total_emissions_avoid_total": total_emissions_avoid * multiplier,
            "net_emissions_total": net_emissions * multiplier,
            "net_emissions_bc_total": net_emissions_bc * multiplier,
        }