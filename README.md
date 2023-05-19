# AllChantBot

Bot that can tag groups of people in telegram chat. You can use @all to tag all people in chat or manage chat members to groups and tag them!

Telegram nickname: 
  - **@callForEverybodyBot**

## Usage
### Important
Before being able to tag a person, the bot must see their message after inviting the bot to the chat.
### Steps
1. Add bot to the chat
2. Use one of following commands: \
    **/group_help** - to get this message (or **/gh**) \
    **/group_list** - to list all groups \
    **/group_create {group_name}** - create group named {group_name} \
    **/group_delete {group_name}** - deletes group named {group_name} \
    **/group_members {group_name}** - returns list of {group_name} members \
    **/group_add_member {group_name} {username}** - add {username} to {group_name} (user's message has to be seen by bot before you being able to add him to group) \
    **/group_del_member {group_name} {username}** - delete {username} from {group_name} \
    **@{group_name}** - tags every user in {group_name}

## Roadmap
- [x] deploy on Heroku
- [x] set up autodeploy
- [x] persistent storage
- [x] feature to manage people into groups and tag groups
- [ ] feature to set user rights to use @all and manage groups
- [ ] add inline buttons