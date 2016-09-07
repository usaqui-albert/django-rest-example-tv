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
