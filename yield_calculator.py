import requests
import time

# --- 1. SIMULATED "AGRIVERSE" DATABASE ---
# (All your dictionaries like yield_factors, farmer_purchases_db, etc. go here)
# ... (I'm omitting them for brevity, but YOU must copy them here) ...
yield_factors = {
    "ADILABAD": {"RICE": 3.7, "PADDY": 3.0, "WHEAT": 2.5},
    "KHAMMAM":  {"RICE": 3.0, "PADDY": 5.0, "WHEAT": 2.0},
    "MEDAK":    {"RICE": 4.0, "PADDY": 1.0, "WHEAT": 5.0}
}
farmer_purchases_db = {
    "FARMER_101": {"seeds": "Premium", "fertilizer": "Standard"},
    "FARMER_102": {"seeds": "Local", "fertilizer": "Standard"},
    "FARMER_103": {"seeds": "Certified", "fertilizer": "Premium"},
}
farmer_history_db = {
    "FARMER_101": {"rating": 5, "training_completed": True},
    "FARMER_102": {"rating": 3, "training_completed": False},
    "FARMER_103": {"rating": 4, "training_completed": True},
}
pest_alert_db = {
    "ADILABAD": {"alert_level": "Low", "report_date": "2025-11-01"},
    "KHAMMAM":  {"alert_level": "High", "report_date": "2025-11-03"},
    "MEDAK":    {"alert_level": "Medium", "report_date": "2025-11-02"},
}
# (Copy ALL your helper functions: get_weather_factor, get_ipqual_factor, etc.)

# --- 2. FACTOR-CALCULATING FUNCTIONS ---

def get_weather_factor(location, api_key):
    # ... (Your full weather function code) ...
    print(f"-> Calling Weather API for {location}...")
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {'q': f"{location},IN", 'appid': api_key, 'units': 'metric'}
    try:
        response = requests.get(base_url, params=params, timeout=5)
        response.raise_for_status() 
        data = response.json()
        temp = data['main']['temp'] 
        print(f"--- API SUCCESS: Current temp in {location} is {temp}°C ---")
        if 25 <= temp <= 35: return 1.0
        elif temp > 35: return 0.7
        elif temp < 25: return 0.85
        else: return 0.9
    except requests.exceptions.RequestException as e:
        print(f"--- API ERROR: {e} ---")
        return 0.9
    except KeyError:
        print(f"--- API ERROR: Unexpected data ---")
        return 0.9

# --- MODIFIED: This function now takes a parameter ---
def get_irrigation_factor(irrigation_type):
    print("-> Querying Irrigation Status...")
    if irrigation_type.upper() == 'I':
        return 1.0  # Fully irrigated
    elif irrigation_type.upper() == 'R':
        return 0.95 # Rainfed / Partial
    else:
        return 1.0 # Default if unknown

def get_ipqual_factor(farmer_id):
    # ... (Your full ipqual function) ...
    print(f"-> Checking Marketplace data for {farmer_id}...")
    if farmer_id in farmer_purchases_db:
        seed_type = farmer_purchases_db[farmer_id].get("seeds")
        if seed_type == "Premium": return 1.05
        elif seed_type == "Certified": return 1.0
        elif seed_type == "Local": return 0.9
    return 1.0

def get_management_factor(farmer_id):
    # ... (Your full management function) ...
    print(f"-> Checking Farmer History for {farmer_id}...")
    if farmer_id in farmer_history_db:
        history = farmer_history_db[farmer_id]
        if history["rating"] >= 4 and history["training_completed"]: return 1.05
        elif history["rating"] >= 3: return 1.0
        else: return 0.9
    return 1.0

def get_pestcon_factor(location):
    # ... (Your full pestcon function) ...
    print(f"-> Checking Pest Alerts for {location}...")
    if location in pest_alert_db:
        alert_level = pest_alert_db.get(location, {}).get("alert_level")
        if alert_level == "High": return 0.7
        elif alert_level == "Medium": return 0.85
        elif alert_level == "Low": return 0.98
    return 1.0

# --- 3. THE MAIN LOGIC FUNCTION ---
# This REPLACES your main() function
# It takes data *in* and returns a dictionary *out*

def calculate_yield(data):
    try:
        # 1. Get data from the frontend
        farmer_id = data['farmer_id'].upper()
        location = data['location'].upper()
        area = float(data['area'])
        crop = data['crop'].upper()
        irrigation_type = data['irrigation_type'] # e.g., "I" or "R"

        # !! Use your real API key here
        YOUR_API_KEY = "a54e9312ddd57ba368ca6e466686a2eb"

        # 2. Step A: Baseline Estimate
        factor = yield_factors.get(location, {}).get(crop)
        if not factor:
            return {"error": f"No yield data for {crop} in {location}."}
        
        BaselineYield = area * factor

        # 3. Step B: Apply Adjustment Factors
        weather = get_weather_factor(location, YOUR_API_KEY)
        irrigation = get_irrigation_factor(irrigation_type)
        ipqual = get_ipqual_factor(farmer_id)
        management = get_management_factor(farmer_id)
        pestcon = get_pestcon_factor(location)
        
        # 4. Final Calculation
        AdjustedYield = BaselineYield * weather * irrigation * management * ipqual * pestcon
        
        x = AdjustedYield * 0.15
        z = AdjustedYield - x
        y = AdjustedYield + x
        
        # 5. Return a dictionary (which becomes JSON)
        return {
            "success": True,
            "baseline_yield": f"{BaselineYield:.2f}",
            "adjusted_yield": f"{AdjustedYield:.2f}",
            "yield_range_min": f"{z:.2f}",
            "yield_range_max": f"{y:.2f}",
            "factors": {
                "weather": weather,
                "irrigation": irrigation,
                "ipqual": ipqual,
                "management": management,
                "pestcon": pestcon
            }
        }

    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}