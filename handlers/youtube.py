import asyncio
import os
import time

import yt_dlp
from aiogram import Router, F, Bot
from aiogram.types import Message, FSInputFile
from aiogram.utils.chat_action import ChatActionSender

from db.requests import get_user
from middlewares import RegistrationCheck


video_router = Router()
video_router.message.middleware(RegistrationCheck())


async def download_video_async(status_msg, url: str, resolution: str):
    file_name = round(time.time() * 1000)
    ydl_opts = {
        'format': (f'bv*[height<={resolution}][ext=mp4][vcodec~="^((he|a)vc|h26[45])"]+ba[ext=m4a]/b[ext=mp4]'
                   f' / bv*+ba/b'),
        'outtmpl': f'media/{file_name}.%(ext)s',
        'progress_hooks': [lambda d: status_msg.edit_text(
            f"{round(d['downloaded_bytes'] / d['total_bytes'] * 100, 2)}%")],
        'quiet': True,
        'no_warnings': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        file_info = ydl.extract_info(url, download=True)
        return [file_name, file_info]


@video_router.message(F.text.startswith('https://www.youtube.com/') |
                      F.text.startswith('https://youtu.be/') |
                      F.text.startswith('https://youtube.com/'))
async def send_video(message: Message, bot: Bot, db_session):
    db_user = await get_user(message.from_user.id, db_session)
    status_msg = await message.answer('Downloading... Wait.')
    url = message.text
    user_resolution = db_user.quality[:-1]  # user requested video resolution
    info = await download_video_async(status_msg, url, user_resolution)
    file_name = info[0]
    file_info = info[1]
    file_path = file_info['requested_downloads'][0]['filepath']
    try:
        await status_msg.edit_text('Sending file to Telegram...')
        try:
            async with ChatActionSender.upload_video(message.chat.id, bot):
                await message.reply_video(
                    video=FSInputFile(file_path),
                    duration=file_info.get('duration'),
                    width=file_info.get('width'),
                    height=file_info.get('height'),
                    caption=file_info.get('title'))
        except Exception as e:
            await message.answer(f"Couldn't send file\n{e}")
            for file in file_info['requested_downloads']:
                os.remove(file['filepath'])
        else:
            for file in file_info['requested_downloads']:
                os.remove(file['filepath'])
        finally:
            await status_msg.delete()
    except Exception as e:
        if isinstance(e, yt_dlp.utils.DownloadError):
            await message.answer(f'Invalid URL\n{e}')
        else:
            await message.answer(f'Error downloading your video\n{e}')
        for file in os.listdir('media'):
            if file.startswith(file_name):
                os.remove(f'media/{file}')
