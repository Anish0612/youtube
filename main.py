from instaloader import Profile, Instaloader
import cv2 as cv
from googleapiclient.http import MediaFileUpload
from Google import Create_Service
from datetime import datetime, timedelta
import pytz
import os
import time
import requests


def verifying_video():
    if len(title) > 99:
        return False
    sponser_keywords = []                      # If the title contains those keyword the video will not upload
    for keyword in sponser_keywords:
        if keyword in post.caption:
            return False
    result = checking_video_duration()      # checking the required video duration


def checking_video_duration():
    global path
    path = filename+'.mp4'
    data = cv.VideoCapture(filename+'.mp4')
    frames = data.get(cv.CAP_PROP_FRAME_COUNT)
    fps = data.get(cv.CAP_PROP_FPS)
    if frames/fps < 3:                         # you can modified minimum duration required to upload to youtube channel
        return False
    else:
        return True


def youtube_authentication():
    global service
    CLIENT_SECRET_FILE = "client_secrets.json"
    API_NAME = 'youtube'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)


def upload_to_youtube():
    youtube_authentication()

    # if you want to publish after an hour, uncomment above two line
    # datetime_india = datetime.now(pytz.timezone('Asia/Kolkata')) + timedelta(hours=1)
    # upload_date_time = datetime_india.isoformat()

    upload_date_time = datetime.now().isoformat()

    request_body = {
        'snippet': {
            'categoryI': 22,
            'title': title,
            'description': post.caption,
            'tags': ['funny', 'sarcasm', 'comedy']
        },
        'status': {
            'privacyStatus': 'private',
            'publishAt': upload_date_time,
            'selfDeclaredMadeForKids': False,
        },
        'notifySubscribers': True
    }

    mediaFile = MediaFileUpload(path)

    service.videos().insert(
        part='snippet,status',
        body=request_body,
        media_body=mediaFile
    ).execute()
    # telegram_send.send(messages=['Upload Successfully'])
    print('Upload Successfully')
    print('-------------------\n')


def delete_old_video():
    all_videos = os.listdir('video')
    for video in all_videos:
        if post.shortcode+'.mp4' != video:
            os.remove('video/'+video)


def main():
    global title, post, filename
    L = Instaloader()
    profile_name = ''               # eg: sarcasticschool_
    profile = Profile.from_username(L.context, profile_name)
    for post in profile.get_posts():
        if post.video_url is not None:
            title_len = post.caption.find('\n')
            title = post.caption[:title_len]
            filename = 'video/' + post.shortcode
            if not os.path.exists('video/'):
                os.mkdir('video')
            file_downloaded = L.download_pic(filename=filename, url=post.video_url,
                                             mtime=post.date_local)
            delete_old_video()
            if file_downloaded:
                print('\nnew video found')
                result = verifying_video()
                if result:
                    upload_to_youtube()
            break


while True:
    try:
        main()
        time.sleep(3600)            # how frequently check (in second)
    except:
        print('Something Problem In main.py Running')
        break
