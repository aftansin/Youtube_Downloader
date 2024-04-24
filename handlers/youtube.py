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


def download_file(url: str, format_id: str):
    resolution = format_id[:-1]
    round(time.time() * 1000)
    ydl_opts = {
        'format': (f'bv*[height<={resolution}][ext=mp4][vcodec~="^((he|a)vc|h26[45])"]+ba[ext=m4a]/b[ext=mp4]'
                   f' / bv*+ba/b'),
        'outtmpl': 'Videos/%(id)s.%(ext)s',
        # 'progress_hooks': [progress],
        'quiet': True,
        'no_warnings': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        file_info = ydl.extract_info(url, download=True)
        return file_info


@video_router.message(F.text.startswith('https://www.youtube.com/') |
                      F.text.startswith('https://youtu.be/') |
                      F.text.startswith('https://youtube.com/'))
async def send_video(message: Message, bot: Bot, db_session) -> None:
    db_user = await get_user(message.from_user.id, db_session)
    status_msg = await message.answer('Downloading... Wait.')
    url = message.text
    res = db_user.quality[:-1]  # user requested video resolution
    file_name = round(time.time() * 1000)  # имя файла возьмем текущее время
    ydl_opts = {
        'format': (f'bv*[height<={res}][ext=mp4][vcodec~="^((he|a)vc|h26[45])"]+ba[ext=m4a]/b[ext=mp4]'
                   f' / bv*+ba/b'),
        'outtmpl': f'Videos/{file_name}.%(ext)s',
        # 'progress_hooks': [progress],
        'quiet': True,
        'no_warnings': True
        }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = info['requested_downloads'][0]['filepath']
        try:
            await status_msg.edit_text('Sending file to Telegram...')
            try:
                async with ChatActionSender.upload_video(message.chat.id, bot):
                    await message.reply_video(
                        video=FSInputFile(file_path),
                        duration=info.get('duration'),
                        width=info.get('width'),
                        height=info.get('height'),
                        caption=info.get('title'))
            except Exception as e:
                await message.answer(f"Couldn't send file\n{e}")
                for file in info['requested_downloads']:
                    os.remove(file['filepath'])
            else:
                for file in info['requested_downloads']:
                    os.remove(file['filepath'])
            finally:
                await status_msg.delete()
        except Exception as e:
            if isinstance(e, yt_dlp.utils.DownloadError):
                await message.answer(f'Invalid URL\n{e}')
            else:
                await message.answer(f'Error downloading your video\n{e}')
            for file in os.listdir('outputs'):
                if file.startswith(str(file_name)):
                    os.remove(f'Videos/{file}')
