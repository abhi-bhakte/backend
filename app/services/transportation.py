import json
from pathlib import Path

data_file = Path(__file__).parent.parent / "data" / "transportation.json"


class TransportationEmissions:
    """
    A class to calculate GHG emissions (CH₄, BC, N₂O, CO₂) from transportation and
    transfer station operations based on fuel consumption and electricity use.

    Attributes:
        waste_formal (float): Waste collected (tons).
        fuel_types_transport (list[str]): Fuel types used in transport.
        fuel_consumed_transport (list[float]): Fuel consumption in liters.
        vehicle_type (str): Type of vehicle used.
        waste_transfer_station (bool): Whether a transfer station is used.
        fuel_types_station (list[str]): Fuel types used in the transfer station.
        fuel_consumed_station (list[float]): Fuel consumption in liters.
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
            fuel_consumed_transport (list[float]): Fuel consumption in liters.
            vehicle_type (str): Type of vehicle used.
            waste_transfer_station (bool): Whether a transfer station is used.
            fuel_types_station (list[str]): Fuel types used in the transfer station.
            fuel_consumed_station (list[float]): Fuel consumption in liters.
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
        self.data_file = data_file
        
        try:
            with open(self.data_file, "r", encoding="utf-8") as file:
                self.data = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {data_file} was not found.")
        except json.JSONDecodeError:
            raise ValueError("Error decoding JSON file. Please check the format.")
    
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




        # Fetch correct fuel data and vehicle data
        fuel_data = self.data.get("fuel_data", {})
        vehicle_data = self.data.get("vehicle_emission_factors", {})

        available_fuels = fuel_data.get("Fuel Type", [])
        available_vehicles = vehicle_data.get("Vehicle Type", [])

        for fuel, consumption in zip(fuel_types, fuel_consumed):
            if fuel in available_fuels:
                fuel_index = available_fuels.index(fuel)
                energy_content = fuel_data["Energy Content (MJ/L)"][fuel_index]
                
                # Check if vehicle type is provided and exists in the dataset
                if vehicle_type and vehicle_type in available_vehicles:
                    vehicle_index = available_vehicles.index(vehicle_type)
                    emission_factor = vehicle_data[factor_key][vehicle_index]
                    fuel_density = fuel_data["Fuel Density (kg/L)"][fuel_index]
                    total_emissions += (consumption * fuel_density * emission_factor)
                else:
                    emission_factor = fuel_data[factor_key][fuel_index]
                    total_emissions += (consumption * energy_content * emission_factor)

        
        return total_emissions / per_waste if per_waste > 0 else 0
    
    def ch4_emit_collection(self):
        """Calculate CH₄ emissions (kgeCO2) per ton of waste collected."""

        gwp_factors=self.data.get("gwp_factors", {})
        # Get methane GWP values
        methane_index = gwp_factors["Type of gas"].index("CH4-fossil")  # Get index of CH4-fossil
        gwp_100_methane = gwp_factors["GWP100"][methane_index]  # Get 100-year GWP

        return (
            gwp_100_methane * (
                self._calculate_emissions(
                    self.fuel_types_transport, 
                    self.fuel_consumed_transport, 
                    "CH4 Emission Factor (kg/MJ)", 
                    self.waste_formal
                ) + self._calculate_emissions(
                    self.fuel_types_station, 
                    self.fuel_consumed_station, 
                    "CH4 Emission Factor (kg/MJ)", 
                    self.waste_handled_at_station
                )
            )
        )
    
    def bc_emit_collection(self):
        """Calculate BC emissions per ton of waste collected based on vehicle type."""

        gwp_factors=self.data.get("gwp_factors", {})

        # Get black carbon GWP values
        black_index = gwp_factors["Type of gas"].index("BC")    
        gwp_100_black = gwp_factors["GWP100"][black_index]


        return (
            gwp_100_black * (
                self._calculate_emissions(
                    self.fuel_types_transport,
                    self.fuel_consumed_transport,
                    "BC Emission Factor (kg/kg fuel)",
                    self.waste_formal,
                    self.vehicle_type
                ) + self._calculate_emissions(
                    self.fuel_types_station,
                    self.fuel_consumed_station,
                    "BC Emissions (kg/MJ)",
                    self.waste_handled_at_station
                )
            )
        )
    
    def n2o_emit_collection(self):
        """Calculate N₂O emissions per ton of waste collected."""

        gwp_factors=self.data.get("gwp_factors", {})

        # Get nitrous oxide GWP values
        nitrous_index = gwp_factors["Type of gas"].index("N2O")
        gwp_100_nitrous = gwp_factors["GWP100"][nitrous_index]

        return (
            gwp_100_nitrous * (
                self._calculate_emissions(
                    self.fuel_types_transport, 
                    self.fuel_consumed_transport, 
                    "N2O Emission Factor (kg/MJ)", 
                    self.waste_formal
                    ) + 
                    self._calculate_emissions(
                    self.fuel_types_station, 
                    self.fuel_consumed_station, 
                    "N2O Emission Factor (kg/MJ)", 
                    self.waste_handled_at_station
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
            "CO2 Emission Factor (kg/MJ)",
            self.waste_formal,
        )

        co2_station = self._calculate_emissions(
            self.fuel_types_station,
            self.fuel_consumed_station,
            "CO2 Emission Factor (kg/MJ)",
            self.waste_handled_at_station,
        )

        # Calculate CO2 emissions from electricity consumption
        grid_emission_factor = self.data.get("electricity_grid_factor", {})
        total_co2_electricity = self.electric_consumed * grid_emission_factor.get(
            "CO2 kg-eq/kWh", 0
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
            "net_emissions": ch4 + co2 + n2o + bc
        }