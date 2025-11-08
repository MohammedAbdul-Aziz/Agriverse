# -*- coding: utf-8 -*-
"""
Created on Fri Nov  7 17:06:09 2025

@author: user
"""

import requests # Still needed for the weather API
import time     # Just for a little simulated "loading" effect

# --- 1. SIMULATED "AGRIVERSE" DATABASE ---
# This is data you'd normally pull from your real database.

# From your brief: "regional_yield_per_acre"
yield_factors = {
    "ADILABAD": {"RICE": 3.7, "PADDY": 3.0, "WHEAT": 2.5},
    "KHAMMAM":  {"RICE": 3.0, "PADDY": 5.0, "WHEAT": 2.0},
    "MEDAK":    {"RICE": 4.0, "PADDY": 1.0, "WHEAT": 5.0}
}

# From your brief: "InputQualityFactor (from marketplace purchases)"
# We'll score seeds: 'Premium'=1.1, 'Certified'=1.0, 'Local'=0.9
farmer_purchases_db = {
    "FARMER_101": {"seeds": "Premium", "fertilizer": "Standard"},
    "FARMER_102": {"seeds": "Local", "fertilizer": "Standard"},
    "FARMER_103": {"seeds": "Certified", "fertilizer": "Premium"},
}

# From your brief: "ManagementFactor (farmer history / training)"
# Let's score them based on a "rating"
farmer_history_db = {
    "FARMER_101": {"rating": 5, "training_completed": True},
    "FARMER_102": {"rating": 3, "training_completed": False},
    "FARMER_103": {"rating": 4, "training_completed": True},
}

# From your brief: "PestDiseaseFactor (from sentinel alerts)"
pest_alert_db = {
    "ADILABAD": {"alert_level": "Low", "report_date": "2025-11-01"},
    "KHAMMAM":  {"alert_level": "High", "report_date": "2025-11-03"},
    "MEDAK":    {"alert_level": "Medium", "report_date": "2025-11-02"},
}

# --- 2. FACTOR-CALCULATING FUNCTIONS ---

# *** THIS IS THE CORRECTED FUNCTION ***
def get_weather_factor(location, api_key):
    """
    Calls the OpenWeatherMap API.
    """
    print(f"-> Calling Weather API for {location}...")
    
    # This is the correct API endpoint for OpenWeatherMap
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    # These params are for OpenWeatherMap (using a city name 'q')
    params = {
        'q': f"{location},IN",  # We add ",IN" to help it find Indian cities
        'appid': api_key,
        'units': 'metric'       # Get temperature in Celsius
    }
    
    # This is the logic that was missing:
    try:
        response = requests.get(base_url, params=params, timeout=5)
        response.raise_for_status() # Raise error if request failed
        
        data = response.json()
        temp = data['main']['temp'] 
        
        print(f"--- API SUCCESS: Current temp in {location} is {temp}°C ---")
        
        # This is your "translator" logic
        if 25 <= temp <= 35:
            return 1.0  # Ideal weather
        elif temp > 35:
            return 0.7  # Too hot
        elif temp < 25:
            return 0.85 # A bit cool
        else:
            return 0.9  # Default
            
    except requests.exceptions.RequestException as e:
        print(f"--- API ERROR: Could not get weather. Error: {e} ---")
        print("--- Using default weather factor of 0.9 ---")
        return 0.9 # If the API fails, fall back to your old value
    except KeyError:
        # This happens if the API response is weird or 'main'/'temp' isn't there
        print(f"--- API ERROR: Unexpected data format from weather API. ---")
        print("--- Using default weather factor of 0.9 ---")
        return 0.9

def get_irrigation_factor():
    """
    Asks the user for irrigation type.
    From your brief: "1.0 if irrigated, <1 if rainfed"
    """
    print("-> Querying Irrigation Status...")
    while True:
        choice = input("   Is the land (I)rrigated or (R)ainfed? [I/R]: ").upper()
        if choice == 'I':
            return 1.0  # Fully irrigated
        elif choice == 'R':
            # You mentioned "partial irrigation" gave 0.95. Let's use that.
            return 0.95 # Rainfed / Partial
        else:
            print("   Invalid choice. Please enter 'I' or 'R'.")
    # Note: This return 1.0 is unreachable, but the function is safe.
    # The 'while True' loop can only be broken by a 'return'.

