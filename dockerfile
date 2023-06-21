FROM golang:latest

###################################
# install pixlet
ENV NODE_URL https://deb.nodesource.com/setup_16.x
#ENV PIXLET_REPO https://github.com/tidbyt/pixlet.git
ENV PIXLET_REPO https://github.com/tavdog/pixlet
ENV TDM_REPO https://github.com/tavdog/tidbyt-manager
ENV TIDBYT_APPS_REPO https://github.com/tidbyt/community

RUN apt update && apt upgrade && apt install cron libwebp-dev python3-venv python3-pip -y

WORKDIR /tmp
RUN curl -fsSL $NODE_URL | bash - && apt-get install -y nodejs npm && node -v

WORKDIR /
RUN git clone $PIXLET_REPO /pixlet
WORKDIR /pixlet
RUN npm install && npm run build && make build

###################################
# install flask and tidbymanager app
RUN git clone $TDM_REPO /app
WORKDIR /app
# install tidbyt apps
RUN git clone $TIDBYT_APPS_REPO tidbyt-apps

# populate the apps.json file
RUN python3 ./gen_app_array.py
# install the crontab directly 
RUN echo '* * * * * root cd /app ; python3 runner.py >> /app/runner.log 2>&1' > /etc/cron.d/tdmrunner
# start the app server
#CMD [".", "env/bin/activate", ";", "gunicorn", "-b", "0.0.0.0:8000", "tidby_manager:create_app()"]
CMD ["/app/run"]
