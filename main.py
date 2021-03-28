import fbchat
import duolingo
import logging
import random
import os
import time
import toml

filehandler = logging.FileHandler(os.path.join(os.path.dirname(__file__), 'events.log'))
filehandler.setFormatter(logging.Formatter(fmt="%(asctime)s:%(levelname)s:%(message)s"))
logger = logging.getLogger("fb-duolingo")
logger.setLevel(logging.INFO)
logger.addHandler(filehandler)

CFG_PATH = os.path.join(os.path.dirname(__file__), 'config.toml')

def readconfig():
    with open(CFG_PATH) as f:
        config = toml.loads(f.read())
    return config

def writeconfig(newconfig):
    with open(CFG_PATH, 'w') as f:
        toml.dump(newconfig, f)

def getcookies(config):
    import os
    os.environ['PATH'] += os.pathsep + "/home/pi/Downloads/geckodriver-0.29.0/target/armv7-unknown-linux-gnueabihf/release"

    from selenium import webdriver
    opts = webdriver.FirefoxOptions()
    opts.add_argument("--headless")
    opts.add_argument("--window-size=1080,1080")
    test_driver = webdriver.Firefox(options=opts)
    test_driver.get("https://www.messenger.com/")

    email_input = test_driver.find_element_by_id("email")
    pass_input = test_driver.find_element_by_id("pass")
    login_button = test_driver.find_element_by_id("loginbutton")
    email_input.send_keys(config['facebook']['email'])
    time.sleep(5)
    pass_input.send_keys(config['facebook']['password'])
    time.sleep(5)
    login_button.submit()
    time.sleep(5)
    allcookies = test_driver.get_cookies()
    
    successes = 0

    for cookie in allcookies:
        if cookie['name'] == 'c_user':
            config['cookies']['c_user'] = cookie['value']
            successes += 1
        elif cookie['name'] == 'xs':
            config['cookies']['xs'] = cookie['value']
            successes += 1

    if successes != 2:
        raise RuntimeError("Selenium Login Failed")
    
    return config

def query_duolingo(config):
    duocfg = config['duolingo']
    try:
        lingo = duolingo.Duolingo(duocfg['username'], duocfg['password'])
    except duolingo.DuolingoException as e:
        logger.error(f"Unable to sign into Duolingo: {e}")
        return

    retval = []

    for uname, fbid in config['people']:
        sleeptime = random.randint(13, 25)
        time.sleep(sleeptime)
        lingo.set_username(uname)
        info = lingo.get_streak_info()
        if info['streak_extended_today']:
            logger.info(f"{uname} already did a lesson today. Yay!")
            continue
        logger.info(f"{uname} has not yet done a lesson today... reminding")
        retval.append((uname, fbid, info['site_streak']))
    
    return retval

def fbremind(config, people):
    refresh = False    
    try:
        msnger = fbchat.Client("", "", session_cookies=config['cookies'], logging_level=logging.WARNING) 
    except fbchat.FBchatException as e:
        logger.warning(f"Unable to sign into Facebook: {e}\nTrying to refresh cookies...")
        refresh = True
    if refresh:
        try:
            config = getcookies(config)
        except RuntimeError as e:
            logger.error(f"Unable to sign into Facebook using Selenium: {e}")
            raise e
        writeconfig(config)
        try:
            msnger = fbchat.Client("", "", session_cookies=config['cookies'], logging_level=logging.WARNING) 
        except fbchat.FBchatException as e:
            logger.warning(f"Unable to sign into Facebook using refreshed cookies: {e}\nSomething is horribly wrong...")
            raise e
    
    for uname, fbid, streaklen in people:
        sleeptime = random.randint(13, 25)
        time.sleep(sleeptime)
        message = f"Do a Duolingo lesson to save your {streaklen} day streak"
        message += '!' * random.randint(1, 6)
        msnger.send(fbchat.Message(text=message), thread_id=fbid)
        logger.info(f"Sent \"{message}\" to {uname}")
        msnger.send(fbchat.Message(sticker=fbchat.Sticker("237317987087861")), thread_id=fbid)

if __name__ == "__main__":
    # config = readconfig()
    # fbremind(config, [])
    config = readconfig()
    notifs = query_duolingo(config)
    if notifs == []:
        logger.info(f"Everyone did their duolingo lessons. Skipping notificaitons...")
    else:
        fbremind(config, notifs)


