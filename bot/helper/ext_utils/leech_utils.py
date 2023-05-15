from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE
from os import path as ospath
from re import search as re_search
from time import time
from math import ceil
from subprocess import run as srun, check_output, Popen

from aiofiles.os import mkdir
from aiofiles.os import path as aiopath
from aiofiles.os import remove as aioremove

from bot import LOGGER, MAX_SPLIT_SIZE, config_dict, user_data
from bot.helper.ext_utils.bot_utils import cmd_exec, sync_to_async
from bot.helper.ext_utils.fs_utils import ARCH_EXT, get_mime_type


async def get_media_streams(path):
    is_video = False
    is_audio = False
    mime_type = get_mime_type(path)
    if mime_type.startswith('audio'):
        is_audio = True
        return is_video, is_audio
    if not mime_type.startswith('video'):
        return is_video, is_audio
    try:
        result = check_output(["ffprobe", "-hide_banner", "-loglevel", "error", "-print_format",
                               "json", "-show_streams", path]).decode('utf-8')
    except Exception as e:
        LOGGER.error(f'{e}. Mostly file not found!')
        return is_video, is_audio
    fields = eval(result).get('streams')
    if fields is None:
        LOGGER.error(f"get_media_streams: {result}")
        return is_video, is_audio
    for stream in fields:
        if stream.get('codec_type') == 'video':
            is_video = True
        elif stream.get('codec_type') == 'audio':
            is_audio = True
    return is_video, is_audio



async def get_media_info(path):
    try:
        result = await cmd_exec(["ffprobe", "-hide_banner", "-loglevel", "error", "-print_format",
                                 "json", "-show_format", path])
        if res := result[1]:
            LOGGER.warning(f'Get Media Info: {res}')
    except Exception as e:
        LOGGER.error(f'Get Media Info: {e}. Mostly File not found!')
        return 0, None, None
    fields = eval(result[0]).get('format')
    if fields is None:
        LOGGER.error(f"get_media_info: {result}")
        return 0, None, None
    duration = round(float(fields.get('duration', 0)))
    tags = fields.get('tags', {})
    artist = tags.get('artist') or tags.get('ARTIST')
    title = tags.get('title') or tags.get('TITLE')
    return duration, artist, title


async def get_document_type(path):
    is_video, is_audio, is_image = False, False, False
    if path.endswith(tuple(ARCH_EXT)) or re_search(r'.+(\.|_)(rar|7z|zip|bin)(\.0*\d+)?$', path):
        return is_video, is_audio, is_image
    mime_type = await sync_to_async(get_mime_type, path)
    if mime_type.startswith('audio'):
        return False, True, False
    if mime_type.startswith('image'):
        return False, False, True
    if not mime_type.startswith('video') and not mime_type.endswith('octet-stream'):
        return is_video, is_audio, is_image
    try:
        result = await cmd_exec(["ffprobe", "-hide_banner", "-loglevel", "error", "-print_format",
                                 "json", "-show_streams", path])
        if res := result[1]:
            LOGGER.warning(f'Get Document Type: {res}')
    except Exception as e:
        LOGGER.error(f'Get Document Type: {e}. Mostly File not found!')
        return is_video, is_audio, is_image
    fields = eval(result[0]).get('streams')
    if fields is None:
        LOGGER.error(f"get_document_type: {result}")
        return is_video, is_audio, is_image
    for stream in fields:
        if stream.get('codec_type') == 'video':
            is_video = True
        elif stream.get('codec_type') == 'audio':
            is_audio = True
    return is_video, is_audio, is_image


async def take_ss(video_file, duration):
    des_dir = 'Thumbnails'
    if not await aiopath.exists(des_dir):
        await mkdir(des_dir)
    des_dir = ospath.join(des_dir, f"{time()}.jpg")
    if duration is None:
        duration = (await get_media_info(video_file))[0]
    if duration == 0:
        duration = 3
    duration = duration // 2
    cmd = ["mutahar", "-hide_banner", "-loglevel", "error", "-ss", str(duration),
           "-i", video_file, "-vf", "thumbnail", "-frames:v", "1", des_dir]
    status = await create_subprocess_exec(*cmd, stderr=PIPE)
    if await status.wait() != 0 or not await aiopath.exists(des_dir):
        err = (await status.stderr.read()).decode().strip()
        LOGGER.error(
            f'Error while extracting thumbnail. Name: {video_file} stderr: {err}')
        return None
    return des_dir


