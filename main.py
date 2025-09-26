import asyncio
import datetime
import threading
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from http.server import BaseHTTPRequestHandler, HTTPServer

API_TOKEN = "8196810650:AAEy59MV1Xmi0XJ8MiyL0wAZpyng_81SgFg"  

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

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


def is_even_week(start_date: datetime.date = datetime.date(2025, 9, 1)) -> bool:
    today = datetime.date.today()
    delta_weeks = (today - start_date).days // 7
    week_number = delta_weeks + 1  # начинаем с 1
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

def get_week_info_from_semester(start_date: datetime.date = datetime.date(2025, 9, 1)):
    """Возвращает номер учебной недели и её чётность"""
    today = datetime.date.today()
    delta_weeks = (today - start_date).days // 7
    week_number = delta_weeks + 1  # учебные недели считаем с 1
    week_type = "even" if week_number % 2 == 0 else "odd"
    return week_number, week_type


def format_schedule(day: str, schedule: dict, week_type: str, group: str = "DIN-253", subgroup: str = "Вторая"):
    """Форматирует расписание в красивый текст"""
    week_number = datetime.date.today().isocalendar()[1]
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

# ---------- ХЕНДЛЕРЫ ----------

@dp.message(F.text == "/start")
async def start_cmd(message: types.Message):
    await message.answer("Выберите день недели:", reply_markup=get_days_keyboard())


@dp.callback_query()
async def callback_days(callback: types.CallbackQuery):
    data = callback.data

    # Назад в меню
    if data == "back":
        await safe_edit(callback, "Выберите день недели:", get_days_keyboard())

# День недели выбран
    elif data.startswith("day_"):
        day = data.split("_", 1)[1]
        week_type = "even" if is_even_week() else "odd"
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

class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_server():
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), PingHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# ---------- ЗАПУСК ----------

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
