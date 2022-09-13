from subprocess import run as srun

UPSTREAM_REPO="https://github.com/ytubeupX/cautious-octo-potato"
UPSTREAM_BRANCH="anasty"

srun([f"git init -q \
&& git config --global user.email uploadmyvie41@gmail.com \
&& git config --global user.name ytubeupX \
&& git add . \
&& git commit -sm update -q \
&& git remote add origin {UPSTREAM_REPO} \
&& git fetch origin -q \
&& git reset --hard origin/{UPSTREAM_BRANCH} -q"], shell=True)
