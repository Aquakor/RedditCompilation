from __future__ import unicode_literals
import os
import sys

import praw
import cv2
import youtube_dl
import config
from moviepy.editor import VideoFileClip, concatenate_videoclips

# Obtain a Reddit Instance.
reddit = praw.Reddit(client_id=config.client_id,
                     client_secret=config.client_secret,
                     user_agent=config.user_agent)

# Array with youtube links to the videos.
youtube_links = []

# Number of videos to scrap
num_videos = 50

# Subreddit name
subreddit_name = 'youtubehaiku'

# Obtain Subreddit Instance and append youtube_links array.
try:
    for submission in reddit.subreddit(subreddit_name).top('day', limit=50):
        if submission.title.startswith('[Poetry]') or submission.title.startswith('[Haiku]'):
            youtube_links.append(submission.url)
    print('Successfully colected {} memes from Reddit'.format(len(youtube_links)))
except:
    sys.exit('Could not connect to the API')

# Attempt to download a video.
for link in youtube_links:
    # Attempt to download a meme
    ydl_opts = {
    'format': 'mp4',
    'noplaylist' : True,
    'outtmpl': './videos/%(title)s.%(ext)s'
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])

# Path to videos dir
vid_dir = './videos/'

# List videos in a given directory
videos = os.listdir(vid_dir)

#  Array with VideoFileClip objects used to craete final video.
clips = []

# Attempt to append clips array with files of format *.mp4s and height of 720
for video in videos:
    if video.endswith('.mp4'):
        video = os.path.join(vid_dir, video)
        vid = cv2.VideoCapture(video)
        height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        if height >= 500:
            clips.append(VideoFileClip(video))
            print('{} has height >= 500px.'.format(video))
        else:
            print('{} has height < 500px.'.format(video))
    else:
        print('{} does not end with .mp4, skipping.'.format(video))

# Create final video.
final_clip = concatenate_videoclips(clips, method='compose')
final_clip.write_videofile("haikus_10-01.mp4")