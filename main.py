#!/usr/bin/env python
# coding: utf-8
import random
import nltk
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)
import sys
sys.path.insert(0, "../csbot/source/")

from bot_config import BOT_CONFIG
from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    Doc,
    NewsNERTagger,
    NamesExtractor,
    PER,
)

X_text = []
y = []

for intent, intent_data in BOT_CONFIG["intents"].items():
    for example in intent_data["examples"]:
        X_text.append(example)
        y.append(intent)

vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(3, 3))
X = vectorizer.fit_transform(X_text)
clf = LinearSVC()
clf.fit(X, y)


def clear_phrase(phrase):
    phrase = phrase.lower()

    alphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя- "
    result = "".join(symbol for symbol in phrase if symbol in alphabet)

    return result.strip()


def classify_intent(replica):
    replica = clear_phrase(replica)

    intent = clf.predict(vectorizer.transform([replica]))[0]

    for example in BOT_CONFIG["intents"][intent]["examples"]:
        example = clear_phrase(example)
        distance = nltk.edit_distance(replica, example)
        if example and distance / len(example) <= 0.5:
            return intent


def get_answer_by_intent(intent):
    if intent in BOT_CONFIG["intents"]:
        responses = BOT_CONFIG["intents"][intent]["responses"]
        if responses:
            return random.choice(responses)


with open("../csbot/source/dialogues.txt", encoding="utf-8") as f:
    content = f.read()

dialogues_str = content.split("\n\n")
dialogues = [dialogue_str.split("\n")[:2] for dialogue_str in dialogues_str]

dialogues_filtered = []
questions = set()

for dialogue in dialogues:
    if len(dialogue) != 2:
        continue

    question, answer = dialogue
    question = clear_phrase(question[2:])
    answer = answer[2:]

    if question != "" and question not in questions:
        questions.add(question)
        dialogues_filtered.append([question, answer])

dialogues_structured = {}  #  {'word': [['...word...', 'answer'], ...], ...}

for question, answer in dialogues_filtered:
    words = set(question.split(" "))
    for word in words:
        if word not in dialogues_structured:
            dialogues_structured[word] = []
        dialogues_structured[word].append([question, answer])

dialogues_structured_cut = {}
for word, pairs in dialogues_structured.items():
    pairs.sort(key=lambda pair: len(pair[0]))
    dialogues_structured_cut[word] = pairs[:1000]

# replica -> word1, word2, word3, ... -> dialogues_structured[word1] + dialogues_structured[word2] + ... -> mini_dataset


def generate_answer(replica):
    replica = clear_phrase(replica)
    words = set(replica.split(" "))
    mini_dataset = []
    for word in words:
        if word in dialogues_structured_cut:
            mini_dataset += dialogues_structured_cut[word]

    # TODO убрать повторы из mini_dataset

    answers = []  # [[distance_weighted, question, answer]]

    for question, answer in mini_dataset:
        if abs(len(replica) - len(question)) / len(question) < 0.2:
            distance = nltk.edit_distance(replica, question)
            distance_weighted = distance / len(question)
            if distance_weighted < 0.2:
                answers.append([distance_weighted, question, answer])

    if answers:
        return min(answers, key=lambda three: three[0])[2]


def get_failure_phrase():
    failure_phrases = BOT_CONFIG["failure_phrases"]
    return random.choice(failure_phrases)


stats = {"intent": 0, "generate": 0, "failure": 0}


def bot(replica):
    # NLU
    intent = classify_intent(replica)

    # Answer generation

    # выбор заготовленной реплики
    if intent:
        answer = get_answer_by_intent(intent)
        if answer:
            stats["intent"] += 1
            return answer

    # вызов генеративной модели
    answer = generate_answer(replica)
    if answer:
        stats["generate"] += 1
        return answer

    # берем заглушку
    stats["failure"] += 1
    return get_failure_phrase()


bot("Сколько времени?")


############### ТЕЛЕГРАММ ###########################

# https://github.com/python-telegram-bot/python-telegram-bot

# get_ipython().system(" pip install python-telegram-bot --upgrade")


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text("Да, я тут)))")


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        "Я бот, только никому не говори, тссс \nУмею общаться, но я ещё учусь (0)-(0)"
    )


def run_bot(update: Update, context: CallbackContext) -> None:
    # Используйте Natasha для анализа текста replica
    segmenter = Segmenter()
    morph_vocab = MorphVocab()

    emb = NewsEmbedding()
    morph_tagger = NewsMorphTagger(emb)
    syntax_parser = NewsSyntaxParser(emb)
    ner_tagger = NewsNERTagger(emb)

    names_extractor = NamesExtractor(morph_vocab)

    # Создаем объект Doc для анализа текста
    replica = update.message.text
    doc = Doc(replica)

    # Применяем сегментацию
    doc.segment(segmenter)
    print("Токены:")
    print(doc.tokens[:5])
    print("Предложения:")
    print(doc.sents[:5])

    # Применяем морфологический анализ
    doc.tag_morph(morph_tagger)
    print("\nТокены после морфологического анализа:")
    print(doc.tokens[:5])
    print("\nМорфологический анализ первого предложения:")
    doc.sents[0].morph.print()

    # Применяем лемматизацию
    for token in doc.tokens:
        token.lemmatize(morph_vocab)
    print("\nТокены после лемматизации:")
    print(doc.tokens[:5])
    print("\nСловарь лемм:")
    {_.text: _.lemma for _ in doc.tokens}

    # Применяем синтаксический анализ
    doc.parse_syntax(syntax_parser)
    print("\nТокены после синтаксического анализа:")
    print(doc.tokens[:5])
    print("\nСинтаксический анализ первого предложения:")
    if len(doc.tokens) >= 2:
        doc.parse_syntax(syntax_parser)
        print("Синтаксическая структура первых 5 токенов:")
        print(doc.tokens[:5])
        print("Синтаксическая структура первого предложения:")
        doc.sents[0].syntax.print()
    else:
        print("Недостаточно слов для синтаксического анализа.")
        print()

    # Применяем НЭР
    doc.tag_ner(ner_tagger)
    print("\nСущности:")
    print(doc.spans[:5])
    print("\nНЭР:")
    doc.ner.print()

    # Применяем нормализацию именнованного объекта
    for span in doc.spans:
        span.normalize(morph_vocab)
        print("\nСущности после нормализации:")
        print(doc.spans[:5])
        print("\nСловарь нормализованных сущностей:")
        {_.text: _.normal for _ in doc.spans if _.text != _.normal}

    # Применяем разбор именнованного объекта
    for span in doc.spans:
        if span.type == PER:
            span.extract_fact(names_extractor)

    print("\nСущности после разбора:")
    print(doc.spans[:5])
    print("\nСловарь фактов:")
    {_.normal: _.fact.as_dict for _ in doc.spans if _.type == PER}

    # Затем продолжите вашу обработку сообщения и отправку ответа
    answer = bot(replica)
    update.message.reply_text(answer)

    print("\nСтатистика:")
    print(stats)
    print("Сообщение пользователя:", replica)
    print("Ответ бота:", answer)
    print()


def main():
    """Start the bot."""
    updater = Updater("ТОКЕН")
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, run_bot))
    # Start the Bot
    updater.start_polling()
    updater.idle()


main()