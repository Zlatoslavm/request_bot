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
# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
CHAT_URL = "https://t.me/+e8gHdGtUCZc3YTAy"
PAYOUT_URL = "https://t.me/+tZHPJfqZfjhlNWVi"
PHOTO_PATH = "foto.png"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# ================= ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ДЛЯ БЛОКИРОВКИ И РАССЫЛКИ =================
# user_status[user_id] = "pending" | "accepted" | "rejected"
user_status: Dict[int, str] = {}

# ================= FSM =================
class Form(StatesGroup):
    step1 = State()
    step2 = State()
    step3 = State()
    step4 = State()
    broadcast = State()  # новое состояние для рассылки (только для админа)

# ================= КЛАВИАТУРЫ =================
def start_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подать заявку →", callback_data="start_form")]
    ])

def admin_kb():
    """Кнопка рассылки для админа"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📨 Запустить рассылку", callback_data="start_broadcast")]
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

# ================= СТАРТ (с проверкой статуса и админ-панелью) =================
@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()  # всегда сбрасываем состояние при /start

    user_id = message.from_user.id

    # ================= АДМИН-ПАНЕЛЬ =================
    if user_id == ADMIN_ID:
        await message.answer(
            "<b>🔧 АДМИН ПАНЕЛЬ</b>\n\n"
            "Нажмите кнопку ниже для рассылки любому тексту/фото/видео всем пользователям, "
            "которые подавали заявку.",
            reply_markup=admin_kb()
        )
        return

    # ================= БЛОКИРОВКА ПОЛЬЗОВАТЕЛЕЙ =================
    # После подачи заявки (pending/accepted/rejected) бот больше НЕ реагирует на /start
    if user_id in user_status:
        status = user_status[user_id]
        if status == "pending":
            await message.answer(
                "⏳ <b>Ваша заявка уже на рассмотрении.</b>\n\n"
                "Ожидайте решения администрации. Повторная подача невозможна."
            )
            return
        elif status == "accepted":
            await message.answer(
                "✅ <b>Вы уже в команде!</b>\n\n"
                "Ваша заявка была одобрена. Бот больше не принимает новые заявки от вас."
            )
            return
        elif status == "rejected":
            await message.answer(
                "❌ <b>Ваша заявка была отклонена.</b>\n\n"
                "Повторная подача невозможна. Бот больше не реагирует на вас."
            )
            return

    # ================= ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ =================
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

# ================= ФОРМА (остаётся без изменений) =================
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

    # === СТАВИМ СТАТУС "pending" — дальше пользователь заблокирован ===
    user_status[user.id] = "pending"

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
    await callback.message.edit_reply_markup(reply_markup=None)
    await bot.send_message(user_id,
        "🎉 <b>Поздравляем! Ваша заявка одобрена.</b>\n\n"
        "Добро пожаловать в команду!\n\n"
        "Присоединяйтесь к нашим каналам:",
        reply_markup=final_kb()
    )
    # Обновляем статус — теперь пользователь полностью заблокирован
    user_status[user_id] = "accepted"
    await callback.answer("Принято ✅")

@dp.callback_query(F.data.startswith("reject_"))
async def reject(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    await callback.message.edit_reply_markup(reply_markup=None)
    await bot.send_message(user_id, "❌ К сожалению, ваша заявка отклонена.")
    # Обновляем статус — теперь пользователь полностью заблокирован
    user_status[user_id] = "rejected"
    await callback.answer("Отклонено ❌")

# ================= РАССЫЛКА (по кнопке) =================
@dp.callback_query(F.data == "start_broadcast")
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступно только администратору!")
        return

    await state.set_state(Form.broadcast)
    await callback.message.edit_text(
        "📨 <b>РЕЖИМ РАССЫЛКИ АКТИВИРОВАН</b>\n\n"
        "Отправьте <b>любое сообщение</b> (текст, фото, видео, документ — что угодно).\n"
        "Оно будет скопировано всем пользователям, которые подавали заявку.\n\n"
        "Для отмены просто напишите /start",
        reply_markup=None
    )
    await callback.answer("Рассылка активирована")

@dp.message(Form.broadcast)
async def send_broadcast(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    # Все пользователи, которые когда-либо подавали заявку
    users_to_send = list(user_status.keys())

    sent = 0
    failed = 0

    for uid in users_to_send:
        try:
            # copy_message поддерживает ЛЮБОЙ тип контента (текст + медиа)
            await bot.copy_message(
                chat_id=uid,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )
            sent += 1
        except:
            failed += 1

    await message.answer(
        f"✅ <b>РАССЫЛКА ЗАВЕРШЕНА!</b>\n\n"
        f"✅ Доставлено: <b>{sent}</b>\n"
        f"❌ Не доставлено: <b>{failed}</b>\n\n"
        f"Всего получателей: {len(users_to_send)}"
    )

    await state.clear()

# ================= ОТМЕНА И ПРОЧЕЕ =================
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
