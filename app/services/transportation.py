import json
from pathlib import Path


DATA_FILE = Path(__file__).parent.parent / "data" / "transportation.json"


class TransportationEmissions:
    """
    A class to calculate GHG emissions (CH₄, BC, N₂O, CO₂) from transportation and
    transfer station operations based on fuel consumption and electricity use.

    Attributes:
        waste_formal (float): Waste collected (tons).
        fuel_types_transport (list[str]): Fuel types used in transport.
        fuel_consumed_transport (list[float]): Fuel consumption values.
        vehicle_type (str): Type of vehicle used.
        waste_transfer_station (bool): Whether a transfer station is used.
        fuel_types_station (list[str]): Fuel types used in the transfer station.
        fuel_consumed_station (list[float]): Fuel consumption values at the station.
        electric_consumed (float): Electricity consumed at the station (kWh).
        waste_handled_at_station (float): Waste handled at the station (tons).
        data (dict): Emission factor data loaded from JSON.
    """
    
    def __init__(
        self, waste_formal, fuel_types_transport, fuel_consumed_transport,
        vehicle_type, waste_transfer_station, fuel_types_station,
        fuel_consumed_station, electric_consumed, waste_handled_at_station):
        """
        Initialize the TransportationEmissions class and validate inputs.
        
        Args:
            waste_formal (float): Waste collected (tons).
            fuel_types_transport (list[str]): Fuel types used in transport.
            fuel_consumed_transport (list[float]): Fuel consumption values.
            vehicle_type (str): Type of vehicle used.
            waste_transfer_station (bool): Whether a transfer station is used.
            fuel_types_station (list[str]): Fuel types used in the transfer station.
            fuel_consumed_station (list[float]): Fuel consumption values.
            electric_consumed (float): Electricity consumed at the station (kWh).
            waste_handled_at_station (float): Waste handled at the station (tons).
    
        
        Raises:
            ValueError: If any fuel, waste, or electricity values are negative.
            FileNotFoundError: If the data file is not found.
            ValueError: If there is an error decoding the JSON file.
        """
        if any(x < 0 for x in [waste_formal, electric_consumed, waste_handled_at_station]):
            raise ValueError("Waste and electricity values cannot be negative.")
        if any(x < 0 for x in fuel_consumed_transport + fuel_consumed_station):
            raise ValueError("Fuel consumption cannot be negative.")
        
        self.waste_formal = waste_formal
        self.fuel_types_transport = fuel_types_transport
        self.fuel_consumed_transport = fuel_consumed_transport
        self.vehicle_type = vehicle_type
        self.waste_transfer_station = waste_transfer_station
        self.fuel_types_station = fuel_types_station
        self.fuel_consumed_station = fuel_consumed_station
        self.electric_consumed = electric_consumed
        self.waste_handled_at_station = waste_handled_at_station
        self.data_file = DATA_FILE
        
        try:
            with open(self.data_file, "r", encoding="utf-8") as file:
                self.data = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {DATA_FILE} was not found.")
        except json.JSONDecodeError:
            raise ValueError("Error decoding JSON file. Please check the format.")

    @staticmethod
    def _normalize_key(text: str) -> str:
        """Normalize free-text keys to snake_case compatible with JSON keys."""
        return (
            (text or "")
            .strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
            .replace("/", "_")
        )

    def _default_units_for_fuels(self, fuel_types):
        """Return a list of default units for the given fuel types.

        Defaults:
        - "cng" -> "kg"
        - "ev"  -> "kWh"
        - others -> "L"
        """
        defaults = []
        for fuel in fuel_types:
            f = self._normalize_key(fuel)
            if f == "cng":
                defaults.append("kg")
            elif f == "ev":
                defaults.append("kWh")
            else:
                defaults.append("L")
        return defaults
    
    def _calculate_emissions(self, fuel_types, fuel_consumed, factor_key, per_waste, vehicle_type=None):
        """
        Generic method to calculate emissions for different gases based on fuel use.
        
        Args:
            fuel_types (list[str]): List of fuel types.
            fuel_consumed (list[float]): Corresponding fuel consumption in liters.
            factor_key (str): The key for the emission factor in the JSON file.
            per_waste (float): The waste amount for normalization.
            vehicle_type (str, optional): Vehicle type for specific emission factors.
        
        Returns:
            float: Emissions per ton of waste.
        """
        total_emissions = 0

        # Fetch correct fuel data and vehicle data (normalized JSON expected)
        fuel_raw = self.data.get("fuel_data", [])
        vehicle_raw = self.data.get("vehicle_emission_factors", [])

        # Available types from normalized JSON
        available_fuels = [f.get("fuel_type") for f in fuel_raw]
        available_vehicles = [v.get("vehicle_type") for v in vehicle_raw]

        # Use hard-coded default units per fuel type
        units = self._default_units_for_fuels(fuel_types)

        for fuel, consumption, unit in zip(fuel_types, fuel_consumed, units):
            f_norm = self._normalize_key(fuel)
            if f_norm in available_fuels:
                f_entry = next((x for x in fuel_raw if x.get("fuel_type") == f_norm), None)
                if f_entry is None:
                    continue
                energy_content = f_entry.get("energy_content_mj_per_l", 0)
                fuel_density = f_entry.get("density_kg_per_l", None)
                # Normalize consumption to the expected basis for each factor
                # When using vehicle-specific BC factor (kg/kg fuel), work with mass (kg)
                # Otherwise, convert to liters to multiply by energy content (MJ/L)
                
                # Special handling for EV: consumption measured in kWh, emissions via grid factor
                if f_norm == "ev":
                    unit_l = unit.lower()
                    if unit_l not in ("kwh", "kwh/day", "kwhd"):
                        # If unit not provided or not kWh, assume the number is already kWh (backward compatible)
                        # but warn by raising if clearly incompatible units like L or kg are specified
                        if unit_l.startswith("l") or unit_l.startswith("kg"):
                            raise ValueError("EV consumption should be provided in kWh. Use unit 'kWh'.")
                    # Only CO2 is considered from electricity using grid factor
                    if factor_key == "co2_kg_per_mj":
                        grid_factor = self.data.get("electricity_grid_factor", {}).get(
                            "co2_kg_per_kwh", 0
                        )
                        total_emissions += consumption * grid_factor
                    else:
                        total_emissions += 0
                    continue
                
                # Check if vehicle type is provided and exists in the dataset
                v_type_norm = self._normalize_key(vehicle_type) if vehicle_type else None
                if v_type_norm and v_type_norm in available_vehicles:
                    # Vehicle-specific factor (only BC kg/kg fuel supported)
                    v_entry = next((v for v in vehicle_raw if v.get("vehicle_type") == v_type_norm), None)
                    emission_factor = v_entry.get(factor_key, 0) if v_entry else 0
                    # Determine fuel mass in kg
                    if unit.lower().startswith("kg"):
                        fuel_mass_kg = consumption
                    else:
                        # unit liters -> convert to kg via density
                        if fuel_density is None:
                            raise ValueError(f"Missing fuel density for {fuel} to convert liters to kg.")
                        fuel_mass_kg = consumption * fuel_density
                    total_emissions += (fuel_mass_kg * emission_factor)
                else:
                    emission_factor = f_entry.get("emission_factors", {}).get(factor_key, 0)
                    # Working on energy basis: MJ/L times liters
                    if unit.lower().startswith("kg"):
                        # Convert kg to liters using density
                        if fuel_density is None or fuel_density == 0:
                            raise ValueError(f"Missing or zero fuel density for {fuel} to convert kg to liters.")
                        consumption_liters = consumption / fuel_density
                    else:
                        consumption_liters = consumption
                    total_emissions += (consumption_liters * energy_content * emission_factor)

        
        return total_emissions / per_waste if per_waste > 0 else 0
    
    def _gwp100(self, key: str):
        """Return GWP100 using the exact JSON key (no mapping)."""
        gwp = self.data.get("gwp_factors", {})
        return gwp.get(key, {}).get("gwp100", 0)

    def ch4_emit_collection(self):
        """Calculate CH₄ emissions (kgCO₂e) per ton of waste collected."""

        gwp_100_methane = self._gwp100("ch4_fossil")

        return (
            gwp_100_methane
            * (
                self._calculate_emissions(
                    self.fuel_types_transport,
                    self.fuel_consumed_transport,
                    "ch4_kg_per_mj",
                    self.waste_formal,
                )
                + self._calculate_emissions(
                    self.fuel_types_station,
                    self.fuel_consumed_station,
                    "ch4_kg_per_mj",
                    self.waste_handled_at_station,
                )
            )
        )
    
    def bc_emit_collection(self):
        """Calculate BC emissions per ton of waste collected based on vehicle type."""

        gwp_100_black = self._gwp100("bc")


        return (
            gwp_100_black * (
                self._calculate_emissions(
                    self.fuel_types_transport,
                    self.fuel_consumed_transport,
                    "bc_kg_per_kg_fuel",
                    self.waste_formal,
                    self.vehicle_type,
                )
                + self._calculate_emissions(
                    self.fuel_types_station,
                    self.fuel_consumed_station,
                    "bc_kg_per_mj",
                    self.waste_handled_at_station,
                )
            )
        )
    
    def n2o_emit_collection(self):
        """Calculate N₂O emissions per ton of waste collected."""

        gwp_100_nitrous = self._gwp100("n2o")

        return (
            gwp_100_nitrous
            * (
                self._calculate_emissions(
                    self.fuel_types_transport,
                    self.fuel_consumed_transport,
                    "n2o_kg_per_mj",
                    self.waste_formal,
                )
                + self._calculate_emissions(
                    self.fuel_types_station,
                    self.fuel_consumed_station,
                    "n2o_kg_per_mj",
                    self.waste_handled_at_station,
                )
            )
        )
    
    def co2_emit_collection(self):
        """
        Calculate CO₂ emissions from:
        1. Collection fuel (transport vehicles).
        2. Transfer station fuel (stationary equipment).
        3. Grid electricity consumption at the transfer station.
        
        Returns:
            float: Total CO₂ emissions per ton of waste collected.
        """
        co2_transport = self._calculate_emissions(
            self.fuel_types_transport,
            self.fuel_consumed_transport,
            "co2_kg_per_mj",
            self.waste_formal,
        )

        co2_station = self._calculate_emissions(
            self.fuel_types_station,
            self.fuel_consumed_station,
            "co2_kg_per_mj",
            self.waste_handled_at_station,
        )

        # Calculate CO2 emissions from electricity consumption
        grid_emission_factor = self.data.get("electricity_grid_factor", {})
        total_co2_electricity = self.electric_consumed * grid_emission_factor.get(
            "co2_kg_per_kwh", 0
        )

        co2_grid = (
            total_co2_electricity / self.waste_handled_at_station
            if self.waste_handled_at_station > 0
            else 0
        )

        return co2_transport + co2_station + co2_grid


    def overall_emissions(self):
        """Calculate total emissions (CH₄, BC, N₂O, CO₂) per ton of waste collected."""

        # Calculate emissions for different gases
        ch4 = self.ch4_emit_collection()
        co2 = self.co2_emit_collection()
        n2o = self.n2o_emit_collection()
        bc = self.bc_emit_collection()

        return {
            "ch4_emissions": ch4,
            "co2_emissions": co2,
            "n2o_emissions": n2o,
            "bc_emissions": bc,
            "total_emissions": ch4 + co2 + n2o + bc,
            "total_emissions_avoid": 0,
            "net_emissions": ch4 + co2 + n2o + bc,
        }