import requests
from seleniumwire import webdriver

login_url = "https://www.united.com/en/us/myunited"

session = requests.Session()

request_payload = {
    "username": "SJ942934",
    "password": "kfy1997!",
    "toPersist": False
}

headers = {
    "authority": "www.united.com",
    "path": "/api/user/signIn",
    "scheme": "https",
    "accept": "application/json",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US",
    "content-type": "application/json",
    "origin": "https://www.united.com",
    "referer": "https://www.united.com/en/us/myunited",
    "sec-ch-ua": '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
}

# Start the selenium browser with a proxy
driver = webdriver.Chrome()

# Navigate to the login page
driver.get('https://www.united.com/en/us/united-mileageplus-signin/')

# Enter your credentials using selenium
username_field = driver.find_element_by_name('loginFormPage.mpInput')
password_field = driver.find_element_by_name('loginFormPage.password')
submit_button = driver.find_element_by_css_selector('button[type="submit"]')

username_field.send_keys('SJ942934')
password_field.send_keys('kfy1997!')
submit_button.click()
"""
# Wait for the login process to complete
driver.wait_for_request('/profile/digital/enrollment/confirmation')

# Get the requests captured by selenium-wire
requests_list = driver.requests

# Get the request headers for the /api/user/signIn endpoint
api_request = None
for request in requests_list:
    if request.path == '/api/user/signIn':
        api_request = request
        break

# Retrieve the request headers
headers = api_request.headers

# Use requests to get the response from the /api/user/signIn endpoint
response = requests.post('https://www.united.com/api/user/signIn', headers=headers)

# Print the response content
print(response.text)"""

# Close the selenium browser
driver.quit()
