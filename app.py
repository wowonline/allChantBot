from flask import Flask, request
import requests

app = Flask(__name__)
url = "https://chant-bot.herokuapp.com/getting"

class Chat:
    def __init__(self):
        self.chat_pairs = {}
    
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
            botSendMessage(chat_instance, chat_id)
    except KeyError:
        pass

def botSendMessage(chat_instance, chat_id):
    from config import token
    msg = f'@{" @".join(chat_instance.chat_pairs[chat_id])}'
    query = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={msg}'
    requests.post(query)

@app.route('/getting', methods=['POST'])
def getting():
    data = request.json
    botParseQueries(chat_instance, data)
    return ''

@app.route('/validate')
def validate():
    from config import token
    requests.post(f"https://api.telegram.org/bot{token}/setWebhook?url={url}")
    return 'validated'

def main():
    from os import environ
    app.run(debug=False, port=environ.get("PORT", 4999), host='0.0.0.0')

if __name__ == '__main__':
    main()
