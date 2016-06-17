# BlueSteel #

### Description ###

- BlueSteel is a tool to help track your project performance per commit and per branch.

### License ###

- This project is released under the terms of the license specified in the project's repository or if not specified, under the MIT License.

### Preparation ###

- Install Python 2.7.10
- Install pip: `sudo easy_install pip`
- Install virtualenv: `sudo pip install virtualenv`
- Create a Bluesteel folder: `mkdir bluesteel-project`, `cd bluesteel-project`
- Create virtual environment: `virtualenv env`
- Activate environment: ` . env/bin/activate`

### Installation ###
 
- Create bluesteel project folder: `mkdir bluesteel`
- Get the code: `git clone https://<user>@bitbucket.org/llorensmarti/stronghold.git bluesteel`
- Install requisits: `cd bluesteel`, `sudo s/install-bluesteel.py`
- Test everything is ok: `s/test-bluesteel.py`

### Install PostgreSQL database (optional)###

- Go to [http://postgresapp.com](http://postgresapp.com) and download the app.
- Install it! (in OS X means to move it to the Applications folder)
- Locate `pg_config` binary. It should live inside: `/Applications/Postgres.app/Contents/Versions/9.3/bin/`
- add that path to $PATH environment variable with: `PATH=$PATH:/Applications/Postgres.app/Contents/Versions/9.3/bin/`
- Install psycopg2 with: `sudo pip install psycopg2==2.6.1`

### How to run tests? ###

- For running tests you simply need to execute: `s/test-bluesteel.py`
- If you want to run an specific set of tests, you can do: `s/test-bluesteel.py <set_name>`

### How to run BlueSteel (development) ###

- Execute `s/run-server-development.py`
- Open a browser and type the url: `localhost:28028`
- See next step `How to edit things inside BlueSteel`

### How to run BlueSteel (production) ###

- Execute `s/run-server-production.py`
- Open a browser and type the url: `localhost:8080`
- See next step `How to edit things inside BlueSteel`

### How to edit things inside BlueSteel ###

- Open a browser and go to: `localhost:28028/admin/`
- Make login with your super user.
- Now you have privileges to create Layouts, Projects, Benchmark Definitions, etc.

### You want to contribute? ###

- Make commits as atomic and small as possible.
- Write test for all the code you write.
- Make a pull request and submit it.
- For any related question, please contact `llorens.marti@gmail.com`