from telegram.ext import MessageFilter
from telegram import Message
from bot import AUTHORIZED_CHATS, SUDO_USERS, OWNER_ID


class CustomFilters:
    class __OwnerFilter(MessageFilter):
        def filter(self, message: Message):
            return message.from_user.id == OWNER_ID

    owner_filter = __OwnerFilter()

    class __AuthorizedUserFilter(MessageFilter):
        def filter(self, message: Message):
            id = message.from_user.id
            return id in AUTHORIZED_CHATS or id in SUDO_USERS or id == OWNER_ID

    authorized_user = __AuthorizedUserFilter()

    class __AuthorizedChat(MessageFilter):
        def filter(self, message: Message):
            return message.chat.id in AUTHORIZED_CHATS

    authorized_chat = __AuthorizedChat()

    class __SudoUser(MessageFilter):
        def filter(self, message: Message):
            return message.from_user.id in SUDO_USERS

    sudo_user = __SudoUser()

    @staticmethod
    def _owner_query(user_id):
        return user_id == OWNER_ID or user_id in SUDO_USERS

    class _MirrorOwner(MessageFilter):
        def filter(self, message: Message):
            user_id = message.from_user.id
            if user_id == OWNER_ID:
                return True
            args = str(message.text).split(' ')
            if len(args) > 1:
                # Cancelling by gid
                with download_dict_lock:
                    for message_id, status in download_dict.items():
                        if status.gid() == args[1] and status.message.from_user.id == user_id:
                            return True
                    else:
                        return False
            if not message.reply_to_message and len(args) == 1:
                return True
            # Cancelling by replying to original mirror message
            reply_user = message.reply_to_message.from_user.id
            return bool(reply_user == user_id)
    mirror_owner_filter = _MirrorOwner()
