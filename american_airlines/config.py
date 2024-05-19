class AmericanAirlinesConfig:
    HEADERS = {
        "authority": "www.aa.com",
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5,ja;q=0.4",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "dnt": "1",
        "origin": "https://www.aa.com",
        "pragma": "no-cache",
        "referer": "https://www.aa.com/booking/choose-flights/1",
        "referrer-policy": "strict-origin-when-cross-origin",
        "sec-ch-ua": "\"Chromium\";v=\"110\", \"Not A(Brand\";v=\"24\", \"Microsoft Edge\";v=\"110\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50",
    }

    ITINERARY_PAYLOAD = {
        "metadata": {
            "selectedProducts": [],
            "tripType": "OneWay",
            "udo": {}
        },
        "passengers": [
            {
                "type": "adult",
                "count": 1
            }
        ],
        "requestHeader": {
            "clientId": "AAcom"
        },
        "slices": [
            {
                "allCarriers": True,
                "cabin": '',
                "departureDate": "",
                "destination": "",
                "destinationNearbyAirports": True,
                "maxStops": None,
                "origin": "",
                "originNearbyAirports": True
            }
        ],
        "tripOptions": {
            "searchType": "Award",
            "corporateBooking": False,
            "locale": "en_US"
        },
        "loyaltyInfo": None,
        "queryParams": {
            "sliceIndex": 0,
            "sessionId": "",
            "solu tionSet": "",
            "solutionId": ""
        }
    }

    ITINERARY_SLICES = {
        "allCarriers": True,
        "cabin": '',
        "departureDate": "",
        "destination": "",
        "destinationNearbyAirports": True,
        "maxStops": None,
        "origin": "",
        "originNearbyAirports": True
    }
