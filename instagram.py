from googleapiclient.http import MediaFileUpload
from instaloader import Profile, Instaloader
from datetime import datetime, timedelta
from moviepy.editor import VideoFileClip
from Google import Create_Service
from time import sleep
import telegram_send
import pickle
import pytz
import os

L = Instaloader()
service = None


def remove_file(path, count):
    with open('outfile', 'rb') as fp:
        itemlist = pickle.load(fp)
    itemlist.insert(count, path)
    print(path, 'insert')
    try:
        itemlist[3]
        file = itemlist.pop(3)
        os.remove(file)
        # telegram_send.send(messages=['Video Removed Successfully'])
        # print(file, 'Video Removed')
    except:
        if len(itemlist) > 3:
            telegram_send.send(messages=['Error : Removing Video'])
            # print('Problem In Removing Video')
        else:
            pass
    finally:
        with open('outfile', 'wb') as fp:
            pickle.dump(itemlist, fp)


def main():
    count = 0
    try:
        # Write Instagram Profile Name In Replace Of Type
        profile = Profile.from_username(L.context, 'Type')
        for get_video in profile.get_posts():
            if get_video.video_url is not None:
                if count < 2:
                    caption = get_video.caption
                    find = caption.find('\n')
                    title = caption[:find]
                    # To Remove Paid Promotion Replace Type With the Name Of Sponsor Name
                    if len(title) > 99 or get_video.caption.find('Type') > 0:
                        if len(title) > 99:
                            telegram_send.send(messages=['This video will not upload Caption:', title])
                        continue
                    else:
                        filename = 'video/' + get_video.shortcode
                        file_exist = L.download_pic(filename=filename, url=get_video.video_url,
                                                    mtime=get_video.date_local)
                        if file_exist is False:
                            break
                        else:
                            path = filename + '.mp4'
                            clip = VideoFileClip(path)
                            if clip.duration < 3:
                                clip.close()
                                sleep(1)
                                os.remove(path)
                                continue
                            else:
                                clip.close()
                                telegram_send.send(messages=['New Video launched'])
                                # print('New Video Launched')
                                try:
                                    youtube_upload(title=title, path=path, count=count)
                                    remove_file(path=path, count=count)
                                except:
                                    # telegram_send.send(messages=['Error : Upload To Youtube'])
                                    os.remove(path)
                                    return False
                    count += 1
                else:
                    break
    except:
        telegram_send.send(messages=['Error : Instagram Video Download'])
        # print('Not Downloadin Instagram Video')
        return False


def youtube_authentication():
    global service
    CLIENT_SECRET_FILE = "client_secrets.json"
    API_NAME = 'youtube'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    # telegram_send.send(messages=['Youtube Authentication Success'])
    # print('Youtube Authentication Success')


def youtube_upload(title, path, count):
    youtube_authentication()

    datetime_india = datetime.now(pytz.timezone('Asia/Kolkata')) + timedelta(hours=(count + 1))
    upload_date_time = datetime_india.isoformat()

    request_body = {
        'snippet': {
            'categoryI': 22,
            'title': title,
            'description': title,
            'tags': ['funny', 'sarcasm', 'comedy']
        },
        'status': {
            'privacyStatus': 'private',
            'publishAt': upload_date_time,
            'selfDeclaredMadeForKids': False,
        },
        'notifySubscribers': False
    }

    mediaFile = MediaFileUpload(path)

    service.videos().insert(
        part='snippet,status',
        body=request_body,
        media_body=mediaFile
    ).execute()
    telegram_send.send(messages=['Upload Successfully'])
    # print('Upload Success')
