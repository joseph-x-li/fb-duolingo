import fbchat
import duolingo
import logging
import random
import os
import time
from passwords import duoname, duopass, fbemail, fbpass, people
filehandler = logging.FileHandler(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'events.log'))
filehandler.setFormatter(logging.Formatter(fmt="%(asctime)s:%(levelname)s:%(message)s"))
logger = logging.getLogger("fb-duolingo")
logger.setLevel(logging.INFO)
logger.addHandler(filehandler)

# see https://github.com/fbchat-dev/fbchat/issues/615#issuecomment-710127001 
import re
fbchat._util.USER_AGENTS    = ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"]
fbchat._state.FB_DTSG_REGEX = re.compile(r'"name":"fb_dtsg","value":"(.*?)"')

def main(patch=None):
    global people
    try:
        lingo = duolingo.Duolingo(duoname, duopass)
    except duolingo.DuolingoException as e:
        logger.error(f"Unable to sign into Duolingo: {e}")
        return
    
    msnger = None
    
    if patch is not None:
        people = [patch]
    
    for uname, fbid in people:
        sleeptime = random.randint(13, 25)
        time.sleep(sleeptime)
        lingo.set_username(uname)
        info = lingo.get_streak_info()
        if info['streak_extended_today']:
            logger.info(f"{uname} already did a lesson today. Yay!")
            continue
        if msnger is None:
            try:
                msnger = fbchat.Client(fbemail, fbpass, logging_level=logging.WARNING)
            except fbchat.FBchatException as e:
                logger.error(f"Unable to sign into Facebook: {e}")
                return
        logger.info(f"{uname} has not yet done a lesson today... reminding")
        message = f"Do a Duolingo lesson to save your {info['site_streak']} day streak"
        message += '!' * random.randint(1,6)
        msnger.send(fbchat.Message(text=message), thread_id=fbid)
        logger.info(f"Sent \"{message}\" to {uname}")
        msnger.send(fbchat.Message(sticker=fbchat.Sticker("237317987087861")), thread_id=fbid)
        
    # left out due to errors that make me have to reset my facebook password
    # msnger.logout()

if __name__ == "__main__":
    main()
