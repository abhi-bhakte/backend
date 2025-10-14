from datetime import datetime, timedelta
from app.db.db import get_db
import pytz

COLLECTION_NAME = "waste_data"
IST = pytz.timezone("Asia/Kolkata")

def parse_date(date_str):
    for fmt in ("%d/%m/%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError

async def get_city_summary_service(city_name, start_date, end_date, db):
    # ...existing code...

    try:
        start_dt = parse_date(start_date)
        end_dt = parse_date(end_date)
    except Exception:
        raise ValueError("Invalid date format. Use dd/mm/yy or yyyy-mm-dd.")

    date_list = []
    current_dt = start_dt
    while current_dt <= end_dt:
        date_list.append(current_dt.strftime("%Y-%m-%d"))
        current_dt += timedelta(days=1)

    query = {
        "scenario.city_name": city_name,
        "scenario.date": {"$in": date_list}
    }
    cursor = db[COLLECTION_NAME].find(query, {"_id": 0})
    formally_collected_cumulative = 0
    informally_collected_cumulative = 0
    uncollected_cumulative = 0
    waste_diverted_cumulative = 0
    dry_percent_sum = 0
    wet_percent_sum = 0
    mixed_percent_sum = 0
    percent_days_count = 0
    treatment_methods = ["composting", "anaerobic_digestion", "recycling", "incineration"]
    ghg_methods = [
        "Composting",
        "Anaerobic Digestion",
        "Recycling",
        "Incineration",
        "Transportation"
    ]
    ghg_emission_cumulative = {"co2": 0, "ch4": 0, "n2o": 0, "bc": 0}
    composition_sums = {}
    composition_days_count = 0

    async for doc in cursor:
        scenario = doc.get("scenario", {})
        formally_collected = scenario.get("formally_collected", 0)
        informally_collected = scenario.get("informally_collected", 0)
        uncollected = scenario.get("uncollected", 0)
        if isinstance(formally_collected, (int, float)):
            formally_collected_cumulative += formally_collected
        if isinstance(informally_collected, (int, float)):
            informally_collected_cumulative += informally_collected
        if isinstance(uncollected, (int, float)):
            uncollected_cumulative += uncollected

        dry_percent = scenario.get("dry_waste_percentage", None)
        wet_percent = scenario.get("wet_waste_percentage", None)
        mixed_percent = scenario.get("mixed_waste_percentage", None)
        if all(isinstance(x, (int, float)) for x in [dry_percent, wet_percent, mixed_percent]):
            dry_percent_sum += dry_percent
            wet_percent_sum += wet_percent
            mixed_percent_sum += mixed_percent
            percent_days_count += 1

        waste_composition = scenario.get("waste_composition", {})
        if isinstance(waste_composition, dict) and waste_composition:
            for k, v in waste_composition.items():
                if isinstance(v, (int, float)):
                    composition_sums[k] = composition_sums.get(k, 0) + v
            composition_days_count += 1

        waste_allocation = scenario.get("waste_allocation", {})
        diverted_sum = 0
        for method in treatment_methods:
            value = waste_allocation.get(method, 0)
            if isinstance(value, (int, float)):
                diverted_sum += value
        waste_diverted_cumulative += diverted_sum

        emissions = doc.get("emissions", {})
        for method in ghg_methods:
            method_obj = emissions.get(method, {})
            for gas in ["co2", "ch4", "n2o", "bc"]:
                value = method_obj.get(gas, 0)
                if isinstance(value, str):
                    try:
                        value = float(value)
                    except ValueError:
                        value = 0
                if isinstance(value, (int, float)):
                    ghg_emission_cumulative[gas] += value


    ghg_emissions_cumulative = round(sum(ghg_emission_cumulative.values()), 2)
    dry_percent_cumulative = round(dry_percent_sum / percent_days_count, 2) if percent_days_count else None
    wet_percent_cumulative = round(wet_percent_sum / percent_days_count, 2) if percent_days_count else None
    mixed_percent_cumulative = round(mixed_percent_sum / percent_days_count, 2) if percent_days_count else None
    if composition_days_count:
        composition_cumulative = {k: round(v / composition_days_count, 2) for k, v in composition_sums.items()}
    else:
        composition_cumulative = None


    # --- Material Recovery Calculation for Recycling ---
    # Use material_composition_formal and material_composition_informal from each document
    recovery_materials = ["paper", "plastic", "aluminum", "metal", "glass"]
    material_recovery_cumulative = {m: 0.0 for m in recovery_materials}
    cursor3 = db[COLLECTION_NAME].find(query, {"_id": 0, "scenario.recycling": 1, "scenario.formally_collected": 1, "scenario.informally_collected": 1})
    async for doc in cursor3:
        scenario = doc.get("scenario", {})
        recycling = scenario.get("recycling", {})
        formally_collected = scenario.get("formally_collected", 0)
        informally_collected = scenario.get("informally_collected", 0)
        material_comp_formal = recycling.get("material_composition_formal", {})
        material_comp_informal = recycling.get("material_composition_informal", {})
        recyc_obj = recycling.get("recyclability", {})
        for material in recovery_materials:
            comp_formal = material_comp_formal.get(material, 0)
            comp_informal = material_comp_informal.get(material, 0)
            recyc = recyc_obj.get(material, 0)
            # Calculate recovered for this doc
            recovered = formally_collected * (comp_formal / 100) * (recyc / 100) + informally_collected * (comp_informal / 100) * (recyc / 100)
            material_recovery_cumulative[material] += recovered
    # Round results
    material_recovery_cumulative = {m: round(v, 2) for m, v in material_recovery_cumulative.items()}

    return {
        "city_name": city_name,
        "start_date": start_date,
        "end_date": end_date,
        "formally_collected_cumulative": formally_collected_cumulative,
        "informally_collected_cumulative": informally_collected_cumulative,
        "uncollected_cumulative": uncollected_cumulative,
        "waste_diverted_cumulative": waste_diverted_cumulative,
        "ghg_emissions_cumulative": ghg_emissions_cumulative,
        "dry_percent_cumulative": dry_percent_cumulative,
        "wet_percent_cumulative": wet_percent_cumulative,
        "mixed_percent_cumulative": mixed_percent_cumulative,
        "composition_cumulative": composition_cumulative,
        "material_recovery_cumulative": material_recovery_cumulative
    }
