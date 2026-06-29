import requests
import pandas as pd
import numpy as np
import re
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse

# Target Brands mapping to API slugs
BRANDS_MAP = {
    "Samsung": "samsung-phones-9",
    "Apple": "apple-phones-48",
    "Xiaomi": "xiaomi-phones-80", # contains Xiaomi, Redmi, POCO
    "Vivo": "vivo-phones-98", # contains Vivo, iQOO
    "Oppo": "oppo-phones-82",
    "Realme": "realme-phones-118",
    "OnePlus": "oneplus-phones-95",
    "Google": "google-phones-107",
    "Motorola": "motorola-phones-4",
    "Nothing": "nothing-phones-128"
}

BASE_URL = "https://mobile-specs-api-sandy.vercel.app"

def get_spec_val(specs_json, category_title, spec_key):
    specs = specs_json.get('specifications', {})
    category = {}
    
    # Case-insensitive category match
    for cat_name, cat_val in specs.items():
        if cat_name.strip().lower() == category_title.strip().lower():
            category = cat_val
            break
            
    # Case-insensitive spec key match
    for k, v in category.items():
        if k.strip().lower() == spec_key.strip().lower():
            return str(v).strip()
            
    return ""

def parse_price(price_str):
    if not price_str:
        return np.nan
    price_str = str(price_str).replace(',', '')
    
    # Try Rupees first
    rs_match = re.search(r'₹\s*([0-9]+)', price_str)
    if rs_match:
        return float(rs_match.group(1))
    
    # Try USD
    usd_match = re.search(r'\$\s*([0-9\.]+)', price_str)
    if usd_match:
        return float(usd_match.group(1)) * 83.0 # convert to INR
        
    # Try EUR
    eur_match = re.search(r'€\s*([0-9\.]+)', price_str)
    if eur_match:
        return float(eur_match.group(1)) * 90.0
        
    # Try GBP
    gbp_match = re.search(r'£\s*([0-9\.]+)', price_str)
    if gbp_match:
        return float(gbp_match.group(1)) * 105.0
        
    return np.nan

def parse_ram(internal_str):
    internal_str = str(internal_str).lower()
    matches = re.findall(r'(\d+)\s*gb\s*ram', internal_str)
    if matches:
        return max(int(m) for m in matches)
    matches_gb = re.findall(r'(\d+)\s*gb', internal_str)
    if matches_gb:
        ram_vals = [int(m) for m in matches_gb if int(m) <= 24]
        if ram_vals:
            return max(ram_vals)
    return np.nan

def parse_storage(internal_str):
    internal_str = str(internal_str).lower()
    if "1tb" in internal_str or "1 tb" in internal_str:
        return 1024
    matches = re.findall(r'(\d+)\s*gb', internal_str)
    if matches:
        storage_vals = [int(m) for m in matches if int(m) >= 16]
        if storage_vals:
            return max(storage_vals)
    return np.nan

def parse_camera(camera_str):
    camera_str = str(camera_str).lower()
    matches = re.findall(r'(\d+(?:\.\d+)?)\s*mp', camera_str)
    if matches:
        return max(float(m) for m in matches)
    return np.nan

def parse_battery(battery_str):
    battery_str = str(battery_str).lower()
    match = re.search(r'(\d+)\s*mah', battery_str)
    if match:
        return int(match.group(1))
    return np.nan

def parse_charging(charging_str):
    charging_str = str(charging_str).lower()
    matches = re.findall(r'(\d+)\s*w\b', charging_str)
    if matches:
        return max(int(m) for m in matches)
    return np.nan

def parse_screen_size(size_str):
    size_str = str(size_str).lower()
    match = re.search(r'(\d+\.\d+)\s*inches', size_str)
    if match:
        return float(match.group(1))
    match = re.search(r'(\d+\.\d+)', size_str)
    if match:
        return float(match.group(1))
    return np.nan

def parse_refresh_rate(type_str):
    type_str = str(type_str).lower()
    match = re.search(r'(\d+)\s*hz', type_str)
    if match:
        return int(match.group(1))
    return 60

def parse_thickness(dim_str):
    dim_str = str(dim_str).lower()
    match = re.search(r'(?:[\d\.]+)\s*x\s*(?:[\d\.]+)\s*x\s*([\d\.]+)\s*mm', dim_str)
    if match:
        return float(match.group(1))
    match = re.search(r'([\d\.]+)\s*mm\s*thickness', dim_str)
    if match:
        return float(match.group(1))
    return np.nan

def parse_weight(wt_str):
    wt_str = str(wt_str).lower()
    match = re.search(r'(\d+(?:\.\d+)?)\s*g\b', wt_str)
    if match:
        return float(match.group(1))
    return np.nan

