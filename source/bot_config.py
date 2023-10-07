import sys
sys.path.insert(0, "../csbot/server/")
from connect import con

with con:
    data = con.execute("SELECT * FROM district")
    for row in data:
        print(row)
    # row = data.fetchone()
BOT_CONFIG = {
    "intents": {
        "hello": {
            "examples": ["Привет", "Добрый день", "Привет, бот"],
            "responses": [
                "Привет, человек!",
                "И вам здравствуйте :)",
                "Доброго времени суток",
            ],
        },
        "bye": {
            "examples": ["Пока", "До свидания", "До свидания", "До скорой встречи"],
            "responses": ["Еще увидимся", "Если что, я всегда тут"],
        },
        "light": {
            "examples": [f"нет света в {row} районе", f"отсутсвует электричество на улице {row}"],
            "responses": [f"по информации в {row} отключение электроэнергии до 22"],
        },
    },
    "failure_phrases": [
        "Непонятно. Перефразируйте, пожалуйста.",
        "Я еще только учусь. Спросите что-нибудь другое",
        "Слишком сложный вопрос для меня.",
    ],
}