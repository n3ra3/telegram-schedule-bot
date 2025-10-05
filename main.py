import asyncio
import datetime
import threading
import os
import json
import pytz
import datetime
from datetime import timedelta
from zoneinfo import ZoneInfo
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from http.server import BaseHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv
from aiogram.exceptions import TelegramConflictError
from http.server import BaseHTTPRequestHandler, HTTPServer

BOT_START_TIME = datetime.datetime.now()

load_dotenv()
# ==========================================================
# 🧠 Конфигурация режима работы: DEV или PROD
# ==========================================================
# Устанавливается через переменную окружения MODE (например, "dev" или "prod")
MODE = os.getenv("MODE", "dev")
DEV_TOKEN = os.getenv("DEV_TOKEN")
PROD_TOKEN = os.getenv("PROD_TOKEN")

print(f"🚀 Запуск бота в режиме: {MODE.upper()}")

if MODE == "prod":
    API_TOKEN = os.getenv("PROD_TOKEN")  # ⚠️ токен боевого бота (Render)
else:
    API_TOKEN = os.getenv("DEV_TOKEN")  # ⚠️ токен тестового бота (локально)

if not API_TOKEN:
    raise ValueError("❌ Не найден API токен! Проверь переменные окружения DEV_TOKEN или PROD_TOKEN.")

# ==========================================================
# 🧠 Основная конфигурация
# ==========================================================
ADMIN_ID = 770511678

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

TZ = ZoneInfo("Europe/Chisinau")  # локальное время Молдовы
REMINDERS_FILE = "reminders.json"

