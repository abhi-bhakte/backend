"""
NOTE:
For CNG and coal, the energy content values in the JSON file are actually in units of MJ per kg, 
not MJ per liter. However, for consistency, the JSON key remains "energy_content_mj_per_l". 
Users should enter CNG and coal consumption in kg, and the code will interpret the energy 
content accordingly for these fuels. This is to maintain database structure consistency.
"""

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
        All fuels except 'ev' are in liters; 'ev' is in kWh."""
        return ["kWh" if self._normalize_key(fuel) == "ev" else "L" for fuel in fuel_types]
    
    def _calculate_emissions(self, fuel_types, fuel_consumed, factor_key, per_waste, vehicle_type=None):
        """
        Generic method to calculate emissions for different gases based on fuel use.
        For BC, if vehicle_type is provided and valid, use (consumption * vehicle_emission_factors[bc_kg_per_kg_fuel] * density_kg_per_l).
        For other gases, use the default logic.
        
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
            if f_norm not in available_fuels:
                continue

            f_entry = next((x for x in fuel_raw if x.get("fuel_type") == f_norm), None)
            if f_entry is None:
                continue

            energy_content = f_entry.get("energy_content_mj_per_l", 0)
            density_kg_per_l = f_entry.get("density_kg_per_l", 1)

            # Special handling for EV: consumption measured in kWh, emissions via grid factor
            if f_norm == "ev":
                if unit.lower() not in ("kwh", "kwh/day", "kwhd"):
                    if unit.lower().startswith("l") or unit.lower().startswith("kg"):
                        raise ValueError(
                            "EV consumption should be provided in kWh. Use unit 'kWh'."
                        )
                if factor_key == "co2_kg_per_mj":
                    grid_factor = self.data.get("electricity_grid_factor", {}).get(
                        "co2_kg_per_kwh", 0
                    )
                    total_emissions += consumption * grid_factor
                else:
                    total_emissions += 0
                continue

            # For BC, use vehicle-specific formula if vehicle_type is provided
            if factor_key == "bc_kg_per_kg_fuel" and vehicle_type:
                v_type_norm = self._normalize_key(vehicle_type)
                if v_type_norm not in available_vehicles:
                    raise ValueError(
                        f"Invalid vehicle_type '{vehicle_type}' for BC emissions. "
                        f"Must be one of: {available_vehicles}"
                    )
                v_entry = next(
                    (v for v in vehicle_raw if v.get("vehicle_type") == v_type_norm), None
                )
                emission_factor = v_entry.get(factor_key, 0) if v_entry else 0
                # Use: (consumption in L) * density_kg_per_l * bc_kg_per_kg_fuel
                total_emissions += consumption * density_kg_per_l * emission_factor
            else:
                emission_factor = f_entry.get("emission_factors", {}).get(factor_key, 0)
                total_emissions += consumption * energy_content * emission_factor

        if per_waste > 0:
            return total_emissions / per_waste
        return 0
    
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

    def ch4_emit_collection_absolute(self):
        """Calculate absolute CH₄ emissions (kgCO₂e) for the given waste quantities.

        Returns:
            float: Total CH₄ emissions in kgCO₂e.
        """

        gwp_100_methane = self._gwp100("ch4_fossil")

        # Absolute emissions = per-ton result multiplied by respective waste amounts.
        # Transport normalized by `waste_formal`, station normalized by `waste_handled_at_station`.
        ch4_transport_per_ton = self._calculate_emissions(
            self.fuel_types_transport,
            self.fuel_consumed_transport,
            "ch4_kg_per_mj",
            self.waste_formal,
        )
        ch4_station_per_ton = self._calculate_emissions(
            self.fuel_types_station,
            self.fuel_consumed_station,
            "ch4_kg_per_mj",
            self.waste_handled_at_station,
        )

        ch4_transport_abs = ch4_transport_per_ton * self.waste_formal
        ch4_station_abs = ch4_station_per_ton * self.waste_handled_at_station

        return gwp_100_methane * (ch4_transport_abs + ch4_station_abs)
    
    def bc_emit_collection(self):
        """Calculate BC emissions (mass, kg) per ton of waste collected based on vehicle type."""
        # Require vehicle_type for BC calculation
        if not self.vehicle_type or not self.vehicle_type.strip():
            raise ValueError("vehicle_type must be provided for BC emissions calculation.")
        # BC is reported as mass (kg), not CO2e. Do not multiply by GWP.
        return (
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

    def bc_emit_collection_absolute(self):
        """Calculate absolute BC mass (kg) for the given waste quantities."""
        bc_transport_per_ton = self._calculate_emissions(
            self.fuel_types_transport,
            self.fuel_consumed_transport,
            "bc_kg_per_kg_fuel",
            self.waste_formal,
            self.vehicle_type,
        )
        bc_station_per_ton = self._calculate_emissions(
            self.fuel_types_station,
            self.fuel_consumed_station,
            "bc_kg_per_mj",
            self.waste_handled_at_station,
        )
        bc_transport_abs = bc_transport_per_ton * self.waste_formal
        bc_station_abs = bc_station_per_ton * self.waste_handled_at_station
        return bc_transport_abs + bc_station_abs
    
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

    def n2o_emit_collection_absolute(self):
        """Calculate absolute N₂O emissions (kgCO₂e) for the given waste quantities."""
        gwp_100_nitrous = self._gwp100("n2o")
        n2o_transport_per_ton = self._calculate_emissions(
            self.fuel_types_transport,
            self.fuel_consumed_transport,
            "n2o_kg_per_mj",
            self.waste_formal,
        )
        n2o_station_per_ton = self._calculate_emissions(
            self.fuel_types_station,
            self.fuel_consumed_station,
            "n2o_kg_per_mj",
            self.waste_handled_at_station,
        )
        n2o_transport_abs = n2o_transport_per_ton * self.waste_formal
        n2o_station_abs = n2o_station_per_ton * self.waste_handled_at_station
        return gwp_100_nitrous * (n2o_transport_abs + n2o_station_abs)
    
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

    def co2_emit_collection_absolute(self):
        """Calculate absolute CO₂ emissions (kgCO₂e) for the given waste quantities."""
        co2_transport_per_ton = self._calculate_emissions(
            self.fuel_types_transport,
            self.fuel_consumed_transport,
            "co2_kg_per_mj",
            self.waste_formal,
        )
        co2_station_per_ton = self._calculate_emissions(
            self.fuel_types_station,
            self.fuel_consumed_station,
            "co2_kg_per_mj",
            self.waste_handled_at_station,
        )
        grid_emission_factor = self.data.get("electricity_grid_factor", {})
        total_co2_electricity = self.electric_consumed * grid_emission_factor.get("co2_kg_per_kwh", 0)
        co2_transport_abs = co2_transport_per_ton * self.waste_formal
        co2_station_abs = co2_station_per_ton * self.waste_handled_at_station
        return co2_transport_abs + co2_station_abs + total_co2_electricity


    def overall_emissions(self):
        """Return both per-ton and absolute outputs for CH4, CO2, N2O; BC is mass.

        Transportation has no avoided emissions; avoided totals are 0.
        """

        # Per-ton emissions
        ch4_e = self.ch4_emit_collection()
        co2_e = self.co2_emit_collection()
        n2o_e = self.n2o_emit_collection()
        bc_e = self.bc_emit_collection()

        # Absolute emissions (kgCO2e or kg for BC)
        ch4_abs = self.ch4_emit_collection_absolute()
        co2_abs = self.co2_emit_collection_absolute()
        n2o_abs = self.n2o_emit_collection_absolute()
        bc_abs = self.bc_emit_collection_absolute()

        # Totals in CO2e exclude BC mass
        total_emissions = ch4_e + co2_e + n2o_e
        total_emissions_total = ch4_abs + co2_abs + n2o_abs

        # Net equals total (no avoided emissions in transportation)
        net_emissions = total_emissions
        net_emissions_total = total_emissions_total
        net_emissions_bc = bc_e
        net_emissions_bc_total = bc_abs

        return {
            # Per-ton outputs
            "ch4_emissions": ch4_e,
            "co2_emissions": co2_e,
            "n2o_emissions": n2o_e,
            "bc_emissions": bc_e,
            "total_emissions": total_emissions,
            "total_emissions_avoid": 0,
            "net_emissions": net_emissions,
            "net_emissions_bc": net_emissions_bc,

            # Absolute outputs
            "ch4_emissions_total": ch4_abs,
            "co2_emissions_total": co2_abs,
            "n2o_emissions_total": n2o_abs,
            "bc_emissions_total": bc_abs,
            "total_emissions_total": total_emissions_total,
            "total_emissions_avoid_total": 0,
            "net_emissions_total": net_emissions_total,
            "net_emissions_bc_total": net_emissions_bc_total,
        }