from .urls import CHOOSE_FLIGHT_PAGE


class UnitedAirlinesConfig:
    HEADERS = {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US",
        "origin": "https://www.united.com",
        "referer": "https://www.united.com/en/us/",
        "pragma": "no-cache",
        "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50"
    }

    CALENDAR_PRICING_PAYLOAD = {"UserSelected": "depart", "Depart": "", "Return": "", "Origin": "", "Destination": "",
                                "IsAward": True, "ClientCurrentDate": "", "IsPremium": False, "IsOneway": True,
                                "ExcludeBasicEconomy": False,
                                "Travelers": {"Adult": 1, "Senior": 0, "Infant": 0, "InfantOnLap": 0, "Children01": 0,
                                              "Children02": 0,
                                              "Children03": 0, "Children04": 0}}

    CALENDAR_API_REFERER = CHOOSE_FLIGHT_PAGE + \
                  "?f={}&t={}&d={}&tt=1&at=1&sc=7&act=3&px=1&taxng=1&newHP=True&clm=30&st=bestmatches&tqp=A"

    FLIGHT_API_REFERER = CHOOSE_FLIGHT_PAGE + \
        "?f={}&t={}&d={}&tt=1&at=1&sc=7&act=3&px=1&taxng=1&newHP=True&clm=7&st=bestmatches&tqp=A"

    NEW_FLIGHT_API_REFERER = CHOOSE_FLIGHT_PAGE + \
        "?f={}&t={}&d={}&tt=1&at=1&sc=7&act=2&px=1&taxng=1&newHP=True&clm=7&st=bestmatches&tqp=A"

    NEW_HEADER = {
        "accept": "application/json",
        "accept-language": "en-US",
        "content-type": "application/json",
        "referer": "https://www.united.com/en/us/fsr/choose-flights?f=JFK&t=HND&d=2023-12-24&tt=1&at=1&sc=7&act=2&px=1&taxng=1&newHP=True&clm=7&st=bestmatches&tqp=A",
        "sec-ch-ua": '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

class UnitedAirlinesLegacyConfig:
    LEGACY_HEADERS = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5,ja;q=0.4",
        "cache-control": "no-cache",
        "content-type": "application/json; charset=UTF-8",
        "sec-ch-ua": "\"Chromium\";v=\"110\", \"Not A(Brand\";v=\"24\", \"Microsoft Edge\";v=\"110\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50"
    }

    LEGACY_QUERY_PARAMETER = """
    https://www.united.com/ual/en/us/flight-search/book-a-flight/results/awd?
    f=TYO&
    t=ORD&
    d=2023-11-14&
    tt=1&
    st=bestmatches&
    at=1&
    rm=1&
    cbm=-1&
    cbm2=-1&
    sc=7&
    px=1&
    taxng=1&
    idx=1&
    act=3
    """


    #  act: 0 = ECO, 1 = PRE_ECO, 2 = BUS, 3 = FIRST
    #  pc: preferred connection
    #  upc: not preferred connection
    #  cp: 0 = all carrier, 1 = united only, 2 = only star alliance
    #  ut: MUA: upgradable
