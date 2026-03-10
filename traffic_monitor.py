import os
import requests
import time
from datetime import datetime
import pandas as pd

# --- 1. SECURE KEY RETRIEVAL (GitHub Actions) ---
API_KEY = os.environ.get('TOMTOM_API_KEY')
if not API_KEY:
    raise ValueError("❌ Error: TOMTOM_API_KEY environment variable not found.")

# --- 2. MULTI-CITY ROUTES CONFIGURATION ---
ALL_ROUTES = {
    "Herentals": {
        "Route 1": {"name1": "Kerkstraat", "name2": "Herenthoutseweg", "loc1": "51.1751809,4.8353323", "loc2": "51.170046,4.8317759"},
        "Route 2": {"name1": "Stadspoortstraat", "name2": "Herenthoutseweg", "loc1": "51.1734252,4.8406267", "loc2": "51.1700577,4.8317838"},
        "Route 3": {"name1": "Hofkwartier", "name2": "Lierseweg", "loc1": "51.1782545,4.8343776", "loc2": "51.1746185,4.819229"},
        "Route 4": {"name1": "Nederrij 1", "name2": "Nederrij 98", "loc1": "51.1820609,4.835208", "loc2": "51.1861229,4.8383586"},
        "Route 5": {"name1": "Gandhiplein", "name2": "Augustijnenlaan", "loc1": "51.1817908,4.8312325", "loc2": "51.1771497,4.8503665"},
        "Route 6": {"name1": "Zavelstraat", "name2": "Poederleeseweg", "loc1": "51.1747728,4.8509194", "loc2": "51.1903507,4.8320427"},
        "Route 7": {"name1": "Lierseweg", "name2": "Oud-Strijderslaan", "loc1": "51.1740307,4.8142362", "loc2": "51.1746541,4.8508607"},
        "Route 8": {"name1": "Grote Markt", "name2": "Stadspoortstraat", "loc1": "51.1760699,4.836609", "loc2": "51.1713524,4.8455946"}
    },
    "Heist-op-den-Berg": {
        "Route 1": {"name1": "Boudewijnlaan", "name2": "Parking Cultuurplein", "loc1": "51.0742144,4.7167971", "loc2": "51.0761264,4.7178662"},
        "Route 2": {"name1": "Averegtenlaan", "name2": "Randparking Vlinderstraat", "loc1": "51.0825038,4.7209886", "loc2": "51.0787202,4.7149789"},
        "Route 3": {"name1": "Molenstraat 152", "name2": "Molenstraat 2", "loc1": "51.0838907,4.728041", "loc2": "51.0779889,4.7165689"},
        "Route 4": {"name1": "Leopoldlei 90", "name2": "Parking Leopoldlei", "loc1": "51.083407,4.7289147", "loc2": "51.0770119,4.7265684"},
        "Route 5": {"name1": "Frans Coeckelbergsstraat", "name2": "Parking Leopoldlei", "loc1": "51.0728231,4.7241473", "loc2": "51.0770119,4.7265684"},
        "Route 6": {"name1": "Stationsstraat 95a", "name2": "Stationsstraat 11", "loc1": "51.0746158,4.7087403", "loc2": "51.0773098,4.7147545"},
        "Route 7": {"name1": "Boudewijnlaan 18", "name2": "Paul Van Roosbroecklaan", "loc1": "51.0739663,4.7146487", "loc2": "51.0724081,4.7244557"},
        "Route 8": {"name1": "Bergstraat 169", "name2": "Spoorwegstraat 14", "loc1": "51.0774554,4.7157428", "loc2": "51.0737621,4.712355"},
        "Route 9": {"name1": "Eugeen Woutersstraat 3", "name2": "Eugeen Woutersstraat 39", "loc1": "51.0795439,4.71961", "loc2": "51.0783914,4.7221169"}
    },
    "Brecht": {
        "Route 1": {"name1": "Parking Dorpsstraat", "name2": "Processieweg", "loc1": "51.3456052,4.6805009", "loc2": "51.3489378,4.675588"},
        "Route 2": {"name1": "Heiken", "name2": "Hoogstraatsebaan", "loc1": "51.3479694,4.669286", "loc2": "51.3505475,4.6755875"},
        "Route 3": {"name1": "Dorpsstraat", "name2": "Ringovenlaan", "loc1": "51.3496858,4.6752577", "loc2": "51.3448027,4.686275"}
    },
    "Mechelen": {
        "Out 1": {"name1": "Q-Park Lamot", "name2": "Kon. Astridlaan", "loc1": "51.0253552,4.4768889", "loc2": "51.0278628,4.4706128"},
        "Out 2": {"name1": "Indigo Hoogstraat", "name2": "Nwe Kapucijnenstraat", "loc1": "51.0235571,4.4743241", "loc2": "51.0225988,4.4729792"},
        "Out 3": {"name1": "Indigo Grote Markt", "name2": "Goswin de Stassartstraat", "loc1": "51.0281672,4.4791899", "loc2": "51.0343664,4.4787359"},
        "Out 4": {"name1": "Indigo Kathedraal", "name2": "Goswin de Stassartstraat", "loc1": "51.0291258,4.4782551", "loc2": "51.0343664,4.4787359"},
        "Out 5": {"name1": "Veemarkt", "name2": "Keizerstraat", "loc1": "51.0293255,4.4840652", "loc2": "51.0290066,4.4882402"},
        "Out 6": {"name1": "Parking Inno", "name2": "Bleekstraat", "loc1": "51.026162,4.4826729", "loc2": "51.0268092,4.4893477"},
        "In 1": {"name1": "Hoogstraat", "name2": "Ganzendries", "loc1": "51.0221317,4.4739587", "loc2": "51.0232432,4.4748595"},
        "In 2": {"name1": "Hoogstraat", "name2": "Q-Park Lamot", "loc1": "51.0221645,4.4739853", "loc2": "51.0253552,4.4768889"},
        "In 3": {"name1": "Sint-Katelijnestraat", "name2": "Indigo Grote Markt", "loc1": "51.0340633,4.4755292", "loc2": "51.0281672,4.4791899"},
        "In 4": {"name1": "Sint-Katelijnestraat", "name2": "Indigo Kathedraal", "loc1": "51.0340559,4.4755295", "loc2": "51.0291258,4.4782551"},
        "In 5": {"name1": "Keizerstraat", "name2": "Veemarkt", "loc1": "51.029008,4.4883295", "loc2": "51.0289292,4.485366"},
        "In 6": {"name1": "Zandpoortvest", "name2": "Parking Inno", "loc1": "51.0234471,4.4873008", "loc2": "51.026162,4.4826729"},
        "Ring CCW 1": {"name1": "Kon. Astridlaan", "name2": "R12 (Zuid)", "loc1": "51.0280133,4.4700838", "loc2": "51.0206859,4.4780253"},
        "Ring CCW 2": {"name1": "R12 (Zuid)", "name2": "Hendrik Speecqvest", "loc1": "51.020591,4.4790632", "loc2": "51.0214784,4.4861257"},
        "Ring CCW 3": {"name1": "Raghenoplein", "name2": "Frans Halsvest", "loc1": "51.0219261,4.4866119", "loc2": "51.0304135,4.4873214"},
        "Ring CCW 4": {"name1": "Goswin de Stassart", "name2": "Battelsesteenweg", "loc1": "51.0345145,4.478636", "loc2": "51.028313,4.4702088"},
        "Ring CCW 5": {"name1": "Hendrik Speecqvest", "name2": "Hoogstratenplein", "loc1": "51.0217205,4.4866604", "loc2": "51.0290022,4.4891542"},
        "Ring CCW 6": {"name1": "R12 (Noord)", "name2": "Kazerne Dossin", "loc1": "51.0310895,4.4868016", "loc2": "51.0344692,4.4792083"},
        "Ring CW 1": {"name1": "Zandpoortvest", "name2": "Stationsstraat", "loc1": "51.0285704,4.4898393", "loc2": "51.0217517,4.4869489"},
        "Ring CW 2": {"name1": "Voochtstraat", "name2": "Raghenoplein", "loc1": "51.028467,4.4893581", "loc2": "51.0223561,4.4867758"}
    }
}

