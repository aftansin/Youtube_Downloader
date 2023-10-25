import os

from yt_dlp import YoutubeDL


def download_video(url: str, format_id):
    ydl_opts = {'format': str(format_id), 'outtmpl': 'Videos/%(id)s.%(ext)s'}
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = f'{info.get("id")}.{info.get("ext")}'
            title = info.get('title')
            duration_string = info.get('duration_string')
            resolution_info = info.get('format')
            thumbnail_url = info.get('thumbnail')
            return file_name, title, duration_string, resolution_info, thumbnail_url
    except Exception as e:
        return e


def list_formats(url):
    """Возвращает список доступных форматов для скачивания. Исключаются
    форматы без видео или аудио. Или вернет исключение yt_dlp.utils.DownloadError.
    [{format_id: int, format_note: str, format: str}, ...]
    [{format_id: 22, format_note: 720p, format: 22 - 1280x720 (720p)}, ...]"""
    ydl_opts = {}
    try:
        with YoutubeDL(ydl_opts) as ydl:
            meta = ydl.extract_info(url, download=False)
            formats = meta.get('formats')
    except Exception as e:
        return e
    result = list()
    for f in formats:
        video_codec = f.get('vcodec')
        audio_codec = f.get('acodec')
        if video_codec != 'none' and audio_codec != 'none':
            format_id = f.get('format_id')
            format_note = f.get('format_note')
            format_full = f.get('format')
            result.append({'format_id': format_id, 'format_note': format_note, 'format': format_full})
    return result


def delete_video(file_name):
    os.remove(f'./Videos/{file_name}')
