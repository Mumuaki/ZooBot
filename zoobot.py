import telebot
import logging
from configbot import TOKEN
from typing import Dict, List, Tuple
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    MessageHandler,
    Filters,
)
import random
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация бота
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")  # Для обратной связи

# Данные о животных
ANIMALS = {
    "Лев": {
        "description": "Царь зверей! Ты сильный, уверенный в себе лидер, который умеет брать на себя ответственность. "
        "Как и лев в зоопарке, ты можешь казаться грозным, но в душе у тебя доброе сердце.",
        "image": "https://moscowzoo.ru/upload/iblock/1c2/1c2a8f1f5c5c8e5e5e5e5e5e5e5e5e5.jpg",
        "facts": [
            "Львы - единственные кошки, которые живут группами (прайдами)",
            "Грива льва - это признак зрелости и статуса",
            "Львицы охотятся чаще, чем львы",
        ],
        "sponsor_link": "https://moscowzoo.ru/my-zoo/become-a-guardian/",
        "emoji": "🦁",
    },
    "Слон": {
        "description": "Ты мудрый и добрый, как слон! Слоны известны своей отличной памятью и сильными семейными узами. "
        "Ты тоже ценишь близких и всегда готов прийти на помощь.",
        "image": "https://moscowzoo.ru/upload/iblock/1c2/1c2a8f1f5c5c8e5e5e5e5e5e5e5e5e6.jpg",
        "facts": [
            "Слоны - самые крупные наземные животные",
            "Они могут узнавать себя в зеркале",
            "Слоны общаются с помощью инфразвука",
        ],
        "sponsor_link": "https://moscowzoo.ru/my-zoo/become-a-guardian/",
        "emoji": "🐘",
    },
    "Фламинго": {
        "description": "Ты яркий и общительный, как фламинго! Ты любишь быть в центре внимания и у тебя отличное чувство стиля. "
        "Как и фламинго, ты выделяешься из толпы.",
        "image": "https://moscowzoo.ru/upload/iblock/1c2/1c2a8f1f5c5c8e5e5e5e5e5e5e5e5e7.jpg",
        "facts": [
            "Фламинго розовые из-за пищи, которую едят",
            "Они стоят на одной ноге для сохранения тепла",
            "Фламинго могут жить до 50 лет",
        ],
        "sponsor_link": "https://moscowzoo.ru/my-zoo/become-a-guardian/",
        "emoji": "🦩",
    },
    "Сурикат": {
        "description": "Ты энергичный и любознательный, как сурикат! Ты всегда начеку и любишь исследовать новое. "
        "Как и сурикаты, ты хорошо работаешь в команде.",
        "image": "https://moscowzoo.ru/upload/iblock/1c2/1c2a8f1f5c5c8e5e5e5e5e5e5e5e5e8.jpg",
        "facts": [
            "Сурикаты всегда выставляют часовых",
            "Они учат своих детенышей охотиться",
            "Сурикаты могут загорать, стоя на задних лапах",
        ],
        "sponsor_link": "https://moscowzoo.ru/my-zoo/become-a-guardian/",
        "emoji": "🐾",
    },
    "Дикобраз": {
        "description": "Ты уникальный и необычный, как дикобраз! Возможно, ты немного колючий снаружи, но внутри ты очень добрый. "
        "Ты умеешь постоять за себя и своих близких.",
        "image": "https://moscowzoo.ru/upload/iblock/1c2/1c2a8f1f5c5c8e5e5e5e5e5e5e5e5e9.jpg",
        "facts": [
            "Иглы дикобраза - это видоизмененные волосы",
            "Они отличные альпинисты",
            "Дикобразы ведут ночной образ жизни",
        ],
        "sponsor_link": "https://moscowzoo.ru/my-zoo/become-a-guardian/",
        "emoji": "🦔",
    },
}

