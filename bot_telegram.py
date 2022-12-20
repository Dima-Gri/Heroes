from aiogram import types
from aiogram.utils import executor
from create_bot import dp
from keyboards.setting_keybords import kb_start
from setting_game import settings
from aiogram.dispatcher.filters import Text

async def on_startup(_):
    print('Бот запущен')

@dp.message_handler(commands="start")
async def cm_start(message: types.Message):
    print(message.from_user.id, type(message.from_user.id))
    await message.reply("Ты кто?", reply_markup=kb_start)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