def get_ipqual_factor(farmer_id):
    """
    Looks up farmer's purchases in our "database".
    From your brief: "InputQualityFactor"
    """
    print(f"-> Checking Marketplace data for {farmer_id}...")
    time.sleep(0.5) # Simulate a database lookup
    
    if farmer_id in farmer_purchases_db:
        purchases = farmer_purchases_db[farmer_id]
        seed_type = purchases.get("seeds")
        
        if seed_type == "Premium":
            # Your example value was 1.05
            return 1.05
        elif seed_type == "Certified":
            return 1.0
        elif seed_type == "Local":
            return 0.9
    
    print(f"   No purchase data found for {farmer_id}. Using default 1.0")
    return 1.0 # Default if no data

def get_management_factor(farmer_id):
    """
    Looks up farmer's history in our "database".
    From your brief: "ManagementFactor"
    """
    print(f"-> Checking Farmer History for {farmer_id}...")
    time.sleep(0.5) # Simulate a database lookup
    
    if farmer_id in farmer_history_db:
        history = farmer_history_db[farmer_id]
        
        # Let's build a simple score
        if history["rating"] >= 4 and history["training_completed"]:
            # Your example value was 1.05
            return 1.05
        elif history["rating"] >= 3:
            return 1.0
        else:
            return 0.9 # Low-rated farmer
            
    print(f"   No history found for {farmer_id}. Using default 1.0")
    return 1.0 # Default if no data

def get_pestcon_factor(location):
    """
    Looks up local pest alerts in our "database".
    From your brief: "PestDiseaseFactor"
    """
    print(f"-> Checking Pest Alerts for {location}...")
    time.sleep(0.5) # Simulate a database lookup
    
    if location in pest_alert_db:
        alert_level = pest_alert_db.get(location, {}).get("alert_level")
        
        if alert_level == "High":
            return 0.7
        elif alert_level == "Medium":
            return 0.85
        elif alert_level == "Low":
            # Your example value was 0.98
            return 0.98
            
    print(f"   No pest alert data for {location}. Using default 1.0")
    return 1.0 # Default (no pests)

# --- 3. MAIN SCRIPT ---

def main():
    print("--- AgriVerse Yield Estimator ---")
    
    # --- Inputs ---
    # We need a Farmer ID to look up their data
    farmer_id = str(input("Please provide Farmer ID (e.g., FARMER_101): ")).upper()
    a = str(input("Please provide the Location (in CAPS): ")).upper()
    b = int(input("Please provide area of yield (in acres): "))
    c = str(input("Please provide the crop (in CAPS): ")).upper()

    # --- Step A: Baseline Estimate ---
    # We use .get() to safely find the factor.
    factor = yield_factors.get(a, {}).get(c)
    
    if not factor:
        print(f"\nError: We do not have yield data for {c} in {a}.")
        return # Exit the script

    BaselineYield = b * factor
    print(f"\n--- Baseline Estimate ---")
    print(f"   {b} acres * {factor} t/acre = {BaselineYield:.2f} t")
    print("\n--- Applying Adjustment Factors ---")

    # --- Step B: Apply Adjustment Factors ---
    
    # !! IMPORTANT: You must get a key from OPENWEATHERMAP.ORG
    # The key you had before was for a different service.
    YOUR_API_KEY = "a54e9312ddd57ba368ca6e466686a2eb" 
    
    if YOUR_API_KEY == "a54e9312ddd57ba368ca6e466686a2eb":
        print("--- WARNING: API Key is missing. Using default weather. ---")
        weather = 0.9 # Default if no key
    else:
        weather = get_weather_factor(a, YOUR_API_KEY)

    irrigation = get_irrigation_factor()
    ipqual = get_ipqual_factor(farmer_id)
    management = get_management_factor(farmer_id)
    pestcon = get_pestcon_factor(a)
    
    # --- Final Calculation ---
    AdjustedYield = BaselineYield * weather * irrigation * management * ipqual * pestcon
    
    print("\n--- Final Calculation ---")
    print(f"   Baseline:    {BaselineYield:.2f} t")
    print(f"   Weather:     x {weather}")
    print(f"   Irrigation:  x {irrigation}")
    print(f"   Input Qual:  x {ipqual}")
    print(f"   Management:  x {management}")
    print(f"   Pest/Disease:x {pestcon}")
    print("   -----------------------")
    print(f"   Adjusted Yield: {AdjustedYield:.2f} t")
    
    # --- Step D: Provide Confidence Band ---
    # Using your ±15% example
    
    # Correcting based on your math (z = Est - x, y = Est + x)
    x = AdjustedYield * 0.15
    z = AdjustedYield - x
    y = AdjustedYield + x
    
    print(f"\n   Estimated Yield Range (±15%): {z:.2f} t - {y:.2f} t")
    print("   Any reported sale outside this band will be flagged.")

# This makes the script runnable
if __name__ == "__main__":
    main()

