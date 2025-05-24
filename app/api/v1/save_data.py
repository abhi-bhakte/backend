from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import os
import json
import logging
from app.services.transportation import TransportationEmissions
from app.services.composting import CompostingEmissions
router = APIRouter()

# Ensure the data directory exists
DATA_DIR = os.path.join(os.path.dirname(__file__), "..","..", "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/save-data")
async def save_data(request: Request):
    """
    Save user data to user_data.json and calculate results to store in results.json.
    """
    try:
        # Parse the JSON data from the request
        data = await request.json()
        logger.info(f"Parsed JSON data: {data}")

        # Define the path to the user_data.json file
        user_data_path = os.path.join(DATA_DIR, "user_data.json")

        # Save the user data to user_data.json
        with open(user_data_path, "w") as json_file:
            json.dump(data, json_file, indent=4)
        logger.info(f"User data saved to {user_data_path}")

        # Perform the calculation using the TransportationEmissions class only if 'transportation' key exists
        if 'transportation' in data:
            emissions_service = TransportationEmissions(
                waste_formal=float(data["collectedByFormal"]),
                fuel_types_transport= data['transportation']['transportationFuelTypes'].split(','),
                fuel_consumed_transport=[float(value) for value in json.loads(data['transportation'].get('transportationFuelAmounts', '{}')).values()],
                vehicle_type=data['transportation']["truckType"],
                waste_transfer_station=True,
                fuel_types_station=data['transportation']['transferStationFuelTypes'].split(','), 
                fuel_consumed_station=[float(value) for value in json.loads(data['transportation'].get('transferStationFuelAmounts', '{}')).values()],
                electric_consumed=float(data['transportation']["transferStationElectricity"]),
                waste_handled_at_station=float(data['transportation']["transferStationWaste"]),
            )
            logger.info("Emissions service initialized successfully")
            transportation_results = emissions_service.overall_emissions()

            # Define the path to the results.json file
            results_path = os.path.join(DATA_DIR, "results.json")

            # Create a new results file with transportation data
            results = {"transportation": transportation_results}

            # Save the results to results.json
            with open(results_path, "w") as json_file:
                json.dump(results, json_file, indent=4)
            logger.info(f"Transportation results saved to {results_path}")

        # Perform the calculation using the CompostingEmissions class only if 'composting' key exists
        if 'composting' in data:
            emissions_service = CompostingEmissions(
                waste_composted=float(data['separatedWaste']['composting']),
                percent_compost_use_agri_garden=float(data['composting']['compostUsagePercentage']),
                compost_prod_potential=float(data['composting']['compostPotential']),
                electricity_consumed=float(data['composting']['electricityAmount']),
                fuel_types_operation=data['composting']['fuelTypes'].split(','),
                fuel_consumed_operation=[float(value) for value in json.loads(data['composting'].get('fuelAmounts', '{}')).values()]
            )
            logger.info("Composting emissions service initialized successfully")
            composting_results = emissions_service.overall_emissions()

            # Define the path to the results.json file
            results_path = os.path.join(DATA_DIR, "results.json")

            # Ensure the results directory exists
            os.makedirs(os.path.dirname(results_path), exist_ok=True)

            # Load existing results if the file exists
            if os.path.exists(results_path):
                with open(results_path, "r") as json_file:
                    results = json.load(json_file)
            else:
                results = {}

            # Update the results with composting data
            results["composting"] = composting_results

            # Save the updated results to results.json
            with open(results_path, "w") as json_file:
                json.dump(results, json_file, indent=4)
            logger.info(f"Composting results saved to {results_path}")

        # Return a success message with the calculated results
        return {"message": "Data saved and results calculated successfully"}

    except Exception as e:
        logger.error(f"Error saving data or calculating results: {e}")
        return {"message": "Failed to save data or calculate results", "error": str(e)}

@router.get("/get-user-data")
async def get_user_data():
    """
    Retrieve the user data from user_data.json.
    """
    try:
        # Define the path to the user_data.json file
        user_data_path = os.path.join(DATA_DIR, "user_data.json")

        # Check if the file exists
        if not os.path.exists(user_data_path):
            return JSONResponse(content={"message": "User data file not found"}, status_code=404)

        # Read the user data from the file
        with open(user_data_path, "r") as json_file:
            data = json.load(json_file)

        return data
    except Exception as e:
        logger.error(f"Error fetching user data: {e}")
        return {"message": "Failed to fetch user data", "error": str(e)}

@router.get("/get-results")
async def get_results():
    """
    Retrieve the calculated results from results.json.
    """
    try:
        # Define the path to the results.json file
        results_path = os.path.join(DATA_DIR, "results.json")

        # Check if the file exists
        if not os.path.exists(results_path):
            return JSONResponse(content={"message": "Results file not found"}, status_code=404)

        # Read the results from the file
        with open(results_path, "r") as json_file:
            results = json.load(json_file)

        return results
    except Exception as e:
        logger.error(f"Error fetching results: {e}")
        return {"message": "Failed to fetch results", "error": str(e)}