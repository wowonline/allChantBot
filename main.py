

class Chat:
    def __init__(self):
        self.chat_pairs = {}
    
    def manage_member(self, chat_id : int, chat_member_username : str):
        if chat_id not in self.chat_pairs.keys():
            self.chat_pairs[chat_id] = [chat_member_username]
        elif chat_member_username not in self.chat_pairs[chat_id]:
            self.chat_pairs[chat_id].append(chat_member_username)


def botParseQueries(chat_instance, response) -> int:
    for i in range(len(response['result'])):
        query = response['result'][i]
        try:
            chat_member_username = query['message']['from']['username']
            chat_id = query['message']['chat']['id']
            message = query['message']['text']
            chat_instance.manage_member(chat_id, chat_member_username)
            if message == '@all':
                botSendMessage(chat_instance, chat_id)
        except KeyError:
            pass
    try:
        return response['result'][-1]['update_id'] + 1
    except KeyError:
        return 0

def botGetUpdates(chat_instance):
    from config import token
    from time import sleep
    import requests
    offset = ''

    while (True):
        sleep(1)
        print(offset)
        print(chat_instance.chat_pairs)
        query = f'https://api.telegram.org/bot{token}/getUpdates?offset={offset}'
        response = requests.get(query).json()
        if response['result'] != []:
            offset = botParseQueries(chat_instance, response)


def botSendMessage(chat_instance, chat_id):
    from config import token
    import requests

    msg = f'@{" @".join(chat_instance.chat_pairs[chat_id])}'
    query = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={msg}'
    requests.post(query)
    

def main():
    chat_instance = Chat()
    botGetUpdates(chat_instance)


if __name__ == '__main__':
    main()