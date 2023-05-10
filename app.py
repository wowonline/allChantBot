from flask import Flask, request
import requests
import os


app = Flask(__name__)


def get_env_or_raise(env_name):
    env_value = os.getenv(env_name)
    error_message = f'{env_name} enviroment variable must be set.'
    assert env_value, error_message
    return env_value


class Chat:
    def __init__(self):
        self.chat_pairs = {}
        # self.chat_metainfo = {}
        self.token = get_env_or_raise('BOT_TOKEN')
        self.url = get_env_or_raise('URL')
    
    # def manage_member(self, chat_id : int, chat_member_username : str, username : str, active_usernames : list):
    def manage_member(self, chat_id : int, chat_member_username : str):
        # self.chat_metainfo[chat_id] = [username, active_usernames]
        if chat_id not in self.chat_pairs.keys():
            self.chat_pairs[chat_id] = [chat_member_username]
        elif chat_member_username not in self.chat_pairs[chat_id]:
            self.chat_pairs[chat_id].append(chat_member_username)


chat_instance = Chat()


def bot_parse_queries(response):
    try:
        chat_member_username = response['message']['from']['username']
        chat_id = response['message']['chat']['id']
        # active_usernames = response['message']['chat']['active_usernames']
        # username = response['message']['chat']['username']
        message = response['message']['text']
        # chat_instance.manage_member(chat_id, chat_member_username, username, active_usernames)
        chat_instance.manage_member(chat_id, chat_member_username)
        if message == '@all':
            bot_send_chant(chat_id)
        if message == 'test':
            bot_send_message(chat_id, 'test')
        if message == 'print':
            bot_print_chat_pairs(chat_id)
    except KeyError:
        pass


def bot_print_chat_pairs(chat_to_print_id):
    chat_pairs = chat_instance.chat_pairs
    msg = ""    
    for chat_id, members_list in chat_pairs.items():
        msg += f'\nChat ID: {chat_id}'
        # meta = chat_instance.chat_metainfo[chat_id]
        # chat_name = meta[0]
        # for usr in chat_name[1]:
        #     msg += f'{usr} '
        # msg += '\n\t'
        for member_username in members_list:
            msg += f'{member_username} '
    bot_send_message(chat_to_print_id, msg)


def bot_send_chant(chat_id):
    msg = f'@{" @".join(chat_instance.chat_pairs[chat_id])}'
    query = f'https://api.telegram.org/bot{chat_instance.token}/sendMessage?chat_id={chat_id}&text={msg}'
    requests.post(query)
    
    
def bot_send_message(chat_id, msg_text):
    query = f'https://api.telegram.org/bot{chat_instance.token}/sendMessage?chat_id={chat_id}&text={msg_text}'
    requests.post(query)


@app.route('/getting', methods=['POST'])
def getting():
    data = request.json
    bot_parse_queries(data)
    return ''


@app.route('/validate')
def validate():
    requests.post(f"https://api.telegram.org/bot{chat_instance.token}/setWebhook?url={chat_instance.url}")
    return 'validated'


def main():
    from os import environ
    app.run(debug=False, port=environ.get("PORT", 4999), host='0.0.0.0')


if __name__ == '__main__':
    main()
