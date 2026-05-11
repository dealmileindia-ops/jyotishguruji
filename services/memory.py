USER_MEMORY = {}
USER_LANGUAGE = {}

def save_memory(user_id, text):
    if user_id not in USER_MEMORY:
        USER_MEMORY[user_id] = []

    USER_MEMORY[user_id].append(text)

def get_memory(user_id):
    return USER_MEMORY.get(user_id, [])

def set_language(user_id, lang):
    USER_LANGUAGE[user_id] = lang

def get_language(user_id):
    return USER_LANGUAGE.get(user_id, "en")