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
    status_msg = await message.answer('Downloading... Wait.')
    url = message.text
    # отправка аудио, если выбран данный формат
    if db_user.quality == 'audio':
        try:
            all_video_data = download_file(url, db_user.quality)
            file_name = f'{all_video_data.get("id")}.{all_video_data.get("ext")}'
            title = all_video_data.get('title')
            await status_msg.edit_text('Uploading... Wait.')
            audio_from_pc = FSInputFile(f"Videos/{file_name}")
            async with ChatActionSender.upload_document(message.chat.id, bot):
                await message.reply_audio(
                    audio=audio_from_pc,
                    caption=title)
            await delete_file(file_name)
        except Exception as e:
            await message.reply(f'ошибка в аудио\n{str(e)}')
        finally:
            await status_msg.delete()
        return

    # отправка видео файла
    try:
        all_video_data = download_file(url, db_user.quality)
        file_name = f'{all_video_data.get("id")}.{all_video_data.get("ext")}'
        title = all_video_data.get('title')
        duration = all_video_data.get('duration')
        width = all_video_data.get('width')
        height = all_video_data.get('height')
        await status_msg.edit_text('Uploading... Wait.')
        video_from_pc = FSInputFile(f"Videos/{file_name}")
        async with ChatActionSender.upload_video(message.chat.id, bot):
            await message.reply_video(
                video=video_from_pc,
                duration=duration,
                width=width,
                height=height,
                caption=title)
        await delete_file(file_name)
    except Exception as e:
        await message.reply(f'ошибка в видео\n{str(e)}')
    finally:
        await status_msg.delete()
