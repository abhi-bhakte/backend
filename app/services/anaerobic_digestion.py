import json
from pathlib import Path
from .transportation import TransportationEmissions

trans_file = Path(__file__).parent.parent / "data" / "transportation.json"
ad_file = Path(__file__).parent.parent / "data" / "ad.json"


class AnaerobicDigestionEmissions:
    """
    A class to calculate GHG emissions (CH₄, CO₂, N₂O) from anaerobic digestion.
    
    Attributes:
        waste_digested (float): Total waste anaerobically digested (tons).
        ad_energy_product (str): Type of product from anaerobic digestion (electricity, heat, biogas).
        fuel_replaced (str): Fossil fuel replaced if the recovered product is heat or biogas.
        compost_recovered (bool): Whether compost (solid digestate) is recovered from AD.
        percent_compost_use_agri_garden (float): Percentage of recovered compost used in agriculture/gardens.
        electricity_consumed (float): Electricity consumed during anaerobic digestion (kWh).
        fuel_types_operation (list[str]): Types of fuel used in anaerobic digestion operations.
        fuel_consumed_operation (list[float]): Fuel consumption in liters.
    """

    def __init__(
        self,
        waste_digested: float,
        ad_energy_product: str,
        fuel_replaced: str,
        compost_recovered: bool,
        percent_compost_use_agri_garden: float,
        electricity_consumed: float,
        fuel_types_operation: list[str],
        fuel_consumed_operation: list[float],
    ):
        """
        Initialize the Anaerobic Digestion Emissions calculator.
        """

        # Debugging logs to verify received data
        print(f"Received waste_digested: {waste_digested}")
        print(f"Received ad_energy_product: {ad_energy_product}")
        print(f"Received fuel_replaced: {fuel_replaced}")
        print(f"Received compost_recovered: {compost_recovered}")
        print(f"Received percent_compost_use_agri_garden: {percent_compost_use_agri_garden}")
        print(f"Received electricity_consumed: {electricity_consumed}")
        print(f"Received fuel_types_operation: {fuel_types_operation}")
        print(f"Received fuel_consumed_operation: {fuel_consumed_operation}")

        self.waste_digested = waste_digested
        self.ad_energy_product = ad_energy_product
        self.fuel_replaced = fuel_replaced
        self.compost_recovered = compost_recovered
        self.percent_compost_use_agri_garden = percent_compost_use_agri_garden
        self.electricity_consumed = electricity_consumed
        self.fuel_types_operation = fuel_types_operation
        self.fuel_consumed_operation = fuel_consumed_operation

        self.ad_file = ad_file
        self.trans_file = trans_file

        # Load emission factor data
        try:
            with open(self.ad_file, "r", encoding="utf-8") as file:
                self.data_ad = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {self.ad_file} was not found.")
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

        # Retrieve fuel data from the dataset
        fuel_data = self.data_ad.get("fuel_data", {})
        available_fuels = fuel_data.get("Fuel Type", [])

        # Iterate through each fuel type and compute emissions
        for fuel, consumption in zip(fuel_types, fuel_consumed):
            if fuel in available_fuels:
                fuel_index = available_fuels.index(fuel)
                energy_content = fuel_data["Energy Content (MJ/L)"][fuel_index]
                emission_factor = fuel_data[factor_key][fuel_index]
                
                # Calculate emissions based on energy content and emission factor
                total_emissions += consumption * energy_content * emission_factor

        # Normalize emissions by waste amount, avoiding division by zero
        return total_emissions / per_waste if per_waste > 0 else 0
    
    def ch4_emit_ad(self):
        """
        Calculate CH₄ emissions from anaerobic digestion (AD).

        Returns:
            float: Total CH₄ emissions in CO₂-equivalent (kg CO₂e), including:
                - Fossil CH₄ emissions from operational fuel combustion
                - Biogenic CH₄ emissions from leakage during digestion
        """

        # Retrieve CH₄ emission factor for biogenic leakage (IPCC default)
        ad_factors = self.data_ad.get("ad_emissions", {})
        bio_leakage_factor = ad_factors["IPCC_default_values"]["CH4_kg_per_ton"]

        # Retrieve Global Warming Potential (GWP) values
        gwp_factors = self.data_trans.get("gwp_factors", {})

        # Get GWP100 value for CH₄-fossil
        ch4_fossil_index = gwp_factors["Type of gas"].index("CH4-fossil")
        gwp_100_fossil = gwp_factors["GWP100"][ch4_fossil_index]

        # Get GWP100 value for CH₄-biogenic
        ch4_biogenic_index = gwp_factors["Type of gas"].index("CH4-biogenic")
        gwp_100_biogenic = gwp_factors["GWP100"][ch4_biogenic_index]

        # Total CH₄ emissions from:
        # 1. Fossil fuel use in operations (e.g., generators, transport)
        # 2. Biogenic CH₄ leakage during anaerobic digestion
        fossil_emissions = self._calculate_emissions(
            self.fuel_types_operation,
            self.fuel_consumed_operation,
            'CH4 Emission Factor (kg/MJ)',
            self.waste_digested
        )

        return (
            gwp_100_fossil * fossil_emissions +
            gwp_100_biogenic * bio_leakage_factor
        )

    def ch4_avoid_ad(self):
        """Calculate methane emissions."""
        return 0

    def co2_emit_ad(self):
        """
        Calculate CO₂ emissions per ton of waste digested.
        
        Returns:
            float: Total CO₂ emissions per ton of waste digested (kg CO₂-eq/ton).
        """
        # Retrieve electricity grid emission factor (kg CO₂-eq per kWh)
        grid_emission_factor = self.data_trans.get("electricity_grid_factor", {})
        co2_per_kwh = grid_emission_factor.get("CO2 kg-eq/kWh", 0)
        
        # Calculate CO₂ emissions from electricity consumption
        total_co2_electricity = self.electricity_consumed * co2_per_kwh
        
        # Calculate CO₂ emissions from fuel consumption
        co2_from_fuel = self._calculate_emissions(
            self.fuel_types_operation,
            self.fuel_consumed_operation,
            "CO2 Emission Factor (kg/MJ)",
            self.waste_digested
        )
        
        return co2_from_fuel + (total_co2_electricity / self.waste_digested)

    def co2_avoid_ad(self):
        """Calculate methane emissions."""
        return 0

    def n2o_emit_ad(self):
        """
        Calculate N₂O emissions per ton of waste composted.
        
        Returns:
            float: Total N₂O emissions per ton of waste digested (kg CO₂-eq/ton).
        """
        # Retrieve Global Warming Potential (GWP) for N₂O
        gwp_factors = self.data_trans.get("gwp_factors", {})
        n2o_index = gwp_factors["Type of gas"].index("N2O")
        gwp_100_n2o = gwp_factors["GWP100"][n2o_index]
        
        # Calculate N₂O emissions from fuel combustion and AD process
        n2o_from_fuel = self._calculate_emissions(
            self.fuel_types_operation,
            self.fuel_consumed_operation,
            "N2O Emission Factor (kg/MJ)",
            self.waste_digested,
        )
        
        return (gwp_100_n2o * n2o_from_fuel)

    def n2o_avoid_ad(self):
        return 0

    def bc_emit_ad(self):
        """
        Calculate black carbon (BC) emissions in kgCO2-equivalent per ton of waste treated.
        """
        # Retrieve GWP (Global Warming Potential) factors
        gwp_factors = self.data_trans.get("gwp_factors", {})
        
        # Get the index for BC in the GWP factors list
        bc_index = gwp_factors["Type of gas"].index("BC")
        
        # Retrieve the 100-year GWP value for BC
        gwp_100_bc = gwp_factors["GWP100"][bc_index]

        
        return (
            gwp_100_bc
            * self._calculate_emissions(
                self.fuel_types_operation,
                self.fuel_consumed_operation,
                "BC Emissions (kg/MJ)",
                self.waste_digested,
            )
        )

    def bc_avoid_ad(self):
        """Calculate methane emissions."""
        return 0

    def overall_emissions(self):
        """kgCO2e emissions and emissions avoided per ton of waste digested."""

        return {
            "ch4_emissions": self.ch4_emit_ad(),
            "ch4_emissions_avoid": self.ch4_avoid_ad(),
            "co2_emissions": self.co2_emit_ad(),
            "co2_emissions_avoid": self.co2_avoid_ad(),
            "n2o_emissions": self.n2o_emit_ad(),
            "n2o_emissions_avoid": self.n2o_avoid_ad(),
            "bc_emissions": self.bc_emit_ad(),
            "bc_emissions_avoid": self.bc_avoid_ad(),
            "total_emissions": (
                self.ch4_emit_ad()
                + self.co2_emit_ad()
                + self.n2o_emit_ad()
                + self.bc_emit_ad()
            ),
            "total_emissions_avoid": (
                self.ch4_avoid_ad()
                + self.co2_avoid_ad()
                + self.n2o_avoid_ad()
                + self.bc_avoid_ad()
            ),
            "net_emissions": (
                self.ch4_emit_ad()
                + self.co2_emit_ad()
                + self.n2o_emit_ad()
                + self.bc_emit_ad()
                - (
                    self.ch4_avoid_ad()
                    + self.co2_avoid_ad()
                    + self.n2o_avoid_ad()
                    + self.bc_avoid_ad()
                )
            ),
        }