if not os.path.exists(REMINDERS_FILE):
    with open(REMINDERS_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

print(f"[MODE] Running in {MODE} mode with token: {API_TOKEN[:5]}...")


# 📆 Дата начала семестра (для расчёта чётности недели)
START_SEMESTER = datetime.date(2025, 9, 1)

schedule_even = {
    "Понедельник": [
        {"num": 2, "subject": "Limba străină", "teacher": "ARMAŞ S.", "room": "9-234", "time": "9:45–11:15"},
        {"num": 3, "subject": "sem. Geometria descriptivă", "teacher": "GORBATIUC A.", "room": "9-122", "time": "11:30–13:00"},
        {"num": 4, "subject": "Limba română", "teacher": "CUCIUC V.", "room": "9-103", "time": "13:30–15:00"},
        {"num": 5, "subject": "lab. Tehnologii informaționale și securitate cibernetică", "teacher": "ȘUVARI D.", "room": "9-P02", "time": "15:15–16:45"},
    ],
    "Вторник": [
        {"num": 1, "subject": "Atelier design", "teacher": "ROŞCA P.", "room": "9-338 / 334", "time": "8:00–9:30"},
        {"num": 2, "subject": "Studiul formei", "teacher": "MAŢCAN-LÎSENCO Inga / BABUC S.", "room": "9-388 / 9-334", "time": "9:45–11:15"},
        {"num": 3, "subject": "curs. Etică și integritate academică", "teacher": "COVALSCHI S.", "room": "9-204", "time": "11:30–13:00"},
        ],
    "Среда": [
        {"num": 4, "subject": "curs. Matematica", "teacher": "LEAH I.", "room": "9-234", "time": "13:30–15:00"}
        ],
    "Четверг": [
        {"num": 2, "subject": "curs. Bazele compoziției și proiectarea de arhitectură", "teacher": "OLEINIC S.", "room": "9-226", "time": "9:45–11:15"},
        {"num": 3, "subject": "Atelier design", "teacher": "ROŞCA P / MAŢCAN-LÎSENCO I.", "room": "9-330", "time": "11:30–13:00"}
        ],
    "Пятница": [
        {"num": 1, "subject": "curs. Istoria artelor plastice", "teacher": "TOCARCIUC A.", "room": "9-324", "time": "8:00–9:30"},
        {"num": 2, "subject": "curs. Tehnologii informaționale și securitate cibernetică", "teacher": "CUJBA R.", "room": "9-326", "time": "9:45–11:15"},
        {"num": 3, "subject": "Desen tehnic", "teacher": "ANATI S.", "room": "9-120", "time": "11:30–13:00"}
        ]
}

schedule_odd = {
    "Понедельник": [
        {"num": 2, "subject": "Limba străină", "teacher": "ARMAŞ S.", "room": "9-234", "time": "9:45–11:15"},
        {"num": 3, "subject": "sem. Geometria descriptivă", "teacher": "GORBATIUC A.", "room": "9-122", "time": "11:30–13:00"},
        {"num": 4, "subject": "Limba română ", "teacher": "CUCIUC V.", "room": "9-103", "time": "13:30–15:00"},
        {"num": 5, "subject": "Educația fizică", "teacher": "CARASTOIANOVA V.", "room": "Sala de sport", "time": "15:15–16:45"},
    ],
    "Вторник": [
        {"num": 1, "subject": "Atelier design", "teacher": "ROŞCA P.", "room": "9-338 / 334", "time": "8:00–9:30"},
        {"num": 2, "subject": "Studiul formei", "teacher": "MAŢCAN-LÎSENCO Inga / BABUC S.", "room": "9-388 / 9-334", "time": "9:45–11:15"},
        {"num": 3, "subject": "curs. Etică și integritate academică", "teacher": "COVALSCHI S.", "room": "9-204", "time": "11:30–13:00"},
        {"num": 4, "subject": "sem. Matematica", "teacher": "CIUHRII V.", "room": "9-234", "time": "13:30–15:00"},
        ],
    "Среда": [
        {"num": 1, "subject": "curs. Geometria descriptivă", "teacher": "ȘTIRBUL I.", "room": " 9-122", "time": "8:00–9:30"},
        {"num": 2, "subject": "curs. Geometria descriptivă", "teacher": "ȘTIRBUL I.", "room": " 9-122", "time": "9:45–11:15"},
        {"num": 3, "subject": "curs. Matematica", "teacher": "LEAH I.", "room": "9-234", "time": "11:30–13:00"},
        {"num": 4, "subject": "curs. Matematica", "teacher": "LEAH I.", "room": "9-234", "time": "13:30–15:00"}
        ],
    "Четверг": [
        {"num": 2, "subject": "curs. Bazele compoziției și proiectarea de arhitectură", "teacher": "OLEINIC S.", "room": "9-226", "time": "9:45–11:15"},
        {"num": 3, "subject": "Atelier design", "teacher": "ROŞCA P / MAŢCAN-LÎSENCO I.", "room": "9-330", "time": "11:30–13:00"},
        {"num": 4, "subject": "Atelier design", "teacher": "ROŞCA P / MAŢCAN-LÎSENCO I.", "room": "9-330", "time": "13:30–15:00"},
        ],
    "Пятница": [
        {"num": 1, "subject": "curs. Istoria artelor plastice", "teacher": "TOCARCIUC A.", "room": "9-324", "time": "8:00–9:30"},
        {"num": 2, "subject": "curs. Tehnologii informaționale și securitate cibernetică", "teacher": "CUJBA R.", "room": "9-326", "time": "9:45–11:15"},
        {"num": 3, "subject": "Desen tehnic", "teacher": "ANATI S.", "room": "9-120", "time": "11:30–13:00"}
        ]
}



# ---------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ----------
async def check_token_conflict(bot: Bot):
    """
    Проверяем, не запущен ли этот токен уже на другом устройстве или сервере.
    """
    try:
        me = await bot.get_me()
        print(f"✅ Бот успешно подключён: {me.first_name} (@{me.username})")
    except TelegramConflictError:
        print("\n❌ [ОШИБКА]: Этот токен уже используется в другом экземпляре бота!")
        print("📌 Решение:")
        print(" - Останови локальный бот, если деплой запущен на Render")
        print(" - Или наоборот — выключи Render, если тестируешь локально")
        print(" - Или используй разные токены для DEV и PROD\n")
        exit(1)



def is_even_week(start_date: datetime.date = datetime.date(2025, 9, 1)) -> bool:
    today = datetime.date.today()
    delta_weeks = (today - start_date).days // 7
    week_number = delta_weeks + 1  # начинаем считать с 1
    return week_number % 2 == 0



def get_days_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="Понедельник", callback_data="day_Понедельник"),
            InlineKeyboardButton(text="Вторник", callback_data="day_Вторник"),
            InlineKeyboardButton(text="Среда", callback_data="day_Среда"),
        ],
        [
            InlineKeyboardButton(text="Четверг", callback_data="day_Четверг"),
            InlineKeyboardButton(text="Пятница", callback_data="day_Пятница"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_schedule_keyboard(day: str, week_type: str):
    """Кнопки для расписания"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Сменить неделю", callback_data=f"switch_{day}_{week_type}")],
            [InlineKeyboardButton(text="⬅ Назад", callback_data="back")]
        ]
    )

def get_week_number_and_type(for_date: datetime.date, start_date: datetime.date = START_SEMESTER):
    delta_weeks = (for_date - start_date).days // 7
    week_number = delta_weeks + 1
    week_type = "even" if (week_number + 1) % 2 == 0 else "odd"  # 👈 добавлен +1
    return week_number, week_type


def format_schedule(day: str, schedule: dict, week_type: str, group: str = "DIN-253", subgroup: str = "Вторая"):
    """Форматирует расписание в красивый текст"""
    week_number, week_type = get_week_number_and_type(datetime.date.today())
    header = (
        f"📘 Расписание группы {group} на {day}\n"
        f"Неделя №{week_number} ({'чётная' if week_type == 'even' else 'нечётная'}) – {subgroup} подгруппа\n\n"
    )

    lessons = schedule.get(day, [])
    if not lessons:
        return header + "❌ Сегодня занятий нет"

    lines = []
    for lesson in lessons:
        lines.append(
            f"{lesson['num']}. {lesson['subject']}\n"
            f"Препод: {lesson['teacher']}\n"
            f"Аудитория: {lesson['room']}\n"
            f"Время: {lesson['time']}\n"
        )

    return header + "\n".join(lines)

async def safe_edit(callback: types.CallbackQuery, new_text: str, new_markup: InlineKeyboardMarkup):
    """Безопасное редактирование текста"""
    try:
        if callback.message.text == new_text and callback.message.reply_markup == new_markup:
            return
        await callback.message.edit_text(new_text, reply_markup=new_markup, parse_mode="HTML")
    except Exception as e:
        if "message is not modified" not in str(e):
            raise


@dp.message(F.text == "/test_reminder")
async def test_reminder(message: types.Message):
    text = build_reminder_text_for_tomorrow()
    if text:
        await message.answer("✅ Тест напоминания:\n\n" + text, parse_mode="HTML")
    else:
        await message.answer("❌ Завтра нет занятий.")


@dp.message(F.text == "/test_in_5min")
async def test_in_5min(message: types.Message):
    now = datetime.datetime.now(TZ)
    test_time = (now + datetime.timedelta(minutes=5)).strftime("%H:%M:%S")

    uid = str(message.from_user.id)
    reminders[uid] = {
        "enabled": True,
        "time": test_time
    }
    save_reminders()

    await message.answer(
        f"✅ Тестовый режим: я отправлю напоминание через 5 минут — в <b>{test_time}</b> (по Кишинёву).",
        parse_mode="HTML"
    )

@dp.message(F.text == "/reset_sent")
async def reset_sent_today(message: types.Message):
    uid = str(message.from_user.id)
    if uid in reminders:
        reminders[uid]["sent_today"] = False
        save_reminders()
        await message.answer("✅ Флаг отправки сброшен. Напоминание снова будет отправлено сегодня.")
    else:
        await message.answer("❌ Ты ещё не настраивал напоминание.")

@dp.message(F.text == "/export_reminders")
async def export_reminders(message: types.Message):
    """📤 Выгрузка reminders.json только для администратора"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У тебя нет прав для этой команды.")
        return

    if not os.path.exists(REMINDERS_FILE):
        await message.answer("❌ Файл reminders.json пока не создан.")
        return

    await message.answer_document(types.FSInputFile(REMINDERS_FILE))
    await message.answer("✅ Файл с напоминаниями успешно выгружен.")


class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/ping"):
            self.send_response(200)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("Bot is running ✅".encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_HEAD(self):
        if self.path in ("/", "/ping"):
            self.send_response(200)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()


def start_http_server():
    """Запускает HTTP-сервер для проверки доступности, если порт не занят."""
    port = int(os.environ.get("PORT", 8000))
    try:
        server = HTTPServer(("0.0.0.0", port), PingHandler)
        print(f"[PING] ✅ HTTP server started on port {port}")
        threading.Thread(target=server.serve_forever, daemon=True).start()
    except OSError as e:
        if e.errno == 98:
            print(f"[PING] ⚠️ Порт {port} уже занят — пропускаем запуск сервера (возможно, он уже работает)")
        else:
            raise

async def self_ping_loop():
    """Периодически пингует сам себя, чтобы Render не засыпал."""
    import aiohttp

    url = os.getenv("PING_URL")  # URL твоего бота на Render, например: https://telegram-schedule-bot-f1bf.onrender.com/ping

    if not url:
        print("[SELF-PING] ⚠️ PING_URL не задан — пропускаем self-ping")
        return

    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    print(f"[SELF-PING] ✅ {url} → {resp.status}")
        except Exception as e:
            print(f"[SELF-PING] ❌ Ошибка self-ping: {e}")

        await asyncio.sleep(300)  # 🔁 пингуем каждые 5 минут


class ReminderState(StatesGroup):
    waiting_time = State()

reminders: dict[str, dict] = {}
last_sent: dict[str, str] = {}  # in-memory: {user_id: "YYYY-MM-DD"} чтобы не спамить несколько раз за минуту

def load_reminders():
    global reminders
    if os.path.exists(REMINDERS_FILE):
        try:
            with open(REMINDERS_FILE, "r", encoding="utf-8") as f:
                reminders = json.load(f)
        except Exception:
            reminders = {}
    else:
        reminders = {}

def save_reminders():
    tmp = REMINDERS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(reminders, f, ensure_ascii=False, indent=2)
    os.replace(tmp, REMINDERS_FILE)

def normalize_time(inp: str) -> str | None:
    """
    Принимает варианты:
    - "9" -> "09:00"
    - "21" -> "21:00"
    - "9:0" -> "09:00"
    - "21:5" -> "21:05"
    - "09:45" -> "09:45"
    """
    s = inp.strip().replace(" ", "")
    if s.isdigit():
        h = int(s)
        if 0 <= h <= 23:
            return f"{h:02d}:00"
        return None
    if ":" in s:
        parts = s.split(":")
        if len(parts) != 2:
            return None
        if not parts[0].isdigit() or not parts[1].isdigit():
            return None
        h = int(parts[0])
        m = int(parts[1])
        if 0 <= h <= 23 and 0 <= m <= 59:
            return f"{h:02d}:{m:02d}"
    return None

def ru_day_from_date(dt: datetime.date) -> str:
    # Monday=0..Sunday=6
    mapping = {0:"Понедельник",1:"Вторник",2:"Среда",3:"Четверг",4:"Пятница",5:"Суббота",6:"Воскресенье"}
    return mapping[dt.weekday()]

def schedule_for_date(dt: datetime.date) -> tuple[str, list[dict]]:
    """Возвращает ('Понедельник', список занятий) для конкретной даты с учётом чётности недели."""
    day_ru = ru_day_from_date(dt)
    _, week_type = get_week_number_and_type(dt)
    sch = schedule_even if week_type == "even" else schedule_odd
    return day_ru, sch.get(day_ru, [])

def is_reminder_day(dt: datetime.date) -> bool:
    # хотим напоминания ВС-ЧТ (вс=6, пн=0, вт=1, ср=2, чт=3)
    return dt.weekday() in {6, 0, 1, 2, 3}

def build_reminder_text_for_tomorrow() -> str | None:
    """Строит текст напоминания на завтра (первая пара: время/аудитория/предмет/препод). Если пар нет — None."""
    now = datetime.datetime.now(TZ)
    tomorrow = (now + datetime.timedelta(days=1)).date()

    # если завтра не учебный день по твоей логике — можно вернуть None (но ты сказал, что пустых дней нет по будням)
    day_ru, lessons = schedule_for_date(tomorrow)
    if not lessons:
        return None

    first = lessons[0]
    start_time = first["time"].split("–", 1)[0].strip()
    subject = first["subject"]
    teacher = first["teacher"]
    room = first["room"]

    return (f"🔔 Напоминание: завтра ({day_ru}) первая пара начинается в <b>{start_time}</b>\n"
            f"📘 Предмет: <b>{subject}</b>\n"
            f"👤 Преподаватель: <b>{teacher}</b>\n"
            f"🏫 Аудитория: <b>{room}</b>")

def reminder_menu_text(user_id: int) -> str:
    data = reminders.get(str(user_id), {"enabled": False, "time": None})
    if data.get("enabled") and data.get("time"):
        return (f"🔔 Напоминания о парах\n\n"
                f"Сейчас: <b>ВКЛ</b>\n"
                f"Время: <b>{data['time']}</b> (по Кишинёву)\n"
                f"Рассылка приходит вс–чт и напоминает о первой паре на следующий день.\n\n"
                f"Можешь изменить время или отключить уведомления.")
    return ("🔔 Напоминания о парах\n\n"
            "Я могу присылать напоминание о первой паре на следующий день в удобное время.\n"
            "Рассылка приходит <b>вс–чт</b> (для пн–пт).\n\n"
            "Нажми «Включить», и я попрошу указать время (например: 21, 21:00, 9, 9:05).")

def reminder_menu_kb(user_id: int) -> InlineKeyboardMarkup:
    data = reminders.get(str(user_id), {"enabled": False, "time": None})
    if data.get("enabled") and data.get("time"):
        kb = [
            [InlineKeyboardButton(text="🕐 Изменить время", callback_data="rem_time_change")],
            [InlineKeyboardButton(text="❌ Отключить уведомления", callback_data="rem_toggle_off")],
            [InlineKeyboardButton(text="⬅ Назад", callback_data="back")],
        ]
    else:
        kb = [
            [InlineKeyboardButton(text="✅ Включить уведомления", callback_data="rem_toggle_on")],
            [InlineKeyboardButton(text="⬅ Назад", callback_data="back")],
        ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

# ---------- ХЕНДЛЕРЫ ----------
@dp.message(F.text == "/start")
async def start_command(message: types.Message):
    first_name = message.from_user.first_name  # берём имя пользователя из Telegram
    text = (
        f"👋 Привет, <b>{first_name}</b>!\n\n"
        "📅 Я — твой личный помощник по расписанию занятий.\n"
        "Моя задача — напоминать тебе о парах и держать тебя в курсе расписания.\n\n"
        "Вот что я умею:\n"
        "🔔 Отправляю уведомления о первой паре на завтра\n"
        "🕐 Позволяю выбрать удобное время напоминания\n"
        "📘 Показываю расписание с учётом чётной/нечётной недели\n\n"
        "📌 Чтобы начать, введи команду /menu или /reminder."
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text == "/botinfo")
async def bot_info(message: types.Message):
    info_text = (
        "🤖 <b>Schedule Reminder Bot</b>\n"
        "📅 Версия: 1.0.0\n"
        "📍 Разработчик: @nervblyati\n"
        "🕐 Часовой пояс: Europe/Chisinau (UTC+3)\n"
        "🧠 Основные функции:\n"
        "   • Напоминания о начале занятий\n"
        "   • Автоматическое определение расписания\n"
        "   • Поддержка чётных и нечётных недель\n"
        "   • Настройка времени уведомлений\n"
        "\n"
        "💡 Бот обновляется и развивается — следите за новыми возможностями!"
    )
    await message.answer(info_text, parse_mode="HTML")

def back_to_schedule_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅ Назад", callback_data="back")]
        ]
    )


@dp.message(F.text == "/info")
async def info_command(message: types.Message):
    help_text = (
        "📚 <b>Доступные команды:</b>\n\n"
        "🔹 /menu — главное меню и доступ ко всем функциям\n"
        "🔹 /reminder — управление уведомлениями о парах\n"
        "🔹 /botinfo — информация о версии и разработчике\n"
        "🔹 /info — справка по командам (это сообщение)\n"
        "\n"
        "💡 Совет: настройте удобное время уведомления — и бот сам напомнит, когда начинается первая пара завтра!"
    )
    await message.answer(help_text, parse_mode="HTML")

class ReportStates(StatesGroup):
    waiting_for_text = State()

@dp.message(F.text == "/report")
async def report_start(message: types.Message, state: FSMContext):
    await message.answer(
        "🛠️ Пожалуйста, опиши проблему или баг, с которым ты столкнулся.\n"
        "📨 После отправки я передам её разработчику."
    )
    await state.set_state(ReportStates.waiting_for_text)

@dp.message(ReportStates.waiting_for_text)
async def report_received(message: types.Message, state: FSMContext):
    report_text = message.text
    user = message.from_user

    # 📩 ID разработчика (твой Telegram ID)
    DEV_ID = 770511678  # <-- поменяй на свой

    # Отправляем отчёт разработчику
    await bot.send_message(
        DEV_ID,
        f"🐛 <b>Новый отчёт об ошибке!</b>\n\n"
        f"👤 Пользователь: {user.full_name} (@{user.username})\n"
        f"🆔 ID: <code>{user.id}</code>\n\n"
        f"📄 Сообщение:\n{report_text}",
        parse_mode="HTML"
    )

    await message.answer("✅ Спасибо! Отчёт успешно отправлен разработчику 🚀")
    await state.clear()

@dp.message(F.text == "/status")
async def status_handler(message: types.Message):
    now = datetime.datetime.now()
    uptime = now - BOT_START_TIME
    days, remainder = divmod(uptime.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)

    # 📊 Подсчёт активных пользователей
    active_users = [uid for uid, data in reminders.items() if data.get("enabled", False)]
    active_count = len(active_users)

    # 📬 Последнее напоминание (ищем самое позднее время отправки)
    last_sent_date = None
    if os.path.exists(REMINDERS_FILE):
        try:
            with open(REMINDERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Здесь ты можешь хранить last_sent_date глобально — если хочешь точнее
            last_sent_date = max(
                (datetime.datetime.combine(datetime.date.today(), datetime.datetime.strptime(v["time"], "%H:%M").time())
                 for v in data.values() if "time" in v),
                default=None
            )
        except Exception:
            pass

    last_sent_str = last_sent_date.strftime("%d.%m.%Y %H:%M") if last_sent_date else "ещё не отправлялось"

    # 📅 Список ближайших напоминаний
    upcoming_list = []
    for uid, info in reminders.items():
        if info.get("enabled", False) and "time" in info:
            upcoming_list.append(f"• UID {uid} — {info['time']}")

    upcoming_text = "\n".join(upcoming_list) if upcoming_list else "❌ Нет активных напоминаний"

    # 📤 Формируем ответ
    text = (
        "📊 <b>Статус бота</b>\n\n"
        f"⏱ Uptime: {int(days)} дн. {int(hours)} ч. {int(minutes)} мин.\n"
        f"👥 Активные пользователи: {active_count}\n"
        f"📬 Последнее напоминание: {last_sent_str}\n\n"
        f"📅 Следующие напоминания:\n{upcoming_text}"
    )

    # ✅ Добавляем кнопку «Назад»
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад к расписанию", callback_data="back_to_menu")]
    ])

    await message.answer(text, parse_mode="HTML", reply_markup=back_to_schedule_kb())



