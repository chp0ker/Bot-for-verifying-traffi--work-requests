from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import aiogram

TOKEN_TG = "ВАШ ТОКЕН"
admin_id = 12345 # АЙДИ БЕЗ КАВЫЧЕК

storage = MemoryStorage()
bot = Bot(token=TOKEN_TG, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)


class info(StatesGroup):
    link_forum_lolz_state = State()
    work_experience_state = State()
    traffic_source_state = State()


def info_keyboard(user_id):
    approve = InlineKeyboardButton(text=" Принять", callback_data=f"approve_{user_id}")
    refusal = InlineKeyboardButton(text=" Отказать", callback_data=f"refusal_{user_id}")
    admin_menu = InlineKeyboardMarkup().add(approve, refusal)
    return admin_menu


@dp.message_handler(commands="start")
async def start_command(message: types.Message):
    all_id = open("all_id.txt", "r", encoding="utf-8")
    if str(message.from_user.id) not in all_id.read():

        print(
            f"Написал новый пользователь с ID: {message.from_user.id} и с UserName: @{message.from_user.username}"
        )

        await message.answer("Укажите ссылку ваш профиль на форуме")
        await info.link_forum_lolz_state.set()
    else:
        await message.answer("Вы ранее подавали заявку")


@dp.message_handler(state=info.link_forum_lolz_state)
async def give_info(message: types.Message, state: FSMContext):
    answer = message.text
    forum = "https://lolz.guru/" and "lolz.guru/"
    if forum not in answer:
        await message.answer("Неверно указана ссылка")
    else:
        await state.update_data(link_forum_lolz_state=answer)
        await message.answer(
            "Был ли у вас опыт в этой сфере, может вы имеете доказательства? – Прикрепите их к сообщению (ссылкой на imgur.com или на prnt.sc)"
        )
        await info.work_experience_state.set()


@dp.message_handler(state=info.work_experience_state)
async def give_info(message: types.Message, state: FSMContext):
    answer = message.text
    if len(answer) < 2:
        await message.answer("Маленькое количество символов")
    else:
        await state.update_data(work_experience_state=answer)
        await message.answer(
            "Какой у вас источник траффика? (Пример: Читы на игры | Кряк программ | Программы для взлома | Спам в комментарии)"
        )
        await info.traffic_source_state.set()


@dp.message_handler(state=info.traffic_source_state)
async def give_info(message: types.Message, state: FSMContext):
    answer = message.text
    if len(answer) < 4:
        await message.answer("Маленькое количество символов")
    else:
        await state.update_data(traffic_source_state=answer)
        data = await state.get_data()
        link_forum_lolz = data.get("link_forum_lolz_state")
        work_experience = data.get("work_experience_state")
        traffic_source = data.get("traffic_source_state")
        username_tg = message.from_user.username
        id_tg = message.from_user.id
        await message.answer(
            f"Ваша заявка успешно отправлена!\n"
            f"Ссылка на форум: {link_forum_lolz}\n"
            f"Опыт работы: {work_experience}\n"
            f"Источник траффика: {traffic_source}\n"
        )
        await bot.send_message(
            admin_id,
            f"Никнейм в телеграмме: @{username_tg} (ID: {id_tg})\n"
            f"Ссылка на форум: {link_forum_lolz}\n"
            f"Опыт работы: {work_experience}\n"
            f"Источник траффика: {traffic_source}\n",
            reply_markup=info_keyboard(id_tg),
        )
        open("all_id.txt", "a", encoding="utf-8").write(str(f"{id_tg}\n"))

        print(
            f"Добавил в базу данных новый ID: {id_tg} (Его UserName: @{message.from_user.username})"
        )

        await state.finish()


approve_info = InlineKeyboardButton(text=" Принят ", callback_data="approve")
approve_info_menu = InlineKeyboardMarkup().add(approve_info)

refusal_info = InlineKeyboardButton(text=" Не принят ", callback_data="refusal")
refusal_info_menu = InlineKeyboardMarkup().add(refusal_info)


@dp.callback_query_handler()
async def handler_call(call: types.CallbackQuery):
    if call.data.startswith("approve_"):
        id_tg = call.data.split("_")[1]
        await call.message.edit_reply_markup(approve_info_menu)
        await bot.send_message(
            id_tg,
            "Вы приняты\n"
            "Ссылка на беседу: https://lolz.guru/neverlucky/\n"
            "Ссылка на админа: https://lolz.guru/neverlucky/",
        )

        print(f"Отправил сообщение пользователю с ID: {id_tg} о том, что он принят")

    elif call.data.startswith("refusal_"):
        id_tg = call.data.split("_")[1]
        await call.message.edit_reply_markup(refusal_info_menu)
        await bot.send_message(id_tg, "Вы не приняты")

        print(f"Отправил сообщение пользователю с ID: {id_tg} о том, что он не принят")


if __name__ == "__main__":
    executor.start_polling(dp)
