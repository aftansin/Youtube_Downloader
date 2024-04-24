from aiogram import Router, F, Bot
from aiogram.types import Message, FSInputFile
from aiogram.utils.chat_action import ChatActionSender

from db.requests import get_user
from middlewares import RegistrationCheck
from utils.ytdlp_functions import download_file, delete_file

video_router = Router()
video_router.message.middleware(RegistrationCheck())


@video_router.message(F.text.startswith('https://www.youtube.com/') |
                      F.text.startswith('https://youtu.be/') |
                      F.text.startswith('https://youtube.com/'))
async def send_file(message: Message, bot: Bot, db_session) -> None:
    db_user = await get_user(message.from_user.id, db_session)
    async with ChatActionSender.upload_video(chat_id=message.chat.id, bot=bot):
        status_msg = await message.answer('Downloading... Wait.')
        url = message.text
        try:
            all_video_data = download_file(url, db_user.quality)
            file_name = f'{all_video_data.get("id")}.{all_video_data.get("ext")}'
            title = all_video_data.get('title')
            duration = all_video_data.get('duration')
            width = all_video_data.get('width')
            height = all_video_data.get('height')
            thumbnail = all_video_data.get('thumbnail')
            caption = all_video_data.get('caption')
            print(duration)
            print(width)
            print(height)
            # print(thumbnail)
            print(caption)
            await status_msg.edit_text('Uploading... Wait.')
            video_from_pc = FSInputFile(f"Videos/{file_name}")
            await message.reply_video(
                video=video_from_pc,
                duration=duration,
                width=width,
                height=height,
                # thumbnail=thumbnail,
                caption=title)
        except Exception as e:
            await message.reply(str(e))
        finally:
            await status_msg.delete()
            delete_file(file_name)