# Вопросы для викторины
QUESTIONS = [
    {
        "text": "Как бы ты описал свой характер?",
        "options": {
            "Сильный и уверенный": "Лев",
            "Мудрый и заботливый": "Слон",
            "Яркий и общительный": "Фламинго",
            "Энергичный и любознательный": "Сурикат",
            "Уникальный и необычный": "Дикобраз",
        },
    },
    {
        "text": "Какое твое любимое времяпрепровождение?",
        "options": {
            "Лидерство в проектах": "Лев",
            "Чтение и размышления": "Слон",
            "Вечеринки с друзьями": "Фламинго",
            "Исследование нового": "Сурикат",
            "Творчество и хобби": "Дикобраз",
        },
    },
    {
        "text": "Как ты ведешь себя в компании?",
        "options": {
            "Я обычно в центре внимания": "Лев",
            "Я слушаю больше, чем говорю": "Слон",
            "Я люблю общаться со всеми": "Фламинго",
            "Я активный участник событий": "Сурикат",
            "Я предпочитаю небольшие компании": "Дикобраз",
        },
    },
    {
        "text": "Какая твоя любимая еда?",
        "options": {
            "Мясо": "Лев",
            "Овощи и фрукты": "Слон",
            "Что-то экзотическое": "Фламинго",
            "Все подряд!": "Сурикат",
            "Что-то необычное": "Дикобраз",
        },
    },
    {
        "text": "Где ты хотел бы жить?",
        "options": {
            "В большом городе": "Лев",
            "В тихом пригороде": "Слон",
            "На берегу моря": "Фламинго",
            "В путешествиях": "Сурикат",
            "Где-нибудь необычно": "Дикобраз",
        },
    },
]

# Состояния бота
(
    START,
    QUIZ,
    RESULT,
    FEEDBACK,
    CONTACT,
    SHARE,
    RESTART,
) = range(7)


