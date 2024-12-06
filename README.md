# tidbyt-manager
This is a very basic flask app for managing externally run applets for your tidbyt.
The docker-compose file will build and create the web app container itself and an mqtt/mosquitto container
```docker-compose up``` should do everything.

default login in admin / password


docker needs port 8000 and 5100-5120 port range opened up (use --network=host to make it easy ((doesn't work on mac docker though))

set DOMAIN value in .env file if not running locally


https://github.com/tavdog/tidbyt-manager/assets/8324295/e83a8795-3cb9-40cb-b854-90d07df8aebd


