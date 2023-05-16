FROM anasty17/mltb:latest

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app
RUN mv /usr/bin/aria2c /usr/bin/mrbeast
RUN mv /usr/bin/qbittorrent-nox /usr/bin/pewdiepie
RUN mv /usr/bin/ffmpeg /usr/bin/mutahar

COPY . .
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["bash", "start.sh"]
