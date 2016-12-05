[![Build Status](https://ci.nekso.io/buildStatus/icon?job=tapvet-dev-be-api)](https://ci.nekso.io/job/tapvet-dev-be-api/)

# TapVet Backend

### Installation: ###

Run the following commands to install some dependencies and virtualenv:

    sudo apt-get install python-lxml
    sudo apt-get install libxml2-dev libxslt-dev
    sudo apt-get install build-essential python-dev

To install pip you can type:

    wget https://bootstrap.pypa.io/get-pip.py
    sudo python get-pip.py

Once you have pip installed run the following to install virtualenv:

    sudo pip install virtualenv

Clonning the project by ssh:

    git clone git@bitbucket.org:blanclink/tapvet-be-api.git

Before get into project folder you just cloned you must create the virtual environment typing the following:

    virtualenv env

This command is going to create an environment called "env", to activate it run:

    source env/bin/activate

After this you can get into the project folder.

    cd tapvet-be-api/

Remember to change to the right branch, then install the dependencies of the project:

    pip install -r requirements.txt
    
Here is an exception, to install pytest-ipdb (used for unit testing) just run:

    pip install git+git://github.com/mverteuil/pytest-ipdb.git

For running the server,you will need the following environment variables:

EMAIL_HOST_USER = The email address from where to send the emails

EMAIL_HOST_PASSWORD =  The password of the email address

MYSQL_PASSWORD = MYSQL password 

MYSQL_DATABASE = MYSQL database

MYSQL_USER =  MYSQL User

MYSQL_SERVER =  MYSQL server (usually localhost)

MEDIA_ROOT = Folder where the media will be storage (Have to be a complete path)

BROKER_URL =  Example: redis://localhost:6379/0

CELERY_RESULT_BACKEND = Example: redis://localhost:6379/1

STRIPE_API_KEY = Strike api Key


### Running ###

To lift the server you can run:

    python manage.py runserver <port_number>

If there is no port_number provided it will take port 8000 by default.

To run migrations to the database you have to type the following command:

    python manage.py migrate

Running tests, htmlcov folder automatically generated with an index.html inside of it:

    py.test

You can open this index.html which contain the coverage status of the project:

    firefox htmlcov/index.html