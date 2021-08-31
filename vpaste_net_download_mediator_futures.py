import concurrent.futures
import threading
from collections import deque

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import proxy_grab as proxy
from fake_useragent import UserAgent

# Parse file to get all IDs in memmory
global lines
with open('vpaste_net_ls_formatted.txt') as f:
    # Get IDs from file
    lines = deque(f.read().splitlines())

# Setup semaphore for multithread
sem = threading.Condition()

def OpenDriver(proxies, ua):
    """
    Function to open a geckodriver with certain options
    
    Parameters
    ----------------
    proxies: [str]
        a list of proxies that will be used
    
    ua: UserAgent
        a useragent object, used to get a random useragent
    """
    # Get random proxy
    rndProxy = proxy.random_proxy(proxies)

    # Set up options
    options = Options()
    options.headless = False
    options.add_argument("--window-size=1920,1200")
    options.add_argument('--proxy-server=%s'%(rndProxy['ip'] + ':' + rndProxy['port']))
    options.add_argument('user-agent=%s'%ua.random)

    # Launch driver
    driver = webdriver.Firefox(options=options, executable_path=r'/home/remnux/Downloads/geckodriver')

    return driver

def parseURL(driver):
    """
    Uses geckodriver to navigate websites and parse data, saves data to file.
    
    Parameters
    ----------------
    driver: [geckodriver]
        An instance of a geckodriver (or other selenium driver).
    """
    while True:
        # Get next line in ID file (next ID to parse)
        sem.acquire()
        currentID = lines.pop()
        sem.release()

        driver.get("http://vpaste.net/"+ str(currentID)+"?raw")
        print("Thread "+ str(threading.get_ident()) + " - " + currentID)

        # If you see 403 Forbidden stop
        try:
            forbidden = driver.find_element_by_xpath('/html/body/center[1]/h1')
            if forbidden.text == "403 Forbidden":
                # Open new driver with new proxy
                # Other possible solution (hackier but probably less time consuming): 
                # https://stackoverflow.com/questions/29776607/python-selenium-webdriver-changing-proxy-settings-on-the-fly
                driver.quit()
                
        except:
            pass

        try:
            # Get data
            data = driver.find_element_by_xpath("/html").text

            # Write data to file
            f = open("vpaste_net_"+ str(currentID), "w")
            f.write(data)
            f.close()
        except:
            pass


class MainThread(threading.Thread):
    # Use mediator to create a shared iterator with a file
    def __init__(self):
        self.file = file = open("vpaste_net_ls_formatted.txt",'rb')

    def run(self):
        # Get a list of proxies
        ua = UserAgent()
        proxies = proxy.get_proxies(ua)

        # Number of drivers to have simultaneously
        N = 3

        # Create drivers
        drivers = list()
        for i in range(N):
            drivers.append(OpenDriver(proxies, ua))
        
        print("\t Drivers created successfully!")
        print("Starting parsing...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=N) as executor:
            executor.map(parseURL, drivers)

    # Destructor method - close file
    def __del__(self):
        self.file.close()


if __name__ == '__main__':
    mainThread = MainThread()
    mainThread.run()