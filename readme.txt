bilal first clone this repo and than do the following inside the repo directory

mkdir venv
python -m venv venv
venv\scripts\activate.bat
pip install -r requirements.txt

and than whenever you want to run the project first make sure your virtual environment is activated and you run the run.py file from that terminal window in which you have activated venv.

oyee bilal i have added a zip file which is patched version of an unmaintained library called marshmallow_mongoengine its used for serialization, what you gotta do is, after setting up venv, extract this zip and inside there will be a folder called marshmallow_mongoengine-a111... and inside that there will be another folder called marshmallow_mongoengine it should contain python source files, copy all those files and paste them into /venv/lib/site_packages/marshmallow_mongoengine.
hope you can get it right.
everything is working i have tested all of it
