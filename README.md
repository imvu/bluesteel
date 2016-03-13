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

### How to run tests? ###

- For running tests you simply need to execute: `s/test-bluesteel.py`
- If you want to run an specific set of tests, you can do: `s/test-bluesteel.py <set_name>`

### How to run BlueSteel ###

- Execute `s/run-server-development.py`
- Open a browser and type the url: `localhost:28028/main/view/`

### You want to contribute? ###

- Make commits as atomic and small as possible.
- Write test for all the code you write.