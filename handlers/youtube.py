import asyncio
import os
import shutil
import time

import yt_dlp
from aiogram import Router, F, Bot
from aiogram.types import Message, FSInputFile
from aiogram.utils.chat_action import ChatActionSender
from hurry.filesize import size, alternative

from db.requests import get_user
from middlewares import RegistrationCheck

video_router = Router()
video_router.message.middleware(RegistrationCheck())

# Глобальная очередь и статус обработки
download_queue = asyncio.Queue()
is_processing = False
# Словарь для хранения сообщений о статусе для каждого пользователя
status_messages = {}


# Запускаем обработчик очереди при старте
async def start_queue_processor():
    """Запустить обработчик очереди"""
    asyncio.create_task(process_queue())


async def process_queue():
    """Функция для обработки очереди"""
    global is_processing

    while True:
        task_data = await download_queue.get()
        is_processing = True

        try:
            await task_data['task_func'](*task_data['args'], **task_data['kwargs'])
        except Exception as e:
            if task_data.get('message'):
                try:
                    await task_data['message'].answer(f"❌ Ошибка обработки: {str(e)}")
                except:
                    pass
        finally:
            # Удаляем сообщение о статусе очереди после завершения задачи
            if task_data.get('message'):
                user_id = task_data['message'].from_user.id
                if user_id in status_messages:
                    try:
                        await status_messages[user_id].delete()
                        del status_messages[user_id]
                    except:
                        pass

            download_queue.task_done()
            is_processing = False


async def add_to_queue(task_func, *args, **kwargs):
    """Добавление задачи в очередь"""
    task_data = {
        'task_func': task_func,
        'args': args,
        'kwargs': kwargs
    }

    # Если есть message в kwargs, добавляем его в task_data
    if 'message' in kwargs:
        task_data['message'] = kwargs['message']

    await download_queue.put(task_data)

    # Возвращаем позицию в очереди
    return download_queue.qsize()


