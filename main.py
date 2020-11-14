import fbchat
import duolingo
import logging
import random
from passwords import duoname, duopass, fbemail, fbpass, people
logging.basicConfig(filename='events.log', level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s")

### see https://github.com/fbchat-dev/fbchat/issues/615#issuecomment-710127001 
import re
fbchat._util.USER_AGENTS    = ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"]
fbchat._state.FB_DTSG_REGEX = re.compile(r'"name":"fb_dtsg","value":"(.*?)"')

def main(patch=None):
    try:
        lingo = duolingo.Duolingo(duoname, "duopass")
    except duolingo.DuolingoException as e:
        logging.error(f"UNABLE TO SIGN INTO DUOLINGO: {e}")
        return
    
    try:
        msnger = fbchat.Client(fbemail, fbpass)
    except fbchat.FBchatException as e:
        logging.error(f"UNABLE TO SIGN INTO FACEBOOK: {e}")
        return

    if patch is not None:
        people = [patch]
    
    for uname, fbid in people:
        lingo.set_username(uname)
        info = lingo.get_streak_info()
        if info['streak_extended_today']:
            continue
        message = f"Do a lesson to save your {info['site_streak']} day streak"
        message += '!' * random.randint(1,5)
        msnger.send(fbchat.Message(text=message), thread_id=fbid)
    
if __name__ == "__main__":
    main()
