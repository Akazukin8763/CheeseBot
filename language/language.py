import json

from language import data


def lang(*message_id):
    def decorator(func):
        def wrapper(*args, **kwargs):
            kwargs['lang_pack'] = get_lang(*message_id)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def set_lang(language: str):
    data.LANG = language
    data.FLAG = True


def get_lang(*message_id: str):
    if data.FLAG:
        with open(f"language_pack/language_{data.LANG}.json", encoding="utf-8") as lang_pack:
            data.datapack = json.load(lang_pack)
        data.FLAG = False

    message = data.datapack
    for _ in message_id:
        message = message[_]

    return message
