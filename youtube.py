import os

from pytube import YouTube


def download_video(link):
    yt = YouTube(link)
    video720 = yt.streams.get_by_resolution(resolution='720p')
    video720.download()
    return video720.default_filename


def delete_video(link):
    yt = YouTube(link)
    video720 = yt.streams.get_by_resolution(resolution='720p')
    filename = video720.default_filename
    os.remove(f'./{filename}')
