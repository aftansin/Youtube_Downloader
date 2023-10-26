from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from middlewares import RegistrationCheck


start_router = Router()
start_router.message.middleware(RegistrationCheck())


@start_router.message(Command("start"))
async def command_start_handler(message: Message) -> None:

    await message.answer(f"Hi, <b>{message.from_user.full_name}!</b>\n"
                         f"Send me the link you want to download..")