# --- 3. FETCH AND APPEND DATA ---
def run_traffic_check():
    print("🚦 Checking traffic...")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results =[]

    for city, routes in ALL_ROUTES.items():
        is_bidirectional = (city != "Mechelen")
        
        for route_id, data in routes.items():
            directions = [
                {"label": f"{route_id}: {data['name1']} -> {data['name2']}", "start": data["loc1"], "end": data["loc2"]}
            ]
            if is_bidirectional:
                directions.append(
                    {"label": f"{route_id}: {data['name2']} -> {data['name1']}", "start": data["loc2"], "end": data["loc1"]}
                )
                
            temp_results =[]
            for direction in directions:
                route_label = direction["label"]
                start_coord = direction["start"]
                end_coord = direction["end"]
                
                gmaps_link = f"https://www.google.com/maps/dir/?api=1&origin={start_coord}&destination={end_coord}&travelmode=driving"
                url = f"https://api.tomtom.com/routing/1/calculateRoute/{start_coord}:{end_coord}/json"
                params = {"key": API_KEY, "traffic": "true", "routeType": "fastest"}
                
                try:
                    response = requests.get(url, params=params)
                    response.raise_for_status() 
                    summary = response.json()['routes'][0]['summary']
                    
                    travel_min = round(summary.get('travelTimeInSeconds', 0) / 60, 1)
                    delay_min = round(summary.get('trafficDelayInSeconds', 0) / 60, 1)
                    
                    temp_results.append({
                        "Timestamp": now,
                        "City": city,
                        "Route": route_label,
                        "Travel Time (min)": travel_min,
                        "Traffic Delay (min)": delay_min,
                        "Warning": "",
                        "Google Maps Link": gmaps_link
                    })
                    print(f"✅ Checked: {route_label}")
                except Exception as e:
                    print(f"❌ Failed {route_label}: {e}")
                    
                time.sleep(1) # Prevent API Rate Limit
                
            # Deviation check for bidirectional routes
            if is_bidirectional and len(temp_results) == 2:
                t1, t2 = temp_results[0]["Travel Time (min)"], temp_results[1]["Travel Time (min)"]
                if t1 > 0 and t2 > 0:
                    diff, ratio = abs(t1 - t2), max(t1, t2) / min(t1, t2)
                    if diff >= 3.0 and ratio >= 1.4:
                        warn = f"⚠️ Deviation (Diff: {round(diff, 1)} min)"
                        temp_results[0]["Warning"] = warn
                        temp_results[1]["Warning"] = warn

            results.extend(temp_results)

    # Append to CSV logic
    if results:
        df = pd.DataFrame(results)
        csv_filename = 'traffic_data.csv'
        
        # Check if file exists to determine if we need to write the header row
        file_exists = os.path.isfile(csv_filename)
        
        # mode='a' appends to the file instead of overwriting it!
        df.to_csv(csv_filename, mode='a', header=not file_exists, index=False)
        print(f"\n💾 Data successfully appended to '{csv_filename}'.")

if __name__ == "__main__":
    run_traffic_check()
