import json
from pathlib import Path
from .transportation import TransportationEmissions


class IncinerationEmissions:
    """
    A class to calculate emissions from incineration processes.

    Attributes:
        waste_incinerated (float): Amount of waste incinerated (ton/day).
        incineration_type (str): Type of incineration.
        fossil_fuel_types (list): List of fossil fuel types used for operation activities.
        fossil_fuel_consumptions (list): List of fossil fuel consumption values (liters/day).
        electricity_used (float): Electricity used for operation activities (kWh/day).
        energy_recovery_type (str): Type of energy recovered (e.g., heat, electricity).
        efficiency_electricity_recovery (float): Efficiency of electricity recovery.
        percentage_electricity_used_onsite (float): Percentage of electricity used onsite.
        efficiency_heat_recovery (float): Efficiency of heat recovery.
        percentage_heat_used_onsite (float): Percentage of recovered heat used onsite.
        fossil_fuel_replaced (list): List of fossil fuel types replaced by recovered heat.
    """

    def __init__(
        self,
        waste_incinerated: float,
        incineration_type: str,
        fossil_fuel_types: list,
        fossil_fuel_consumptions: list,
        electricity_used: float,
        energy_recovery_type: str,
        efficiency_electricity_recovery: float,
        percentage_electricity_used_onsite: float,
        efficiency_heat_recovery: float,
        percentage_heat_used_onsite: float,
        fossil_fuel_replaced: list,
    ):
        self.waste_incinerated = waste_incinerated
        self.incineration_type = incineration_type
        self.fossil_fuel_types = fossil_fuel_types
        self.fossil_fuel_consumptions = fossil_fuel_consumptions
        self.electricity_used = electricity_used
        self.energy_recovery_type = energy_recovery_type
        self.efficiency_electricity_recovery = efficiency_electricity_recovery
        self.percentage_electricity_used_onsite = percentage_electricity_used_onsite
        self.efficiency_heat_recovery = efficiency_heat_recovery
        self.percentage_heat_used_onsite = percentage_heat_used_onsite
        self.fossil_fuel_replaced = fossil_fuel_replaced

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

    def _calculate_emissions(
        self, fuel_types: list, fuel_consumed: list, factor_key: str, per_waste: float
    ) -> float:
        """
        Calculate emissions for different gases based on fuel consumption.

        Args:
            fuel_types (list): List of fuel types used.
            fuel_consumed (list): Corresponding fuel consumption in liters per tonne waste treated.
            factor_key (str): Key for the emission factor in the JSON file.
            per_waste (float): Amount of waste incinerated.

        Returns:
            float: Emissions per ton of waste.
        """
        if not isinstance(fuel_types, list):
            fuel_types = [fuel_types]
        if not isinstance(fuel_consumed, list):
            fuel_consumed = [fuel_consumed]

        total_emissions = 0
        fuel_data = self.data_incineration.get("fuel_data", {})
        available_fuels = fuel_data.get("Fuel Type", [])

        for fuel, consumption in zip(fuel_types, fuel_consumed):
            if fuel in available_fuels:
                fuel_index = available_fuels.index(fuel)
                energy_content = fuel_data["Energy Content (MJ/L)"][fuel_index]
                emission_factor = fuel_data[factor_key][fuel_index]
                total_emissions += consumption * energy_content * emission_factor

        return total_emissions / per_waste if per_waste > 0 else 0

    def waste_combustion_emissions(
        self, incineration_type: str, emission_type: str
    ) -> float:
        """
        Retrieve the emission factor for a given incineration type and emission type.

        Args:
            incineration_type (str): Type of incineration.
            emission_type (str): Type of emission.

        Returns:
            float: Emission factor for the given incineration type and emission type.
        """
        incineration_emissions = self.data_incineration.get("incineration_emissions", {})

        if incineration_type not in incineration_emissions:
            raise ValueError(
                f"Incineration type '{incineration_type}' not found in the dataset."
            )

        emissions_data = incineration_emissions[incineration_type]

        if emission_type not in emissions_data:
            raise ValueError(
                f"Emission type '{emission_type}' not found for incineration type '{incineration_type}'."
            )

        return emissions_data[emission_type]

    def ch4_emit_incineration(self) -> float:
        """
        Calculate CH4 (methane) emissions from incineration.

        Returns:
            float: Total CH4 emissions in terms of CO2-equivalent (kg CO2e).
        """
        gwp_factors = self.data_trans.get("gwp_factors", {})
        methane_fossil_index = gwp_factors["Type of gas"].index("CH4-fossil")
        methane_bio_index = gwp_factors["Type of gas"].index("CH4-biogenic")
        gwp_100_fossil = gwp_factors["GWP100"][methane_fossil_index]
        gwp_100_biogenic = gwp_factors["GWP100"][methane_bio_index]

        ch4_waste_combustion = self.waste_combustion_emissions(
            self.incineration_type, "CH4 emissions (kg/tonne of wet waste)"
        )
        ch4_fuel_combustion = self._calculate_emissions(
            self.fossil_fuel_types,
            self.fossil_fuel_consumptions,
            "CH4 Emission Factor (kg/MJ)",
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
        # Placeholder logic for CH4 emissions avoided
        return 0.0

    def co2_emit_incineration(self) -> float:
        """
        Calculate CO2 (carbon dioxide) emissions from incineration.

        Returns:
            float: Total CO2 emissions (kg CO2e).
        """
        grid_emission_factor = self.data_trans.get("electricity_grid_factor", {})
        co2_per_kwh = grid_emission_factor.get("CO2 kg-eq/kWh", 0)
        total_co2_electricity = self.electricity_used * co2_per_kwh / self.waste_incinerated

        co2_fuel_combustion = self._calculate_emissions(
            self.fossil_fuel_types,
            self.fossil_fuel_consumptions,
            "CO2 Emission Factor (kg/MJ)",
            self.waste_incinerated,
        )

        fossil_based_co2_emissions = self.data_incineration.get("fossil_based_co2_emissions", {})
        total_co2_waste_combustion = 0
        for waste_type, properties in fossil_based_co2_emissions.items():
            dry_matter_content = properties.get("Dry matter content (%)", 0)
            total_carbon_content = properties.get("Total carbon content (%)", 0)
            fossil_carbon_fraction = properties.get("Fossil carbon fraction (%)", 0)
            oxidation_factor = properties.get("Oxidation factor (%)", 0)
            mixed_waste_composition = properties.get("Mixed Waste Composition (%)", 0)

            fossil_carbon_wet_waste = (
                (dry_matter_content / 100)
                * (total_carbon_content / 100)
                * (fossil_carbon_fraction / 100)
                * (oxidation_factor / 100)
            )
            co2_emission = (
                1000
                * fossil_carbon_wet_waste
                * (mixed_waste_composition / 100)
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
        # Placeholder logic for CO2 emissions avoided
        return 0.0

    def n2o_emit_incineration(self) -> float:
        """
        Calculate N2O (nitrous oxide) emissions from incineration.

        Returns:
            float: Total N2O emissions in terms of CO2-equivalent (kg CO2e).
        """
        gwp_factors = self.data_trans.get("gwp_factors", {})
        n2o_index = gwp_factors["Type of gas"].index("N2O")
        gwp_100_n2o = gwp_factors["GWP100"][n2o_index]

        n2o_waste_combustion = self.waste_combustion_emissions(
            self.incineration_type, "N2O emissions (kg/tonne of wet waste)"
        )
        n2o_fuel_combustion = self._calculate_emissions(
            self.fossil_fuel_types,
            self.fossil_fuel_consumptions,
            "N2O Emission Factor (kg/MJ)",
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
        # Placeholder logic for N2O emissions avoided
        return 0.0

    def bc_emit_incineration(self) -> float:
        """
        Calculate BC (black carbon) emissions from incineration.

        Returns:
            float: Total BC emissions in terms of CO2-equivalent (kg CO2e).
        """
        gwp_factors = self.data_trans.get("gwp_factors", {})
        bc_index = gwp_factors["Type of gas"].index("BC")
        gwp_100_bc = gwp_factors["GWP100"][bc_index]

        bc_waste_combustion = self.waste_combustion_emissions(
            self.incineration_type, "BC emissions (kg/tonne of wet waste)"
        )
        bc_fuel_combustion = self._calculate_emissions(
            self.fossil_fuel_types,
            self.fossil_fuel_consumptions,
            "BC Emission Factor (kg/MJ)",
            self.waste_incinerated,
        )

        total_bc_emissions = gwp_100_bc * (bc_fuel_combustion + bc_waste_combustion)
        return total_bc_emissions

    def bc_avoid_incineration(self) -> float:
        """
        Calculate black carbon emissions avoided due to incineration.

        Returns:
            float: Total BC emissions avoided (kg CO2e).
        """
        # Placeholder logic for BC emissions avoided
        return 0.0

    def overall_emissions(self):
        """
        Calculate kgCO2e emissions and emissions avoided per ton of waste treated for incineration.

        Returns:
            dict: A dictionary containing emissions, avoided emissions, total emissions, 
                total avoided emissions, and net emissions.
        """
        return {
            "ch4_emissions": self.ch4_emit_incineration(),
            "ch4_emissions_avoid": self.ch4_avoid_incineration(),
            "co2_emissions": self.co2_emit_incineration(),
            "co2_emissions_avoid": self.co2_avoid_incineration(),
            "n2o_emissions": self.n2o_emit_incineration(),
            "n2o_emissions_avoid": self.n2o_avoid_incineration(),
            "bc_emissions": self.bc_emit_incineration(),
            "bc_emissions_avoid": self.bc_avoid_incineration(),
            "total_emissions": (
                self.ch4_emit_incineration()
                + self.co2_emit_incineration()
                + self.n2o_emit_incineration()
                + self.bc_emit_incineration()
            ),
            "total_emissions_avoid": (
                self.ch4_avoid_incineration()
                + self.co2_avoid_incineration()
                + self.n2o_avoid_incineration()
                + self.bc_avoid_incineration()
            ),
            "net_emissions": (
                self.ch4_emit_incineration()
                + self.co2_emit_incineration()
                + self.n2o_emit_incineration()
                + self.bc_emit_incineration()
                - (
                    self.ch4_avoid_incineration()
                    + self.co2_avoid_incineration()
                    + self.n2o_avoid_incineration()
                    + self.bc_avoid_incineration()
                )
            ),
        }