@dp.message(F.text == "/menu")
async def start_cmd(message: types.Message):
    await message.answer("Выберите день недели:", reply_markup=get_days_keyboard())


@dp.callback_query()
async def callback_router(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
    except:
        pass

    data = callback.data

    # Назад в меню
    if data == "back":
        await state.clear()  # 🔥 СБРАСЫВАЕМ состояние FSM
        await safe_edit(callback, "Выберите день недели:", get_days_keyboard())
        return

 # === Открыть меню напоминаний
    if data == "reminder_open":
        await state.clear()  # 🔥 очищаем состояние, если пользователь передумал вводить время
        await safe_edit(callback, reminder_menu_text(callback.from_user.id), reminder_menu_kb(callback.from_user.id))
        return


    # === Включить уведомления -> запрос времени
    if data == "rem_toggle_on":
        await state.set_state(ReminderState.waiting_time)
        await safe_edit(callback,
                        "⏰ Введи время для напоминаний (по Кишинёву).\n\n"
                        "Примеры: <code>21</code>, <code>21:00</code>, <code>9</code>, <code>9:05</code>",
                        InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="⬅ Отмена", callback_data="reminder_open")]
                        ]))
        return

    # === Отключение — подтверждение
    if data == "rem_toggle_off":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, отключить", callback_data="rem_off_yes"),
             InlineKeyboardButton(text="❌ Нет", callback_data="reminder_open")]
        ])
        await safe_edit(callback,
                        "⚠️ Вы уверены, что хотите отключить напоминания?",
                        kb)
        return

    if data == "rem_off_yes":
        uid = str(callback.from_user.id)
        if uid in reminders:
            reminders[uid]["enabled"] = False
            save_reminders()
        await safe_edit(callback,
                        "❌ Напоминания отключены.\n\nМожешь включить их снова и выбрать удобное время.",
                        reminder_menu_kb(callback.from_user.id))
        return

    # === Изменение времени — запрос
    if data == "rem_time_change":
        await state.set_state(ReminderState.waiting_time)
        await safe_edit(callback,
                        "⏰ Введи новое время (по Кишинёву).\nПримеры: <code>21</code>, <code>21:00</code>, <code>9</code>, <code>9:05</code>",
                        InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="⬅ Отмена", callback_data="reminder_open")]
                        ]))
        return




