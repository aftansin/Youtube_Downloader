from aiogram import Router, F, Bot
from aiogram.types import Message, FSInputFile
from aiogram.utils.chat_action import ChatActionSender

from middlewares import RegistrationCheck
from utils.ytdlp_functions import download_file, delete_file

video_router = Router()
video_router.message.middleware(RegistrationCheck())

USER_FORMAT = '1080'


@video_router.message(F.text.startswith('https://www.youtube.com/') |
                      F.text.startswith('https://youtu.be/') |
                      F.text.startswith('https://youtube.com/'))
async def send_file(message: Message, bot: Bot) -> None:
    async with ChatActionSender.upload_video(chat_id=message.chat.id, bot=bot):
        status_msg = await message.answer('Downloading... Wait.')
        url = message.text
        try:
            video_data = download_file(url, USER_FORMAT)
            file_name = f'{video_data.get("id")}.{video_data.get("ext")}'
            title = video_data.get('title')
            await status_msg.edit_text('Uploading... Wait.')
            video_from_pc = FSInputFile(f"Videos/{file_name}")
            await message.reply_video(video_from_pc, caption=title)
        except Exception as e:
            await message.reply(str(e))
        finally:
            await status_msg.delete()
            delete_file(file_name)
