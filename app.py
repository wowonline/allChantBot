from flask import Flask, request
import requests
import os
import db


app = Flask(__name__)


def get_env_or_raise(env_name):
    env_value = os.getenv(env_name)
    error_message = f'{env_name} environment variable must be set.'
    assert env_value, error_message
    return env_value


def get_group_help_string():
    return """Use /group_help to get help"""



class Chat:
    def __init__(self):
        self.chat_pairs = {}
        self.chat_metainfo = {}
        self.token = get_env_or_raise('BOT_TOKEN')
        self.url = get_env_or_raise('URL')
    
    def manage_member(self, chat_id : int, chat_member_username : str, chat_type : str, chat_username : str, chat_title : str):
        self.chat_metainfo[chat_id] = [chat_type, chat_username, chat_title]
        if chat_id not in self.chat_pairs.keys():
            self.chat_pairs[chat_id] = [chat_member_username]
        elif chat_member_username not in self.chat_pairs[chat_id]:
            self.chat_pairs[chat_id].append(chat_member_username)

    def get_chat_name(self, chat_id):
        type, username, title = self.chat_metainfo[chat_id]
        if type == 'private':
            return username
        else:
            return title


chat_instance = Chat()



def bot_parse_queries(response):
    try:
        chat_member_username = response['message']['from']['username']
        chat_member_id = response['message']['from']['id']
        
        message = response['message']['text']
        chat_id = response['message']['chat']['id']
        chat_type = response['message']['chat']['type']
        chat_username = None
        chat_title = None
        if (chat_type == 'private'):
            chat_username = response['message']['chat']['username']
        else:
            chat_title = response['message']['chat']['title']
        
        chat_instance.manage_member(chat_id, chat_member_username, chat_type, chat_username, chat_title)
        # to remove chat_instance and make it BOT instance for
        # containing env variables
        
        debug_chat_id = -943279534
        
        # DATABASE PART
        
        if (db.check_if_chat_is_new(chat_id)):
            db.add_chat_and_create_group_all(chat_id, chat_type, chat_title)
            db.group_add_member(chat_id, "all", chat_member_username, chat_member_id)
            bot_send_message(debug_chat_id, f"user {chat_member_username} was INITIALLY added to {chat_id}")
            
        elif (db.check_if_user_is_new(chat_id, chat_member_username)):
            db.group_add_member(chat_id, "all", chat_member_username, chat_member_id)
            bot_send_message(debug_chat_id, f"user {chat_member_username} was added to {chat_id}")
        
            
        if message == '@all':
            bot_send_chant(chat_id)
            return
            
        elif message == 'test':
            bot_send_message(chat_id, f'Chat type: {chat_type}\nChat ID: {chat_id}\nChat name: {chat_instance.get_chat_name(chat_id)}')
            return
            
        elif message == 'print':
            bot_print_chat_pairs(chat_id)
            return
        
        
        
        elif message == '/group_list':
            group_names = db.get_all_group_names(chat_id)
            msg = f"Groups:\n{group_names}"
            bot_send_message(chat_id, msg)
            return

        elif message == '/group_help':
            msg = get_group_help_string()
            bot_send_message(chat_id, msg)
            return

        words = message.split()
        try:
            if words[0] == '/group_create':
                try:
                    gr_name = words[1]
                    ret = db.group_create(chat_id, gr_name)
                    if ret == False:
                        msg = f"Group \"{gr_name}\" is already exists!"
                    else:
                        msg = f"Group \"{gr_name}\" was created!"
                    bot_send_message(chat_id, msg)
                except IndexError:
                    err_msg = "You need to specify name of the group!"
                    bot_send_message(chat_id, err_msg)
                
                
            elif words[0] == '/group_add_member':
                try:
                    gr_name = words[1]
                    try:
                        username = words[2]
                        ret = db.group_add_member(chat_id, gr_name, username)
                        if ret == False:
                            msg = f"User {username} is already in group \"{gr_name}\" or group \"{gr_name}\" does't exists!"
                        else:
                            msg = f"User {username} was added to group \"{gr_name}\"!"
                        bot_send_message(chat_id, msg)
                    except IndexError:
                        err_msg = "You need to specify username!"
                        bot_send_message(chat_id, err_msg)
                except IndexError:
                    err_msg = "You need to specify name of the group!"
                    bot_send_message(chat_id, err_msg)
            
            
            elif words[0] == '/group_del_member':
                try:
                    gr_name = words[1]
                    try:
                        username = words[2]
                        ret = db.group_del_member(chat_id, gr_name, username)
                        if ret == False:
                            msg = f"User {username} doesn't belongs to group \"{gr_name}\"!"
                        else:
                            msg = f"User {username} was deleted from group \"{gr_name}\"!"
                        bot_send_message(chat_id, msg)
                    except IndexError:
                        err_msg = "You need to specify username!"
                        bot_send_message(chat_id, err_msg)
                except IndexError:
                    err_msg = "You need to specify name of the group!"
                    bot_send_message(chat_id, err_msg)
            
            
            elif words[0] == '/group_del':
                try:
                    gr_name = words[1]
                    ret = db.group_delete(chat_id, gr_name)
                    if ret == False:
                        if gr_name == "all":
                            msg = "Group \"all\" can not be deleted!"
                        else:
                            msg = f"Group \"{gr_name}\" doesn't exists!"
                    else:
                        msg = f"Group {gr_name} was deleted!"
                    bot_send_message(chat_id, msg)
                except IndexError:
                    err_msg = "You need to specify name of the group!"
                    bot_send_message(chat_id, err_msg)

            
            elif words[0][0] == '@':
                groups = db.get_all_group_names()
                # members = group_get_members(chat_id)
                groups_set = set(groups.split())
                
                # check if first word without '@' is a group name
                if (words[0][1:] in groups_set):
                    gr_name = words[0][1:] # may be try except?
                    users = db.group_get_members(chat_id, gr_name)
                    msg = f"@{' @'.join(users.split())}"
                    bot_send_message(chat_id, msg)
                
            
        except IndexError:
            pass
        
        
        
        
    except KeyError:
        pass


# only for debug
def bot_print_chat_pairs(chat_to_print_id):
    chat_pairs = chat_instance.chat_pairs
    msg = ""    
    for chat_id, members_list in chat_pairs.items():
        msg += f'\nChat ID: {chat_id} (Chat name: {chat_instance.get_chat_name(chat_id)})\n\t'
        for member_username in members_list:
            msg += f'{member_username} '
    bot_send_message(chat_to_print_id, msg)


def bot_send_chant(chat_id):
    msg = f'@{" @".join(chat_instance.chat_pairs[chat_id])}'
    bot_send_message(chat_id, msg)
    
    
def bot_send_message(chat_id, msg):
    query = f'https://api.telegram.org/bot{chat_instance.token}/sendMessage?chat_id={chat_id}&text={msg}'
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
