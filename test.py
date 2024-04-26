import sys

from yt_dlp import YoutubeDL


# sys.path.append('/d/Develop/Youtube_Downloader')

URL_SMALL = 'https://youtube.com/shorts/2bNl9PnWl4g?si=B_J0EUFgLhLsArwE'
URL_BIG = 'https://youtu.be/xxtCsa0j6eM?si=Qj1VON0TDvuAHLLE'
FORMAT = '480'

ydl_opts = {'format': f'bv*[height<={FORMAT}][ext=mp4][vcodec~="^((he|a)vc|h26[45])"]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b',
            'outtmpl': 'Videos/%(id)s.%(ext)s',
            # 'progress_hooks': [progress],
            'quiet': True,
            'no_warnings': True}


with YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(URL_SMALL, download=True)
    ydl.list_formats(info)
    width = info.get('width')
    height = info.get('height')
    print(width)
    print(height)
