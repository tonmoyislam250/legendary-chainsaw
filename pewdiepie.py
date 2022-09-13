from subprocess import run as srun

https://github.com/tonmoyislam250/legendary-chainsaw"
UPSTREAM_BRANCH="pulled"

srun([f"git init -q \
&& git config --global user.email su6087031@gmail.com \
&& git config --global user.name tonmoyislam250 \
&& git add . \
&& git commit -sm update -q \
&& git remote add origin {UPSTREAM_REPO} \
&& git fetch origin -q \
&& git reset --hard origin/{UPSTREAM_BRANCH} -q"], shell=True)
