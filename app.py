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
        self.token = get_env_or_raise('BOT_TOKEN')
        self.url = get_env_or_raise('URL')
    
    def manage_member(self, chat_id : int, chat_member_username : str):
        if chat_id not in self.chat_pairs.keys():
            self.chat_pairs[chat_id] = [chat_member_username]
        elif chat_member_username not in self.chat_pairs[chat_id]:
            self.chat_pairs[chat_id].append(chat_member_username)


chat_instance = Chat()


def botParseQueries(chat_instance, response) -> int:
    try:
        chat_member_username = response['message']['from']['username']
        chat_id = response['message']['chat']['id']
        message = response['message']['text']
        chat_instance.manage_member(chat_id, chat_member_username)
        if message == '@all':
            botSendChant(chat_instance, chat_id)
        if message == 'test':
            botSendMessage(chat_id, 'test')
    except KeyError:
        pass


def botSendChant(chat_instance, chat_id):
    msg = f'@{" @".join(chat_instance.chat_pairs[chat_id])}'
    query = f'https://api.telegram.org/bot{chat_instance.token}/sendMessage?chat_id={chat_id}&text={msg}'
    requests.post(query)
    
    
def botSendMessage(chat_id, msg_text):
    query = f'https://api.telegram.org/bot{chat_instance.token}/sendMessage?chat_id={chat_id}&text={msg_text}'
    requests.post(query)


@app.route('/getting', methods=['POST'])
def getting():
    data = request.json
    botParseQueries(chat_instance, data)
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
