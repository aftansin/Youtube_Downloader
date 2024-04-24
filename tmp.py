import sys
from typing import Dict

from yt_dlp import YoutubeDL

# sys.path.append('/d/Develop/Youtube_Downloader')

LINK = 'https://youtube.com/shorts/FH2aQO1K0Ns?si=N7vTEPaV2IXMwY_z'

options_audio_only = {
    'format': 'bestaudio/best',  # choice of quality
    'extractaudio': True,  # only keep the audio
    'audioformat': "mp3",  # convert to mp3
    'outtmpl': 'Videos/%(id)s.%(ext)s',  # name the file the ID of the video
    'noplaylist': True,  # only download single song, not playlist
    'quiet': True,
    'no_warnings': True
}

ydl_opts = {'format': 'bv*[height<=1080][ext=mp4][vcodec~="^((he|a)vc|h26[45])"]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b',
            'outtmpl': 'Videos/%(id)s.%(ext)s',
            # 'progress_hooks': [progress],
            'quiet': True,
            'no_warnings': True}

ydl_opts1 = {
    'format': 'm4a/bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'm4a',
    }]
}


with YoutubeDL(ydl_opts) as ydl:
    info: Dict = ydl.extract_info(LINK, download=True)
    file_name = f'{info.get("id")}.{info.get("ext")}'
    title = info.get('title')
    duration_string = info.get('duration_string')
    resolution_info = info.get('format')
    thumbnail_url = info.get('thumbnail')
    ydl.list_formats(info)

















