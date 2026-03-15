import asyncio
import logging
from typing import Dict, Any

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardRemove, FSInputFile
)

# ================= НАСТРОЙКИ =================
TOKEN = "8793621177:AAHe1NJ-L3fcs6qWcx8pzSsGMqO7OVkKDds"
ADMIN_ID = 8419332734

CHAT_URL = "https://t.me/+e8gHdGtUCZc3YTAy"
PAYOUT_URL = "https://t.me/+tZHPJfqZfjhlNWVi"

PHOTO_PATH = "foto.png"  # ← файл должен лежать рядом со скриптом

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())


# ================= FSM =================
class Form(StatesGroup):
    step1 = State()  # Где узнали
    step2 = State()  # Что важно
    step3 = State()  # Готовы учиться
    step4 = State()  # Опыт


# ================= КЛАВИАТУРЫ =================
def start_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подать заявку →", callback_data="start_form")]
    ])


def get_step1_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Рекомендации знакомых", callback_data="q1_rec")],
        [InlineKeyboardButton(text="Тематические сообщества", callback_data="q1_comm")],
        [InlineKeyboardButton(text="Реклама", callback_data="q1_ads")],
        [InlineKeyboardButton(text="Форумы", callback_data="q1_forum")],
        [InlineKeyboardButton(text="« Отменить", callback_data="cancel")],
    ])


def get_step2_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Стабильность", callback_data="q2_stab")],
        [InlineKeyboardButton(text="Высокий доход", callback_data="q2_income")],
        [InlineKeyboardButton(text="Возможность роста", callback_data="q2_growth")],
        [InlineKeyboardButton(text="Командная атмосфера", callback_data="q2_team")],
        [InlineKeyboardButton(text="Гибкость и самостоятельность", callback_data="q2_flex")],
        [InlineKeyboardButton(text="Каждый критерий важен", callback_data="q2_all")],
        [InlineKeyboardButton(text="« Отменить", callback_data="cancel")],
    ])


def get_step3_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="q3_yes")],
        [InlineKeyboardButton(text="Да, если будет поддержка/обучение", callback_data="q3_yes_support")],
        [InlineKeyboardButton(text="Предпочитаю работать по знакомым...", callback_data="q3_no")],
        [InlineKeyboardButton(text="« Отменить", callback_data="cancel")],
    ])


def get_step4_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пропустить »", callback_data="q4_skip")],
        [InlineKeyboardButton(text="« Отменить", callback_data="cancel")],
    ])


def final_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Наш чат", url=CHAT_URL)],
        [InlineKeyboardButton(text="💰 Выплаты", url=PAYOUT_URL)],
    ])


# ================= СТАРТ (фото + кнопка) =================
@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    text = (
        "<b>ПОДАЧА ЗАЯВКИ</b>\n\n"
        "📗 <b>Добро пожаловать › Подача заявки</b>\n\n"
        "Наш сервис работает по принципу закрытых заявок. "
        "Чтобы присоединиться к нашей команде, заполните форму — это займет не более двух минут."
    )
    await message.answer_photo(
        photo=FSInputFile(PHOTO_PATH),
        caption=text,
        reply_markup=start_kb()
    )


# ================= ФОРМА =================
@dp.callback_query(F.data == "start_form")
async def start_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Form.step1)
    await callback.message.edit_caption(
        caption="<b>ПОДАЧА ЗАЯВКИ [1/4]</b>\n\nУкажите, где вы впервые услышали о нашем проекте.\n\n<b>Как вы узнали о нашем проекте?</b>",
        reply_markup=get_step1_kb()
    )
    await callback.answer()


@dp.callback_query(Form.step1, F.data.startswith("q1_"))
async def step1(callback: CallbackQuery, state: FSMContext):
    await state.update_data(q1={
        "q1_rec": "Рекомендации знакомых",
        "q1_comm": "Тематические сообщества",
        "q1_ads": "Реклама",
        "q1_forum": "Форумы"
    }.get(callback.data, "Не указано"))

    await state.set_state(Form.step2)
    await callback.message.edit_caption(
        caption="<b>ПОДАЧА ЗАЯВКИ [2/4]</b>\n\nЧто для вас наиболее важно в работе?\n\n<b>Что для вас наиболее важно в работе?</b>",
        reply_markup=get_step2_kb()
    )
    await callback.answer()


