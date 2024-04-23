import os

from yt_dlp import YoutubeDL


def download_file(url: str, format_id: str):
    """Загружает видео в папку, и возвращает информация о файле и видео.
    Либо вернет исключение"""
    if format_id == 'audio':
        ydl_opts = {'format': 'm4a/bestaudio/best',
                    'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'm4a'}],
                    'quiet': True,
                    'no_warnings': True}
    else:
        ydl_opts = {'format': f'bv*[height<={format_id}]+ba/b',
                    'outtmpl': 'Videos/%(id)s.%(ext)s',
                    # 'progress_hooks': [progress],
                    'quiet': True,
                    'no_warnings': True}
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
    """Возвращает список доступных форматов для скачивания (под индексом 4). Исключаются
    форматы без видео или аудио. Или вернет исключение yt_dlp.utils.DownloadError.
    Под индексами 0, 1, 2, 3 - Общая информация о видео.
    [{format_id: int, format_note: str, format: str}, ...]
    [{format_id: 22, format_note: 720p, format: 22 - 1280x720 (720p)}, ...]"""
    ydl_opts = {}
    try:
        with YoutubeDL(ydl_opts) as ydl:
            meta = ydl.extract_info(url, download=False)
            formats = meta.get('formats')
    except Exception as e:
        return e
    required_formats = list()
    title = meta.get('title')
    thumbnail = meta.get('thumbnail')
    description = meta.get('description')
    duration = meta.get('duration_string')
    for f in formats:
        video_codec = f.get('vcodec')
        audio_codec = f.get('acodec')
        format_id = f.get('format_id')
        format_note = f.get('format_note')
        format_full = f.get('format')
        required_formats.append({'format_id': format_id, 'format_note': format_note, 'format': format_full})
        # if video_codec != 'none' and audio_codec != 'none':
        #     format_id = f.get('format_id')
        #     format_note = f.get('format_note')
        #     format_full = f.get('format')
        #     required_formats.append({'format_id': format_id, 'format_note': format_note, 'format': format_full})
    return title, thumbnail, description, duration, required_formats


def delete_video(file_name):
    """Удаляет файл"""
    try:
        os.remove(f'./Videos/{file_name}')
    except OSError:
        pass
