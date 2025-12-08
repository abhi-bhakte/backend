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
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON file {self.ad_file}: {e}")
        
        # Load emission factor data
        try:
            with open(self.trans_file, "r", encoding="utf-8") as file:
                self.data_trans = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {self.trans_file} was not found.")
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON file {self.trans_file}: {e}")

    @staticmethod
    def _normalize_key(value: str) -> str:
        """Normalize strings for key matching (lowercase, underscores)."""
        return str(value).strip().lower().replace(" ", "_")

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
        total_emissions = 0.0

        # Retrieve fuel data from the dataset (standardized list of objects)
        fuel_data_list = self.data_ad.get("fuel_data", [])

        # Iterate through each fuel type and compute emissions
        for fuel, consumption in zip(fuel_types, fuel_consumed):
            fuel_norm = self._normalize_key(fuel)

            # Find matching fuel object
            fuel_obj = next(
                (f for f in fuel_data_list if self._normalize_key(f.get("fuel_type")) == fuel_norm),
                None,
            )
            if not fuel_obj:
                continue

            energy_content = float(fuel_obj.get("energy_content_mj_per_l", 0) or 0)
            emission_factor = float(
                (fuel_obj.get("emission_factors", {}) or {}).get(factor_key, 0) or 0
            )

            # Calculate emissions based on energy content and emission factor
            total_emissions += float(consumption or 0) * energy_content * emission_factor

        # Normalize emissions by waste amount, avoiding division by zero
        return total_emissions / per_waste if per_waste > 0 else 0.0
    
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
        bio_leakage_factor = (
            ad_factors.get("ipcc_default_values", {}).get("ch4_kg_per_ton", 0) or 0
        )

        # Retrieve Global Warming Potential (GWP) values (standardized keys)
        gwp_factors = self.data_trans.get("gwp_factors", {})
        gwp_100_fossil = (gwp_factors.get("ch4_fossil", {}) or {}).get("gwp100", 0) or 0
        gwp_100_biogenic = (gwp_factors.get("ch4_biogenic", {}) or {}).get("gwp100", 0) or 0

        # Total CH₄ emissions from:
        # 1. Fossil fuel use in operations (e.g., generators, transport)
        # 2. Biogenic CH₄ leakage during anaerobic digestion
        fossil_emissions = self._calculate_emissions(
            self.fuel_types_operation,
            self.fuel_consumed_operation,
            "ch4_kg_per_mj",
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
        # Retrieve electricity grid emission factor (kg CO₂ per kWh)
        grid_emission_factor = self.data_trans.get("electricity_grid_factor", {})
        co2_per_kwh = grid_emission_factor.get("co2_kg_per_kwh", 0) or 0
        
        # Calculate CO₂ emissions from electricity consumption
        total_co2_electricity = self.electricity_consumed * co2_per_kwh
        
        # Calculate CO₂ emissions from fuel consumption
        co2_from_fuel = self._calculate_emissions(
            self.fuel_types_operation,
            self.fuel_consumed_operation,
            "co2_kg_per_mj",
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
        gwp_100_n2o = (gwp_factors.get("n2o", {}) or {}).get("gwp100", 0) or 0
        
        # Calculate N₂O emissions from fuel combustion and AD process
        n2o_from_fuel = self._calculate_emissions(
            self.fuel_types_operation,
            self.fuel_consumed_operation,
            "n2o_kg_per_mj",
            self.waste_digested,
        )
        
        return (gwp_100_n2o * n2o_from_fuel)

    def n2o_avoid_ad(self):
        return 0

    def bc_emit_ad(self):
        """
        Calculate black carbon (BC) mass in kg per ton of waste treated (not CO2e).
        """
        # Direct mass of BC from fuel combustion (kg), no GWP conversion
        return self._calculate_emissions(
            self.fuel_types_operation,
            self.fuel_consumed_operation,
            "bc_kg_per_mj",
            self.waste_digested,
        )

    def bc_avoid_ad(self):
        """Calculate methane emissions."""
        return 0

    def overall_emissions(self):
        """kgCO2e emissions and emissions avoided per ton of waste digested, plus total (kgCO2e) outputs."""
        ch4_e = self.ch4_emit_ad()
        co2_e = self.co2_emit_ad()
        n2o_e = self.n2o_emit_ad()
        bc_e = self.bc_emit_ad()

        ch4_a = self.ch4_avoid_ad()
        co2_a = self.co2_avoid_ad()
        n2o_a = self.n2o_avoid_ad()
        bc_a = self.bc_avoid_ad()

        # Totals are in CO2e and should exclude BC mass (tracked separately)
        total_emissions = ch4_e + co2_e + n2o_e
        total_emissions_avoid = ch4_a + co2_a + n2o_a
        net_emissions = total_emissions - total_emissions_avoid
        net_emissions_bc = bc_e - bc_a

        # Total outputs (kgCO2e, not per tonne)
        multiplier = self.waste_digested if self.waste_digested > 0 else 1
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
            "net_emissions": net_emissions,
            "net_emissions_bc": net_emissions_bc,

            # New total outputs (kgCO2e, not per tonne)
            "ch4_emissions_total": ch4_e * multiplier,
            "ch4_emissions_avoid_total": ch4_a * multiplier,
            "co2_emissions_total": co2_e * multiplier,
            "co2_emissions_avoid_total": co2_a * multiplier,
            "n2o_emissions_total": n2o_e * multiplier,
            "n2o_emissions_avoid_total": n2o_a * multiplier,
            "bc_emissions_total": bc_e * multiplier,
            "bc_emissions_avoid_total": bc_a * multiplier,
            "total_emissions_total": total_emissions * multiplier,
            "total_emissions_avoid_total": total_emissions_avoid * multiplier,
            "net_emissions_total": net_emissions * multiplier,
            "net_emissions_bc_total": net_emissions_bc * multiplier,
        }
