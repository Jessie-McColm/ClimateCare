# ClimateCare - Technical Document

## Requirements

In order to locally run and test this application, it is 
required for machine to have [**Python 3.x**](https://www.python.org/downloads/)
installed, and added to your system's path.

It is further required for your Python environment to have
**django** and **haversine** installed. These are the only
two external dependencies.

If you have the package installer for python, or
[**pip**](https://pypi.org/project/pip/), you can install
these dependencies through your command line:
- Open the terminal
- Type and execute `pip install django`, and wait for it to 
finish installing
- Type and execute `pip install haversine`.

## Running Tests

A total of 40 tests have been written for this project - 6
for the "users" section of the app, and 32 for the "climate"
section.

In order to run all the tests, navigate to the 
`ClimateCare/creature_care` directory in a command terminal
(using the `cd path/to/our/app/ClimateCare/creature_care
command`), and then execute `python manage.py test` on Linux
and macOS machines, or `py manage.py test` for Windows 
machines.

This will then execute all the tests in the `test.py` files.

If instead you desire to only run the tests for the users view
or climate view, you can execute `python manage.py test users` or
`python manage.py test climate`, respectively. On Windows
machines, replace `python` with `py`.

## Cloud Server

The ClimateCare app is currently deployed at
[climatecare.pythonanywhere.com](https://climatecare.pythonanywhere.com/climate/kitty).
Any changes made to the git repository are **not** automatically
reflected in the cloud deployment, and instead have to be
manually cloned and reloaded.

Updating the server is a 9-step process:
- Log into the ClimateCare account at [**pythonanywhere**](https://www.pythonanywhere.com)
- Open the terminal for the remote server
- Delete the server's version of the application
- Use the `git clone` command to copy the latest version of
the repository to the remote server
- Exit the terminal, and navigate to the "files" tab
- Navigate to the "settings.py" file
- Set `DEBUG` to `False`, and add 'climatecare.pythonanywhere.com'
the allowed hosts
- Exit the "files" tab and navigate to the "web" tab
- Reload the server

After completing the above steps, the latest version of the project
should be running on the server. If any errors occur,
consult the server's error log.

## Running Locally

In order to run the project locally, you must ensure that you
have the needed requirements, as described above.

Assuming that you do, running the server locally is a 3-step
process:
- Open the command terminal
- Using the `cd` command, navigate to the `/.../ClimateCare/creature_care`
directory
- Execute the command `py manage.py runserver` for Windows, or `python manage.py runserver`
for Linux/MacOS.

## Modifying the Database

In order for developers and game masters to add items to the database, either
locally or on the cloud server, you can navigate to the
[climatecare.pythonanywhere.com/admin](https://climatecare.pythonanywhere.com/admin)
page.

If you're logged in as an admin user, you should be
prompted with a page that allows you to add, remove, and modify
database items.