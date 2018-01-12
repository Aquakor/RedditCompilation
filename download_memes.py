from __future__ import unicode_literals
import os
import sys

import praw
import cv2
import youtube_dl
import config
from moviepy.editor import VideoFileClip, concatenate_videoclips

def get_submissions_yt(subreddit_name, time_filter, num_submission, reddit):
    """
    Get list with youtube links from given subreddit using praw module.

    :param subreddit_name:
        Name of subreddit, e.g. 'youtubehaiku'.

    :param time_filter:
        Type to sort top posts, can be:
        all, day, hour, month, week, year.

    :param submission_num:
        Number of submissions to scrap from reddit, e.g. 50.

    :param reddit:
        Reddit Instance from praw.

    :return:
        List with youtube links.
    """

    # Empty list to store youtube links.
    youtube_links = []

    # Obtain Subreddit Instance.
    submissions = reddit.subreddit(subreddit_name)

    # Get top posts from Subreddit Instance.
    submissions = submissions.top(time_filter, limit=num_submission)

    for submission in submissions:
        vid_url = submission.url
        # If url of submission is a youtube.com link append the list.
        if "youtube.com" in vid_url:
            youtube_links.append(vid_url)

    print('Successfully colected {} videos from Reddit'.format(len(youtube_links)))
    return youtube_links

def download_videos_yt(dir_videos, youtube_links):
    """
    Download youtube videos from provided list using youtube-dl module.

    :param dir_videos:
        Path to directory with downloaded videos.

    :param youtube_links:
        List with youtube links to download.

    :return:
        None.
    """

    for link in youtube_links:
        # ydl_opts is a dictionary used in youtube-dl module.
        # All options can be found in following link: 
        # https://github.com/rg3/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L128-L278
        ydl_opts = {
        'format': 'mp4',
        'noplaylist' : True,
        'outtmpl': os.path.join(dir_videos, '%(title)s.%(ext)s')
        }

        # Download video
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])

def compile_videos(dir_videos, output_name):
    """
    Compile videos  using concatenate method from movie-py module.

    :param dir_videos:
        Path to directory with downloaded videos.

    :param output_name:
        Name of the output video. Do not include extension of the video.

    :return:
        None.
    """

    # List videos in a given directory.
    videos = os.listdir(dir_videos)

    #  List to append VideoFileClip objects used to create final video.
    clips = []

    # Attempt to append clips with files of format *.mp4s.
    for video in videos:
        if video.endswith('.mp4'):
            video = os.path.join(dir_videos, video)
            vid = cv2.VideoCapture(video)
            height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
            # Skip any videos that has height lower then 500px, otherwise
            # the final video looks scuffed. You can lower this threshold
            # in order to increase the number of videos in final video.
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

    # Obtain Reddit Instance.
    reddit = praw.Reddit(client_id=config.client_id,
                     client_secret=config.client_secret,
                     user_agent=config.user_agent)

    subreddit = 'youtubehaiku'
    time_filter = 'day'
    num_submission = 5

    dir_videos = './videos/'
    output_name = 'haikus_12.01'

    yt_links = get_submissions_yt(subreddit, time_filter, num_submission, reddit)
    download_videos_yt(dir_videos, yt_links)
    compile_videos(dir_videos, output_name)