def start(update: Update, context: CallbackContext) -> int:
    """Начало взаимодействия с ботом."""
    user = update.message.from_user
    context.user_data.clear()  # Очищаем данные пользователя

    welcome_text = (
        f"Привет, {user.first_name}! 👋\n\n"
        "Я бот Московского зоопарка, и я помогу тебе узнать, какое животное из нашего зоопарка "
        "является твоим тотемным животным! 🦁🐘🦩\n\n"
        "Ответь на несколько простых вопросов, и я скажу, кто ты по духу!"
    )

    keyboard = [
        [InlineKeyboardButton("Начать викторину 🎉", callback_data=str(QUIZ))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(welcome_text, reply_markup=reply_markup)

    return START


def start_quiz(update: Update, context: CallbackContext) -> int:
    """Начало викторины."""
    query = update.callback_query
    query.answer()

    context.user_data["quiz_answers"] = {}
    context.user_data["current_question"] = 0

    return ask_question(update, context)


def ask_question(update: Update, context: CallbackContext) -> int:
    """Задаем вопрос пользователю."""
    current_question = context.user_data["current_question"]
    question_data = QUESTIONS[current_question]

    keyboard = []
    for option, animal in question_data["options"].items():
        keyboard.append([InlineKeyboardButton(option, callback_data=animal)])

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Для первого вопроса используем edit_message_text, для последующих - send_message
    if current_question == 0:
        update.callback_query.edit_message_text(
            text=f"Вопрос {current_question + 1}/{len(QUESTIONS)}: {question_data['text']}",
            reply_markup=reply_markup,
        )
    else:
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=f"Вопрос {current_question + 1}/{len(QUESTIONS)}: {question_data['text']}",
            reply_markup=reply_markup,
        )

    return QUIZ


def process_answer(update: Update, context: CallbackContext) -> int:
    """Обработка ответа пользователя."""
    query = update.callback_query
    query.answer()

    selected_animal = query.data
    quiz_answers = context.user_data.setdefault("quiz_answers", {})

    # Увеличиваем счетчик для выбранного животного
    quiz_answers[selected_animal] = quiz_answers.get(selected_animal, 0) + 1

    # Переходим к следующему вопросу
    context.user_data["current_question"] += 1

    if context.user_data["current_question"] < len(QUESTIONS):
        return ask_question(update, context)
    else:
        return show_result(update, context)


def show_result(update: Update, context: CallbackContext) -> int:
    """Показываем результат викторины."""
    quiz_answers = context.user_data.get("quiz_answers", {})
    
    if not quiz_answers:
        # Если по какой-то причине нет ответов, выбираем случайное животное
        final_animal = random.choice(list(ANIMALS.keys()))
    else:
        # Выбираем животное с наибольшим количеством голосов
        final_animal = max(quiz_answers.items(), key=lambda x: x[1])[0]

    animal_data = ANIMALS[final_animal]

    # Формируем текст результата
    result_text = (
        f"🎉 Твое тотемное животное в Московском зоопарке - {final_animal} {animal_data['emoji']}!\n\n"
        f"{animal_data['description']}\n\n"
        "Интересные факты:\n"
        f"• {animal_data['facts'][0]}\n"
        f"• {animal_data['facts'][1]}\n"
        f"• {animal_data['facts'][2]}\n\n"
        "Хочешь узнать больше об этом животном или даже взять его под опеку?"
    )

    # Кнопки после результата
    keyboard = [
        [
            InlineKeyboardButton("Узнать об опеке 🏡", callback_data="sponsor"),
            InlineKeyboardButton("Поделиться результатом 📢", callback_data="share"),
        ],
        [
            InlineKeyboardButton("Связаться с зоопарком 📞", callback_data="contact"),
            InlineKeyboardButton("Пройти еще раз 🔄", callback_data="restart"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем изображение животного
    context.bot.send_photo(
        chat_id=update.callback_query.message.chat_id,
        photo=animal_data["image"],
        caption=result_text,
        reply_markup=reply_markup,
    )

    return RESULT


def show_sponsor_info(update: Update, context: CallbackContext) -> int:
    """Показываем информацию о программе опеки."""
    query = update.callback_query
    query.answer()

    sponsor_text = (
        "🐾 Программа 'Возьми животное под опеку' 🐾\n\n"
        "Это возможность помочь любимому животному и внести вклад в сохранение биоразнообразия планеты!\n\n"
        "Как это работает:\n"
        "• Вы выбираете животное и сумму пожертвования\n"
        "• Средства идут на корм, ветеринарное обслуживание и улучшение условий содержания\n"
        "• Вы получаете сертификат опекуна и возможность навещать своего подопечного\n\n"
        "Подробнее на сайте: https://moscowzoo.ru/my-zoo/become-a-guardian/"
    )

    keyboard = [
        [InlineKeyboardButton("Назад к результату ↩️", callback_data="back_to_result")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_caption(caption=sponsor_text, reply_markup=reply_markup)

    return RESULT


def back_to_result(update: Update, context: CallbackContext) -> int:
    """Возвращаемся к результату из информации об опеке."""
    query = update.callback_query
    query.answer()

    quiz_answers = context.user_data.get("quiz_answers", {})
    final_animal = max(quiz_answers.items(), key=lambda x: x[1])[0]
    animal_data = ANIMALS[final_animal]

    result_text = (
        f"🎉 Твое тотемное животное в Московском зоопарке - {final_animal} {animal_data['emoji']}!\n\n"
        f"{animal_data['description']}\n\n"
        "Интересные факты:\n"
        f"• {animal_data['facts'][0]}\n"
        f"• {animal_data['facts'][1]}\n"
        f"• {animal_data['facts'][2]}\n\n"
        "Хочешь узнать больше об этом животном или даже взять его под опеку?"
    )

    keyboard = [
        [
            InlineKeyboardButton("Узнать об опеке 🏡", callback_data="sponsor"),
            InlineKeyboardButton("Поделиться результатом 📢", callback_data="share"),
        ],
        [
            InlineKeyboardButton("Связаться с зоопарком 📞", callback_data="contact"),
            InlineKeyboardButton("Пройти еще раз 🔄", callback_data="restart"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Обновляем сообщение с результатом
    query.edit_message_caption(caption=result_text, reply_markup=reply_markup)

    return RESULT


def share_result(update: Update, context: CallbackContext) -> int:
    """Предлагаем поделиться результатом."""
    query = update.callback_query
    query.answer()

    quiz_answers = context.user_data.get("quiz_answers", {})
    final_animal = max(quiz_answers.items(), key=lambda x: x[1])[0]
    animal_data = ANIMALS[final_animal]

    share_text = (
        f"Я прошел викторину Московского зоопарка и узнал, что мое тотемное животное - {final_animal} {animal_data['emoji']}!\n\n"
        "Пройди викторину и узнай свое тотемное животное: @MoscowZooTotemBot"
    )

    keyboard = [
        [InlineKeyboardButton("Назад к результату ↩️", callback_data="back_to_result")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_caption(
        caption=f"Расскажи друзьям о своем тотемном животном!\n\n{share_text}",
        reply_markup=reply_markup,
    )

    return SHARE


def contact_zoo(update: Update, context: CallbackContext) -> int:
    """Предлагаем связаться с зоопарком."""
    query = update.callback_query
    query.answer()

    contact_text = (
        "📞 Контакты Московского зоопарка:\n\n"
        "Телефон: +7 (499) 255-57-63\n"
        "Email: mail@moscowzoo.ru\n\n"
        "Если у тебя есть вопросы о программе опеки, напиши нам, "
        "и мы с радостью на них ответим!"
    )

    keyboard = [
        [InlineKeyboardButton("Назад к результату ↩️", callback_data="back_to_result")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_caption(caption=contact_text, reply_markup=reply_markup)

    return CONTACT


def restart_quiz(update: Update, context: CallbackContext) -> int:
    """Перезапускаем викторину."""
    query = update.callback_query
    query.answer()

    context.user_data["quiz_answers"] = {}
    context.user_data["current_question"] = 0

    return ask_question(update, context)


def feedback(update: Update, context: CallbackContext) -> int:
    """Обработка отзыва пользователя."""
    user_feedback = update.message.text
    user = update.message.from_user

    feedback_text = (
        f"Отзыв от {user.first_name} {user.last_name} (@{user.username}):\n\n"
        f"{user_feedback}"
    )

    # Отправляем отзыв администратору
    context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=feedback_text)

    update.message.reply_text(
        "Спасибо за твой отзыв! Мы ценим твое мнение и постараемся стать лучше!"
    )

    return RESULT


def cancel(update: Update, context: CallbackContext) -> int:
    """Завершаем взаимодействие с пользователем."""
    update.message.reply_text(
        "Если захочешь узнать свое тотемное животное - просто напиши /start!"
    )
    return -1


def error_handler(update: Update, context: CallbackContext) -> None:
    """Логируем ошибки."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    if update and update.effective_message:
        update.effective_message.reply_text(
            "Упс! Что-то пошло не так. Попробуй еще раз или напиши /start."
        )


def main() -> None:
    """Запуск бота."""
    # Создаем Updater и передаем ему токен бота
    updater = Updater(TOKEN)

    # Получаем диспетчер для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Определяем обработчики команд и сообщений
    conv_handler = {
        "entry_points": [CommandHandler("start", start)],
        "states": {
            START: [CallbackQueryHandler(start_quiz, pattern=f"^{QUIZ}$")],
            QUIZ: [CallbackQueryHandler(process_answer)],
            RESULT: [
                CallbackQueryHandler(show_sponsor_info, pattern="^sponsor$"),
                CallbackQueryHandler(share_result, pattern="^share$"),
                CallbackQueryHandler(contact_zoo, pattern="^contact$"),
                CallbackQueryHandler(restart_quiz, pattern="^restart$"),
                CallbackQueryHandler(back_to_result, pattern="^back_to_result$"),
            ],
            FEEDBACK: [MessageHandler(Filters.text & ~Filters.command, feedback)],
        },
        "fallbacks": [CommandHandler("cancel", cancel)],
    }

    dispatcher.add_handler(conv_handler)

    # Регистрируем обработчик ошибок
    dispatcher.add_error_handler(error_handler)

    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == "__main__":
    main()