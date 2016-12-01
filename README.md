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
- Create virtual environment: `virtualenv --no-site-packages env`
- Activate environment: ` . env/bin/activate`

### Installation ###
 
- Create bluesteel project folder: `mkdir bluesteel`
- Get the code: `git clone https://<user>@bitbucket.org/llorensmarti/stronghold.git bluesteel`
- Install requisits: `cd bluesteel`, `s/install-bluesteel.py`
- Test everything is ok: `s/test-bluesteel.py`

### Install PostgreSQL database (optional)###

- Go to [http://postgresapp.com](http://postgresapp.com) and download the app.
- Install it! (in OS X means to move it to the Applications folder)
- Locate `pg_config` binary. It should live inside: `/Applications/Postgres.app/Contents/Versions/9.5/bin/`
- add that path to $PATH environment variable with: `PATH=$PATH:/Applications/Postgres.app/Contents/Versions/9.5/bin/`
- (linux only) install postgres development package: `sudo apt-get install libpq-dev python-dev`
- Install psycopg2 with: `sudo pip install psycopg2==2.6.2`
- Open a PostgreSQL shell. 
    * in macOS you can open the Postgres App shell through the icon.
    * in linux you can execute:
        * `sudo su - postgres`
        * `psql -d postgres`
- Execute command: `CREATE DATABASE bluesteeldb;`
- Execute command: `CREATE USER bluesteeluser;`
- Execute command: `GRANT ALL PRIVILEGES ON DATABASE bluesteeldb TO bluesteeluser;`
- Execute command: `ALTER USER bluesteeluser CREATEDB;`
- Execute command: `ALTER USER bluesteeluser WITH PASSWORD 'pass';`
- Execute command: `SET effective_cache_size TO '1000 MB';`
- Modify the values of the previous commands as you need.
- Modify Django settings files to use this DB instead of SQLite.
- Execute command: `./manage.py migrate`

### How to run tests? ###

- For running tests you simply need to execute: `s/test-bluesteel.py`
- If you want to run an specific set of tests, you can do: `s/test-bluesteel.py <set_name>`

### How to run BlueSteel (development) ###

- Execute command: `s/run-server.py`
- Open a browser and type the url: `localhost:28028`
- See next step `How to edit things inside BlueSteel`

### How to run BlueSteel (production) ###

- Execute command: `s/run-server.py` with parameter `--mode=production` and `--open=yes`
- Open a browser and type the url: `localhost:8080`
- See next step `How to edit things inside BlueSteel`
- You can also specify `--port` if you want it to run on another port. 

### How to edit things inside BlueSteel ###

- Create a super user if you don't have one with: `./manage.py createsuperuser`
- Open a browser and go to: `localhost:28028/admin/`
- Make login with your super user.
- Now you have privileges to create Layouts, Projects, Benchmark Definitions, etc.

### You want to contribute? ###

- Make commits as atomic and small as possible.
- Write test for all the code you write.
- Make a pull request and submit it.
- For any related question, please contact `llorens.marti@gmail.com`

### How BlueSteel source code is organized ###

All the BlueSteel code lives inside the `app/` folder and it is divided into 2 parts:

- Presenter
- Logic

The **Presneter** folder contains all the code that builds the html front web page, contains the Json public API, deals with urls, and utilizes all the apps located on the `logic/` folder to handle the data properly. All the code that interacts with the user should live in this folder.

The **Logic** folder contains all the internal apps, each of these apps is in charge of handle BlueSteel's internal data. No public API calls / Urls / Views are allowed at this level. The majority of the apps tries to follow the pattern of Controller - Model, where the Controller holds almost all the logic to interact with the models.

## Working with BlueSteel ##

### How to setup a Layout in BlueSteel ###

- Go to the main page: `localhost:28028`
- Click on `Layout` tab.
- Click on `+ Add Layout` button.
    - After the Layout is created, you will see that a default Project is created as well and associated with this layout.
    - Each project will represent a project in a git repository.
    - You can add as many projects as needed. Sometimes we need more projects to allow benchmark scripts of a Project B to benchmark old commits of Project A.

**1.- Layout setup**

- Setup a proper name for your layout.
- Select the project where all its commits will be benchmarked from BlueSteel.
- Click `Save` to save the layout information.

**2.- Project setup**

- Select a proper name for the project.
- Select a local path where the `.git` folder will be found inside the project.
    - This path indicates the git repository where all the commits will be benchmarked.
    - The default value is `.`, but you can specify another local path in the case you have many git repositories inside your project.
- Add/Modify all the commands necessary to clone this project.
    - BlueSteel workers will use this commands the first time to clone this project.
- Add/Modify all the commands necessary to fetch commits.
    - BlueSteel workers will use this commands to fetch commits, the default commands should be good to go.
- Click `Save`.

**3.- Layout Activation**

- Select `ACTIVE` on the layout setup properties.
- Click `Save`.

### How to setup a Worker in BlueSteel ###

**1.- Worker Download process**

- Go to the main page: `localhost:28028`
- Click on `Workers` tab.
- Click on `Download Worker` button.
- Uncompress the downloaded file to some convenient location.
- Execute `python core/Worker.py --auto-update=yes`
- The worker was designed to take care of everything, so at this point, everything should be working.

**2.- Worker Configuration**

- Click on `Workers` tab.
- Select the desired worker and click `Edit` button.
- Edit the description of the worker.
- Select if this worker will feed commits to BlueSteel.
    - It is recommended to only have 1 feeder, more than one will not provide any advantage.
- Select the maximum amount of reports to keep.
    - If the reports are extensive in size, it is recommended to keep as few as possible.
- Click `Save` button.

### How to setup a Benchmark Definitions in BlueSteel ###

**1.- Benchmark Definition Setup**

- Go to the main page: `localhost:28028`
- Click on `Definitions` tab.
- Click on `+ Add Definition` button.
- Click on `Edit` button of the new created definition.
- Select a proper name for the definition.
- Select the `Layout` that the definition will be referring to.
- Select the `Project` that the definition will run its commands on.
- Add/Modify the commands that will be executed for this definition.
- Select the required maximum amount of fluctuation between Benchmark Executions to send a notification (email) to the commit author.
- Add fluctuation overrides if necessary.
- Select the maximum weeks old a commit can be to rise a notification if a fluctuation happens.
- Click `Save` button.

While adding commands, you can use `{command_hash}` string. This string will be replaced by the current git commit hash.
For example, we can define the list of commands of one Benchmark Definition as:

    git checkout {commit_hash}
    git submodule update --init --recursive
    s/build_project
    s/benchmark_project

These commands will be executed for every commit replacing the `{commit_hash}` by the proper value, for example:

    git checkout 0000100001000010000100001000010000100001
    git submodule update --init --recursive
    s/build_project
    s/benchmark_project


**2.- Benchmark Executions**

For every benchmark definition and every commit of that benchmark definition's project, BlueSteel will create a Benchmark Execution. A Benchmark Execution will hold the results of the commands specified on the Benchmark Definition.

BlueSteel can understand 3 types of outputs now:

**Text**

If the output of a command is a json string with the form below, BlueSteel will show a text on the benchmark execution page. In this case, "data" field should be a string.


```
#!python

{
    "id" : <id_here>
    "type" : "text",
    "data" : "This is a text that will be shown on the result page."
}
```

**Vertical Bars**

If the output of a command is a json string that follows the form below, BlueSteel will show a chart with vertical bars representing the "data" property. In this case, the "data" field should be a vector of numbers.


```
#!python

{
    "id" : <id_here>
    "type" : "vertical_bars",
    "data" : [28, 28, 29, 30, 30]
}
```

- In the case of vertical bars, BlueSteel knows how to stack them to visualize in a single chart many commits. This is helpful to see which is the performance across several commits.

**Unknown output**

If the command output is something different than the previous two types (text, vertical_bars), BlueSteel will mark the output as an unknown type and will show the output as it is in the result page.