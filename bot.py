import sqlite3

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor


bot_token = 'YOUR_TOKEN'
bot = Bot(token=bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class RegistrationForm(StatesGroup):
    name = State()
    nickname = State()


@dp.message_handler(Command('start', prefixes='!/'), state='*')
async def start(message: types.Message):
    await RegistrationForm.name.set()
    await message.answer('What is your name?')


@dp.message_handler(state=RegistrationForm.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await RegistrationForm.next()
    await message.answer('What is your nickname?')


@dp.message_handler(state=RegistrationForm.nickname)
async def process_nickname(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['nickname'] = message.text
        
    user_profile_photos = await bot.get_user_profile_photos(message.from_user.id)
    if not user_profile_photos.photos:
        url = None
    else:
        file_id = user_profile_photos.photos[0][-1].file_id
        file = await bot.get_file(file_id)
        resp = await file.download()
        url = resp.name

    user_data = {
        'name': data['name'],
        'nickname': data['nickname'],
        'photo': url,
        'telegram_id': message.from_user.id
    }
    save_user_data(user_data)

    await message.answer(f'You can access your account with this id: {message.from_user.id}')


def save_user_data(user_data):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  nickname TEXT NOT NULL,
                  photo TEXT,
                  telegram_id INTEGER NOT NULL)''')
    c.execute('''INSERT INTO users (name, nickname, photo, telegram_id)
                 VALUES (?, ?, ?, ?)''', (user_data['name'], user_data['nickname'], user_data['photo'], user_data['telegram_id']))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

