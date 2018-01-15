from __future__ import unicode_literals
import urllib.request
import os
import sys

import praw
import cv2
import youtube_dl
import config
from moviepy.editor import VideoFileClip, concatenate_videoclips

def get_submissions(subreddit_name, time_filter, num_submission, reddit):
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
        List with youtube links and list with twitch links.
    """

    # Empty list to store links.
    links = []

    # Obtain Subreddit Instance.
    submissions = reddit.subreddit(subreddit_name)

    # Get top posts from Subreddit Instance.
    submissions = submissions.top(time_filter, limit=num_submission)

    for submission in submissions:
        vid_url = submission.url
        # If url of submission is a youtube.com link append the list.
        if "youtube.com" in vid_url:
            links.append(vid_url)
        elif "twitch.tv" in vid_url:
            twitch_link = get_twitch_mp4_url(vid_url)
            links.append(twitch_link)


    print('Successfully colected {} videos from Reddit'.format(len(links)))
    return links

def get_twitch_mp4_url(url):
    """
    Finds url to .mp4 file in .html in the clips.twitch.tv link.
    We could retrieve the .mp4 link using Twitch API, but it will 
    eventually be removed on 12/31/18 so I use this method inspired
    by https://github.com/GeordieP/clip-downloader/blob/master/tcd.py.
    The method in link is actually outdated because .html page changes
    overtime so this method should last longer.

    :param url:
    Url to twitch clip.

    :returns:
    Clip link with .mp4 format.
    """

    # Read the conent of the page.
    html = str(urllib.request.urlopen(url).read())

    # Start and end of the link to .mp4 clip.
    start_url = "https://"
    end_url = ".mp4"

    # Split html string.
    html = html.split()

    # Search for mp4 link in every line.
    for line in html:
        if '.mp4' in line:
            id_start = line.find(start_url)
            id_end = line.find(end_url)
            mp4url = line[id_start:id_end+4]
            return mp4url

def download_videos(dir_videos, links):
    """
    Download youtube videos from provided list using youtube-dl module.

    :param dir_videos:
        Path to directory with downloaded videos.

    :param links:
        List with youtube links to download.

    :return:
        None.
    """

    # ydl_opts is a dictionary used in youtube-dl module.
    # All options can be found in following link: 
    # https://github.com/rg3/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L128-L278
    ydl_opts = {
    'format': 'mp4',
    'noplaylist' : True,
    'outtmpl': os.path.join(dir_videos, '%(title)s.%(ext)s')
    }

    for link in links:
        if "youtube.com" in link:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
        elif "twitch.tv" in link:
            # Extract unique id of clip to get unique file name.
            # The file_name should be something like 12345.mp4.
            file_name = link.split('/')
            file_name = file_name[len(file_name)-1]

            # Output path to video.
            output_path = os.path.join(dir_videos, file_name)

            # Download the .mp4 file.
            try:
                urllib.request.urlretrieve(link, output_path)
                print("File {} successfully downloaded.".format(file_name))
            except:
                print("Could not download {} file from twitch.tv".format(file_name))

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

    subreddit = 'livestreamfail'
    time_filter = 'day'
    num_submission = 5

    dir_videos = './videos/'
    output_name = 'haikus_12.01'

    links = get_submissions(subreddit, time_filter, num_submission, reddit)

    print(links)
    download_videos(dir_videos, links)
    compile_videos(dir_videos, output_name)