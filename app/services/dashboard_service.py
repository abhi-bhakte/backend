from datetime import datetime, timedelta
from collections import defaultdict
from typing import Any, Dict, List

from app.db.db import get_db
import pytz

COLLECTION_NAME = "waste_data"
IST = pytz.timezone("Asia/Kolkata")


def parse_date(date_str: str) -> datetime:
    for fmt in ("%d/%m/%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError


def to_float(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return 0.0
    return 0.0


def extract_emission_total(method_obj: Dict[str, Any]) -> float:
    if not isinstance(method_obj, dict):
        return 0.0
    for key in ("total_emissions_total", "total_emissions"):
        value = method_obj.get(key)
        total = to_float(value)
        if total:
            return round(total, 2)

    totals = []
    for gas in ("co2", "ch4", "n2o", "bc"):
        total_key = f"{gas}_total"
        if total_key in method_obj:
            totals.append(to_float(method_obj[total_key]))
    if totals:
        return round(sum(totals), 2)

    values = []
    for gas in ("co2", "ch4", "n2o", "bc"):
        if gas in method_obj:
            values.append(to_float(method_obj[gas]))
    return round(sum(values), 2) if values else 0.0


def normalize_method_name(method: str) -> str:
    return method.strip().lower().replace(" ", "_")

async def get_city_summary_service(city_name, start_date, end_date, db):
    # ...existing code...


    try:
        start_dt = parse_date(start_date)
        end_dt = parse_date(end_date)
    except Exception:
        raise ValueError("Invalid date format. Use dd/mm/yy or yyyy-mm-dd.")

    date_list: List[str] = []
    current_dt = start_dt
    while current_dt <= end_dt:
        date_list.append(current_dt.strftime("%Y-%m-%d"))
        current_dt += timedelta(days=1)

    # Case-insensitive city name matching using regex in query
    query = {
        "scenario.general.city_name": {"$regex": f"^{city_name}$", "$options": "i"},
        "scenario.general.date": {"$in": date_list}
    }

    matched_documents = []
    cursor = db[COLLECTION_NAME].find(query, {"_id": 0})
    async for doc in cursor:
        matched_documents.append(doc)

    stats_by_date: Dict[str, Dict[str, Any]] = {}
    formally_collected_cumulative = 0.0
    informally_collected_cumulative = 0.0
    uncollected_cumulative = 0.0
    generated_cumulative = 0.0
    dry_percent_sum = 0.0
    wet_percent_sum = 0.0
    mixed_percent_sum = 0.0
    percent_days_count = 0
    composition_sums: Dict[str, float] = defaultdict(float)
    composition_days_count = 0
    waste_allocation_totals: Dict[str, float] = defaultdict(float)
    emission_totals_by_method: Dict[str, float] = defaultdict(float)
    recovery_materials = ["paper", "plastic", "aluminum", "metal", "glass"]
    material_recovery_cumulative: Dict[str, float] = {m: 0.0 for m in recovery_materials}
    recycle_informal_total = 0.0

    for doc in matched_documents:
        scenario = doc.get("scenario", {})
        general = scenario.get("general", {})
        date_val = general.get("date")
        if not isinstance(date_val, str):
            continue

        formally_collected = to_float(general.get("formally_collected", 0))
        informally_collected = to_float(general.get("informally_collected", 0))
        uncollected = to_float(general.get("uncollected", 0))
        total_generated = to_float(general.get("total_waste_generation", formally_collected + informally_collected + uncollected))

        formally_collected_cumulative += formally_collected
        informally_collected_cumulative += informally_collected
        uncollected_cumulative += uncollected
        generated_cumulative += total_generated

        dry_percent = general.get("dry_waste_percentage")
        wet_percent = general.get("wet_waste_percentage")
        mixed_percent = general.get("mixed_waste_percentage")
        if all(isinstance(x, (int, float)) for x in [dry_percent, wet_percent, mixed_percent]):
            dry_percent_sum += float(dry_percent)
            wet_percent_sum += float(wet_percent)
            mixed_percent_sum += float(mixed_percent)
            percent_days_count += 1

        waste_composition = general.get("waste_composition", {})
        if isinstance(waste_composition, dict) and waste_composition:
            for k, v in waste_composition.items():
                composition_sums[k] += to_float(v)
            composition_days_count += 1

        waste_allocation = general.get("waste_allocation", {})
        if isinstance(waste_allocation, dict):
            for method_key, value in waste_allocation.items():
                waste_allocation_totals[method_key] += to_float(value)

        stats_entry = stats_by_date.setdefault(
            date_val,
            {
                "date": date_val,
                "collected": 0.0,
                "emissions": 0.0,
                "emissions_by_method": {}
            },
        )
        stats_entry["collected"] += round(formally_collected + informally_collected, 2)

        emissions_raw = doc.get("emissions", {})
        method_emissions: Dict[str, Any] = {}
        if isinstance(emissions_raw, dict):
            process_block = emissions_raw.get("process")
            if isinstance(process_block, dict):
                method_emissions = process_block
            else:
                method_emissions = emissions_raw
        if method_emissions:
            for method_name, method_obj in method_emissions.items():
                method_total = extract_emission_total(method_obj)
                if method_total:
                    stats_entry["emissions"] += method_total
                    stats_entry["emissions_by_method"][method_name] = (
                        stats_entry["emissions_by_method"].get(method_name, 0.0) + method_total
                    )
                    normalized = normalize_method_name(method_name)
                    emission_totals_by_method[normalized] += method_total

        recycling = scenario.get("recycling", {})
        if isinstance(recycling, dict):
            recycle_formal = to_float(recycling.get("recycle_collected_formal", 0))
            recycle_informal = to_float(recycling.get("recycle_collected_informal", 0))
            recycle_informal_total += recycle_informal
            material_comp_formal = recycling.get("material_composition_formal", {})
            material_comp_informal = recycling.get("material_composition_informal", {})
            recyclability = recycling.get("recyclability", {})
            for material in recovery_materials:
                comp_formal = to_float(material_comp_formal.get(material, 0))
                comp_informal = to_float(material_comp_informal.get(material, 0))
                recyc_pct = to_float(recyclability.get(material, 0))
                recovered = recycle_formal * (comp_formal / 100) * (recyc_pct / 100)
                recovered += recycle_informal * (comp_informal / 100) * (recyc_pct / 100)
                material_recovery_cumulative[material] += recovered

    for date_str in date_list:
        stats_by_date.setdefault(
            date_str,
            {
                "date": date_str,
                "collected": 0.0,
                "emissions": 0.0,
                "emissions_by_method": {}
            },
        )

    daily_stats = [
        {
            "date": date_str,
            "collected": round(stats_by_date[date_str]["collected"], 2),
            "emissions": round(stats_by_date[date_str]["emissions"], 2),
        }
        for date_str in date_list
    ]

    # Waste diverted excludes landfill (sum of all treatments except landfill)
    waste_diverted_cumulative = sum(
        v for k, v in waste_allocation_totals.items()
        if normalize_method_name(k) not in ("landfill", "landfilling")
    )

    dry_percent_cumulative = (
        round(dry_percent_sum / percent_days_count, 2) if percent_days_count else None
    )
    wet_percent_cumulative = (
        round(wet_percent_sum / percent_days_count, 2) if percent_days_count else None
    )
    mixed_percent_cumulative = (
        round(mixed_percent_sum / percent_days_count, 2) if percent_days_count else None
    )

    if composition_days_count:
        composition_cumulative = {
            k: round(v / composition_days_count, 2)
            for k, v in composition_sums.items()
        }
    else:
        composition_cumulative = None

    material_recovery_cumulative = {
        material: round(value, 2)
        for material, value in material_recovery_cumulative.items()
    }

    ghg_emissions_cumulative = round(sum(emission_totals_by_method.values()), 2)

    method_field_map = {
        "composting": "compostingGWP",
        "anaerobic_digestion": "anaerobicDigestionGWP",
        "recycling": "recyclingGWP",
        "incineration": "incinerationGWP",
        "landfilling": "landfillGWP",
        "landfill": "landfillGWP",
        "pyrolysis": "pyrolysisGWP",
    }

    method_totals_formatted: Dict[str, float] = {}
    for method_key, response_field in method_field_map.items():
        if response_field not in method_totals_formatted:
            method_totals_formatted[response_field] = 0.0
        method_totals_formatted[response_field] += round(emission_totals_by_method.get(method_key, 0.0), 2)

    waste_generated_total = (
        generated_cumulative
        if generated_cumulative
        else formally_collected_cumulative + informally_collected_cumulative + uncollected_cumulative
    )

    transfers = []
    if waste_generated_total:
        if formally_collected_cumulative:
            transfers.append({
                "source": "Waste Generated",
                "target": "Formally Collected",
                "value": round(formally_collected_cumulative, 2),
            })
        if informally_collected_cumulative:
            transfers.append({
                "source": "Waste Generated",
                "target": "Informally Collected",
                "value": round(informally_collected_cumulative, 2),
            })
        if uncollected_cumulative:
            transfers.append({
                "source": "Waste Generated",
                "target": "Uncollected",
                "value": round(uncollected_cumulative, 2),
            })

    method_label_map = {
        "composting": "Composting",
        "anaerobic_digestion": "Anaerobic Digestion",
        "incineration": "Incineration",
        "landfilling": "Landfilling",
        "pyrolysis": "Pyrolysis",
    }

    for method_key, label in method_label_map.items():
        allocation_value = waste_allocation_totals.get(method_key, 0.0)
        if allocation_value:
            transfers.append({
                "source": "Formally Collected",
                "target": label,
                "value": round(allocation_value, 2),
            })

    recycling_allocation = waste_allocation_totals.get("recycling", 0.0)
    if recycling_allocation:
        transfers.append({
            "source": "Formally Collected",
            "target": "Recycling",
            "value": round(recycling_allocation, 2),
        })

    if recycle_informal_total:
        transfers.append({
            "source": "Informally Collected",
            "target": "Recycling",
            "value": round(recycle_informal_total, 2),
        })

    response = {
        "city_name": city_name,
        "start_date": start_date,
        "end_date": end_date,
        "formally_collected_cumulative": round(formally_collected_cumulative, 2),
        "informally_collected_cumulative": round(informally_collected_cumulative, 2),
        "uncollected_cumulative": round(uncollected_cumulative, 2),
        "waste_diverted_cumulative": round(waste_diverted_cumulative, 2),
        "ghg_emissions_cumulative": ghg_emissions_cumulative,
        "dry_percent_cumulative": dry_percent_cumulative,
        "wet_percent_cumulative": wet_percent_cumulative,
        "mixed_percent_cumulative": mixed_percent_cumulative,
        "composition_cumulative": composition_cumulative,
        "material_recovery_cumulative": material_recovery_cumulative,
        "daily_stats": daily_stats,
        "transfers": transfers,
    }

    response.update(method_totals_formatted)

    return response
