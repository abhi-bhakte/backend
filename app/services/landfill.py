import json
from pathlib import Path
from .transportation import TransportationEmissions


class LandfillEmissions:
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
        grid_electricity (float): Grid electricity used for operation activities (kWh).
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
        grid_electricity: float,
        gas_collection_efficiency: float = 0.0,
        gas_treatment_method: str = None,
        lfg_utilization_efficiency: float = 0.0,
        gas_recovery_start_year: int = None,
        gas_recovery_end_year: int = None,
        replaced_fossil_fuel_type: str = None,
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
            grid_electricity (float): Grid electricity used for operation activities (kWh).
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
                grid_electricity,
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
        self.grid_electricity = grid_electricity
        self.gas_collection_efficiency = gas_collection_efficiency
        self.gas_treatment_method = gas_treatment_method
        self.lfg_utilization_efficiency = lfg_utilization_efficiency
        self.gas_recovery_start_year = gas_recovery_start_year
        self.gas_recovery_end_year = gas_recovery_end_year
        self.replaced_fossil_fuel_type = replaced_fossil_fuel_type

        # Load emission factor data
        self.trans_file = Path(__file__).parent.parent / "data" / "transportation.json"
        self.landfill_file = Path(__file__).parent.parent / "data" / "landfill.json"

        self.data_landfill = self._load_json_file(self.landfill_file)
        self.data_trans = self._load_json_file(self.trans_file)

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

    def ch4_emit_landfill(self) -> float:
        """
        Calculate CH₄ emissions (kg CO₂-eq) per ton of waste landfilled, applying GWP100.

        Returns:
            float: CH₄ emissions from fuel combustion, as CO₂-eq.
        """
        ch4_fuel_combustion = self._calculate_emissions(
            self.fossil_fuel_types,
            self.fossil_fuel_consumed,
            "ch4_kg_per_mj",
            self.waste_disposed,
        )
        # Use fossil GWP for landfill fuel combustion
        gwp_100_fossil = self._gwp100("ch4_fossil")
        return ch4_fuel_combustion * gwp_100_fossil

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

        total_co2_electricity = self.grid_electricity * co2_per_kwh / amount_deposited if amount_deposited > 0 else 0

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
        Calculate kgCO2e emissions and BC mass per ton of waste treated, matching composting.py output format.

        Returns:
            dict: Dictionary containing all emissions, avoided emissions, total emissions,
                  total avoided emissions, and net emissions. BC is reported as mass (kg/ton).
        """
        ch4_e = self.ch4_emit_landfill()
        ch4_a = self.ch4_avoid_landfill()
        co2_e = self.co2_emit_landfill()
        co2_a = self.co2_avoid_landfill()
        n2o_e = self.n2o_emit_landfill()
        n2o_a = self.n2o_avoid_landfill()
        bc_e = self.bc_emit_landfill()
        bc_a = self.bc_avoid_landfill()

        total_emissions = ch4_e + co2_e + n2o_e
        total_emissions_avoid = ch4_a + co2_a + n2o_a

        return {
            "ch4_emissions": ch4_e,
            "ch4_emissions_avoid": ch4_a,
            "co2_emissions": co2_e,
            "co2_emissions_avoid": co2_a,
            "n2o_emissions": n2o_e,
            "n2o_emissions_avoid": n2o_a,
            "bc_emissions": bc_e,           # kg BC/ton
            "bc_emissions_avoid": bc_a,     # kg BC/ton
            "total_emissions": total_emissions,
            "total_emissions_avoid": total_emissions_avoid,
            "net_emissions": total_emissions - total_emissions_avoid,
            "net_emissions_bc": bc_e - bc_a # kg BC/ton
        }