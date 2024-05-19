import requests
import json

url = "https://jbrest.jetblue.com/lfs-rwb/outboundLFS"
headers = {
    "Accept": "application/json",
    "Api-Version": "v3",
    "Application-Channel": "Desktop_Web",
    "Booking-Application-Type": "NGB",
    "Content-Type": "application/json",
    "Referer": "https://www.jetblue.com/booking/flights?from=JFK&to=BOS&depart=2024-02-10&isMultiCity=false&noOfRoute=1&lang=en&adults=1&children=0&infants=0&sharedMarket=false&roundTripFaresFlag=false&usePoints=true",
    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

with open("jetblue.json") as f:
    payload = json.load(f)

json_payload = json.dumps(payload, ensure_ascii=False).encode("utf-8")

result = requests.post(url, headers=headers, data=json_payload)

print(result)

print(result.text)