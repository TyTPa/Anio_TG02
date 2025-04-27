import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ContentType, Message
from aiogram import Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import F
from googletrans import Translator
import asyncio
from config import TOKEN
from aiogram.client.bot import DefaultBotProperties



# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создаем экземпляры бота и диспетчера
bot = Bot(token=TOKEN, properties=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

# Убедитесь, что папка 'img' существует
if not os.path.exists('img'):
    os.makedirs('img')
# Создаем экземпляр переводчика
translator = Translator()
# Создаем роутер для обработчиков
router = Router()

@router.message(Command('photo'))
async def send_welcome(message: Message):
    await message.reply("Привет! Отправь мне фото, и я сохраню его.")

@router.message(F.content_type == ContentType.PHOTO)
async def handle_photo(message: Message, bot: Bot):
    # Выберите фотографию с наибольшим разрешением
    photo = message.photo[-1]
    # Скачайте файл
    file_path = f'img/{photo.file_id}.jpg'
    await bot.download(photo, destination=file_path)
    await message.reply(f'Фото сохранено как {photo.file_id}.jpg')

@router.message(Command('start'))
async def send_welcome(message: Message):
    await message.reply("Привет! Отправь мне текст на русском, и я переведу его на английский.")

@router.message(F.text)
async def translate_text(message: Message):
    # Переводим текст с русского на английский
    translation = translator.translate(message.text, src='ru', dest='en')
    await message.reply(translation.text)


@router.message(Command("voice"))
async def send_voice_message(message: Message):
    # Путь к голосовому файлу в формате OGG
    voice_file = 'path/to/your/voice_file.ogg'
    # Отправка голосового сообщения
    voice = types.input_file.InputFile(voice_file)
    await message.answer_voice(voice=voice)

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

