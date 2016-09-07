# TapVet Backend

### Installation: ###

Run the following commands to install some dependencies and virtualenv:

    sudo apt-get install python-lxml
    sudo apt-get install libxml2-dev libxslt-dev
    sudo apt-get install python-pip build-essential python-dev
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

### Running ###

To lift the server you can run:

    python manage.py runserver <port_number>

If there is no port_number provided it will take port 8000 by default.

To run migrations to the database you have to type the following command:

    python manage.py migrate

To run unit tests type the following:

    py.test
