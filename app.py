from flask import Flask, request
import requests, os
import db
import commands


def get_env_or_raise(env_name):
    env_value = os.getenv(env_name)
    error_message = f'{env_name} environment variable must be set.'
    assert env_value, error_message
    return env_value


app = Flask(__name__)
DEFAULT_PORT = 4999
BOT_TOKEN = get_env_or_raise('BOT_TOKEN')
URL = get_env_or_raise('URL')


def delete_paragraph(string):
    if string == None:
        return None
    return string.replace('\'', '')


def contains_only_alpha_symbols(string):
    return string.isalpha()


def is_username_valid(username):
    allowed_symbols = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
    for c in username:
        if c not in allowed_symbols:
            return False
    return True


def bot_parse_queries(response):
    try:
        chat_member_username = response['message']['from']['username']
        chat_member_id = response['message']['from']['id']
        message = response['message']['text']
        chat_id = response['message']['chat']['id']
        chat_type = response['message']['chat']['type']
        chat_title = response['message']['chat']['title']
        
        chat_member_username = delete_paragraph(chat_member_username)
        chat_title = delete_paragraph(chat_title)
        message = delete_paragraph(message)
 
        msg = None
        if (db.check_if_chat_is_new(chat_id)):
            db.add_chat_and_create_group_all(chat_id, chat_type, chat_title)
            db.group_add_member(chat_id, "all", chat_member_username, chat_member_id, False)
        
        elif (db.check_if_user_is_new(chat_id, chat_member_username)):
            db.group_add_member(chat_id, "all", chat_member_username, chat_member_id, False)
        
        elif message == '/group_list':
            msg = commands.group_list(chat_id)
        
        elif message == '/group_help' or message == '/gh':
            msg = commands.group_help_string()
        
        else:
            words = message.split()
            group_commands = set(["/group_create", "/group_add_member",
                                "/group_del_member", "/group_del",
                                "/group_members"])
                
            try:
                if words[0][0] == '@':
                    msg = commands.group_tag(chat_id, words)
               
                elif words[0] in group_commands:
                    command = words[0]
                    try:
                        gr_name = words[1]
                        if not contains_only_alpha_symbols(gr_name):
                            msg = f"Group name can't contain non-alphabet symbols!"
                
                        else:
                            if command == "/group_create":
                                msg = commands.group_create(chat_id, gr_name)
                
                            elif command == "/group_del":
                                msg = commands.group_delete(chat_id, gr_name)
                
                            elif command == "/group_members":
                                msg = commands.group_members(chat_id, gr_name)
                
                            else:
                                try:
                                    username = words[2]
                                    if "@" in username:
                                        msg = "Username must not contain \"@\" symbol!"
                
                                    elif not is_username_valid(username):
                                        msg = "Username is not valid! (It may contain a-Z, 0-9 and underscore symbols only)"
                
                                    else:
                                        if command == "/group_add_member":
                                            msg = commands.group_add_member(chat_id, gr_name, username, chat_member_id)   
                
                                        elif command == "/group_del_member":
                                            msg = commands.group_del_member(chat_id, gr_name, username)
                                except IndexError:
                                    msg = "You have to specify username!"
                    except IndexError:
                        msg = "You have to specify name of the group!"
            except IndexError:
                pass
        if msg != None:
            bot_send_message(chat_id, msg)
    except KeyError:
        pass
        

def bot_send_message(chat_id, msg):
    query = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={msg}'
    requests.post(query)


@app.route('/getting', methods=['POST'])
def getting():
    data = request.json
    bot_parse_queries(data)
    return ''


@app.route('/validate')
def validate():
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={URL}")
    return 'validated'


def main():
    from os import environ
    app.run(debug=False, port=environ.get("PORT", DEFAULT_PORT), host='0.0.0.0')


if __name__ == '__main__':
    main()
