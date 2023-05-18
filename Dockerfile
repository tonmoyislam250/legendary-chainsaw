FROM ghcr.io/tonmoyislam250/megasdkpython:latest
WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app
CMD ["ash", "start.sh"]
