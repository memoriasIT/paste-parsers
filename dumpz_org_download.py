from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import threading
import proxy_grab as proxy
from fake_useragent import UserAgent

# Current paste ID to use in url
# Current value is not representative as it should be changed in the main
currentID = 0

class PasswordException(Exception):
    """Exception thrown for password protected pastes. Only used for logging."""
    pass

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

def GetData(proxies, ua):
    """
    Uses geckodriver to navigate websites and parse data, saves data to file.
    
    Parameters
    ----------------
    proxies: [str]
        a list of proxies that will be used
    
    ua: UserAgent
        a useragent object, used to get a random useragent
    """

    # currentID variable used in mutex
    global currentID
    
    # Open driver
    driver = OpenDriver(proxies, ua)

    while True:
        driver.get("https://dumpz.org/"+ str(currentID))

        # If you see 403 Forbidden stop
        try:
            forbidden = driver.find_element_by_xpath('/html/body/center[1]/h1')
            if forbidden.text == "403 Forbidden":
                # Open new driver with new proxy
                # Other possible solution (hackier but probably less time consuming): 
                # https://stackoverflow.com/questions/29776607/python-selenium-webdriver-changing-proxy-settings-on-the-fly
                driver.quit()
                OpenDriver(proxies, ua)
                
        except:
            pass

        # Page is password protected
        try:
            if driver.get('url').find("password") != -1:
                raise PasswordException('Password protected paste')

            # Try getting title as it is not mandatory field
            try:
                title = driver.find_element_by_xpath('/html/body/div[1]/div[1]/h3')
            except:
                title = ""

            # Date is not present in older pastes
            try:
                date = driver.find_element_by_xpath("/html/body/div[1]/div[1]/div[1]/div/span[3]").text
            except:
                date = ""

            # There should be no problem, just in case
            try:
                text = driver.find_element_by_xpath("/html/body/div[1]/div[2]/table/tbody/tr/td[2]/div").text
            except:
                text = ""
            
            # Write data to file
            f = open("dumpz_org_"+ str(currentID) + "_" + date, "w")
            f.write(text)
            f.close()
        
        finally:
            # Decrement current id by one in mutex
            sem.acquire()
            currentID -= 1
            sem.release()

if __name__ == '__main__':
    # Set up currentID as lastid
    f = open("dumpz_org_lastID.txt", "r")
    currentID = int(float(f.read()))
    f.close()

    # Setup semaphore for multithread
    sem = threading.Semaphore()

    # Get a list of proxies
    ua = UserAgent()
    proxies = proxy.get_proxies(ua)

    # Thread 1
    t = threading.Thread(target = GetData, args=(proxies, ua))
    t.start()

    # Thread 2
    t2 = threading.Thread(target = GetData, args=(proxies, ua))
    t2.start()