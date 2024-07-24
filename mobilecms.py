import requests
from weds import webflow_bearer_token
from datetime import datetime
import locale

# Set locale for Norwegian date format
locale.setlocale(locale.LC_TIME, 'nb_NO.UTF-8')

def get_collection_items(collection_id, offset=0, limit=100):
    url = f"https://api.webflow.com/v2/collections/{collection_id}/items"
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {webflow_bearer_token}"
    }
    params = {
        "offset": offset,
        "limit": limit
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

def analyze_mobilabonnement():
    collection_id = "6660c15ec77f5270c0a534d2"
    target_values = [1, 5, 10, 20, 30, 100]
    prices = {value: [] for value in target_values}
    
    offset = 0
    while True:
        data = get_collection_items(collection_id, offset)
        items = data.get("items", [])
        
        if not items:
            break
        
        for item in items:
            field_data = item.get("fieldData", {})
            mobildata = field_data.get("mobildata")
            pris = field_data.get("pris")
            
            if mobildata is not None and pris is not None:
                try:
                    mobildata = int(mobildata)
                    pris = float(pris)
                    
                    if mobildata in target_values:
                        prices[mobildata].append(pris)
                except ValueError:
                    continue
        
        offset += 100
    
    return prices

def calculate_average(prices):
    return round(sum(prices) / len(prices)) if prices else 0

# Analyze Mobilabonnement
mobilabonnement_prices = analyze_mobilabonnement()

# Calculate averages
avg_prices = {value: calculate_average(prices) for value, prices in mobilabonnement_prices.items()}

# Print results
print("\n=== MOBILABONNEMENT ===")
for value, avg_price in avg_prices.items():
    print(f"Average price for {value} GB: {avg_price}")

# Prepare data for Webflow update
update_data = {
    "fieldData": {
        "name": "mobilabonnement stats",
        "slug": "mobilabonnement-stats",
        "mobil-avg-1": str(avg_prices.get(1, "")),
        "mobil-avg-100": str(avg_prices.get(100, "")),
        "mobil-avg-20": str(avg_prices.get(20, "")),
        "mobilg-avg-10": str(avg_prices.get(10, "")),
        "mobilg-avg-5": str(avg_prices.get(5, "")),
        "mobilt-avg-30": str(avg_prices.get(30, "")),
        "sist-oppdatert": datetime.now().strftime("%d. %B %Y")
    }
}

# Update Webflow item
url = "https://api.webflow.com/v2/collections/669feab7aab58234f40c295d/items/669fec0819ae2e1ae90f7b25/live"
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": f"Bearer {webflow_bearer_token}"
}
response = requests.patch(url, headers=headers, json=update_data)

# Print response code and content
print(f"\nWebflow API Response Code: {response.status_code}")
print(f"Webflow API Response Content: {response.text}")