@dp.callback_query(Form.step2, F.data.startswith("q2_"))
async def step2(callback: CallbackQuery, state: FSMContext):
    await state.update_data(q2={
        "q2_stab": "Стабильность", "q2_income": "Высокий доход", "q2_growth": "Возможность роста",
        "q2_team": "Командная атмосфера", "q2_flex": "Гибкость и самостоятельность",
        "q2_all": "Каждый критерий важен"
    }.get(callback.data, "Не указано"))

    await state.set_state(Form.step3)
    await callback.message.edit_caption(
        caption="<b>ПОДАЧА ЗАЯВКИ [3/4]</b>\n\nГотовы ли вы обучаться новому при необходимости?\n\n<b>Готовы ли вы обучаться новому?</b>",
        reply_markup=get_step3_kb()
    )
    await callback.answer()


@dp.callback_query(Form.step3, F.data.startswith("q3_"))
async def step3(callback: CallbackQuery, state: FSMContext):
    await state.update_data(q3={
        "q3_yes": "Да",
        "q3_yes_support": "Да, если будет поддержка/обучение",
        "q3_no": "Предпочитаю работать по знакомым..."
    }.get(callback.data, "Не указано"))

    await state.set_state(Form.step4)
    await callback.message.edit_caption(
        caption="<b>ПОДАЧА ЗАЯВКИ [4/4]</b>\n\nРасскажите о вашем опыте (можно пропустить):\n\n<b>Опишите ваш опыт:</b>",
        reply_markup=get_step4_kb()
    )
    await callback.answer()


# ================= ФИНАЛ =================
@dp.callback_query(Form.step4, F.data == "q4_skip")
async def skip_step4(callback: CallbackQuery, state: FSMContext):
    await state.update_data(q4="Пропущено")
    await finish_application(callback.message, state, callback.from_user)


@dp.message(Form.step4)
async def finish(message: Message, state: FSMContext):
    await state.update_data(q4=message.text)
    await finish_application(message, state, message.from_user)


async def finish_application(msg: Message, state: FSMContext, user: Any):
    data: Dict = await state.get_data()

    admin_text = (
        f"<b>НОВАЯ ЗАЯВКА</b>\n\n"
        f"👤 Юзер: @{user.username or 'нет'} (ID: <code>{user.id}</code>)\n\n"
        f"1. Как узнали: <b>{data.get('q1')}</b>\n"
        f"2. Что важно: <b>{data.get('q2')}</b>\n"
        f"3. Готовы учиться: <b>{data.get('q3')}</b>\n"
        f"4. Опыт: <b>{data.get('q4')}</b>"
    )

    kb_admin = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_{user.id}"),
        InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{user.id}")
    ]])

    await bot.send_message(ADMIN_ID, admin_text, reply_markup=kb_admin)

    await msg.answer(
        "✅ <b>Ваша заявка отправлена!</b>\n\n"
        "Она на рассмотрении у администрации. Ожидайте решения.",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


# ================= АДМИН =================
@dp.callback_query(F.data.startswith("accept_"))
async def accept(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    await bot.send_message(user_id,
                           "🎉 <b>Поздравляем! Ваша заявка одобрена.</b>\n\n"
                           "Добро пожаловать в команду!\n\n"
                           "Присоединяйтесь к нашим каналам:",
                           reply_markup=final_kb()
                           )
    await callback.answer("Принято ✅")


@dp.callback_query(F.data.startswith("reject_"))
async def reject(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    await bot.send_message(user_id, "❌ К сожалению, ваша заявка отклонена.")
    await callback.answer("Отклонено ❌")


@dp.callback_query(F.data == "cancel")
async def cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_caption("❌ Заявка отменена. Напишите /start для новой.")
    await callback.answer()


@dp.message(Command("myid"))
async def myid(message: Message):
    await message.answer(f"Ваш ID: <code>{message.from_user.id}</code>")


# ================= ЗАПУСК =================
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())