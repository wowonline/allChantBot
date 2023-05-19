import db


def group_tag(chat_id, words):
    groups = db.get_all_group_names(chat_id)
    groups_set = set(groups.split())
    msg = None
    if (words[0][1:] in groups_set):
        gr_name = words[0][1:]
        ret, users = db.group_get_members(chat_id, gr_name)
        if ret == 2:
            msg = "You can't tag an empty group!"
        elif ret == 0:
            msg = f"@{' @'.join(users.split())}"
    return msg


def group_create(chat_id, gr_name):
    ret = db.group_create(chat_id, gr_name)
    msg = None
    if ret == 1:
        msg = f"Group \"{gr_name}\" is already exists!"
    elif ret == 0:
        msg = f"Group \"{gr_name}\" was created!"
    return msg


def group_del(chat_id, gr_name):
    ret = db.group_delete(chat_id, gr_name)
    msg = None
    if ret == 1:
        msg = "Group \"all\" can't be deleted!"
    elif ret == 2:
        msg = f"Group \"{gr_name}\" doesn't exists!"
    elif ret == 0:
        msg = f"Group \"{gr_name}\" was deleted!"
    return msg


def group_members(chat_id, gr_name):
    ret_code, members = db.group_get_members(chat_id, gr_name)
    msg = None
    if ret_code == 1:
        msg = f"Group \"{gr_name}\" doesn't exists!"
    elif ret_code == 2:
        msg = f"Group \"{gr_name}\" doesn't have any member!"
    elif ret_code == 0:
        members = ", ".join(members.split()).rstrip()
        msg = f"Group \"{gr_name}\" contains of\n{members}"
    return msg


def group_add_member(chat_id, gr_name, username, chat_member_id):
    ret = db.group_add_member(chat_id, gr_name, username, chat_member_id, True)
    msg = None
    if ret == 1:
        msg = f"Group {gr_name} doesn't exists!"
    elif ret == 2:
        msg = f"User can't be added to group \"all\" manually!"
    elif ret == 3:
        msg = f"User {username} wasn't recognized by bot before!\nFirstly, he has to write something in chat!"
    elif ret == 4:
        msg = f"User {username} is already in group \"{gr_name}\"!"
    elif ret == 0:
        msg = f"User {username} was added to group \"{gr_name}\"!"
    return msg


def group_del_member(chat_id, gr_name, username):
    ret = db.group_del_member(chat_id, gr_name, username)
    msg = None
    if ret == 1:
        msg = "You can't delete anybody from group \"all\""
    elif ret == 2:
        msg = f"User {username} doesn't belongs to group \"{gr_name}\"!"
    elif ret == 0:
        msg = f"User {username} was deleted from group \"{gr_name}\"!"
    return msg
