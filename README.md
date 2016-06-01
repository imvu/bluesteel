# BlueSteel #

### Description ###

- BlueSteel is a tool to help track your project performance per commit and per branch.

### License ###

- This project is released under the terms of the license specified in the project's repository or if not specified, under the MIT License.

### Preparation ###

- install Python 2.7.10
- install pip: `sudo easy_install pip`
- install virtualenv: `sudo pip install virtualenv`
- create a Bluesteel folder: `mkdir bluesteel-project`, `cd bluesteel-project`
- create virtual environment: `virtualenv env`
- activate environment: ` . env/bin/activate`

### Installation ###
 
- create bluesteel project folder: `mkdir bluesteel`
- Get the code: `git clone https://<user>@bitbucket.org/llorensmarti/stronghold.git bluesteel`
- install requisits: `cd bluesteel`, `sudo s/install-bluesteel.py`
- test everything is ok: `s/test-bluesteel.py`

### Install PostgreSQL database (optional)###

- go to [http://postgresapp.com](http://postgresapp.com) and download the app
- install it! (in OS X means to move it to the Applications folder)
- locate `pg_config` binary. It should live inside: `/Applications/Postgres.app/Contents/Versions/9.3/bin/`
- add that path to $PATH environment variable with: `PATH=$PATH:/Applications/Postgres.app/Contents/Versions/9.3/bin/`
- install psycopg2 with: `sudo pip install psycopg2==2.6.1`

### How to run tests? ###

- For running tests you simply need to execute: `s/test-bluesteel.py`
- If you want to run an specific set of tests, you can do: `s/test-bluesteel.py <set_name>`

### How to run BlueSteel ###

- Execute `s/run-server-development.py`
- Open a browser and type the url: `localhost:28028`

### You want to contribute? ###

- Make commits as atomic and small as possible.
- Write test for all the code you write.
- For any related question, please contact `llorens.marti@gmail.com`