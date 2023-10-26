from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, URLInputFile, CallbackQuery, FSInputFile
from aiogram.utils.chat_action import ChatActionSender

from utils import list_formats, download_video, delete_video


video_router = Router()


def get_keyboard(formats, url):
    """Генерация инлайн кнопок доступных для скачивания форматов."""
    buttons = []
    for data in formats:
        txt = data.get('format')[5:]
        call_data = data.get('format_id') + f' {url}'
        buttons.append([InlineKeyboardButton(text=txt, callback_data=call_data)])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


@video_router.message(F.text.startswith('https://www.youtube.com/') | F.text.startswith('https://youtu.be/'))
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
        description = video_data[2]
        duration = video_data[3]
        formats = video_data[4]
        txt = f'{title}\n<u>Duration: {duration}</u>'
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
        quality_id, url = action[0], action[1]
        try:
            video_data = download_video(url, quality_id)
            file_name = video_data[0]
            title = video_data[1]
            await status_msg.edit_text('Uploading... Wait.')
            video_from_pc = FSInputFile(f"Videos/{file_name}")
            await callback.message.answer_video(video_from_pc, caption=title)
        except Exception as e:
            await callback.message.reply(str(e))
        finally:
            await status_msg.delete()
            delete_video(file_name)
