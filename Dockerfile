FROM ghcr.io/tonmoyislam250/alpinedocker:jmdkh2
WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
CMD ["ash", "start.sh"]