# День недели выбран
    elif data.startswith("day_"):
        day = data.split("_", 1)[1]
        today = datetime.date.today()
        _, week_type = get_week_number_and_type(today)
        schedule = schedule_even if week_type == "even" else schedule_odd
        new_text = format_schedule(day, schedule, week_type)
        await safe_edit(callback, new_text, get_schedule_keyboard(day, week_type))


# Переключение недели
    elif data.startswith("switch_"):
        _, day, current_week = data.split("_")
        new_week = "odd" if current_week == "even" else "even"
        schedule = schedule_even if new_week == "even" else schedule_odd
        new_text = format_schedule(day, schedule, new_week)
        await safe_edit(callback, new_text, get_schedule_keyboard(day, new_week))



    await callback.answer()

# Ввод времени для напоминаний
@dp.message(ReminderState.waiting_time)
async def reminder_set_time(message: types.Message, state: FSMContext):
    raw = message.text.strip()
    norm = normalize_time(raw)
    if not norm:
        await message.answer("❌ Неверный формат. Попробуй ещё раз, например: <code>21</code>, <code>21:00</code>, <code>9</code>, <code>9:05</code>", parse_mode="HTML")
        return

    uid = str(message.from_user.id)
    data = reminders.get(uid, {"enabled": False, "time": None})
    data["time"] = norm
    data["enabled"] = True
    reminders[uid] = data
    save_reminders()
    await state.clear()

    await message.answer(
        f"✅ Готово! Я буду присылать напоминание вс–чт в <b>{norm}</b> (по Кишинёву).",
        parse_mode="HTML"
    )
    # показать меню
    await message.answer(reminder_menu_text(message.from_user.id),
                         reply_markup=reminder_menu_kb(message.from_user.id),
                         parse_mode="HTML")

