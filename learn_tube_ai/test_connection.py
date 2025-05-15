import requests

urls_to_test = [
    "https://www.google.com",
    "https://www.youtube.com" # This will likely still fail if the script can't use the VPN
]

for url in urls_to_test:
    try:
        print(f"Attempting to connect to {url}...")
        # Add a timeout to the request
        response = requests.get(url, timeout=10) # 10-second timeout
        print(f"Successfully connected to {url}. Status code: {response.status_code}")
    except requests.exceptions.Timeout:
        print(f"Timeout when trying to connect to {url}.")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to {url}: {e}")
    print("-" * 20)