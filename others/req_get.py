import requests

url = 'https://www.google.com/'

def req_get(url):
    r = requests.get(url)
    return r

response = req_get(url)
print(response)