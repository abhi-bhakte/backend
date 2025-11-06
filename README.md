# Backend

## Transportation emissions units

The transportation calculate endpoint infers units by fuel type (no units arrays required):

Defaults applied per fuel type:
- CNG → kg
- EV → kWh
- All other fuels → liters

Example request (no units fields needed):

```
{
	"waste_formal": 100,
	"fuel_types_transport": ["diesel", "cng", "ev"],
	"fuel_consumed_transport": [1200, 500, 800],
	"vehicle_type": "Modern trucks",
	"waste_transfer_station": false,
	"waste_handled_at_station": 100,
	"fuel_types_station": [],
	"fuel_consumed_station": [],
	"electric_consumed": 0
}
```

Internally:
- Liquid/gaseous fuels use per-fuel density (kg/L) from `app/data/transportation.json` to convert between liters and kilograms as needed.
- EV uses the grid emission factor (`electricity_grid_factor.CO2 kg-eq/kWh`) and only contributes to CO2 (CH4/N2O/BC are treated as 0 in this stage).
- Vehicle-specific black carbon factors (kg/kg fuel) operate on mass directly.

