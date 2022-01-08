# First Time Setup

Create a venv

```
python3 -m venv venv
```

Depending on your shell and platform, activate the venv using the appropriate command:\\

### POSIX

```
bash/zsh    $ source <venv>/bin/activate

fish        $ source <venv>/bin/activate.fish

csh/tcsh    $ source <venv>/bin/activate.csh

PowerShell Core  $ <venv>/bin/Activate.ps1
```

### Windows

```
cmd.exe  C:\> <venv>\Scripts\activate.bat

PowerShell  PS C:\> <venv>\Scripts\Activate.ps1
```

Now, run

```
pip3 install -r requirements.txt
```

# How To Run

To run the application, enable the venv and run

```
python3 ./src/wsgi.py         [-c=CONFIG_FILE] [--help]
```

# Creating New Endpoints

See https://flask-restx.readthedocs.io/en/latest/quickstart.html#a-minimal-api

# Creating New Namespaces

To create a new namespace, create a folder under the latest API version named `NAMESPACE` and create a file named `routes.py`

The file should look like:

```python
from flask import current_app as app
from flask_restx import Namespace

api = Namespace('NAMESPACE NAME', description='NAMESPACE DESCRIPTION', path='/NAMESPACE PATH')

# register routes
...
```

Add this to `src/app/VERSION/__init__.py`

```python
api.add_namespace(NAMESPACE)
```

# Creating New Versions

To create a new API version, create a new folder named `VERSION`

Create `__init__.py` in the new folder

The file should look like:

```python
from flask import Blueprint, blueprints
from flask_restx import Api

# create api
blueprint = Blueprint('api', __name__, url_prefix='/VERSION')
api = Api(blueprint, title='Flourish API', version='VERSION', description='API to interact with the Flourish backend')

# mount endpoints
...
```

Add this to `src/app/__init__.py`

```python
from .VERSION import blueprint as VERSION
app.register_blueprint(VERSION)
```
