import json
from pathlib import Path


class IncinerationEmissions:
    """
    A class to calculate emissions from incineration processes.
    Accepts grouped input sections: fuel_consumption, incinerator_info, energy_recovery.
    """


    def __init__(
        self,
        waste_incinerated: float,
        electricity_kwh_per_day: float,
        fuel_consumption: dict,
        incinerator_info: dict,
        energy_recovery: dict,
        mixed_waste_composition: dict,
    ):
        self.waste_incinerated = waste_incinerated
        self.electricity_used = electricity_kwh_per_day

        # Unpack fuel_consumption dict to lists for calculation
        fc = fuel_consumption or {}
        self.fossil_fuel_types = list(fc.keys())
        self.fossil_fuel_consumptions = list(fc.values())

        # Unpack incinerator_info
        self.incineration_type = (incinerator_info or {}).get("incineration_type", "")
        self.calorific_value_mj_per_kg = (incinerator_info or {}).get("calorific_value_mj_per_kg", None)

        # Unpack energy_recovery
        er = energy_recovery or {}
        self.energy_recovery_type = er.get("energy_recovery_type", "")
        self.efficiency_electricity_recovery = er.get("electricity_recovery_efficiency", 0)
        self.percentage_electricity_used_onsite = er.get("electricity_used_onsite_percent", 0)
        self.efficiency_heat_recovery = er.get("heat_recovery_efficiency", 0)
        self.percentage_heat_used_onsite = er.get("recovered_heat_usage_percent", 0)
        self.fossil_fuel_replaced = er.get("fossil_fuel_replaced", [])

        # Unpack mixed waste composition
        self.mixed_waste_composition = mixed_waste_composition or {}

        # Define file paths for data
        self.incineration_file = (
            Path(__file__).parent.parent / "data" / "incineration.json"
        )
        self.trans_file = Path(__file__).parent.parent / "data" / "transportation.json"

        # Load emission factor data
        self.data_incineration = self._load_json_file(self.incineration_file)
        self.data_trans = self._load_json_file(self.trans_file)

    @staticmethod
    def _load_json_file(file_path: Path) -> dict:
        """
        Load a JSON file and return its content.

        Args:
            file_path (Path): Path to the JSON file.

        Returns:
            dict: Parsed JSON data.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {file_path} was not found.")
        except json.JSONDecodeError:
            raise ValueError(f"Error decoding JSON file: {file_path}")
        
    @staticmethod
    def _normalize_key(value: str) -> str:
        """Normalize strings for key matching (lowercase, underscores)."""
        return str(value).strip().lower().replace(" ", "_")

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
        fuel_data = self.data_incineration.get("fuel_data", [])

        for fuel, consumption in zip(fuel_types, fuel_consumed):
            fuel_entry = next((f for f in fuel_data if f.get("fuel_type") == fuel), None)
            if fuel_entry is not None:
                energy_content = fuel_entry.get("energy_content_mj_per_l", 0)
                emission_factors = fuel_entry.get("emission_factors", {})
                emission_factor = emission_factors.get(factor_key, 0)
                total_emissions += consumption * energy_content * emission_factor

        return total_emissions / per_waste if per_waste > 0 else 0
    
    def _calculate_avoided_emissions(self, factor_key: str) -> float:
        """Compute avoided emissions from energy recovery.

        This method estimates emissions avoided due to energy recovered from
        the incineration process. Heat recovery avoids burning a specified
        fossil fuel by displacing its energy-equivalent. Electricity recovery
        avoids grid electricity emissions.

        Args:
            factor_key: Emission factor key to use for the displaced fuel,
                e.g., "co2_kg_per_mj", "ch4_kg_per_mj", "n2o_kg_per_mj",
                or "bc_kg_per_mj".

        Returns:
            float: Avoided emissions per ton of waste treated, in the same
                pollutant mass unit as the selected factor key (kg/ton).
        """

        # Defaults to robustly handle missing inputs and partial configs
        avoided_total = 0.0
        heat_recovered = 0.0
        electricity_recovered = 0.0

        # ---- Heat energy recovery (MJ -> avoided pollutant mass) ----
        # Displace a specific fossil fuel if provided (use first item if list).
        displaced_fuel = (
            self.fossil_fuel_replaced[0]
            if isinstance(self.fossil_fuel_replaced, list)
            and len(self.fossil_fuel_replaced) > 0
            else None
        )

        if (
            displaced_fuel
            and self.calorific_value_mj_per_kg is not None
            and self.efficiency_heat_recovery > 0
        ):
            fuel_data = self.data_incineration.get("fuel_data", [])
            fuel_obj = next(
                (f for f in fuel_data if f.get("fuel_type") == displaced_fuel),
                None,
            )
            if fuel_obj:
                emission_factor = float(
                    (fuel_obj.get("emission_factors", {}) or {}).get(
                        factor_key, 0
                    )
                    or 0
                )
                # MJ per ton available for sale after on-site heat usage
                total_heat_mj = (
                    (self.efficiency_heat_recovery / 100.0)
                    * 1000.0
                    * self.calorific_value_mj_per_kg
                )
                exportable_heat_mj = (
                    (100.0 - self.percentage_heat_used_onsite) / 100.0
                ) * total_heat_mj
                # Convert exportable MJ to avoided pollutant mass (kg)
                heat_recovered = emission_factor * exportable_heat_mj

        # ---- Electricity energy recovery (MJ -> kWh -> avoided CO2) ----
        # Only relevant when displacing grid electricity (CO2 is applicable).
        if (
            factor_key == "co2_kg_per_mj"
            and self.calorific_value_mj_per_kg is not None
            and self.efficiency_electricity_recovery > 0
        ):
            grid_factor = self.data_trans.get("electricity_grid_factor", {})
            co2_per_kwh = float(grid_factor.get("co2_kg_per_kwh", 0) or 0)
            # Total electricity (kWh/ton) recovered from waste energy (MJ/ton)
            total_elec_kwh = (
                (self.efficiency_electricity_recovery / 100.0)
                * 1000.0
                * self.calorific_value_mj_per_kg
                / 3.6
            )  # MJ to kWh
            sellable_elec_kwh = (
                (100.0 - self.percentage_electricity_used_onsite) / 100.0
            ) * total_elec_kwh
            electricity_recovered = co2_per_kwh * sellable_elec_kwh

        # Combine according to configured recovery mode: heat, electricity, both
        mode = (self.energy_recovery_type or "").strip().lower()
        if mode == "heat":
            avoided_total = heat_recovered
        elif mode == "electricity":
            avoided_total = electricity_recovered
        else:  # both or unspecified
            avoided_total = heat_recovered + electricity_recovered

        return avoided_total


    def waste_combustion_emissions(
        self, incineration_type: str, emission_type: str
    ) -> float:
        """
        Retrieve the emission factor for a given incineration type and emission type.

        Args:
            incineration_type (str): Type of incineration (e.g., 'continuous_stoker').
            emission_type (str): Type of emission (e.g., 'ch4_kg_per_ton').

        Returns:
            float: Emission factor for the given incineration type and emission type.
        """
        incineration_emissions = self.data_incineration.get("incineration_emissions", [])
        entry = next((e for e in incineration_emissions if e.get("type") == incineration_type), None)
        if entry is None:
            raise ValueError(f"Incineration type '{incineration_type}' not found in the dataset.")
        if emission_type not in entry:
            raise ValueError(f"Emission type '{emission_type}' not found for incineration type '{incineration_type}'.")
        return entry[emission_type]

    def ch4_emit_incineration(self) -> float:
        """
        Calculate CH4 (methane) emissions from incineration.

        Returns:
            float: Total CH4 emissions in terms of CO2-equivalent (kg CO2e).
        """
        gwp_factors = self.data_trans.get("gwp_factors", {})
        gwp_100_fossil = gwp_factors.get("ch4_fossil", {}).get("gwp100", 0)
        gwp_100_biogenic = gwp_factors.get("ch4_biogenic", {}).get("gwp100", 0)

        ch4_waste_combustion = self.waste_combustion_emissions(
            self.incineration_type, "ch4_kg_per_ton"
        )
        ch4_fuel_combustion = self._calculate_emissions(
            self.fossil_fuel_types,
            self.fossil_fuel_consumptions,
            "ch4_kg_per_mj",
            self.waste_incinerated,
        )

        total_ch4_emissions = (
            gwp_100_fossil * ch4_fuel_combustion
            + gwp_100_biogenic * ch4_waste_combustion
        )
        return total_ch4_emissions

    def ch4_avoid_incineration(self) -> float:
        """
        Calculate CH4 (methane) emissions avoided due to incineration.

        Returns:
            float: Total CH4 emissions avoided (kg CO2e).
        """
        # Avoided CH4 mass (kg/ton) from recovered energy displacing fossil fuel
        avoided_ch4 = self._calculate_avoided_emissions("ch4_kg_per_mj")
        # Convert avoided CH4 to CO2e using 100-year GWP for fossil CH4
        gwp_factors = self.data_trans.get("gwp_factors", {})
        gwp_100_ch4_fossil = (gwp_factors.get("ch4_fossil", {}) or {}).get("gwp100", 0) or 0
        return gwp_100_ch4_fossil * avoided_ch4
    


    def co2_emit_incineration(self) -> float:
        """
        Calculate CO2 (carbon dioxide) emissions from incineration.

        Returns:
            float: Total CO2 emissions (kg CO2e).
        """
        grid_emission_factor = self.data_trans.get("electricity_grid_factor", {})
        co2_per_kwh = grid_emission_factor.get("co2_kg_per_kwh", 0)
        total_co2_electricity = self.electricity_used * co2_per_kwh / self.waste_incinerated if self.waste_incinerated > 0 else 0

        co2_fuel_combustion = self._calculate_emissions(
            self.fossil_fuel_types,
            self.fossil_fuel_consumptions,
            "co2_kg_per_mj",
            self.waste_incinerated,
        )

        fossil_based_co2_emissions = self.data_incineration.get("fossil_based_co2_emissions", [])
        total_co2_waste_combustion = 0
        for properties in fossil_based_co2_emissions:
            dry_matter_content = properties.get("dry_matter_percent", 0)
            total_carbon_content = properties.get("total_carbon_percent", 0)
            fossil_carbon_fraction = properties.get("fossil_carbon_percent", 0)
            oxidation_factor = properties.get("oxidation_factor_percent", 0)
            waste_type = properties.get("waste_type", "")
            # Get user-provided composition for this waste type
            user_percent = self.mixed_waste_composition.get(waste_type.lower().replace("/", "_").replace(" ", "_"), 0)

            fossil_carbon_wet_waste = (
                (dry_matter_content / 100)
                * (total_carbon_content / 100)
                * (fossil_carbon_fraction / 100)
                * (oxidation_factor / 100)
            )
            co2_emission = (
                1000
                * fossil_carbon_wet_waste
                * (user_percent / 100)
                * (44 / 12)
            )
            total_co2_waste_combustion += co2_emission

        total_co2_emissions = total_co2_electricity + co2_fuel_combustion + total_co2_waste_combustion
        return total_co2_emissions

    def co2_avoid_incineration(self) -> float:
        """
        Calculate CO2 (carbon dioxide) emissions avoided due to incineration.

        Returns:
            float: Total CO2 emissions avoided (kg CO2e).
        """
        # Avoided CO2 from: (a) heat displacing fossil fuel, (b) electricity
        # displacing grid emissions (handled internally when factor_key is CO2)
        return self._calculate_avoided_emissions("co2_kg_per_mj")

    def n2o_emit_incineration(self) -> float:
        """
        Calculate N2O (nitrous oxide) emissions from incineration.

        Returns:
            float: Total N2O emissions in terms of CO2-equivalent (kg CO2e).
        """
        gwp_factors = self.data_trans.get("gwp_factors", {})
        gwp_100_n2o = gwp_factors.get("n2o", {}).get("gwp100", 0)

        n2o_waste_combustion = self.waste_combustion_emissions(
            self.incineration_type, "n2o_kg_per_ton"
        )
        n2o_fuel_combustion = self._calculate_emissions(
            self.fossil_fuel_types,
            self.fossil_fuel_consumptions,
            "n2o_kg_per_mj",
            self.waste_incinerated,
        )

        total_n2o_emissions = gwp_100_n2o * (n2o_fuel_combustion + n2o_waste_combustion)
        return total_n2o_emissions

    def n2o_avoid_incineration(self) -> float:
        """
        Calculate N2O (nitrous oxide) emissions avoided due to incineration.

        Returns:
            float: Total N2O emissions avoided (kg CO2e).
        """
        # Avoided N2O mass (kg/ton) from recovered energy displacing fossil fuel
        avoided_n2o = self._calculate_avoided_emissions("n2o_kg_per_mj")
        # Convert avoided N2O to CO2e using 100-year GWP
        gwp_factors = self.data_trans.get("gwp_factors", {})
        gwp_100_n2o = (gwp_factors.get("n2o", {}) or {}).get("gwp100", 0) or 0
        return gwp_100_n2o * avoided_n2o

    def bc_emit_incineration(self):
        """
        Calculate BC (black carbon) emissions from incineration.
        Returns:
            float: BC mass in kg/ton.
        """
        bc_waste_combustion = self.waste_combustion_emissions(
            self.incineration_type, "bc_kg_per_ton"
        )
        bc_fuel_combustion = self._calculate_emissions(
            self.fossil_fuel_types,
            self.fossil_fuel_consumptions,
            "bc_kg_per_mj",
            self.waste_incinerated,
        )
        bc_mass = bc_fuel_combustion + bc_waste_combustion
        return bc_mass

    def bc_avoid_incineration(self) -> float:
        """
        Calculate black carbon emissions avoided due to incineration.

        Returns:
            float: Total BC emissions avoided (kg CO2e).
        """
        # Avoided BC mass (kg/ton) from recovered energy displacing fossil fuel
        return self._calculate_avoided_emissions("bc_kg_per_mj")

    def overall_emissions(self):
        """
        Calculate kgCO2e emissions and emissions avoided per ton of waste treated for incineration, plus total (kgCO2e) outputs.
        Returns:
            dict: A dictionary containing emissions, avoided emissions, total emissions, 
                total avoided emissions, and net emissions. BC is reported as both mass (kg/ton) and CO2e (kgCO2e/ton).
        """
        ch4_e = self.ch4_emit_incineration()
        ch4_a = self.ch4_avoid_incineration()
        co2_e = self.co2_emit_incineration()
        co2_a = self.co2_avoid_incineration()
        n2o_e = self.n2o_emit_incineration()
        n2o_a = self.n2o_avoid_incineration()
        bc_e = self.bc_emit_incineration()
        bc_a = self.bc_avoid_incineration()

        # Totals in CO2e exclude BC mass
        total_emissions = ch4_e + co2_e + n2o_e
        total_emissions_avoid = ch4_a + co2_a + n2o_a
        net_emissions = total_emissions - total_emissions_avoid
        net_emissions_bc = bc_e - bc_a

        # Total outputs (kgCO2e, not per tonne)
        multiplier = self.waste_incinerated if self.waste_incinerated > 0 else 1
        return {
            "ch4_emissions": ch4_e,
            "ch4_emissions_avoid": ch4_a,
            "co2_emissions": co2_e,
            "co2_emissions_avoid": co2_a,
            "n2o_emissions": n2o_e,
            "n2o_emissions_avoid": n2o_a,
            "bc_emissions": bc_e,
            "bc_emissions_avoid": bc_a,
            "total_emissions": total_emissions,
            "total_emissions_avoid": total_emissions_avoid,
            "net_emissions": net_emissions,
            "net_emissions_bc": net_emissions_bc,

            # New total outputs (kgCO2e, not per tonne)
            "ch4_emissions_total": ch4_e * multiplier,
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