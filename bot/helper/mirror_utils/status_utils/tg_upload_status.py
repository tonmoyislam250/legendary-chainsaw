from bot.helper.ext_utils.bot_utils import MirrorStatus, get_readable_file_size, get_readable_time
from bot import DOWNLOAD_DIR
from pkg_resources import get_distribution

class TgUploadStatus:
    def __init__(self, obj, size, gid, listener):
        self.__obj = obj
        self.__size = size
        self.__uid = listener.uid
        self.__gid = gid
        self.message = listener.message
        self.source = self.__source()
        self.engine = engine_

    def path(self):
        return f"{DOWNLOAD_DIR}{self.__uid}"

    def processed_bytes(self):
        return self.__obj.uploaded_bytes

    def size_raw(self):
        return self.__size

    def size(self):
        return get_readable_file_size(self.__size)

    def status(self):
        return MirrorStatus.STATUS_UPLOADING

    def name(self):
        return self.__obj.name

    def progress_raw(self):
        try:
            return self.__obj.uploaded_bytes / self.__size * 100
        except ZeroDivisionError:
            return 0

    def progress(self):
        return f'{round(self.progress_raw(), 2)}%'

    def speed_raw(self):
        """
        :return: Upload speed in Bytes/Seconds
        """
        return self.__obj.speed

    def speed(self):
        return f'{get_readable_file_size(self.speed_raw())}/s'

    def eta(self):
        try:
            seconds = (self.__size - self.__obj.uploaded_bytes) / self.speed_raw()
            return f'{get_readable_time(seconds)}'
        except ZeroDivisionError:
            return '-'

    def gid(self) -> str:
        return self.__gid

    def download(self):
        return self.__obj
    def __source(self):
        reply_to = self.message.reply_to_message
        return reply_to.from_user.username or reply_to.from_user.id if reply_to and \
            not reply_to.from_user.is_bot else self.message.from_user.username \
                or self.message.from_user.id