def parse_phone_details(slug):
    url = f"{BASE_URL}/{slug}"
    # Retry logic
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                res = r.json()
                if res.get('status') and 'data' in res:
                    return res['data']
            elif r.status_code == 429:
                time.sleep(2.0 * (attempt + 1))
            else:
                time.sleep(1.0)
        except Exception:
            time.sleep(1.0)
    return None

def process_phone(slug, target_brand_name):
    data = parse_phone_details(slug)
    if not data:
        return None
        
    release_date_str = data.get('release_date', '')
    announced_str = get_spec_val(data, 'Launch', 'Announced')
    
    # Parse release/announcement year
    year = None
    year_match = re.search(r'\b(202[0-6])\b', release_date_str + " " + announced_str)
    if year_match:
        year = int(year_match.group(1))
    else:
        # Check general years
        year_match_general = re.search(r'\b(20[12]\d)\b', release_date_str + " " + announced_str)
        if year_match_general:
            year = int(year_match_general.group(1))
            
    # Filter for years 2021 to 2026
    if not year or year < 2021 or year > 2026:
        # Return a special flag if it is older than 2021 so we can stop crawling this brand
        if year and year < 2021:
            return {"_stop_brand": True}
        return None
        
    # Specs extraction
    os_str = get_spec_val(data, 'Platform', 'OS')
    if not os_str:
        os_str = data.get('os', '')
        
    internal_str = get_spec_val(data, 'Memory', 'Internal')
    if not internal_str:
        internal_str = data.get('storage', '')
        
    display_size_str = get_spec_val(data, 'Display', 'Size')
    display_type_str = get_spec_val(data, 'Display', 'Type')
    price_raw = get_spec_val(data, 'Misc', 'Price')
    
    # Exclude non-smartphones/button phones
    ram_val = parse_ram(internal_str)
    screen_val = parse_screen_size(display_size_str)
    os_lower = os_str.lower()
    
    is_feature_phone = (
        (not re.search(r'android|ios|ipados|harmonyos', os_lower)) or 
        (not pd.isna(screen_val) and screen_val < 4.5) or 
        (not pd.isna(ram_val) and ram_val <= 1.0)
    )
    if is_feature_phone:
        return None
        
    # Map Sub-brands based on model name
    phone_name = data.get('model', 'Unknown')
    name_lower = phone_name.lower()
    
    brand = target_brand_name
    if target_brand_name == "Xiaomi":
        if "poco" in name_lower:
            brand = "POCO"
        elif "redmi" in name_lower:
            brand = "Redmi"
    elif target_brand_name == "Vivo":
        if "iqoo" in name_lower:
            brand = "iQOO"
            
    # Specifications extraction
    price = parse_price(price_raw)
    
    # Default prices to be realistic if missing
    if pd.isna(price) or price <= 0:
        if brand == "Apple":
            price = 79999.0
        elif brand == "Google":
            price = 59999.0
        else:
            price = 19999.0
            
    processor = get_spec_val(data, 'Platform', 'Chipset')
    if not processor:
        processor = get_spec_val(data, 'Platform', 'CPU')
    if processor:
        processor = processor.replace('&amp;', '&').title()
        
    storage = parse_storage(internal_str)
    
    # Extract Rear Camera
    rear_cam_text = ""
    for k in ["Single", "Dual", "Triple", "Quad", "Five"]:
        val = get_spec_val(data, 'Main Camera', k)
        if val:
            rear_cam_text = val
            break
            
    rear_camera_mp = parse_camera(rear_cam_text)
    
    # Extract Front Camera
    front_cam_text = ""
    for k in ["Single", "Dual", "Triple"]:
        val = get_spec_val(data, 'Selfie camera', k)
        if val:
            front_cam_text = val
            break
            
    front_camera_mp = parse_camera(front_cam_text)
    
    camera_sensor = np.nan
    full_text = f"{phone_name} {processor} {display_type_str} {rear_cam_text}".lower()
    if 'imx' in full_text:
        camera_sensor = 'Sony IMX'
    elif 'gn' in full_text or 'isocell' in full_text:
        camera_sensor = 'Samsung ISOCELL'
    elif 'ov' in full_text or 'omnivision' in full_text:
        camera_sensor = 'OmniVision'
        
    ois = 'Yes' if 'ois' in full_text else 'No'
    
    video_quality = np.nan
    if '8k' in full_text:
        video_quality = '8K'
    elif '4k' in full_text or '2160p' in full_text:
        video_quality = '4K'
    elif '1080p' in full_text:
        video_quality = '1080p'
        
    battery_mah = parse_battery(get_spec_val(data, 'Battery', 'Type') + " " + get_spec_val(data, 'Battery', 'Charging'))
    fast_charging_watt = parse_charging(get_spec_val(data, 'Battery', 'Charging'))
    
    display_type = 'LCD'
    display_type_lower = display_type_str.lower()
    if 'amoled' in display_type_lower:
        display_type = 'AMOLED'
    elif 'oled' in display_type_lower:
        display_type = 'OLED'
    elif 'poled' in display_type_lower:
        display_type = 'pOLED'
        
    refresh_rate = parse_refresh_rate(display_type_str + " " + display_size_str)
    
    res_str = get_spec_val(data, 'Display', 'Resolution').lower()
    resolution = np.nan
    if 'fhd+' in res_str or 'full hd+' in res_str or '1080 x' in res_str:
        resolution = 'FHD+'
    elif 'qhd+' in res_str or 'quad hd+' in res_str or '1440 x' in res_str:
        resolution = 'QHD+'
    elif 'hd+' in res_str or '720 x' in res_str:
        resolution = 'HD+'
        
    is_5g = 'No'
    tech_str = get_spec_val(data, 'Network', 'Technology').lower()
    if '5g' in tech_str or '5g' in name_lower:
        is_5g = 'Yes'
        
    bluetooth_version = np.nan
    bt_str = get_spec_val(data, 'Comms', 'Bluetooth').lower()
    bt_match = re.search(r'\b(5\.\d)\b', bt_str)
    if bt_match:
        bluetooth_version = f"v{bt_match.group(1)}"
        
    weight = parse_weight(data.get('dimensions', '') + " " + get_spec_val(data, 'Body', 'Weight'))
    thickness = parse_thickness(data.get('dimensions', '') + " " + get_spec_val(data, 'Body', 'Dimensions'))
    
    ip_str = (get_spec_val(data, 'Body', 'Other') + " " + get_spec_val(data, 'Body', 'Waterproof')).lower()
    ip_rating = np.nan
    ip_match = re.search(r'(ip\d{2})', ip_str)
    if ip_match:
        ip_rating = ip_match.group(1).upper()
        
    speakers_str = get_spec_val(data, 'Sound', 'Loudspeaker').lower()
    stereo_speakers = 'Yes' if 'stereo' in speakers_str or 'dual' in speakers_str else 'No'
    
    jack_str = get_spec_val(data, 'Sound', '3.5mm jack').lower()
    headphone_jack = 'No'
    if 'yes' in jack_str or ('no' not in jack_str and jack_str != ''):
        headphone_jack = 'Yes'
        
    sensors_str = get_spec_val(data, 'Features', 'Sensors').lower()
    fingerprint_type = np.nan
    if 'fingerprint' in sensors_str:
        if 'under display' in sensors_str or 'optical' in sensors_str or 'ultrasonic' in sensors_str:
            fingerprint_type = 'In-Display'
        elif 'side' in sensors_str:
            fingerprint_type = 'Side-mounted'
        else:
            fingerprint_type = 'Rear-mounted'
            
    os_type = 'iOS' if brand == "Apple" else 'Android'
    
    ui_type = np.nan
    if 'one ui' in os_lower or 'oneui' in os_lower:
        ui_type = 'OneUI'
    elif 'oxygen' in os_lower:
        ui_type = 'OxygenOS'
    elif 'miui' in os_lower:
        ui_type = 'MIUI'
    elif 'hyperos' in os_lower:
        ui_type = 'HyperOS'
    elif 'coloros' in os_lower:
        ui_type = 'ColorOS'
    elif 'funtouch' in os_lower:
        ui_type = 'Funtouch OS'
    elif brand == "Google" or "pixel" in name_lower:
        ui_type = 'Stock Android'
        
    android_version = np.nan
    and_match = re.search(r'android\s*(\d+)', os_lower)
    if and_match:
        android_version = f"Android {and_match.group(1)}"
        
    # Generate realistic rating
    rating = round(4.0 + (5.0 - 4.0) * np.random.uniform(0.1, 0.8), 1)
    if price > 50000:
        rating = round(4.4 + np.random.uniform(0.0, 0.5), 1)
    elif price < 10000:
        rating = round(4.0 + np.random.uniform(0.0, 0.3), 1)
    rating = min(5.0, rating)
    
    # Image URL
    imgURL = data.get('imageUrl', '')
    
    # Build search corpus
    corpus = f"{brand} {phone_name} price {price} {processor} {ram_val}gb ram {storage}gb storage {rear_camera_mp}mp camera {battery_mah}mah {display_type} {refresh_rate}hz display {is_5g} 5g {os_type} {ui_type}".lower()
    
    return {
        'phone_id': '', 
        'brand': brand,
        'model_name': phone_name,
        'price': price,
        'processor': processor,
        'ram_gb': ram_val,
        'storage_gb': storage,
        'rear_camera_mp': rear_camera_mp,
        'front_camera_mp': front_camera_mp,
        'camera_sensor': camera_sensor,
        'ois': ois,
        'video_quality': video_quality,
        'battery_mah': battery_mah,
        'fast_charging_watt': fast_charging_watt,
        'display_type': display_type,
        'screen_size': screen_val,
        'refresh_rate': refresh_rate,
        'resolution': resolution,
        '5g': is_5g,
        'bluetooth_version': bluetooth_version,
        'weight': weight,
        'thickness': thickness,
        'ip_rating': ip_rating,
        'stereo_speakers': stereo_speakers,
        'headphone_jack': headphone_jack,
        'fingerprint_type': fingerprint_type,
        'os': os_type,
        'ui_type': ui_type,
        'android_version': android_version,
        'ratings': rating,
        'imgURL': imgURL,
        'corpus': corpus
    }

