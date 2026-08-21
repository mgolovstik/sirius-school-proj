from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import TargetEncoder
class OrdinalByTargetEncoder(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.te = TargetEncoder(target_type="continuous", random_state=10)

    def fit(self, X, y):
        self.te = self.te.fit(X, y)
        
    def transform(self, X, y=None):
        X_copy = X.copy()
        for i, col in enumerate(X.columns):
            cat_dict = dict(zip(self.te.categories_[i], self.te.encodings_[i]))
            ordinal_categories = sorted(cat_dict, key=cat_dict.get)
            ordinal_mapping = dict(zip(ordinal_categories, range(len(ordinal_categories))))
            X_copy[col] = X_copy[col].map(ordinal_mapping)
            X_copy[col] = X_copy[col].fillna(len(ordinal_categories) // 2)
        return X_copy

    def fit_transform(self, X, y):
        self.fit(X, y)
        return self.transform(X)

    def set_output(self, *, transform=None):
        """Scikit-learn 1.2+ requirement"""
        return self

import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import os
from main import predict
from dotenv import load_dotenv
from pydantic import ValidationError
from schemas import AdvertInput, AdvertOutput
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from var import BOT_TOKEN

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
    chdist = State()


change_req_buttons = [
    [InlineKeyboardButton(text="Изменить широту (lat)", callback_data="chlat"), 
    InlineKeyboardButton(text="Изменить долготу (lng)", callback_data="chlng")],
    [InlineKeyboardButton(text="Изменить общую площадь", callback_data="chsquare"),
    InlineKeyboardButton(text="Изменить этаж", callback_data="chfloor")],
    [InlineKeyboardButton(text="Изменить расстояние до метро", callback_data="chdist")],
    [InlineKeyboardButton(text="Обновить", callback_data="update")],
    [InlineKeyboardButton(text="Предсказать", callback_data="predict")]
]
change_req_button_menu = InlineKeyboardMarkup(inline_keyboard=change_req_buttons)

async def convert_data_to_request(data: dict):
    lat = data.get("lat", 55.621211)
    lon = data.get("lng", 37.745600)
    square = data.get("square", 0.0)
    metro_dist = data.get("metro_dist", 0.0)
    floor = data.get("floor", 0)
    object_type = data.get("object_type", "Торговое / Свободного назначения")
    return {
        'lat': lat,
        'lng': lon,
        'Общая площадь': square,
        'Расстояние до метро, км': metro_dist,
        'Этаж': floor,
        'Вид объекта': object_type,
    }

async def convert_data_to_str(data: dict) -> str:
    str_data =\
        "Широта (lat): " + str(data['lat'])+'\n'+\
        "Долгота (lng): " + str(data['lng'])+'\n'+\
        "Общая площадь, м^2: " + str(data['Общая площадь'])+'\n'+\
        "Расстояние до метро, км: " + str(data['Расстояние до метро, км'])+'\n'+\
        "Этаж: " + str(data['Этаж'])+'\n'+\
        "Вид объекта: " + str(data['Вид объекта'])+'\n'
    return str_data

async def convert_pred_to_str(pred: dict):
    return f"Средняя цена за аренду помещения с такими параметрами: {round(pred['pred'], -3)} руб./мес"

@dp.callback_query(F.data == "update")
async def cmd_chreq(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    data = await convert_data_to_request(data)
    str_data = await convert_data_to_str(data)
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=str_data,
        reply_markup=change_req_button_menu
    )

@dp.callback_query(F.data == "chdist")
async def cmd_chdist(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer("Введите расстояние до метро (км)")
    await state.set_state(Form.chdist)
@dp.message(Form.chdist)
async def change_dist(message: types.Message, state: FSMContext):
    try:
        await state.update_data(metro_dist=float(message.text))
        await state.set_state(None)
    except:
        await message.answer("Данные введены неверно, попробуйте ещё раз.\n" +\
                            "Данные должны быть числом")

@dp.callback_query(F.data == "chlat")
async def cmd_chlat(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer("Введите lat")
    await state.set_state(Form.lat)
@dp.message(Form.lat)
async def change_lat(message: types.Message, state: FSMContext):
    try:
        await state.update_data(lat=float(message.text))
        await state.set_state(None)
    except:
        await message.answer("Данные введены неверно, попробуйте ещё раз.\n" +\
                            "Данные должны быть числом")

@dp.callback_query(F.data == "chlng")
async def cmd_chlng(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer("Введите lng")
    await state.set_state(Form.lng)
@dp.message(Form.lng)
async def change_lon(message: types.Message, state: FSMContext):
    try:
        await state.update_data(lng=float(message.text))
        await state.set_state(None)
    except:
        await message.answer("Данные введены неверно, попробуйте ещё раз.\n" +\
                            "Данные должны быть числом")

@dp.callback_query(F.data == "chsquare")
async def cmd_chsquare(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer("Введите общую площадь")
    await state.set_state(Form.square)
@dp.message(Form.square)
async def change_square(message: types.Message, state: FSMContext):
    try:
        await state.update_data(square=float(message.text))
        await state.set_state(None)
    except:
        await message.answer("Данные введены неверно, попробуйте ещё раз.\n" +\
                            "Данные должны быть числом")

@dp.callback_query(F.data == "chfloor")
async def cmd_chfloor(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer("Введите этаж")
    await state.set_state(Form.floor)
@dp.message(Form.floor)
async def change_floor(message: types.Message, state: FSMContext):
    try:
        await state.update_data(floor=int(message.text))
        await state.set_state(None)
    except:
        await message.answer("Данные введены неверно, попробуйте ещё раз.\n" +\
                            "Данные должны быть целым числом")

@dp.callback_query(F.data == "predict")
async def cmd_predict(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    data = await convert_data_to_request(data)
    try:
        data = AdvertInput(**data)
    except ValidationError as e:
        print(e)
        await callback_query.message.answer("Не все данные введены корректно. Используйте /req, чтобы проверить их")
        await callback_query.answer("wa")
        return
    try:
        ans = await predict(data)
    except BaseException as ex:
        await callback_query.answer("wa")
        raise ex
    str_ans = await convert_pred_to_str(ans.model_dump())
    await callback_query.message.answer(str_ans)
    # await callback_query.answer("ok")

@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await message.answer("Бот работает. Введите команду /start")

@dp.message(Command("req"))
async def cmd_req(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data = await convert_data_to_request(data)
    str_data = await convert_data_to_str(data)
    await message.answer(str_data, reply_markup=change_req_button_menu)

# Основная функция запуска бота
async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())