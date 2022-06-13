from instaloader import Profile, Instaloader
from instagram import main
from time import sleep
import telegram_send
import pickle
from datetime import datetime, timedelta
import pytz
import sys



def run():
    L = Instaloader()
    # Write Instagram Profile Name In Replace Of Type
    profile = Profile.from_username(L.context, 'Type')
    for get_video in profile.get_posts():
        if get_video.video_url is not None:
            date = get_video.date
            with open('date', 'rb') as fp:
                itemlist = pickle.load(fp)
            if date > itemlist:
                check = main()
                if check == False:
                    telegram_send.send(messages=['Uploading Youtube maximum reached'])
                    while True:
                        india_time = datetime.now(pytz.timezone('Asia/Kolkata'))
                        if india_time.hour == 13:
                            break
                        else:
                            sleep(20 * 60)
                else:
                    with open('date', 'wb') as fp:
                        pickle.dump(get_video.date, fp)
            break


# telegram_send.send(messages=['Youtube Server Started'])
while True:
    try:
        run()
        sleep(5 * 60)
    except:
        telegram_send.send(messages=['Something Problem In main.py Running'])
        break
