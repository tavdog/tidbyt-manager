FROM golang:latest
#FROM pixletflask:latest

############
#set the domain env here if you don't want to use localhost. required to get the pixlet serve in iframe to work
# ENV DOMAIN=tdm.wildc.net
ENV DOMAIN=localhost

# ###################################
# install pixlet
ENV NODE_URL=https://deb.nodesource.com/setup_21.x
#ENV PIXLET_REPO=https://github.com/tavdog/pixlet
ENV PIXLET_REPO_ZIP=https://github.com/tavdog/pixlet/archive/refs/heads/config_merge.zip

ENV TDM_REPO=https://github.com/tavdog/tidbyt-manager
ENV TIDBYT_APPS_REPO=https://github.com/tidbyt/community

RUN apt update && apt upgrade -y && apt install cron libwebp-dev python3-pip python3-flask python3-gunicorn -y
RUN pip3 install --break-system-packages python-dotenv paho-mqtt python-pidfile
WORKDIR /tmp
RUN curl -fsSL $NODE_URL | bash - && apt-get install -y nodejs && node -v

WORKDIR /
# RUN git clone --depth 1 -b config_merge $PIXLET_REPO /pixlet
RUN apt install unzip
RUN wget $PIXLET_REPO_ZIP -O pixlet-main.zip && unzip pixlet-main.zip
RUN mv pixlet-config_merge pixlet
WORKDIR /pixlet
RUN npm install && npm run build && make build

WORKDIR /app
####################################### uncomment all below for final deployment
### during docker development using a mount to the app dir
# ###################################
# # install tidbymanager app
# COPY . /app
# #RUN git clone $TDM_REPO /app
# WORKDIR /app

# # install tidbyt apps
# RUN git clone $TIDBYT_APPS_REPO tidbyt-apps
# # or copy  your own list over
# #COPY tidbyt-apps /app/tidbyt-apps 

# # populate the apps.json file
# RUN python3 ./gen_app_array.py

# install the crontab directly 
#RUN echo '* * * * * root cd /app ; python3 runner.py >> /app/runner.log 2>&1' > /etc/cron.d/tdmrunner
EXPOSE 8000 5100 5101
# start the app
CMD ["./run"]
