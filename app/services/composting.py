import json
from pathlib import Path
from .transportation import TransportationEmissions

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
        fuel_data = self.data_comp.get("fuel_data", {})
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

    def ch4_emit_composting(self):
        """
        Calculate CH₄ emissions (kg CO₂-eq) per ton of waste treated.
        
        Returns:
            float: CH₄ emissions in kg CO₂-eq per ton of waste.
        """
        # Retrieve CH₄ emission factor for biogenic degradation
        compost_factor = self.data_comp.get("composting_emissions", {})
        bio_compost_factor = compost_factor["IPCC_default_values"]["CH4_kg_per_ton"]

        # Retrieve GWP values
        gwp_factors = self.data_trans.get("gwp_factors", {})

        # Get index and value for CH₄-fossil GWP
        methane_fossil_index = gwp_factors["Type of gas"].index("CH4-fossil")
        gwp_100_fossil = gwp_factors["GWP100"][methane_fossil_index]
        
        # Get index and value for CH₄-biogenic GWP
        methane_bio_index = gwp_factors["Type of gas"].index("CH4-biogenic")
        gwp_100_biogenic = gwp_factors["GWP100"][methane_bio_index]

        return (
            gwp_100_fossil
            * self._calculate_emissions(
                self.fuel_types_operation,
                self.fuel_consumed_operation,
                "CH4 Emission Factor (kg/MJ)",
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
        # Retrieve fertilizer production emission factor
        ferti_factors = self.data_comp.get("fertilizer_production_emissions", {})

        # Get index and value for total CH₄ emissions from fertilizer production
        total_ch4_index = ferti_factors["fertilizer_types"].index("Total")
        ferti_ch4_factor = ferti_factors["CH4_emission_g_per_kg_fertilizer"][total_ch4_index]

        # Retrieve methane GWP values
        gwp_factors = self.data_trans.get("gwp_factors", {})

        # Get index and value for CH₄-fossil GWP
        methane_fossil_index = gwp_factors["Type of gas"].index("CH4-fossil")
        gwp_100_fossil = gwp_factors["GWP100"][methane_fossil_index]

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
        co2_per_kwh = grid_emission_factor.get("CO2 kg-eq/kWh", 0)
        
        # Calculate CO₂ emissions from electricity consumption
        total_co2_electricity = self.electricity_consumed * co2_per_kwh
        
        # Calculate CO₂ emissions from fuel consumption
        co2_from_fuel = self._calculate_emissions(
            self.fuel_types_operation,
            self.fuel_consumed_operation,
            "CO2 Emission Factor (kg/MJ)",
            self.waste_composted
        )
        
        return co2_from_fuel + (total_co2_electricity / self.waste_composted)

    def co2_avoid_composting(self):
        """
        Calculate avoided CO₂ emissions per ton of waste composted due to reduced fertilizer use.
        
        Returns:
            float: Avoided CO₂ emissions per ton of waste composted (kg CO₂-eq/ton).
        """
        # Retrieve fertilizer production emission factors
        ferti_factors = self.data_comp.get("fertilizer_production_emissions", {})
        
        # Get the emission factor for total fertilizer production (g CO₂ per kg fertilizer)
        total_co2_index = ferti_factors["fertilizer_types"].index("Total")
        ferti_co2_factor = ferti_factors["CO2_emission_g_per_kg_fertilizer"][total_co2_index]
        
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
        n2o_compost
        
        _factor = compost_factor["IPCC_default_values"]["N2O_kg_per_ton"]
        
        # Retrieve Global Warming Potential (GWP) for N₂O
        gwp_factors = self.data_trans.get("gwp_factors", {})
        n2o_index = gwp_factors["Type of gas"].index("N2O")
        gwp_100_n2o = gwp_factors["GWP100"][n2o_index]
        
        # Calculate N₂O emissions from fuel combustion and composting process
        n2o_from_fuel = self._calculate_emissions(
            self.fuel_types_operation,
            self.fuel_consumed_operation,
            "N2O Emission Factor (kg/MJ)",
            self.waste_composted,
        )
        
        return gwp_100_n2o * (n2o_from_fuel + n2o_compost_factor)

    def n2o_avoid_composting(self):
        """
        Calculate avoided N₂O emissions per ton of waste composted due to reduced fertilizer use.
        
        Returns:
            float: Avoided N₂O emissions per ton of waste composted (kg CO₂-eq/ton).
        """
        # Retrieve fertilizer production N₂O emission factors (g N₂O per kg fertilizer)
        ferti_factors = self.data_comp.get("fertilizer_production_emissions", {})
        total_n2o_index = ferti_factors["fertilizer_types"].index("Total")
        ferti_n2o_factor = ferti_factors["N2O_emission_g_per_kg_fertilizer"][total_n2o_index]
        
        # Retrieve Global Warming Potential (GWP) for N₂O
        gwp_factors = self.data_trans.get("gwp_factors", {})
        n2o_index = gwp_factors["Type of gas"].index("N2O")
        gwp_100_n2o = gwp_factors["GWP100"][n2o_index]
        
        # Convert grams to kilograms and calculate avoided emissions
        return (
            gwp_100_n2o *
            (self.compost_prod_potential / 1000) *  # Convert kg to tons
            (self.percent_compost_use_agri_garden / 100) *  # Percentage used in agriculture/gardens
            ferti_n2o_factor  # N₂O emission factor
        )

    def bc_emit_composting(self):
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
                self.waste_composted
            )
        )

    def bc_avoid_composting(self):
        """
        Calculate black carbon (BC) avoided emissions per ton of waste composted.
        """
        # Retrieve fertilizer production emission factors
        ferti_factors = self.data_comp.get("fertilizer_production_emissions", {})
        
        # Get the index for 'Total' fertilizer type in the emissions data
        total_bc_index = ferti_factors["fertilizer_types"].index("Total")
        
        # Retrieve the BC emission factor for fertilizer production (g per kg of fertilizer)
        ferti_bc_factor = ferti_factors["BC_emission_g_per_kg_fertilizer"][total_bc_index]
        
        # Retrieve GWP factors for BC
        gwp_factors = self.data_trans.get("gwp_factors", {})
        
        # Get the index for BC in the GWP factors list
        bc_index = gwp_factors["Type of gas"].index("BC")
        
        # Retrieve the 100-year GWP value for BC
        gwp_100_bc = gwp_factors["GWP100"][bc_index]
        
        return (
            gwp_100_bc
            * (
                (self.compost_prod_potential / 1000)
                * (self.percent_compost_use_agri_garden / 100)
                * ferti_bc_factor
            )
        )

    def overall_emissions(self):
        """kgCO2e emissions and emissions avoided per ton of waste treated."""

        return {
            "ch4_emissions": self.ch4_emit_composting(),
            "ch4_emissions_avoid": self.ch4_avoid_composting(),
            "co2_emissions": self.co2_emit_composting(),
            "co2_emissions_avoid": self.co2_avoid_composting(),
            "n2o_emissions": self.n2o_emit_composting(),
            "n2o_emissions_avoid": self.n2o_avoid_composting(),
            "bc_emissions": self.bc_emit_composting(),
            "bc_emissions_avoid": self.bc_avoid_composting(),
            "total_emissions": (
                self.ch4_emit_composting()
                + self.co2_emit_composting()
                + self.n2o_emit_composting()
                + self.bc_emit_composting()
            ),
            "total_emissions_avoid": (
                self.ch4_avoid_composting()
                + self.co2_avoid_composting()
                + self.n2o_avoid_composting()
                + self.bc_avoid_composting()
            ),
            "net_emissions": (
                self.ch4_emit_composting()
                + self.co2_emit_composting()
                + self.n2o_emit_composting()
                + self.bc_emit_composting()
                - (
                    self.ch4_avoid_composting()
                    + self.co2_avoid_composting()
                    + self.n2o_avoid_composting()
                    + self.bc_avoid_composting()
                )
            ),
        }


