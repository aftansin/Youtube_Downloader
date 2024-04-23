import os

from yt_dlp import YoutubeDL


def download_file(url: str, format_id: str):
    if format_id == 'audio':
        ydl_opts = {'format': 'm4a/bestaudio/best',
                    'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'm4a'}],
                    'quiet': True,
                    'no_warnings': True}
    else:
        ydl_opts = {'format': f'bv*[height<={format_id}][ext=mp4][vcodec~="^((he|a)vc|h26[45])"]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b',
                    'outtmpl': 'Videos/%(id)s.%(ext)s',
                    # 'progress_hooks': [progress],
                    'quiet': True,
                    'no_warnings': True}
    try:
        with YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=True)
    except Exception as e:
        return e


def delete_file(file_name: str):
    try:
        os.remove(f'./Videos/{file_name}')
    except OSError:
        pass
