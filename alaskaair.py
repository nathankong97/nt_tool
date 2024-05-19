import requests
import json


url = "https://www.alaskaair.com/search/api/flightresults"
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate,br,zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Adrum": "isAjax:true",
    "Cache-Control": "no-cache",
    "Content-Type": "text/plain;charset-UTF-8",
    "Origin": "https://www.alaskaair.com",
    "Pragma": "no-cache",
    "Referer": "https://www.alaskaair.com/search/results?A=1&O=la5&D=tyo&OD=2024-02-05&OT=Anytime&RT=false&ShoppingMethod=onlineaward&awardType=MilesOnly&UPG=none",
    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin"
}

with open("alaskaair.json") as f:
    payload = json.load(f)

json_payload = json.dumps(payload, ensure_ascii=False).encode("utf-8")

result = requests.post(url, headers=headers, data=json_payload)

print(result)

print(result.text)
