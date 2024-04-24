import os

from yt_dlp import YoutubeDL


def download_file(url: str, format_id: str):
    resolution = format_id[:-1]
    fmt = f'bv*[height<={resolution}][ext=mp4][vcodec~="^((he|a)vc|h26[45])"]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b'
    ydl_opts = {
        'format': fmt,
        'outtmpl': 'Videos/%(id)s.%(ext)s',
        # 'progress_hooks': [progress],
        'quiet': True,
        'no_warnings': True
    }
    with YoutubeDL(ydl_opts) as ydl:
        file_info = ydl.extract_info(url, download=True)
        return file_info


async def delete_file(file_name: str):
    os.remove(f'./Videos/{file_name}')