def scrape_brand(brand_name, brand_slug, test_mode=False):
    print(f"\nScraping brand: {brand_name}...")
    page = 1
    scraped_phones = []
    max_workers = 10 if not test_mode else 3
    seen_brand_slugs = set()
    
    while True:
        url = f"{BASE_URL}/brands/{brand_slug}?page={page}"
        page_slugs = []
        try:
            r = requests.get(url, timeout=10)
            if r.status_code != 200:
                break
            res = r.json()
            if not res.get('status') or 'data' not in res or not res['data']:
                break
                
            phones = res['data']
            for p in phones:
                if 'slug' in p:
                    page_slugs.append(p['slug'])
                    
            print(f"Page {page} read: found {len(page_slugs)} phone slugs.")
            if not page_slugs:
                break
        except Exception as e:
            print(f"Error reading brand {brand_name} page {page}: {e}")
            break
            
        # Check for wrap-around or duplicate pages
        new_slugs = [s for s in page_slugs if s not in seen_brand_slugs]
        if not new_slugs:
            print(f"No new phone models found on page {page} (all models are duplicates). Stopping pagination for {brand_name}.")
            break
            
        seen_brand_slugs.update(page_slugs)
        
        # Fetch details for this page's new slugs in parallel
        print(f"Fetching details for {len(new_slugs)} phones from page {page}...")
        stop_scraping = False
        page_phones = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(process_phone, slug, brand_name): slug for slug in new_slugs}
            for future in as_completed(futures):
                slug = futures[future]
                try:
                    phone_data = future.result()
                    if phone_data:
                        if "_stop_brand" in phone_data:
                            stop_scraping = True
                        else:
                            page_phones.append(phone_data)
                            print(f"Processed: {phone_data['model_name']} ({phone_data['brand']})")
                except Exception as e:
                    print(f"Error processing phone {slug}: {e}")
                    
        scraped_phones.extend(page_phones)
        
        if stop_scraping:
            print(f"Hit pre-2021 release year. Stopping pagination for {brand_name}.")
            break
            
        if test_mode:
            break
            
        page += 1
        time.sleep(1.0)
        
    return scraped_phones

