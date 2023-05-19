import os
import psycopg2


def get_env_or_raise(env_name):
    env_value = os.getenv(env_name)
    error_message = f'{env_name} environment variable must be set.'
    assert env_value, error_message
    return env_value


DATABASE_URL = get_env_or_raise('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL, sslmode='require')


def drop_db():
    cur = conn.cursor()
    cur.execute(
    """
    DROP TABLE IF EXISTS chat, groups, users, group_user;            
    """)
    cur.connection.commit()
    cur.close()


def initialize_db():
    cur = conn.cursor()
    cur.execute(
    """
    CREATE TABLE chat(
    tg_chat_id bigint,
    tg_chat_type text,
    tg_chat_name text,
    PRIMARY KEY(tg_chat_id)
    );
    """)
    
    cur.execute(
    """
    CREATE TABLE groups(
    id_group serial,
    group_name text,
    tg_chat_id bigint,
    PRIMARY KEY(id_group),
    CONSTRAINT fk_chat
        FOREIGN KEY(tg_chat_id)
        REFERENCES chat(tg_chat_id)
        ON DELETE CASCADE
    );
    """)

    cur.execute(
    """
    CREATE TABLE users(
    id_user serial,
    tg_user_id bigint,
    tg_username text,
    PRIMARY KEY(id_user)
    );
    """)
    
    cur.execute(
    """
    CREATE TABLE group_user(
    id_group int,
    id_user int,
    id_group_user serial,
    PRIMARY KEY(id_group_user),
    CONSTRAINT fk_group
        FOREIGN KEY(id_group)
        REFERENCES groups(id_group)
        ON DELETE CASCADE,
    CONSTRAINT fk_customer
        FOREIGN KEY(id_user)
        REFERENCES users(id_user)
        ON DELETE CASCADE
    );
    """)
    
    cur.connection.commit()
    cur.close()


def debug_print_chats() -> None:
    cur = conn.cursor()
    query = """
    SELECT * FROM chat;
    """
    cur.execute(query)
    cur.connection.commit()
    print(cur.fetchall())
    cur.close()
    
    
def debug_print_groups_of_chat(chat_id) -> None:
    cur = conn.cursor()
    query = f"""
    SELECT * FROM groups WHERE groups.tg_chat_id = {chat_id};
    """
    cur.execute(query)
    cur.connection.commit()
    print(cur.fetchall())
    cur.close()
    
    
def debug_print_group_user():
    cur = conn.cursor()
    query = f"""
    SELECT * FROM group_user;
    """
    cur.execute(query)
    cur.connection.commit()
    print(cur.fetchall())
    cur.close()
    

def check_if_chat_is_new(chat_id) -> bool:
    cur = conn.cursor()
    query = f"""
    SELECT EXISTS(SELECT 1 FROM chat WHERE chat.tg_chat_id = {chat_id})
    """
    cur.execute(query)
    cur.connection.commit()
    fetched = cur.fetchone()[0]
    cur.close()
    return not fetched


def add_chat_and_create_group_all(chat_id, chat_type, chat_name) -> None:
    if not check_if_chat_is_new(chat_id):
        return
    cur = conn.cursor()
    query = f"""
    INSERT INTO chat (tg_chat_id, tg_chat_type, tg_chat_name) VALUES
        ({chat_id}, '{chat_type}', '{chat_name}');
    """
    cur.execute(query)
    cur.connection.commit()
    cur.close()
    group_create(chat_id, "all")


def check_if_group_exists(chat_id, gr_name) -> bool:
    """returns true if group exists"""
    cur = conn.cursor()
    query = f"""
    SELECT EXISTS(SELECT 1 FROM groups WHERE groups.tg_chat_id = {chat_id} AND
                                             groups.group_name = '{gr_name}')
    """
    cur.execute(query)
    cur.connection.commit()
    fetched = cur.fetchone()[0]
    cur.close()
    return fetched


#returns string such as "gr_name1 gr_name2 gr_name3"
def get_all_group_names(chat_id):
    cur = conn.cursor()
    query = f"""
    SELECT groups.group_name FROM groups WHERE groups.tg_chat_id = {chat_id}
    """
    cur.execute(query)
    cur.connection.commit()
    ret = ""
    for tup in cur.fetchall():
        ret += tup[0] + "\n"
    cur.close()
    
    return ret.rstrip()


def group_create(chat_id, gr_name) -> bool:
    if check_if_group_exists(chat_id, gr_name):
        return False
    cur = conn.cursor()
    query = f"""
    INSERT INTO groups (group_name, tg_chat_id) VALUES
        ('{gr_name}', {chat_id})
    """
    cur.execute(query)
    cur.connection.commit()
    cur.close()
    return True


def group_delete(chat_id, gr_name) -> bool:
    if gr_name == "all" or not check_if_group_exists(chat_id, gr_name):
        return False
    cur = conn.cursor()
    query = f"""
    DELETE FROM groups
    WHERE groups.tg_chat_id = {chat_id} AND 
          groups.group_name = '{gr_name}';
    """
    cur.execute(query)
    cur.connection.commit()
    cur.close()
    return True


# need to check if group exists
def group_get_id_by_name(chat_id, gr_name):
    cur = conn.cursor()
    id_group_query = f"""
    SELECT groups.id_group FROM groups WHERE
        groups.group_name = '{gr_name}' AND
        groups.tg_chat_id = {chat_id}
        limit 1;
    """
    cur.execute(id_group_query)
    cur.connection.commit()
    id_group = cur.fetchone()[0]
    cur.close()
    #if cur.fetchone() none
    return id_group


def group_add_member(chat_id, gr_name, username, tg_user_id) -> bool:
    if not check_if_group_exists(chat_id, gr_name):
        return 1
    
    # creating user if adding to group 'all'
    if (gr_name == "all"):
        cur = conn.cursor()
        user_add_query = f"""
        INSERT INTO users (tg_user_id, tg_username) VALUES
            ({tg_user_id}, '{username}');
        """
        cur.execute(user_add_query)
        cur.connection.commit()
        cur.close()
        
    if check_if_user_is_new(chat_id, username):
        return 2
    
    if group_contains_member(chat_id, gr_name, username):
        return 3
    
    id_group = group_get_id_by_name(chat_id, gr_name)
    id_user = user_get_id_by_username(chat_id, username)
    
    cur = conn.cursor()
    add_to_group_user_table_query = f"""
    INSERT INTO group_user (id_group, id_user) VALUES
        ({id_group}, {id_user});
    """
    cur.execute(add_to_group_user_table_query)
    cur.connection.commit()
    cur.close()
    return 0


def group_contains_member(chat_id, gr_name, username):
    if not check_if_group_exists(chat_id, gr_name):
        return False
    
    if check_if_user_is_new(chat_id, username):
        return False
    
    id_group = group_get_id_by_name(chat_id, gr_name)
    id_user = user_get_id_by_username(chat_id, username)
    
    cur = conn.cursor()
    query = f"""
    SELECT EXISTS(SELECT 1 FROM group_user WHERE
                    group_user.id_group = {id_group} AND
                    group_user.id_user = {id_user});
    """
    cur.execute(query)
    cur.connection.commit()
    fetched = cur.fetchone()[0]
    cur.close()
    
    print("DEBUG: ", fetched)
    return fetched


def group_del_member(chat_id, gr_name, username) -> bool:
    if gr_name == 'all':
        return 1
    
    if not group_contains_member(chat_id, gr_name, username):
        return 2
    
    id_group = group_get_id_by_name(chat_id, gr_name)
    id_user = user_get_id_by_username(chat_id, username)
    
    cur = conn.cursor()
    query = f"""
    DELETE FROM group_user
    WHERE group_user.id_group = {id_group} AND
          group_user.id_user = {id_user};
    """
    cur.execute(query)
    cur.connection.commit()
    cur.close()
    return 0


#returns string such as "usrname1 usrname2 usrname3"
def group_get_members(chat_id, gr_name):
    if not check_if_group_exists(gr_name):
        return (1, None)
    cur = conn.cursor()
    query = f"""
    SELECT tg_username FROM users, group_user, groups WHERE
        groups.tg_chat_id = {chat_id} AND
        groups.group_name = '{gr_name}' AND
        group_user.id_group = groups.id_group AND
        users.id_user = group_user.id_user;
    """
    cur.execute(query)
    cur.connection.commit()
    ret = ""
    for tup in cur.fetchall():
        ret += tup[0] + " "
    cur.close()
    return (0, ret.rstrip())



# !!!!!!!!!!!!!!!!!!!
# there will be problems when one user will be in
# several chats where bot is added
def check_if_user_is_new(chat_id, username):
    cur = conn.cursor()
    query = f"""
    SELECT EXISTS(SELECT 1 FROM users WHERE
                    users.tg_username='{username}')
    """
    cur.execute(query)
    cur.connection.commit()
    ans = cur.fetchone()[0]
    cur.close()
    return not ans

# need to check if user exists
def user_get_id_by_username(chat_id, username):
    cur = conn.cursor()
    id_user_query = f"""
    SELECT id_user FROM users WHERE
        users.tg_username = '{username}'
        limit 1;
    """
    cur.execute(id_user_query)
    cur.connection.commit()
    id_user = cur.fetchone()[0]
    cur.close()
    #if cur.fetchone() none
    return id_user



def main():
    # drop_db()
    # initialize_db()
    
    debug_print_chats()
    debug_print_group_user()
    pass
    
    
if __name__ == "__main__":
    main()
    