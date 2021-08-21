from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import random

# Proxy grabber based from https://github.com/joe-habel/YouTube-View-Bot/
# It had to be modified as the website was changed and tags where not relevant anymore
def get_proxies(ua):
    proxies = []
    proxies_req = Request('https://www.sslproxies.org/')
    proxies_req.add_header('User-Agent', ua.random)
    proxies_doc = urlopen(proxies_req).read().decode('utf8')

    soup = BeautifulSoup(proxies_doc, 'html.parser')
    proxies_section = soup.find(id='list')
    proxies_table = soup.find("table")

  # Save proxies in the array
    for row in proxies_table.tbody.find_all('tr'):
        proxies.append({
                        'ip':   row.find_all('td')[0].string,
                        'port': row.find_all('td')[1].string})
    return proxies

def random_proxy(proxies):
  return random.choice(proxies)

if __name__ == '__main__':
    print(get_proxies(UserAgent()))
