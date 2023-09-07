import io
# import os


# from concurrent.futures import ThreadPoolExecutor
# import subprocess

import requests
from pytube import YouTube
from pytube.exceptions import RegexMatchError
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_audio

from logger import logger

size_threshold = 40_999_999  # 49 MB


def send_video(url: str):
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

        if stream.filesize > size_threshold:
            logger.info(f'File size is {stream.filesize_mb}, get smaller file')
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').first()

        if stream.filesize > size_threshold:
            logger.error(f'File size is {stream.filesize_mb}| IS A MINIMUM')
            raise Exception('File too large for uploading. Telegram limited us to 50mb')

        if not stream:
            logger.error('No video streams found')
            raise Exception("No video streams found")

        response = requests.get(stream.url)
        if not response.ok:
            logger.error(f'Got unexpected response | {response.status_code}')
            raise Exception("Failed to download video")
        return io.BytesIO(response.content)
    except RegexMatchError as exx:
        raise exx
    except Exception as ex:
        raise ex


def send_audio(url):
    try:
        yt = YouTube(url)

        audio_stream = yt.streams.filter(only_audio=True).first()

        if audio_stream.filesize > size_threshold:
            logger.error(f'File size is {audio_stream.filesize_mb}| IS A MINIMUM')
            raise Exception('File too large for uploading. Telegram limited us to 50mb')

        if audio_stream:
            audio_stream.download()
            
            mp4_file_path = f"{yt.title.replace('#', '')}.mp4"
            mp3_file_path = f"{yt.title.replace('#', '')}.mp3"
            ffmpeg_extract_audio(mp4_file_path, mp3_file_path)
            logger.info('File downloaded, sending ...')
            return yt.title
            
           
        else:
            
            logger.error('No video streams found')
            raise Exception("No video streams found")

    except Exception as e:
        raise f"An error occurred: {e}"


# def send_audio(url: str):
#     try:
#         youtube = YouTube(url)

#         audio_stream = youtube.streams.get_audio_only()
#         audio_filename = audio_stream.default_filename[:-4]

#         if audio_stream.filesize > size_threshold:
#             # logger.error(f'File size is {audio_stream.filesize_mb}| IS A MINIMUM')
#             raise Exception('File too large for uploading. Telegram limited us to 50mb')
#         # logger.info(f'File size is {audio_stream.filesize_mb}mb')

#         def download_audio(audio_stream):
#             audio_file = audio_stream.download(output_path="./", filename=audio_filename)
#             return audio_file

#         def convert_audio(audio_file):
#             subprocess.run(
#                 ['ffmpeg', '-i', audio_file, '-codec:a', 'libmp3lame', '-qscale:a', '2', f'{audio_filename}.mp3'])
#             os.remove(audio_file)

#         with ThreadPoolExecutor(max_workers=2) as executor:
#             download_task = executor.submit(download_audio, audio_stream)
#             audio_file = download_task.result()
#             convert_task = executor.submit(convert_audio, audio_file)
#             convert_task.result()
#         return audio_filename
#     except Exception as ex:
#         raise ex


# print(send_audio("https://youtu.be/XfWXHdW45Nk?si=d4hTybHkewId6jix"))