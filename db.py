import os
import psycopg2


def get_env_or_raise(env_name):
    env_value = os.getenv(env_name)
    error_message = f'{env_name} environment variable must be set.'
    assert env_value, error_message
    return env_value


DATABASE_URL = get_env_or_raise('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()


def drop_db():
    cur.execute(
    """
    DROP TABLE IF EXISTS chat, groups, users, group_user;            
    """)
    cur.connection.commit()


def initialize_db():
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


def debug_print_chats() -> None:
    query = """
    SELECT * FROM chat;
    """
    cur.execute(query)
    cur.connection.commit()
    print(cur.fetchall())
    
    
def debug_print_groups_of_chat(chat_id) -> None:
    query = f"""
    SELECT * FROM groups WHERE groups.tg_chat_id = {chat_id};
    """
    cur.execute(query)
    cur.connection.commit()
    print(cur.fetchall())
    
    
def debug_print_group_user():
    query = f"""
    SELECT * FROM group_user;
    """
    cur.execute(query)
    cur.connection.commit()
    print(cur.fetchall())
    

def check_if_chat_is_new(chat_id) -> bool:
    query = f"""
    SELECT EXISTS(SELECT 1 FROM chat WHERE chat.tg_chat_id = {chat_id})
    """
    cur.execute(query)
    cur.connection.commit()
    return cur.fetchone()[0]


def add_chat_and_create_group_all(chat_id, chat_type, chat_name) -> None:
    query = f"""
    INSERT INTO chat (tg_chat_id, tg_chat_type, tg_chat_name) VALUES
        ({chat_id}, '{chat_type}', '{chat_name}');
    """
    cur.execute(query)
    cur.connection.commit()
    group_create(chat_id, "all")


# returns true if group exists
def check_if_group_exists(chat_id, gr_name) -> bool:
    query = f"""
    SELECT EXISTS(SELECT 1 FROM groups WHERE groups.tg_chat_id = {chat_id} AND
                                             groups.group_name = '{gr_name}')
    """
    cur.execute(query)
    cur.connection.commit()
    return cur.fetchone()[0]


#returns string such as "gr_name1 gr_name2 gr_name3"
def get_all_group_names(chat_id):
    query = f"""
    SELECT groups.group_name FROM groups WHERE groups.tg_chat_id = {chat_id}
    """
    cur.execute(query)
    cur.connection.commit()
    ret = ""
    for tup in cur.fetchall():
        ret += tup[0] + " "
    
    return ret.rstrip()


def group_create(chat_id, gr_name) -> bool:
    if check_if_group_exists(chat_id, gr_name):
        return False
    query = f"""
    INSERT INTO groups (group_name, tg_chat_id) VALUES
        ('{gr_name}', {chat_id})
    """
    cur.execute(query)
    cur.connection.commit()
    return True


def group_delete(chat_id, gr_name) -> bool:
    if gr_name == "all" or not check_if_group_exists(chat_id, gr_name):
        return False
    query = f"""
    DELETE FROM groups
    WHERE groups.tg_chat_id = {chat_id} AND 
          groups.group_name = '{gr_name}';
    """
    cur.execute(query)
    cur.connection.commit()
    return True


# need to check if group exists
def group_get_id_by_name(chat_id, gr_name):
    id_group_query = f"""
    SELECT groups.id_group FROM groups WHERE
        groups.group_name = '{gr_name}' AND
        groups.tg_chat_id = {chat_id}
        limit 1;
    """
    cur.execute(id_group_query)
    cur.connection.commit()
    id_group = cur.fetchone()[0]
    #if cur.fetchone() none
    return id_group


def group_add_member(chat_id, gr_name, username, tg_user_id) -> bool:
    # creating user if adding to group 'all'
    if (gr_name == "all"):
        user_add_query = f"""
        INSERT INTO users (tg_user_id, tg_username) VALUES
            ({tg_user_id}, '{username}');
        """
        cur.execute(user_add_query)
        cur.connection.commit()
        
    if group_contains_member(chat_id, gr_name, username):
        return False
    
    #check on if group not exist
    
    id_group = group_get_id_by_name(chat_id, gr_name)
    #debug print
    print(f"id user: {id_group}")
    
    id_user = user_get_id_by_username(chat_id, username)
    #debug print
    print(f"id user: {id_user}")
    
    add_to_group_user_table_query = f"""
    INSERT INTO group_user (id_group, id_user) VALUES
        ({id_group}, {id_user});
    """
    cur.execute(add_to_group_user_table_query)
    cur.connection.commit()
    return True


def group_contains_member(chat_id, gr_name, username):
    if not check_if_group_exists(chat_id, gr_name):
        return False
    id_group = group_get_id_by_name(chat_id, gr_name)
    id_user = user_get_id_by_username(chat_id, username)
    
    query = f"""
    SELECT EXISTS(SELECT 1 FROM group_user WHERE
                    group_user.id_group = {id_group} AND
                    group_user.id_user = {id_user});
    """
    cur.execute(query)
    cur.connection.commit()
    
    fetched = cur.fetchone()[0]
    print("DEBUG: ", fetched)
    return fetched


def group_del_member(chat_id, gr_name, username) -> bool:
    if not group_contains_member(chat_id, gr_name, username):
        return False
    
    id_group = group_get_id_by_name(chat_id, gr_name)
    id_user = user_get_id_by_username(chat_id, username)
    
    query = f"""
    DELETE FROM group_user
    WHERE group_user.id_group = {id_group} AND
          group_user.id_user = {id_user};
    """
    cur.execute(query)
    cur.connection.commit()
    return True



#returns string such as "usrname1 usrname2 usrname3"
def group_get_members(chat_id, gr_name):
    pass


def check_if_user_is_new(chat_id, username):
    query = f"""
    SELECT EXISTS(SELECT 1 FROM users WHERE
                    users.tg_username='{username}')
    """
    cur.execute(query)
    cur.connection.commit()
    ans = cur.fetchone()[0]
    return not ans

# need to check if user exists
def user_get_id_by_username(chat_id, username):
    id_user_query = f"""
    SELECT id_user FROM users WHERE
        users.tg_username = '{username}'
        limit 1;
    """
    cur.execute(id_user_query)
    cur.connection.commit()
    id_user = cur.fetchone()[0]
    #if cur.fetchone() none
    return id_user



def main():
    # drop_db()
    # initialize_db()
    
    # add_chat_and_create_group_all(100, "private", "ayabot")
    # add_chat_and_create_group_all(101, "public", "mama_talks")
    # debug_print_chats()
    # print(check_if_chat_is_new(100))
    
    # group_create(100, 'duraki')
    # debug_print_groups_of_chat(100)
    # group_delete(100, 'all')
    # debug_print_groups_of_chat(100)
    
    # print(get_all_group_names(100))
    # # group_add_member(100, "all", "vanya", 25)
    # group_add_member(100, "kachki", "danya", 8888)
    # debug_print_group_user()
    # group_del_member(100, "kachki", "danya")
    # debug_print_group_user()
    # print(check_if_user_is_new(100, "danya"))
    # print(check_if_user_is_new(100, "jenya"))
    pass
    
    
if __name__ == "__main__":
    main()