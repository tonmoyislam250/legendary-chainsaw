from bot.helper.ext_utils.bot_utils import MirrorStatus, get_readable_file_size, get_readable_time
from pkg_resources import get_distribution
engine_ = f"Google Api v{get_distribution('google-api-python-client').version}"


class CloneStatus:
    def __init__(self, obj, size, message, gid):
        self.__obj = obj
        self.__size = size
        self.message = message
        self.__gid = gid
        self.source = self.__source()
        self.engine = engine_

    def processed_bytes(self):
        return self.__obj.transferred_size

    def size_raw(self):
        return self.__size

    def size(self):
        return get_readable_file_size(self.__size)

    def status(self):
        return MirrorStatus.STATUS_CLONING

    def name(self):
        return self.__obj.name

    def gid(self) -> str:
        return self.__gid

    def progress_raw(self):
        try:
            return self.__obj.transferred_size / self.__size * 100
        except ZeroDivisionError:
            return 0

    def progress(self):
        return f'{round(self.progress_raw(), 2)}%'

    def speed_raw(self):
        """
        :return: Download speed in Bytes/Seconds
        """
        return self.__obj.cspeed()

    def speed(self):
        return f'{get_readable_file_size(self.speed_raw())}/s'

    def eta(self):
        try:
            seconds = (self.__size - self.__obj.transferred_size) / self.speed_raw()
            return f'{get_readable_time(seconds)}'
        except ZeroDivisionError:
            return '-'

    def download(self):
        return self.__obj
    def __source(self):
        reply_to = self.message.reply_to_message
        return reply_to.from_user.username or reply_to.from_user.id if reply_to and \
            not reply_to.from_user.is_bot else self.message.from_user.username \
                or self.message.from_user.id
