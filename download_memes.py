from __future__ import unicode_literals
import os
import sys

import praw
import cv2
import youtube_dl
import config
from moviepy.editor import VideoFileClip, concatenate_videoclips

# Array with youtube links to the videos.
youtube_links = []

# Number of videos to scrap
num_videos = 50

# Subreddit name
subreddit_name = 'youtubehaiku'

def get_submissions_yt(subreddit_name, time_filter, num_submission, reddit):
    """
    Get array with youtube links from submissions(posts).

    Args:
        subreddit_name: Name of subreddit, e.g. 'youtubehaiku'.
        time_filter: Type to sort top posts, can be: 
            all, day, hour, month, week, year
        submission_num: Number of submissions to scrap.
        reddit: Instance of reddit.
        
    Returns:
        Array with youtube links.

    """
    youtube_links = []
    # Obtain Subreddit Instance and append youtube_links array.
    submissions = reddit.subreddit(subreddit_name)
    submissions = submissions.top(time_filter, limit=num_submission)

    for submission in submissions:
        vid_url = submission.url
        # If url of submission is a youtube.com link
        if "youtube.com" in vid_url:
            youtube_links.append(vid_url)
    print('Successfully colected {} videos from Reddit'.format(len(youtube_links)))
    return youtube_links

def download_videos_yt(youtube_links):
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

def compile_videos(dir_videos, output_name):
    # List videos in a given directory
    videos = os.listdir(dir_videos)

    #  Array with VideoFileClip objects used to craete final video.
    clips = []

    # Attempt to append clips array with files of format *.mp4s and height of 720
    for video in videos:
        if video.endswith('.mp4'):
            video = os.path.join(dir_videos, video)
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
    final_clip.write_videofile(output_name + '.mp4')


if __name__ == "__main__":
    print("Obtaining reddit instance...")
    reddit = praw.Reddit(client_id=config.client_id,
                     client_secret=config.client_secret,
                     user_agent=config.user_agent)
    yt_links = get_submissions_yt('youtubehaiku', 'day', 5, reddit)
    download_videos_yt(yt_links)
    compile_videos('./videos/', 'haikus_12_01')