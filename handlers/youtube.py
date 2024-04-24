import os

from aiogram import Router, F, Bot
from aiogram.types import Message, FSInputFile
from aiogram.utils.chat_action import ChatActionSender
from yt_dlp import YoutubeDL

from db.requests import get_user
from middlewares import RegistrationCheck


video_router = Router()
video_router.message.middleware(RegistrationCheck())


def download_file(url: str, format_id: str):
    resolution = format_id[:-1]
    ydl_opts = {
        'format': (f'bv*[height<={resolution}][ext=mp4][vcodec~="^((he|a)vc|h26[45])"]+ba[ext=m4a]/b[ext=mp4]'
                   f' / bv*+ba/b'),
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


@video_router.message(F.text.startswith('https://www.youtube.com/') |
                      F.text.startswith('https://youtu.be/') |
                      F.text.startswith('https://youtube.com/'))
async def send_video(message: Message, bot: Bot, db_session) -> None:
    db_user = await get_user(message.from_user.id, db_session)
    status_msg = await message.answer('Downloading... Wait.')
    url = message.text
    try:
        all_video_data = download_file(url, db_user.quality)
        file_name = f'{all_video_data.get("id")}.{all_video_data.get("ext")}'
        title = all_video_data.get('title')
        file_from_pc = FSInputFile(f"Videos/{file_name}")
        duration = all_video_data.get('duration')
        width = all_video_data.get('width')
        height = all_video_data.get('height')
        async with ChatActionSender.upload_video(message.chat.id, bot):
            await message.reply_video(
                video=file_from_pc,
                duration=duration,
                width=width,
                height=height,
                caption=title)
        await delete_file(file_name)
    except Exception as e:
        await message.answer(str(e))
    finally:
        await status_msg.delete()