# Команда /reminder (то же самое, что кнопка)
@dp.message(F.text.in_({"/reminder", "reminder"}))
async def reminder_cmd(message: types.Message):
    await message.answer(reminder_menu_text(message.from_user.id),
                         reply_markup=reminder_menu_kb(message.from_user.id),
                         parse_mode="HTML")


# ---------- ЗАПУСК ----------
async def reminder_worker(bot: Bot):
    global reminders, last_sent, _last_reset_date  # ✅ объявляем глобальные переменные один раз в начале
    tz = pytz.timezone("Europe/Chisinau")

    # создаём глобальную переменную для сброса отправок, если её нет
    if "_last_reset_date" not in globals():
        _last_reset_date = None

    while True:
        now_dt = datetime.datetime.now(tz)
        now_hms = now_dt.strftime("%H:%M:%S")
        today = now_dt.date()

        # 🌅 Сброс флага отправки при наступлении нового дня
        if _last_reset_date != today:
            for _uid in list(reminders.keys()):
                reminders[_uid]["sent_today"] = False
            save_reminders()
            _last_reset_date = today
            print(f"[RESET] sent_today flags cleared for {today}")


        # Напоминания нужны вс–чт (перед пн–пт), значит в пт/сб НЕ шлём
        if now_dt.weekday() in (4, 5):  # 4=Пт, 5=Сб
            print(f"[SCAN] {now_hms} skip (Fri/Sat)")
            await asyncio.sleep(10)
            continue

        for uid, data in reminders.items():
            enabled = data.get("enabled", False)
            time_str = data.get("time")

            print(f"[SCAN] uid={uid} enabled={enabled} user_time={time_str} now={now_hms}")

            if not enabled or not time_str:
                continue

            # ✅ ВСТАВЬ ЗДЕСЬ НОВЫЙ КОД
            try:
                reminder_time = datetime.datetime.strptime(time_str, "%H:%M:%S").time()
            except ValueError:
                try:
                    reminder_time = datetime.datetime.strptime(time_str, "%H:%M").time()
                except ValueError:
                    print(f"[WARN] uid={uid} bad time format: {time_str}")
                    continue

            # ---- РАСЧЁТ Δt ----
            target_dt = tz.localize(datetime.datetime.combine(today, reminder_time))
            delta_s = (now_dt - target_dt).total_seconds()

            uid_str = str(uid)
            if "sent_today" not in reminders.get(uid_str, {}):
                reminders.setdefault(uid_str, {})["sent_today"] = False

            tomorrow = (now_dt + datetime.timedelta(days=1)).date()
            tomorrow_wd = tomorrow.weekday()
            is_allowed_day = tomorrow_wd in (0, 1, 2, 3, 4)

            BEFORE, AFTER = 2, 60
            in_window = (-BEFORE <= delta_s < AFTER)

            print(
                f"[CHECK] uid={uid} time={time_str} now={now_hms} delta={int(delta_s)}s "
                f"window={in_window} sent_today={reminders[uid_str]['sent_today']} "
                f"tomorrow_wd={tomorrow_wd} (0=Mon)"
            )

            if not is_allowed_day:
                print(f"[SKIP] uid={uid} — завтра не учебный день (сб/вс)")
                continue

            if not in_window:
                continue

            if reminders[uid_str]["sent_today"]:
                print(f"[SKIP] uid={uid} — уже отправляли сегодня")
                continue

            # ---- СБОР ТЕКСТА И ОТПРАВКА ----
            day_ru, lessons = schedule_for_date(tomorrow)
            if lessons:
                first = lessons[0]
                text = (
                    f"🔔 Напоминание: завтра ({day_ru}) первая пара начинается в <b>{first['time']}</b>\n"
                    f"📘 Предмет: <b>{first['subject']}</b>\n"
                    f"👤 Преподаватель: <b>{first['teacher']}</b>\n"
                    f"🏫 Аудитория: <b>{first['room']}</b>"
                )
            else:
                text = "🔔 Напоминание: завтра пар нет 🎉"

            try:
                await bot.send_message(int(uid), text, parse_mode="HTML")
                reminders[uid_str]["sent_today"] = True
                save_reminders()
                print(f"[SEND] ✅ uid={uid} at {now_hms}")
            except Exception as e:
                print(f"[ERROR] uid={uid} send failed: {e}")


        # каждые 10 сек проверяем всех пользователей
        await asyncio.sleep(10)



async def main():
    load_reminders()

    # ✅ Проверка наличия sent_today
    for uid, data in reminders.items():
        if "sent_today" not in data:
            data["sent_today"] = False
    save_reminders()

    # ✅ Запускаем фоновый self-ping, чтобы Render не засыпал
    asyncio.create_task(self_ping_loop())

    # ✅ Запускаем фонового воркера напоминаний
    asyncio.create_task(reminder_worker(bot))

    # ✅ Проверяем токен и запускаем Telegram-бота
    await check_token_conflict(bot)
    await dp.start_polling(bot)



if __name__ == "__main__":
    if "RENDER" in os.environ or os.getenv("PORT"):
        start_http_server()

    async def runner():
        # ⚙️ Запускаем основную логику
        await main()

    asyncio.run(runner())