"""
NOTE:
For CNG and coal, the energy content values in the JSON file are actually in units of MJ per kg, 
not MJ per liter. However, for consistency, the JSON key remains "energy_content_mj_per_l". 
Users should enter CNG and coal consumption in kg, and the code will interpret the energy 
content accordingly for these fuels. This is to maintain database structure consistency.
"""
import json
from pathlib import Path
from .transportation import TransportationEmissions

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
        # Fraction of recyclables treated by the formal sector
        formal_fraction = self.recycle_collected_formal / (
            self.recycle_collected_formal + self.recycle_collected_informal
        )
        informal_fraction = self.recycle_collected_informal / (
            self.recycle_collected_formal + self.recycle_collected_informal
        )

        # Load the electricity grid factor from the JSON file (only if electricity is included)
        grid_factor = self.data_recycling["electricity_grid_factor"].get("co2_kg_eq_per_kwh", 0) if include_electricity else 0

        # Initialize total emissions for the formal and informal sectors
        total_emissions_formal = 0
        total_emissions_informal = 0

        # Calculate emissions for the formal sector
        for material, composition_percentage in self.material_composition_formal.items():
            # Emissions from fuel
            fuel_emissions = (composition_percentage / 100) * self._calculate_fuel_emissions(
                self.fuel_types_operation.get(material, []),  # Fuel types for the material
                self.fuel_consumed_operation.get(material, []),  # Fuel consumption for the material
                emission_factor_key  # Emission factor key (e.g., "co2_kg_per_mj")
            )
            # Emissions from electricity (if included)
            electricity_emissions = (composition_percentage / 100) * (
                self.electricity_consumed.get(material, 0) * grid_factor
            ) if include_electricity else 0
            # Total emissions for the material
            total_emissions_formal += fuel_emissions + electricity_emissions

        # Scale emissions by the formal fraction
        total_emissions_formal *= formal_fraction

        # Calculate emissions for the informal sector
        for material, composition_percentage in self.material_composition_informal.items():
            # Emissions from fuel
            fuel_emissions = (composition_percentage / 100) * self._calculate_fuel_emissions(
                self.fuel_types_operation.get(material, []),  # Fuel types for the material
                self.fuel_consumed_operation.get(material, []),  # Fuel consumption for the material
                emission_factor_key  # Emission factor key (e.g., "co2_kg_per_mj")
            )
            # Emissions from electricity (if included)
            electricity_emissions = (composition_percentage / 100) * (
                self.electricity_consumed.get(material, 0) * grid_factor
            ) if include_electricity else 0
            # Total emissions for the material
            total_emissions_informal += fuel_emissions + electricity_emissions

        # Scale emissions by the informal fraction
        total_emissions_informal *= informal_fraction

        # Combine emissions from both sectors
        total_emissions = total_emissions_formal + total_emissions_informal

        return total_emissions

    def _gwp100(self, key: str) -> float:
        """Return GWP100 using the exact JSON key from transportation data."""
        gwp = self.data_trans.get("gwp_factors", {})
        return gwp.get(key, {}).get("gwp100", 0)

    def ch4_emit_recycling(self):
        """
        Calculate CH₄ emissions (kg CO₂-eq) per ton of waste recycled for both formal and informal sectors.
        """
        gwp_100_ch4 = self._gwp100("ch4_fossil")
        return gwp_100_ch4 * self.calculate_emissions("ch4_kg_per_mj")

    def ch4_avoid_recycling(self):
        """
        Placeholder for calculating CH₄ emissions (kg CO₂-eq) per ton of waste recycled.
        """
        return (0)

    def bc_emit_recycling(self):
        """
        Calculate black carbon (BC) mass in kg per ton of waste recycled (not CO2e).
        """
        return self.calculate_emissions("bc_kg_per_mj")

    def bc_avoid_recycling(self):
        """
        Placeholder for calculating black carbon (BC) avoided (kg/ton).
        """
        return 0

    def co2_emit_recycling(self):
        """
        Calculate CO₂ emissions (kg CO₂-eq) per ton of waste recycled for both formal and informal sectors.
        """
        return self.calculate_emissions("co2_kg_per_mj", include_electricity=True)

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
        return gwp_100_n2o * self.calculate_emissions("n2o_kg_per_mj")

    def n2o_avoid_recycling(self):
        """
        Placeholder for calculating N₂O emissions per ton of waste recycled.
        """
        return (0)

    def overall_emissions(self):
        """kgCO2e emissions per ton (CH4, CO2, N2O) and BC mass tracked separately."""

        ch4_e = self.ch4_emit_recycling()
        ch4_a = self.ch4_avoid_recycling()
        co2_e = self.co2_emit_recycling()
        co2_a = self.co2_avoid_recycling()
        n2o_e = self.n2o_emit_recycling()
        n2o_a = self.n2o_avoid_recycling()
        bc_e = self.bc_emit_recycling()
        bc_a = self.bc_avoid_recycling()

        total_emissions = ch4_e + co2_e + n2o_e
        total_emissions_avoid = ch4_a + co2_a + n2o_a

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
        }