async def get_file_size(url, user_resolution):
    ydl_opts = {
        'format': (f'bv*[height<={user_resolution}][ext=mp4][vcodec~="^((he|a)vc|h26[45])"]+ba[ext=m4a]/b[ext=mp4]'
                   f' / bv*+ba/b'),
        'quiet': True,
        'no_warnings': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        file_info = ydl.extract_info(url, download=False)
        original_url = file_info.get('original_url')
        filesize_approx = file_info.get('filesize_approx')
        return original_url, filesize_approx


async def send_video_to_user(file_info, file_name, file_path, message, status_msg, bot: Bot):
    try:
        await status_msg.edit_text('⬆️ Отправляю в Telegram...')
        try:
            async with ChatActionSender.upload_video(message.chat.id, bot):
                await message.answer_video(
                    video=FSInputFile(file_path),
                    duration=file_info.get('duration'),
                    width=file_info.get('width'),
                    height=file_info.get('height'),
                    caption=file_info.get('title'),
                    disable_notification=True)
        except Exception as e:
            await message.answer(f"Couldn't send file\n{e}")
            for file in file_info['requested_downloads']:
                os.remove(file['filepath'])
        else:
            for file in file_info['requested_downloads']:
                os.remove(file['filepath'])
        finally:
            await status_msg.delete()
            await message.delete()
    except Exception as e:
        if isinstance(e, yt_dlp.utils.DownloadError):
            await message.answer(f'Invalid URL\n{e}')
        else:
            await message.answer(f'Ошибка!\n{e}')
        for file in os.listdir('media'):
            if file.startswith(file_name):
                os.remove(f'media/{file}')


def download_youtube_video(url: str, resolution: str):
    file_name = round(time.time() * 1000)
    ydl_opts = {
        'format': (f'bv*[height<={resolution}][ext=mp4][vcodec~="^((he|a)vc|h26[45])"]+ba[ext=m4a]/b[ext=mp4]'
                   f' / bv*+ba/b'),
        'outtmpl': f'media/{file_name}.%(ext)s',
        'quiet': True,
        'no_warnings': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        file_info = ydl.extract_info(url, download=True)
        return [file_name, file_info]


def download_tiktok_video(url: str):
    file_name = round(time.time() * 1000)
    ydl_opts = {
        'outtmpl': f'media/{file_name}.%(ext)s',
        'quiet': True,
        'no_warnings': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        file_info = ydl.extract_info(url, download=True)
        return [file_name, file_info]


async def download_youtube_video_async(url: str, resolution: str):
    loop = asyncio.get_event_loop()
    info = await loop.run_in_executor(None, download_youtube_video, url, resolution)
    file_name, file_info = info[0], info[1]
    return [file_name, file_info]


async def download_tiktok_video_async(url: str):
    loop = asyncio.get_event_loop()
    info = await loop.run_in_executor(None, download_tiktok_video, url)
    file_name, file_info = info[0], info[1]
    return [file_name, file_info]


async def youtube_video_processor(message: Message, bot: Bot, db_session):
    """Обработчик для YouTube видео (будет вызываться из очереди)"""
    db_user = await get_user(message.from_user.id, db_session)
    url = message.text
    user_resolution = db_user.quality[:-1]  # user requested video resolution

    original_url, filesize_approx = await get_file_size(url, user_resolution)
    free_space = shutil.disk_usage("/")[2]
    if filesize_approx * 1.5 < free_space:
        status_msg = await message.answer(f'⬇️ Скачиваю {size(filesize_approx)} ... Ждите.',
                                          disable_notification=True)
        info = await download_youtube_video_async(url, user_resolution)
        file_name = info[0]
        file_info = info[1]
        file_path = file_info['requested_downloads'][0]['filepath']
        await send_video_to_user(file_info, file_name, file_path, message, status_msg, bot)
    else:
        await message.answer(
            f'Слишком большой файл {size(filesize_approx, system=alternative)} ... Уменьшите качество видео.',
            disable_notification=True)


async def tiktok_video_processor(message: Message, bot: Bot):
    """Обработчик для TikTok видео (будет вызываться из очереди)"""
    status_msg = await message.answer('⬇️ Downloading... Wait.', disable_notification=True)
    info = await download_tiktok_video_async(message.text)
    file_name = info[0]
    file_info = info[1]
    file_path = file_info['requested_downloads'][0]['filepath']
    await send_video_to_user(file_info, file_name, file_path, message, status_msg, bot)


@video_router.message(F.text.regexp(r'(?:https?:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?\/?.*'))
async def youtube_video(message: Message, bot: Bot, db_session):
    """Обработчик сообщений YouTube"""
    # Добавляем задачу в очередь
    queue_position = await add_to_queue(
        youtube_video_processor,
        message=message,
        bot=bot,
        db_session=db_session
    )

    # Сохраняем сообщение о статусе для последующего удаления
    if queue_position >= 1:
        status_msg = await message.answer(
            f"📋 Ваш запрос добавлен в очередь. Позиция: {queue_position+1}\n"
            f"⏳ Обработка начнется после завершения текущих задач.",
            disable_notification=True
        )
    else:
        status_msg = await message.answer(
            "🔄 Начинаю обработку вашего запроса...",
            disable_notification=True
        )

    # Сохраняем сообщение о статусе в словарь
    status_messages[message.from_user.id] = status_msg


@video_router.message(F.text.regexp(r'^.*https:\/\/(?:m|www|vm)?\.?tiktok\.com\/((?:.*\b(?:('
                                    r'?:usr|v|embed|user|video)\/|\?shareId=|\&item_id=)(\d+))|\w+)'))
async def tiktok_video(message: Message, bot: Bot):
    """Обработчик сообщений TikTok"""
    # Добавляем задачу в очередь
    queue_position = await add_to_queue(
        tiktok_video_processor,
        message=message,
        bot=bot
    )

    # Сохраняем сообщение о статусе для последующего удаления
    if queue_position >= 1:
        status_msg = await message.answer(
            f"📋 Ваш запрос добавлен в очередь. Позиция: {queue_position+1}\n"
            f"⏳ Обработка начнется после завершения текущих задач.",
            disable_notification=True
        )
    else:
        status_msg = await message.answer(
            "🔄 Начинаю обработку вашего запроса...",
            disable_notification=True
        )

    # Сохраняем сообщение о статусе в словарь
    status_messages[message.from_user.id] = status_msg


@video_router.message(F.text)
async def any_video(message: Message):
    await message.answer(f'Function is in progress. Sorry')