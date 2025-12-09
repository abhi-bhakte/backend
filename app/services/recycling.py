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

    def _emission_totals(self, emission_factor_key, include_electricity=False, gwp_factor=1.0):
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
        Placeholder for calculating CH₄ emissions (kg CO₂-eq) per ton of waste recycled.
        """
        return (0)

    def bc_emit_recycling(self):
        """
        Calculate black carbon (BC) mass in kg per ton of waste recycled (not CO2e).
        """
        return self._emission_totals("bc_kg_per_mj")["per_ton"]

    def bc_avoid_recycling(self):
        """
        Placeholder for calculating black carbon (BC) avoided (kg/ton).
        """
        return 0

    def co2_emit_recycling(self):
        """
        Calculate CO₂ emissions (kg CO₂-eq) per ton of waste recycled for both formal and informal sectors.
        """
        return self._emission_totals("co2_kg_per_mj", include_electricity=True)["per_ton"]

    def co2_avoid_recycling(self):
        """
        Placeholder for calculating CO₂ emissions per ton of waste recycled.
        """
        return (0)

    def n2o_emit_recycling(self):
        """
        Calculate N₂O emissions (kg CO₂-eq) per ton of waste recycled for both formal and informal sectors.
        """
        gwp_100_n2o = self._gwp100("n2o")
        return self._emission_totals("n2o_kg_per_mj", gwp_factor=gwp_100_n2o)["per_ton"]

    def n2o_avoid_recycling(self):
        """
        Placeholder for calculating N₂O emissions per ton of waste recycled.
        """
        return (0)

    def overall_emissions(self):
        """kgCO2e emissions per ton (CH4, CO2, N2O) and BC mass tracked separately."""

        ch4_data = self._emission_totals("ch4_kg_per_mj", gwp_factor=self._gwp100("ch4_fossil"))
        ch4_e = ch4_data["per_ton"]
        ch4_a = self.ch4_avoid_recycling()
        ch4_total = ch4_data["total"]
        co2_data = self._emission_totals("co2_kg_per_mj", include_electricity=True)
        co2_e = co2_data["per_ton"]
        co2_a = self.co2_avoid_recycling()
        co2_total = co2_data["total"]
        n2o_data = self._emission_totals("n2o_kg_per_mj", gwp_factor=self._gwp100("n2o"))
        n2o_e = n2o_data["per_ton"]
        n2o_a = self.n2o_avoid_recycling()
        n2o_total = n2o_data["total"]
        bc_data = self._emission_totals("bc_kg_per_mj")
        bc_e = bc_data["per_ton"]
        bc_a = self.bc_avoid_recycling()
        bc_total = bc_data["total"]

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
