import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ContentType, Message, FSInputFile
from aiogram import Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import F
from deep_translator import GoogleTranslator
import asyncio
from config import TOKEN
from aiogram.client.bot import DefaultBotProperties
from gtts import gTTS

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создаем экземпляры бота и диспетчера
bot = Bot(token=TOKEN, properties=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

# Убедитесь, что папка 'img' существует
if not os.path.exists('img'):
    os.makedirs('img')

# Убедитесь, что папка 'voices' существует
if not os.path.exists('voices'):
    os.makedirs('voices')

# Создаем роутер для обработчиков
router = Router()

@router.message(Command('photo'))
async def send_photo_welcome(message: Message):
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
async def send_start_welcome(message: Message):
    await message.reply("Привет! Отправь мне текст на русском, и я переведу его на английский.")

async def translate_text(text: str, src: str, dest: str) -> str:
    translator = GoogleTranslator(source=src, target=dest)
    return translator.translate(text)

@router.message(Command('trans'))
async def translate_and_send_voice(message: Message):
    # Получаем текст для перевода, убирая команду
    text_to_translate = message.text[len('/trans '):]

    if text_to_translate:
        # Переводим текст с русского на английский
        translated_text = await translate_text(text_to_translate, 'ru', 'en')

        # Отправляем переведенный текст обратно пользователю
        await message.reply(f"Переведенный текст: {translated_text}")

        # Создаем голосовое сообщение из переведенного текста
        voice_file = f'voices/{message.message_id}.ogg'
        tts = gTTS(text=translated_text, lang='en')
        tts.save(voice_file)

        # Отправляем голосовое сообщение
        voice = FSInputFile(voice_file)
        await message.answer_voice(voice=voice)
    else:
        await message.reply("Пожалуйста, введите текст для перевода после команды /trans.")

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