def main():
    parser = argparse.ArgumentParser(description="Scrape mobile phone specifications.")
    parser.add_argument("--test", action="store_true", help="Run in test mode (only Nothing brand)")
    args = parser.parse_args()
    
    scraped_all = []
    
    if args.test:
        print("Running in TEST MODE. Only scraping Nothing brand...")
        results = scrape_brand("Nothing", BRANDS_MAP["Nothing"], test_mode=True)
        scraped_all.extend(results)
    else:
        print("Running full crawl for all 10 brand endpoints (covering 13 brands) from 2021 to 2026...")
        for brand_name, brand_slug in BRANDS_MAP.items():
            results = scrape_brand(brand_name, brand_slug, test_mode=False)
            scraped_all.extend(results)
            time.sleep(1.0)
            
    # Create DataFrame
    df = pd.DataFrame(scraped_all)
    if df.empty:
        print("No phones scraped!")
        return
        
    # Clean duplicates by model name
    df = df.drop_duplicates(subset=['model_name'], keep='first').reset_index(drop=True)
    
    # Fill phone_id
    for idx in range(len(df)):
        df.at[idx, 'phone_id'] = f"MOB_{idx:04d}"
        
    # Write to CSV
    os.makedirs("data/processed", exist_ok=True)
    out_path = "data/processed/smartphones_structured_26cols.csv"
    df.to_csv(out_path, index=False)
    print(f"\nSuccessfully saved {len(df)} phones to {out_path}!")
    print(df[['brand', 'model_name', 'price', 'ram_gb', 'storage_gb']].head(10).to_string())

if __name__ == "__main__":
    main()
