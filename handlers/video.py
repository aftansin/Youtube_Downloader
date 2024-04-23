from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, URLInputFile, CallbackQuery, FSInputFile
from aiogram.utils.chat_action import ChatActionSender

from middlewares import RegistrationCheck
from utils import list_formats, download_file, delete_video


video_router = Router()
video_router.message.middleware(RegistrationCheck())


def get_keyboard(formats, url):
    """Генерация инлайн кнопок доступных для скачивания форматов."""
    buttons = [[InlineKeyboardButton(text='audio only', callback_data=f'audio {url}')]]
    for format_data in formats:
        callback_data = format_data + f' {url}'
        buttons.append([InlineKeyboardButton(text=format_data, callback_data=callback_data)])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


@video_router.message(F.text.startswith('https://www.youtube.com/') |
                      F.text.startswith('https://youtu.be/') |
                      F.text.startswith('https://youtube.com/'))
async def get_video_format_handler(message: Message, bot: Bot) -> None:
    """Отправка сообщения доступных для скачивания форматов видео."""
    async with ChatActionSender.typing(chat_id=message.chat.id, bot=bot):
        status_msg = await message.answer('Getting info... Wait.')
        url = message.text
        video_data = list_formats(url)
        if isinstance(video_data, Exception):  # Если при обработке выскочило исключение, то отправим ошибку
            await status_msg.delete()
            await message.answer('Something went wrong.. Try again')
            return
        title = video_data[0]
        thumbnail = video_data[1]
        duration = video_data[3]
        formats = video_data[4]
        txt = f'{title}\nDuration: {duration}'
        await message.reply_photo(URLInputFile(thumbnail),
                                  caption=txt,
                                  reply_markup=get_keyboard(formats, url))
        await status_msg.delete()


@video_router.callback_query(F.data)
async def download_video_by_callback(callback: CallbackQuery):
    """Обработка callback сообщения, загрузка и отправка видео пользователю."""
    async with ChatActionSender.upload_video(chat_id=callback.message.chat.id, bot=callback.bot):
        status_msg = await callback.message.answer('Downloading... Wait.')
        await callback.answer()
        action = callback.data.split()
        quality_id, url = action[0][:-1], action[1]
        try:
            video_data = download_file(url, quality_id)
            file_name = video_data[0]
            title = video_data[1]
            await status_msg.edit_text('Uploading... Wait.')
            video_from_pc = FSInputFile(f"Videos/{file_name}")
            await callback.message.answer_video(video_from_pc, caption=title)
            await callback.message.delete()
        except Exception as e:
            await callback.message.reply(str(e))
        finally:
            await status_msg.delete()
            delete_video(file_name)
