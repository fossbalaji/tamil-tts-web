# Clone The Repository
```shell
git clone https://github.com/fossbalaji/tamil-tts-web.git
```
## Enter into the working directory

```shell
cd tamil-tts-web
```
## Mysql is needed for this project to run
```shell
sudo apt-get install mysql-server
sudo apt-get install python3-dev libmysqlclient-dev python3-pip
```

## Install Rabbitmq
```shell
sudo apt-get update
sudo apt-get install rabbitmq-server
sudo systemctl start rabbitmq-server
rabbitmq-plugins enable rabbitmq_management
sudo systemctl restart rabbitmq-server
```
#### Note: if any error in installation, check [here](https://www.rabbitmq.com/install-debian.html#bintray-apt-repo-erlang)

## Install the requirements
```shell
virtualenv -p python3 envtts
. envtts/bin/activate
pip intsall -r requirements.txt
```
### Note: if this fails, supporting library is missing, google the error msg to solve the issue



## Note: Change Enviroment variables to your mysql user name and password in `envsetup.sh` script

## Run the envsetup file by
```shell
sh envsetup.sh
```

## Create database on mysql

```shell
mysql -u yourusername -p
create database tamiltts
```

## Run command line tool setup
```shell
./tamil-tts.sh --clean --setup
```

## Finally migrate and run the server
```shell
python manage.py migrate
python manage.py runserver
```

## Open this on your browser
http://127.0.0.1:8000

## open another tab
```shell
cd tamil-tts-web
. envsetup.sh
. envtts/bin/activate
celery -A tamil_tts_web worker --loglevel=info
```
