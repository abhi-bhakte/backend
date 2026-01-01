"""
NOTE:
For CNG and coal, the energy content values in the JSON file are actually in units of MJ per kg, 
not MJ per liter. However, for consistency, the JSON key remains "energy_content_mj_per_l". 
Users should enter CNG and coal consumption in kg, and the code will interpret the energy 
content accordingly for these fuels. This is to maintain database structure consistency.
"""
import json
from pathlib import Path

class RecyclingEmissions:
    """
    A class to calculate GHG emissions (CH₄, CO₂, N₂O) from recycling operations.

    Attributes:
        recycle_collected_formal (float): Total recyclable collected by the formal sector (tons).
        recycle_collected_informal (float): Total recyclable collected by the informal sector (tons).
        material_composition_formal (dict): Composition (%) of materials collected by the formal sector.
        material_composition_informal (dict): Composition (%) of materials collected by the informal sector.
        electricity_consumed (dict): Electricity consumed during recycling for each material (kWh).
        fuel_types_operation (dict): Types of fuel used in recycling operations for each material.
        fuel_consumed_operation (dict): Fuel consumption in liters for each material.
        recyclability (dict): Recyclability of materials.
    """

    def __init__(
        self,
        recycle_collected_formal: float,
        recycle_collected_informal: float,
        material_composition_formal: dict,
        material_composition_informal: dict,
        electricity_consumed: dict,
        fuel_consumption: dict, 
        recyclability: dict,
    ):
        # Validate inputs
        if any(x < 0 for x in [recycle_collected_formal, recycle_collected_informal]):
            raise ValueError("Recyclable collection values cannot be negative.")
        if any(value < 0 for value in electricity_consumed.values()):
            raise ValueError("Electricity consumption values cannot be negative.")
        for mat, fuels in fuel_consumption.items():
            if any(v < 0 for v in fuels.values()):
                raise ValueError(f"Fuel consumption values for {mat} cannot be negative.")

        self.recycle_collected_formal = recycle_collected_formal
        self.recycle_collected_informal = recycle_collected_informal
        self.material_composition_formal = material_composition_formal
        self.material_composition_informal = material_composition_informal
        self.electricity_consumed = electricity_consumed
        self.recyclability = recyclability
        self.fuel_types_operation = {}
        self.fuel_consumed_operation = {}
        for material, fuels in fuel_consumption.items():
            self.fuel_types_operation[material] = list(fuels.keys())
            self.fuel_consumed_operation[material] = list(fuels.values())

        # Define file paths for data
        self.recycling_file = Path(__file__).parent.parent / "data" / "recycling.json"
        self.trans_file = Path(__file__).parent.parent / "data" / "transportation.json"

        # Load emission factor data
        try:
            with open(self.recycling_file, "r", encoding="utf-8") as file:
                self.data_recycling = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {self.recycling_file} was not found.")
        except json.JSONDecodeError:
            raise ValueError("Error decoding JSON file. Please check the format.")

        try:
            with open(self.trans_file, "r", encoding="utf-8") as file:
                self.data_trans = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {self.trans_file} was not found.")
        except json.JSONDecodeError:
            raise ValueError("Error decoding JSON file. Please check the format.")

    def _calculate_fuel_emissions(self, fuel_types, fuel_consumed, factor_key):
        """
        Calculate emissions for different gases based on fuel consumption.

        Args:
            fuel_types (list[str]): List of fuel types used.
            fuel_consumed (list[float]): Corresponding fuel consumption in liters per tonne waste treated.
            factor_key (str): Key for the emission factor in the JSON file (should match emission_factors keys directly).

        Returns:
            float: Emissions per ton of waste.
        """
        # Ensure inputs are lists
        if not isinstance(fuel_types, list):
            fuel_types = [fuel_types]
        if not isinstance(fuel_consumed, list):
            fuel_consumed = [fuel_consumed]

        total_emissions = 0

        # Retrieve fuel data from the dataset (now a list of dicts)
        fuel_data_list = self.data_recycling.get("fuel_data", [])

        # Iterate through each fuel type and compute emissions
        for fuel, consumption in zip(fuel_types, fuel_consumed):
            for fuel_entry in fuel_data_list:
                if fuel_entry.get("fuel_type") == fuel:
                    energy_content = fuel_entry.get("energy_content_mj_per_l", 0)
                    emission_factors = fuel_entry.get("emission_factors", {})
                    emission_factor = emission_factors.get(factor_key, 0)
                    # Calculate emissions based on energy content and emission factor
                    total_emissions += consumption * energy_content * emission_factor
                    break

        return total_emissions

    def _emission_breakdown(self, emission_factor_key, include_electricity=False):
        """Return per-ton emissions for formal, informal, and combined waste streams."""
        total_collected = self.recycle_collected_formal + self.recycle_collected_informal
        if total_collected > 0:
            formal_fraction = self.recycle_collected_formal / total_collected
            informal_fraction = self.recycle_collected_informal / total_collected
        else:
            formal_fraction = 0
            informal_fraction = 0

        grid_factor = self.data_recycling["electricity_grid_factor"].get("co2_kg_eq_per_kwh", 0) if include_electricity else 0

        formal_per_ton = 0
        for material, composition_percentage in self.material_composition_formal.items():
            fuel_emissions = (composition_percentage / 100) * self._calculate_fuel_emissions(
                self.fuel_types_operation.get(material, []),
                self.fuel_consumed_operation.get(material, []),
                emission_factor_key,
            )
            electricity_emissions = (composition_percentage / 100) * (
                self.electricity_consumed.get(material, 0) * grid_factor
            ) if include_electricity else 0
            formal_per_ton += fuel_emissions + electricity_emissions

        informal_per_ton = 0
        for material, composition_percentage in self.material_composition_informal.items():
            fuel_emissions = (composition_percentage / 100) * self._calculate_fuel_emissions(
                self.fuel_types_operation.get(material, []),
                self.fuel_consumed_operation.get(material, []),
                emission_factor_key,
            )
            electricity_emissions = (composition_percentage / 100) * (
                self.electricity_consumed.get(material, 0) * grid_factor
            ) if include_electricity else 0
            informal_per_ton += fuel_emissions + electricity_emissions

        combined_per_ton = (
            formal_per_ton * formal_fraction + informal_per_ton * informal_fraction
            if total_collected > 0
            else 0
        )

        return {
            "formal_per_ton": formal_per_ton,
            "informal_per_ton": informal_per_ton,
            "combined_per_ton": combined_per_ton,
        }
    


    def _calculate_avoided_emissions(self, factor_key: str) -> float:
        """
        Compute avoided emissions per ton for formal and informal streams.

        This estimates emissions avoided by substituting virgin material
        production with recycled inputs across paper, plastic, aluminum, steel,
        and glass. Results are weighted by material composition and
        recyclability for each stream.

        Args:
            factor_key (str): Emission factor key. One of
                "co2_kg_per_mj", "ch4_kg_per_mj", "n2o_kg_per_mj",
                or "bc_kg_per_mj".

        Returns:
            tuple[float, float]: (formal_avoided_per_ton, informal_avoided_per_ton).
                Units depend on `factor_key`:
                - "co2_kg_per_mj": kg CO2 per ton
                - "ch4_kg_per_mj": kg CH4 per ton
                - "n2o_kg_per_mj": kg N2O per ton
                - "bc_kg_per_mj": kg BC per ton
        """
        total_collected = (
            self.recycle_collected_formal + self.recycle_collected_informal
        )
        if total_collected > 0:
            formal_fraction = self.recycle_collected_formal / total_collected
            informal_fraction = self.recycle_collected_informal / total_collected
        else:
            formal_fraction = 0.0
            informal_fraction = 0.0

        # Accumulators for avoided emissions across streams
        formal_avoided = 0.0
        informal_avoided = 0.0

        # Shortcut index for fuel metadata
        fuel_data = {
            fd["fuel_type"]: fd for fd in self.data_recycling.get("fuel_data", [])
        }

        # ---------------------
        # Virgin paper emissions
        # ---------------------
        virgin_paper = (
            self.data_recycling.get("virgin_material_production", {}).get("paper", {})
        )
        virgin_paper_emission = 0.0

        if factor_key in ("ch4_kg_per_mj", "n2o_kg_per_mj"):
            # Fossil energy share times respective fuel emission factors (per MJ)
            total_energy_mj = virgin_paper.get(
                "total_energy_requirement_mj_per_ton", 0
            )
            biomass_pct = virgin_paper.get("energy_supply_from_biomass_percent", 0)
            cng_pct = virgin_paper.get("energy_supply_from_cng_percent", 0)
            diesel_pct = virgin_paper.get(
                "energy_supply_from_fossil_fuel_percent", 0
            )

            cng_factor = (
                fuel_data.get("cng", {})
                .get("emission_factors", {})
                .get(factor_key, 0)
            )
            diesel_factor = (
                fuel_data.get("diesel", {})
                .get("emission_factors", {})
                .get(factor_key, 0)
            )

            fossil_energy_mj = total_energy_mj * (100 - biomass_pct) / 100
            virgin_paper_emission = (
                fossil_energy_mj * (cng_pct / 100) * cng_factor
                + fossil_energy_mj * (diesel_pct / 100) * diesel_factor
            )

        elif factor_key == "bc_kg_per_mj":
            # BC share expressed relative to PM2.5 mass
            pm25_mass = virgin_paper.get("pm2.5_dried_pulp_kg_per_mg", 0)
            bc_pct = virgin_paper.get("bc_pm2.5_dried_pulp_percent", 0)
            virgin_paper_emission = pm25_mass * bc_pct / 100

        elif factor_key == "co2_kg_per_mj":
            # Weighted average across paper grades (kgCO2/tonne)
            weighted_avg_ton = (
                virgin_paper.get("corrugated_containers_percent", 0) / 100
                * virgin_paper.get("corrugated_containers_co2_kg_per_tonne", 0)
                + virgin_paper.get("magazines_mail_percent", 0) / 100
                * virgin_paper.get("magazines_mail_co2_kg_per_tonne", 0)
                + virgin_paper.get("newspapers_percent", 0) / 100
                * virgin_paper.get("newspapers_co2_kg_per_tonne", 0)
                + virgin_paper.get("office_paper_percent", 0) / 100
                * virgin_paper.get("office_paper_co2_kg_per_tonne", 0)
            )
            # Unit conversion retained from original implementation
            virgin_paper_emission = weighted_avg_ton * 1000 / 0.907

        # ----------------------
        # Virgin plastic emissions
        # ----------------------
        virgin_plastic = (
            self.data_recycling.get("virgin_material_production", {})
            .get("plastic", {})
        )

        # Average fossil energy (GJ/tonne) and electricity (MWh/tonne) across polymers
        fossil_hdpe = virgin_plastic.get("fossil_energy_hdpe_gj_per_tonne", 0)
        fossil_ldpe = virgin_plastic.get("fossil_energy_ldpe_gj_per_tonne", 0)
        fossil_pp = virgin_plastic.get("fossil_energy_pp_gj_per_tonne", 0)
        fossil_pet = virgin_plastic.get("fossil_energy_pet_gj_per_tonne", 0)
        avg_fossil_gj = (fossil_hdpe + fossil_ldpe + fossil_pp + fossil_pet) / 4

        electric_hdpe = virgin_plastic.get("electric_energy_hdpe_mwh_per_tonne", 0)
        electric_ldpe = virgin_plastic.get("electric_energy_ldpe_mwh_per_tonne", 0)
        electric_pp = virgin_plastic.get("electric_energy_pp_mwh_per_tonne", 0)
        electric_pet = virgin_plastic.get("electric_energy_pet_mwh_per_tonne", 0)
        avg_electric_mwh = (
            electric_hdpe + electric_ldpe + electric_pp + electric_pet
        ) / 4

        virgin_plastic_emission = 0.0
        if factor_key in ("ch4_kg_per_mj", "n2o_kg_per_mj"):
            # Proxy natural gas by CNG emission factor (per MJ)
            cng_factor_mj = (
                fuel_data.get("cng", {})
                .get("emission_factors", {})
                .get(factor_key, 0)
            )
            virgin_plastic_emission = avg_fossil_gj * 1000 * cng_factor_mj

        elif factor_key == "bc_kg_per_mj":
            # Approximate BC from CNG usage equivalent to fossil energy
            bc_factor_mj = (
                fuel_data.get("cng", {})
                .get("emission_factors", {})
                .get(factor_key, 0)
            )
            # actually constant is in the per kg unit(to keep the key same as others)
            cng_energy_mj_per_kg = (
                fuel_data.get("cng", {}).get("energy_content_mj_per_l", 1)
            )
            cng_density_kg_per_l = fuel_data.get("cng", {}).get("density_kg_per_l")

            cng_liters = (avg_fossil_gj * 1000) / (cng_energy_mj_per_kg *cng_density_kg_per_l)
            # Retain original formulation (units per original codebase)
            virgin_plastic_emission = cng_liters * bc_factor_mj

        elif factor_key == "co2_kg_per_mj":
            # Fossil (MJ-based) component
            co2_factor_mj = (
                fuel_data.get("cng", {})
                .get("emission_factors", {})
                .get(factor_key, 0)
            )
            co2_fossil = avg_fossil_gj * 1000 * co2_factor_mj

            # Electricity (kWh-based) component
            grid_factor = self.data_recycling.get("electricity_grid_factor", {}).get(
                "co2_kg_eq_per_kwh", 0
            )
            co2_electric = avg_electric_mwh * 1000 * grid_factor
            virgin_plastic_emission = co2_fossil + co2_electric

        # -----------------------
        # Virgin aluminum emissions
        # -----------------------
        virgin_aluminum = (
            self.data_recycling.get("virgin_material_production", {})
            .get("aluminum", {})
        )
        virgin_aluminum_emission = 0.0

        if factor_key == "ch4_kg_per_mj":
            virgin_aluminum_emission = virgin_aluminum.get(
                "ch4_emission_kg_per_tonne", 0
            )
        elif factor_key == "n2o_kg_per_mj":
            virgin_aluminum_emission = virgin_aluminum.get(
                "n2o_emission_kg_per_tonne", 0
            )
        elif factor_key == "bc_kg_per_mj":
            virgin_aluminum_emission = virgin_aluminum.get(
                "bc_emission_kg_per_tonne", 0
            )
        elif factor_key == "co2_kg_per_mj":
            # Fossil component (kg CO2/tonne)
            co2_fossil = virgin_aluminum.get("co2_fossil_emission_kg_per_tonne", 0)
            # Electricity component (kWh/tonne * kg CO2/kWh)
            grid_factor = self.data_recycling.get("electricity_grid_factor", {}).get(
                "co2_kg_eq_per_kwh", 0
            )
            electric_kwh = virgin_aluminum.get("electric_emission_kwh_per_tonne", 0)
            co2_electric = electric_kwh * grid_factor
            virgin_aluminum_emission = co2_fossil + co2_electric

        # --------------------
        # Virgin steel emissions
        # --------------------
        virgin_steel = (
            self.data_recycling.get("virgin_material_production", {})
            .get("steel", {})
        )
        coal_used_kg = virgin_steel.get("coal_used_kg_per_tonne", 0)
        cng_used_m3 = virgin_steel.get("cng_used_m3_per_tonne", 0)
        coal_cal_mj_per_kg = virgin_steel.get("coal_calorific_value_mj_per_kg", 0)

        coal_factor_mj = (
            fuel_data.get("coal", {})
            .get("emission_factors", {})
            .get(factor_key, 0)
        )
        cng_factor_mj = (
            fuel_data.get("cng", {})
            .get("emission_factors", {})
            .get(factor_key, 0)
        )
        cng_energy_mj_per_kg = (
            fuel_data.get("cng", {}).get("energy_content_mj_per_l", 1)
        )
        cng_density_kg_per_l = fuel_data.get("cng", {}).get("density_kg_per_l")

        coal_energy_mj = coal_used_kg * coal_cal_mj_per_kg
        cng_energy_mj = cng_used_m3 * 1000 * cng_energy_mj_per_kg * cng_density_kg_per_l  # 1 m3 = 1000 L
        virgin_steel_emission = (
            coal_energy_mj * coal_factor_mj + cng_energy_mj * cng_factor_mj
        )

        # ----------------------
        # Virgin glass emissions
        # ----------------------
        virgin_glass = (
            self.data_recycling.get("virgin_material_production", {})
            .get("glass", {})
        )
        virgin_glass_emission = 0.0
        if factor_key == "ch4_kg_per_mj":
            virgin_glass_emission = virgin_glass.get("ch4_emission_kg_per_tonne", 0)
        elif factor_key == "n2o_kg_per_mj":
            virgin_glass_emission = virgin_glass.get("n2o_emission_kg_per_tonne", 0)
        elif factor_key == "bc_kg_per_mj":
            virgin_glass_emission = virgin_glass.get("bc_emission_kg_per_tonne", 0)
        elif factor_key == "co2_kg_per_mj":
            virgin_glass_emission = virgin_glass.get("co2_fossil_emission_kg_per_tonne", 0)

        # -------------------------
        # Aggregate by composition
        # -------------------------
        for material, composition in self.material_composition_formal.items():
            rec_pct = self.recyclability.get(material, 100)
            share = (composition / 100) * (rec_pct / 100)
            mat = material.lower()
            if mat == "paper":
                formal_avoided += share * virgin_paper_emission
            elif mat == "plastic":
                formal_avoided += share * virgin_plastic_emission
            elif mat == "aluminum":
                formal_avoided += share * virgin_aluminum_emission
            elif mat == "steel":
                formal_avoided += share * virgin_steel_emission
            elif mat == "glass":
                formal_avoided += share * virgin_glass_emission
        

        for material, composition in self.material_composition_informal.items():
            rec_pct = self.recyclability.get(material, 100)
            share = (composition / 100) * (rec_pct / 100)
            mat = material.lower()
            if mat == "paper":
                informal_avoided += share * virgin_paper_emission
            elif mat == "plastic":
                informal_avoided += share * virgin_plastic_emission
            elif mat == "aluminum":
                informal_avoided += share * virgin_aluminum_emission
            elif mat == "steel":
                informal_avoided += share * virgin_steel_emission
            elif mat == "glass":
                informal_avoided += share * virgin_glass_emission



        return ((formal_avoided * formal_fraction), (informal_avoided * informal_fraction))
    


    def calculate_emissions(self, emission_factor_key, include_electricity=False):
        """
        Calculate emissions (kg CO₂-eq) per ton of waste recycled for both formal and informal sectors,
        optionally including emissions from electricity consumption.

        Args:
            emission_factor_key (str): The key for the emission factor in the JSON file (e.g., "co2_kg_per_mj").
            include_electricity (bool): Whether to include electricity emissions in the calculation (default is False).

        Returns:
            float: Combined emissions (kg CO₂-eq) for both formal and informal sectors.
        """
        breakdown = self._emission_breakdown(emission_factor_key, include_electricity)
        return breakdown["combined_per_ton"]

    def _emission_totals(self, emission_factor_key, include_electricity=False, gwp_factor=1):
        """Return per-ton and absolute emissions for the supplied factor."""
        breakdown = self._emission_breakdown(emission_factor_key, include_electricity)

        formal_total = breakdown["formal_per_ton"] * self.recycle_collected_formal
        informal_total = breakdown["informal_per_ton"] * self.recycle_collected_informal

        return {
            "per_ton": breakdown["combined_per_ton"] * gwp_factor,
            "formal_total": formal_total * gwp_factor,
            "informal_total": informal_total * gwp_factor,
            "total": (formal_total + informal_total) * gwp_factor,
        }

    def _gwp100(self, key: str) -> float:
        """Return GWP100 using the exact JSON key from transportation data."""
        gwp = self.data_trans.get("gwp_factors", {})
        return gwp.get(key, {}).get("gwp100", 0)

    def ch4_emit_recycling(self):
        """
        Calculate CH₄ emissions (kg CO₂-eq) per ton of waste recycled for both formal and informal sectors.
        """
        gwp_100_ch4 = self._gwp100("ch4_fossil")
        return self._emission_totals("ch4_kg_per_mj", gwp_factor=gwp_100_ch4)["per_ton"]

    def ch4_avoid_recycling(self):
        """
        Return avoided CH₄ emissions as CO₂e per ton for each stream.

        Uses GWP100 for fossil CH₄ to convert mass to CO₂-equivalent.

        Returns:
            tuple[float, float]: (formal_kgCO2e_per_ton, informal_kgCO2e_per_ton).
        """
        gwp_100_ch4 = self._gwp100("ch4_fossil")
        emission_formal_kgch4, emission_informal_kgch4 = self._calculate_avoided_emissions("ch4_kg_per_mj")
        emission_formal_kgco2e = emission_formal_kgch4 * gwp_100_ch4
        emission_informal_kgco2e = emission_informal_kgch4 * gwp_100_ch4
        return (emission_formal_kgco2e, emission_informal_kgco2e)

    def bc_emit_recycling(self):
        """
        Calculate black carbon (BC) mass in kg per ton of waste recycled (not CO2e).
        """
        return self._emission_totals("bc_kg_per_mj")["per_ton"]

    def bc_avoid_recycling(self):
        """
        Return avoided black carbon (BC) mass per ton for each stream.

        BC is tracked as mass (kg/ton), not CO₂e.

        Returns:
            tuple[float, float]: (formal_kgBC_per_ton, informal_kgBC_per_ton).
        """
        # BC tracked as mass (kg/ton), not CO2e
        return self._calculate_avoided_emissions("bc_kg_per_mj")

    def co2_emit_recycling(self):
        """
        Calculate CO₂ emissions (kg CO₂-eq) per ton of waste recycled for both formal and informal sectors.
        """
        return self._emission_totals("co2_kg_per_mj", include_electricity=True)["per_ton"]

    def co2_avoid_recycling(self):
        """
        Return avoided CO₂ emissions per ton for each stream.

        CO₂ uses GWP=1, so values are kg CO₂ per ton.

        Returns:
            tuple[float, float]: (formal_kgCO2_per_ton, informal_kgCO2_per_ton).
        """
        # CO2e (GWP=1); avoidance based on virgin paper production
        return self._calculate_avoided_emissions("co2_kg_per_mj")

    def n2o_emit_recycling(self):
        """
        Calculate N₂O emissions (kg CO₂-eq) per ton of waste recycled for both formal and informal sectors.
        """
        gwp_100_n2o = self._gwp100("n2o")
        return self._emission_totals("n2o_kg_per_mj", gwp_factor=gwp_100_n2o)["per_ton"]

    def n2o_avoid_recycling(self):
        """
        Return avoided N₂O emissions as CO₂e per ton for each stream.

        Uses GWP100 for N₂O to convert mass to CO₂-equivalent.

        Returns:
            tuple[float, float]: (formal_kgCO2e_per_ton, informal_kgCO2e_per_ton).
        """
        gwp_100_n2o = self._gwp100("n2o")
        emission_formal_kgn2o, emission_informal_kgn2o = self._calculate_avoided_emissions("n2o_kg_per_mj")
        emission_formal_kgco2e = emission_formal_kgn2o * gwp_100_n2o
        emission_informal_kgco2e = emission_informal_kgn2o * gwp_100_n2o
        return (emission_formal_kgco2e, emission_informal_kgco2e)

    def overall_emissions(self):
        """kgCO2e emissions per ton (CH4, CO2, N2O) and BC mass tracked separately."""

        ch4_data = self._emission_totals("ch4_kg_per_mj", gwp_factor=self._gwp100("ch4_fossil"))
        ch4_e = ch4_data["per_ton"]
        formal_ch4_a, informal_ch4_a = self.ch4_avoid_recycling()
        ch4_a = (formal_ch4_a + informal_ch4_a)
        ch4_total = (formal_ch4_a * self.recycle_collected_formal) + (informal_ch4_a * self.recycle_collected_informal)

        co2_data = self._emission_totals("co2_kg_per_mj", include_electricity=True)
        co2_e = co2_data["per_ton"]
        formal_co2_a, informal_co2_a = self.co2_avoid_recycling()
        co2_a = (formal_co2_a + informal_co2_a)
        co2_total = (formal_co2_a * self.recycle_collected_formal) + (informal_co2_a * self.recycle_collected_informal)

        n2o_data = self._emission_totals("n2o_kg_per_mj", gwp_factor=self._gwp100("n2o"))
        n2o_e = n2o_data["per_ton"]
        formal_n2o_a, informal_n2o_a = self.n2o_avoid_recycling()
        n2o_a = (formal_n2o_a + informal_n2o_a)
        n2o_total = (formal_n2o_a * self.recycle_collected_formal) + (informal_n2o_a * self.recycle_collected_informal)

        bc_data = self._emission_totals("bc_kg_per_mj")
        bc_e = bc_data["per_ton"]
        formal_bc_a, informal_bc_a = self.bc_avoid_recycling()
        bc_a = (formal_bc_a + informal_bc_a)
        bc_total = (formal_bc_a * self.recycle_collected_formal) + (informal_bc_a * self.recycle_collected_informal)

        total_emissions = ch4_e + co2_e + n2o_e
        total_emissions_avoid = ch4_a + co2_a + n2o_a

        total_collected = self.recycle_collected_formal + self.recycle_collected_informal
        total_emissions_total = ch4_total + co2_total + n2o_total
        total_emissions_avoid_total = total_emissions_avoid * total_collected
        net_emissions_total = total_emissions_total - total_emissions_avoid_total
        bc_emissions_total = bc_total
        bc_emissions_avoid_total = bc_a * total_collected
        net_emissions_bc_total = bc_emissions_total - bc_emissions_avoid_total

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
            "net_emissions": total_emissions - total_emissions_avoid,
            "net_emissions_bc": bc_e - bc_a,
            "ch4_emissions_total": ch4_total,
            "ch4_emissions_avoid_total": ch4_a * total_collected,
            "co2_emissions_total": co2_total,
            "co2_emissions_avoid_total": co2_a * total_collected,
            "n2o_emissions_total": n2o_total,
            "n2o_emissions_avoid_total": n2o_a * total_collected,
            "bc_emissions_total": bc_emissions_total,
            "bc_emissions_avoid_total": bc_emissions_avoid_total,
            "total_emissions_total": total_emissions_total,
            "total_emissions_avoid_total": total_emissions_avoid_total,
            "net_emissions_total": net_emissions_total,
            "net_emissions_bc_total": net_emissions_bc_total,
        }
