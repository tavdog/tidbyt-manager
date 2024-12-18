# tidbyt-manager
This is a flask app for managing your apps on your Tronbyt (flashed tidbyt).  This project is meant be used to run your Tronbyt/Tidbyt completely locally without using the backend servers run/ran by tidbyt.
The docker-compose file will build and create the web app container

```docker-compose up``` should do everything.

default login in admin / password

docker needs port 8000 and 5100,5101 ports opened up (use --network=host to make it easy ((doesn't work on mac docker though))
docker-compose handles this though.

set DOMAIN value in .env file if not running locally

The way this app works is as follows :
1. Acess the webapp at http://localhost:8000 (or whatever domain you are using) with default login admin/password
2. Add your tronbyt as a device in the manager. (Default install will already have a device call Tronbyt 1)
3. Make note of the "Image URL" field for the device as this is what you'll need to set when flashing firmware.
4. Add an app and configure it via the built in pixlet interface.
5. Click save and you'll see the app preview in the app listing page.
6. Go flash your tidbyt into a Tronbyt with the [tronbyt-firmware-http](https://github.com/tavdog/tronbyt-firmware-http) 

The video below is a bit outdated but shows some of the flow of setting up your device and apps.

https://github.com/tavdog/tidbyt-manager/assets/8324295/e83a8795-3cb9-40cb-b854-90d07df8aebd


