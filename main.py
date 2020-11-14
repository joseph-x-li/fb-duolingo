import fbchat
import duolingo
import logging
from passwords import duoname, duopass, fbemail, fbpass

logging.basicConfig(filename='events.log', level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s")

duoppl = [
    "KonwooKim",
]


def main():
    try:
        lingo = duolingo.Duolingo(duoname, "duopass")
    except duolingo.DuolingoException as e:
        logging.error(f"UNABLE TO SIGN INTO DUOLINGO: {e}")
        return

    # for person in duoppl:

    # Auth into duolingo and facebook messenger
    #     check if it is within some "check" timeframe
    #     if it is, reload the duolingo auth and check whether mr kim did his shit
    #     if he didnt, send a message
    #     Check whether it is 9:00 on a saturday
    #         rush in the regular crowd to ethan lu


if __name__ == "__main__":
    main()