async def split_file(path, size, file_, dirpath, split_size, listener, start_time=0, i=1, inLoop=False, noMap=False):
    if listener.seed and not listener.newDir:
        dirpath = f"{dirpath}/splited_files_wz"
        if not ospath.exists(dirpath):
            mkdir(dirpath)
    user_id = listener.message.from_user.id
    user_dict = user_data.get(user_id, False)
    leech_split_size = int((user_dict and user_dict.get('split_size')) or config_dict['LEECH_SPLIT_SIZE'])
    parts = ceil(size/leech_split_size)
    if ((user_dict and user_dict.get('equal_splits')) or config_dict['EQUAL_SPLITS']) and not inLoop:
        split_size = ceil(size/parts) + 1000
    if (await get_media_streams(path))[0]:
        duration = (await get_media_info(path))[0]
        base_name, extension = ospath.splitext(file_)
        split_size = split_size - 5000000
        while i <= parts:
            parted_name = f"{str(base_name)}.part{str(i).zfill(3)}{str(extension)}"
            out_path = ospath.join(dirpath, parted_name)
            if not noMap:
                listener.suproc = Popen(["mutahar", "-hide_banner", "-loglevel", "error", "-ss", str(start_time),
                                         "-i", path, "-fs", str(split_size), "-map", "0", "-map_chapters", "-1",
                                         "-c", "copy", out_path])
            else:
                listener.suproc = Popen(["mutahar", "-hide_banner", "-loglevel", "error", "-ss", str(start_time),
                                          "-i", path, "-fs", str(split_size), "-map_chapters", "-1", "-c", "copy",
                                          out_path])
            listener.suproc.wait()
            if listener.suproc.returncode == -9:
                return False
            elif listener.suproc.returncode != 0 and not noMap:
                LOGGER.warning(f"Retrying without map, -map 0 not working in all situations. Path: {path}")
                try:
                    osremove(out_path)
                except:
                    pass
                return await split_file(path, size, file_, dirpath, split_size, listener, start_time, i, True, True)
            elif listener.suproc.returncode != 0:
                LOGGER.warning(f"Unable to split this video, if it's size less than {config_dict['LEECH_SPLIT_SIZE']} will be uploaded as it is. Path: {path}")
                try:
                    osremove(out_path)
                except:
                    pass
                return "errored"
            out_size = get_path_size(out_path)
            if out_size > (config_dict['LEECH_SPLIT_SIZE'] + 1000):
                dif = out_size - (config_dict['LEECH_SPLIT_SIZE'] + 1000)
                split_size = split_size - dif + 5000000
                osremove(out_path)
                return  await split_file(path, size, file_, dirpath, split_size, listener, start_time, i, True, noMap)
            lpd = (await get_media_info(out_path))[0]
            if lpd == 0:
                LOGGER.error(f'Something went wrong while splitting mostly file is corrupted. Path: {path}')
                break
            elif duration == lpd:
                if not noMap:
                    LOGGER.warning(f"Retrying without map, -map 0 not working in all situations. Path: {path}")
                    try:
                        osremove(out_path)
                    except:
                        pass
                    return await split_file(path, size, file_, dirpath, split_size, listener, start_time, i, True, True)
                else:
                    LOGGER.warning(f"This file has been splitted with default stream and audio, so you will only see one part with less size from orginal one because it doesn't have all streams and audios. This happens mostly with MKV videos. noMap={noMap}. Path: {path}")
                    break
            elif lpd <= 4:
                osremove(out_path)
                break
            start_time += lpd - 3
            i = i + 1
    else:
        out_path = ospath.join(dirpath, f"{file_}.")
        listener.suproc = Popen(["split", "--numeric-suffixes=1", "--suffix-length=3",
                                f"--bytes={split_size}", path, out_path])
        listener.suproc.wait()
        if listener.suproc.returncode == -9:
            return False
    return True
