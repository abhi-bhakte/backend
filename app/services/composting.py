"""
NOTE:
For CNG and coal, the energy content values in the JSON file are actually in units of MJ per kg, 
not MJ per liter. However, for consistency, the JSON key remains "energy_content_mj_per_l". 
Users should enter CNG and coal consumption in kg, and the code will interpret the energy 
content accordingly for these fuels. This is to maintain database structure consistency.
"""
import json
from pathlib import Path

trans_file = Path(__file__).parent.parent / "data" / "transportation.json"
comp_file = Path(__file__).parent.parent / "data" / "composting.json"


class CompostingEmissions:
    """
    A class to calculate GHG emissions (CH₄, CO₂, N₂O) from composting operations.

    Attributes:
        waste_composted (float): Total waste composted (tons).
        percent_compost_use_agri_garden (float): Percentage of compost used in agriculture/gardens.
        compost_prod_potential (float): Compost production potential (kg compost/tons waste).
        electricity_consumed (float): Electricity consumed during composting (kWh).
        fuel_types_operation (list[str]): Types of fuel used in composting operations.
        fuel_consumed_operation (list[float]): Fuel consumption in liters.
    """

    def __init__(
        self,
        waste_composted: float,
        percent_compost_use_agri_garden: float,
        compost_prod_potential: float,
        electricity_consumed: float,
        fuel_types_operation: list,
        fuel_consumed_operation: list,
    ):
        """
        Initialize the CompostingEmissions class and validate inputs.

        Args:
            waste_composted (float): Total waste composted (tons).
            percent_compost_use_agri_garden (float): Percentage of compost used in agriculture/gardens.
            compost_prod_potential (float): Compost production potential (tons).
            electricity_consumed (float): Electricity consumed during composting (kWh).
            fuel_types_operation (list[str]): Types of fuel used in composting operations.
            fuel_consumed_operation (list[float]): Fuel consumption in liters.

        Raises:
            ValueError: If any waste, electricity, or fuel values are negative.
            FileNotFoundError: If the data file is not found.
            ValueError: If there is an error decoding the JSON file.
        """
        # Validate inputs
        if any(x < 0 for x in [waste_composted, percent_compost_use_agri_garden, compost_prod_potential, electricity_consumed]):
            raise ValueError("Waste, compost percentages, and electricity values cannot be negative.")
        if any(x < 0 for x in fuel_consumed_operation):
            raise ValueError("Fuel consumption values cannot be negative.")

        # Initialize attributes
        self.waste_composted = waste_composted
        self.percent_compost_use_agri_garden = percent_compost_use_agri_garden
        self.compost_prod_potential = compost_prod_potential
        self.electricity_consumed = electricity_consumed
        self.fuel_types_operation = fuel_types_operation
        self.fuel_consumed_operation = fuel_consumed_operation

        self.comp_file = comp_file
        self.trans_file = trans_file

        # Load emission factor data
        try:
            with open(self.comp_file, "r", encoding="utf-8") as file:
                self.data_comp = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {self.comp_file} was not found.")
        except json.JSONDecodeError:
            raise ValueError("Error decoding JSON file. Please check the format.")
        
        # Load emission factor data
        try:
            with open(self.trans_file, "r", encoding="utf-8") as file:
                self.data_trans = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {self.trans_file} was not found.")
        except json.JSONDecodeError:
            raise ValueError("Error decoding JSON file. Please check the format.")


    @staticmethod
    def _normalize_key(text: str) -> str:
        return (
            (text or "")
            .strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
            .replace("/", "_")
        )

    def _gwp100(self, key: str) -> float:
        """Return GWP100 using the exact JSON key from transportation data."""
        gwp = self.data_trans.get("gwp_factors", {})
        return gwp.get(key, {}).get("gwp100", 0)

    def _calculate_emissions(self, fuel_types, fuel_consumed, factor_key, per_waste):
        """
        Calculate emissions for different gases based on fuel consumption.

        Args:
            fuel_types (list[str]): List of fuel types used.
            fuel_consumed (list[float]): Corresponding fuel consumption in liters.
            factor_key (str): Key for the emission factor in the JSON file.
            per_waste (float): Waste amount for normalization.

        Returns:
            float: Emissions per ton of waste.
        """
        total_emissions = 0

        # Retrieve fuel data from the dataset (normalized JSON expected)
        fuel_raw = self.data_comp.get("fuel_data", [])
        available_fuels = [f.get("fuel_type") for f in fuel_raw]

        # Iterate through each fuel type and compute emissions
        for fuel, consumption in zip(fuel_types, fuel_consumed):
            f_norm = self._normalize_key(fuel)
            if f_norm in available_fuels:
                f_entry = next((x for x in fuel_raw if x.get("fuel_type") == f_norm), None)
                if not f_entry:
                    continue
                energy_content = f_entry.get("energy_content_mj_per_l", 0)
                emission_factor = f_entry.get("emission_factors", {}).get(factor_key, 0)
                total_emissions += consumption * energy_content * emission_factor

        # Normalize emissions by waste amount, avoiding division by zero
        return total_emissions / per_waste if per_waste > 0 else 0

    def ch4_emit_composting(self):
        """
        Calculate CH₄ emissions (kg CO₂-eq) per ton of waste treated.
        
        Returns:
            float: CH₄ emissions in kg CO₂-eq per ton of waste.
        """
        # Retrieve CH₄ emission factor for biogenic degradation
        compost_factor = self.data_comp.get("composting_emissions", {})
        bio_compost_factor = compost_factor.get("ipcc_default_values", {}).get("ch4_kg_per_ton", 0)

        # Retrieve GWP values (normalized)
        gwp_100_fossil = self._gwp100("ch4_fossil")
        gwp_100_biogenic = self._gwp100("ch4_biogenic")

        return (
            gwp_100_fossil
            * self._calculate_emissions(
                self.fuel_types_operation,
                self.fuel_consumed_operation,
                "ch4_kg_per_mj",
                self.waste_composted,
            )
            + gwp_100_biogenic * bio_compost_factor
        )

    def ch4_avoid_composting(self):
        """
        Calculate CH₄ emissions avoided per ton of waste composted.
        
        Returns:
            float: CH₄ emissions avoided in kg CO₂-eq per ton of waste.
        """
        # Retrieve fertilizer production emission factor (total)
        ferti_list = self.data_comp.get("fertilizer_production_emissions", [])
        total_entry = next((x for x in ferti_list if x.get("fertilizer_type") == "total"), {})
        ferti_ch4_factor = total_entry.get("ch4_emission_g_per_kg", 0)

        # Retrieve methane GWP values (fossil)
        gwp_100_fossil = self._gwp100("ch4_fossil")

        return (
            gwp_100_fossil
            * (
                self.compost_prod_potential
                / 1000
                * self.percent_compost_use_agri_garden
                / 100
                * ferti_ch4_factor
            )
        )

    def co2_emit_composting(self):
        """
        Calculate CO₂ emissions per ton of waste composted.
        
        Returns:
            float: Total CO₂ emissions per ton of waste composted (kg CO₂-eq/ton).
        """
        # Retrieve electricity grid emission factor (kg CO₂-eq per kWh)
        grid_emission_factor = self.data_trans.get("electricity_grid_factor", {})
        co2_per_kwh = grid_emission_factor.get("co2_kg_per_kwh", 0)
        
        # Calculate CO₂ emissions from electricity consumption
        total_co2_electricity = self.electricity_consumed * co2_per_kwh
        
        # Calculate CO₂ emissions from fuel consumption
        co2_from_fuel = self._calculate_emissions(
            self.fuel_types_operation,
            self.fuel_consumed_operation,
            "co2_kg_per_mj",
            self.waste_composted
        )
        
        return co2_from_fuel + (total_co2_electricity / self.waste_composted)

    def co2_avoid_composting(self):
        """
        Calculate avoided CO₂ emissions per ton of waste composted due to reduced fertilizer use.
        
        Returns:
            float: Avoided CO₂ emissions per ton of waste composted (kg CO₂-eq/ton).
        """
        # Retrieve fertilizer production emission factors (total)
        ferti_list = self.data_comp.get("fertilizer_production_emissions", [])
        total_entry = next((x for x in ferti_list if x.get("fertilizer_type") == "total"), {})
        ferti_co2_factor = total_entry.get("co2_emission_g_per_kg", 0)
        
        # Convert grams to kilograms (1 g = 0.001 kg) and calculate avoided emissions
        return (
            (self.compost_prod_potential / 1000) *  # Convert kg to tons
            (self.percent_compost_use_agri_garden / 100) *  # Percentage used in agriculture/gardens
            ferti_co2_factor  # CO₂ emission factor
        )

    def n2o_emit_composting(self):
        """
        Calculate N₂O emissions per ton of waste composted.
        
        Returns:
            float: Total N₂O emissions per ton of waste composted (kg CO₂-eq/ton).
        """
        # Retrieve composting N₂O emission factor (kg N₂O per ton of waste)
        compost_factor = self.data_comp.get("composting_emissions", {})
        n2o_compost_factor = compost_factor.get("ipcc_default_values", {}).get("n2o_kg_per_ton", 0)
        
        # Retrieve Global Warming Potential (GWP) for N₂O
        gwp_100_n2o = self._gwp100("n2o")
        
        # Calculate N₂O emissions from fuel combustion and composting process
        n2o_from_fuel = self._calculate_emissions(
            self.fuel_types_operation,
            self.fuel_consumed_operation,
            "n2o_kg_per_mj",
            self.waste_composted,
        )
        
        return gwp_100_n2o * (n2o_from_fuel + n2o_compost_factor)

    def n2o_avoid_composting(self):
        """
        Calculate avoided N₂O emissions per ton of waste composted due to reduced fertilizer use.
        
        Returns:
            float: Avoided N₂O emissions per ton of waste composted (kg CO₂-eq/ton).
        """
        # Retrieve fertilizer production N₂O emission factors (total)
        ferti_list = self.data_comp.get("fertilizer_production_emissions", [])
        total_entry = next((x for x in ferti_list if x.get("fertilizer_type") == "total"), {})
        ferti_n2o_factor = total_entry.get("n2o_emission_g_per_kg", 0)
        
        # Retrieve Global Warming Potential (GWP) for N₂O
        gwp_100_n2o = self._gwp100("n2o")
        
        # Convert grams to kilograms and calculate avoided emissions
        return (
            gwp_100_n2o *
            (self.compost_prod_potential / 1000) *  # Convert kg to tons
            (self.percent_compost_use_agri_garden / 100) *  # Percentage used in agriculture/gardens
            ferti_n2o_factor  # N₂O emission factor
        )

    def bc_emit_composting(self):
        """
        Calculate black carbon (BC) mass in kg per ton of waste treated (not CO2e).
        """
        
        return (
            self._calculate_emissions(
                self.fuel_types_operation,
                self.fuel_consumed_operation,
                "bc_kg_per_mj",
                self.waste_composted
            )
        )

    def bc_avoid_composting(self):
        """
        Calculate black carbon (BC) avoided emissions per ton of waste composted.
        """
        # Retrieve fertilizer production emission factors (total)
        ferti_list = self.data_comp.get("fertilizer_production_emissions", [])
        total_entry = next((x for x in ferti_list if x.get("fertilizer_type") == "total"), {})
        ferti_bc_factor = total_entry.get("bc_emission_g_per_kg", 0)
        
        
        return (
            (self.compost_prod_potential / 1000)
            * (self.percent_compost_use_agri_garden / 100)
            * ferti_bc_factor
        )

    def overall_emissions(self):
        """kgCO2e emissions per ton (CH4, CO2, N2O) and BC mass tracked separately."""

        # Compute once per gas
        ch4_e = self.ch4_emit_composting()
        ch4_a = self.ch4_avoid_composting()
        co2_e = self.co2_emit_composting()
        co2_a = self.co2_avoid_composting()
        n2o_e = self.n2o_emit_composting()
        n2o_a = self.n2o_avoid_composting()
        bc_e = self.bc_emit_composting()
        bc_a = self.bc_avoid_composting()

        # Totals in CO2e exclude BC mass
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


