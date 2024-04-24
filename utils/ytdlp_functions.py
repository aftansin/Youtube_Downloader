import os

from yt_dlp import YoutubeDL


def download_file(url: str, format_id: str):
    if format_id == 'audio':
        ydl_opts = {'format': 'm4a/bestaudio/best',
                    'outtmpl': 'Videos/%(id)s.%(ext)s',
                    'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'm4a'}],
                    'quiet': True,
                    'no_warnings': True}
    else:
        res_id = format_id[:-1]
        ydl_opts = {'format': f'bv*[height<={res_id}][ext=mp4][vcodec~="^((he|a)vc|h26[45])"]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b',
                    'outtmpl': 'Videos/%(id)s.%(ext)s',
                    # 'progress_hooks': [progress],
                    'quiet': True,
                    'no_warnings': True}
    with YoutubeDL(ydl_opts) as ydl:
        file_info = ydl.extract_info(url, download=True)
        return file_info


async def delete_file(file_name: str):
    os.remove(f'./Videos/{file_name}')
