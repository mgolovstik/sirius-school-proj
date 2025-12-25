import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import os
from main import predict
from dotenv import load_dotenv
from pydantic import ValidationError
from schemas import AdvertInput, AdvertOutput

assert load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Определение состояний (FSM - Finite State Machine)
class Form(StatesGroup):
    lat = State()
    lng = State()
    square = State()
    floor = State()


# Обработчик команды /chlat
@dp.message(Command("chlat"))
async def cmd_chreq(message: types.Message, state: FSMContext):
    await message.answer("Введите lat")
    await state.set_state(Form.lat)
@dp.message(Form.lat)
async def change_lat(message: types.Message, state: FSMContext):
    await state.update_data(lat=message.text)
    await state.set_state(None)

# Обработчик команды /chlng
@dp.message(Command("chlng"))
async def cmd_chreq(message: types.Message, state: FSMContext):
    await message.answer("Введите lng")
    await state.set_state(Form.lng)
@dp.message(Form.lng)
async def change_lon(message: types.Message, state: FSMContext):
    await state.update_data(lng=message.text)
    await state.set_state(None)

# Обработчик команды /chsquare
@dp.message(Command("chsquare"))
async def cmd_chreq(message: types.Message, state: FSMContext):
    await message.answer("Введите общую площадь")
    await state.set_state(Form.square)
@dp.message(Form.square)
async def change_lat(message: types.Message, state: FSMContext):
    await state.update_data(square=message.text)
    await state.set_state(None)

# Обработчик команды /chfloor
@dp.message(Command("chfloor"))
async def cmd_chfloor(message: types.Message, state: FSMContext):
    await message.answer("Введите этаж")
    await state.set_state(Form.floor)
@dp.message(Form.floor)
async def change_lat(message: types.Message, state: FSMContext):
    await state.update_data(floor=message.text)
    await state.set_state(None)

def convert_data_to_request(data: dict):
    lat = data.get("lat", 0)
    lon = data.get("lng", 0)
    square = data.get("square", 0)
    metro_dist = data.get("metro_dist", 0.0)
    floor = data.get("floor", 0)
    author_type = data.get("author_type", "Частное лицо")
    object_type = data.get("object_type", "Торговое / Свободного назначения")
    metro_district = data.get("metro_district", "Неизвестно")
    return {
        'lat': float(lat),
        'lng': float(lon),
        'Общая площадь': float(square),
        'Расстояние до метро, км': float(metro_dist),
        'Этаж': int(floor),
        'Тип автора': str(author_type),
        'Вид объекта': str(object_type),
        'Метро/Район': str(metro_district)
    }

@dp.message(Command("req"))
async def cmd_req(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data = convert_data_to_request(data)
    str_data = str(data)
    await message.answer(str_data)

@dp.message(Command("predict"))
async def cmd_predict(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data = convert_data_to_request(data)
    try:
        data = AdvertInput(**data)
    except ValidationError as e:
        print(e)
        await message.answer("Не все данные введены корректно. Используйте /req, чтобы проверить их")
        return
    ans = await predict(data)
    ans = ans.model_dump()["pred"]
    await message.answer(str(ans))

# Основная функция запуска бота
async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())