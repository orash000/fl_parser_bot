import asyncio
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

from app.habr_parser import fetch_and_format_tasks


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("🔍 Начинаем отслеживание новых заказов...", parse_mode="HTML")

    while True:
        tasks = fetch_and_format_tasks()

        if tasks:
            for task in tasks:
                await message.answer(task, parse_mode="HTML")
        else:
            await message.answer("🔍 Заказов нет", parse_mode="HTML")

        await asyncio.sleep(300)


@router.message(Command('update'))
async def cmd_refetch(message: Message):
    await message.answer("🔍 Обновление заказов...", parse_mode="HTML")
    tasks = fetch_and_format_tasks()

    if tasks:
        for task in tasks:
            await message.answer(task, parse_mode="HTML")
    else:
        await message.answer("🔍 Заказов нет", parse_mode="HTML")
