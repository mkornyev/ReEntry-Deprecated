# <a href="https://newera-app.herokuapp.com/" target="_blank">NewERA412 Platform</a>

* Organization: ReEntry412
* Client Contact: <a href="mailto:Taili.Thompson@alleghenycounty.us">`Taili Thompson`</a>
* Student Consultants: <a href="https://github.com/brentthongg">`Brent Hong`</a>, <a href="">`Max Kornyev`</a>, and <a href="https://github.com/epiccrash">`Joseph Perrino`</a>

### Versions

* `Python 3.6.6`
* `Django 3.0.2 final`

### Dependency Setup 

###### First Time: 

The following will set up a python environment **in the same directory** as the cloned project. This allows you to keep all your project dependencies (or `pip modules`) in isolation, and running their correct versions. 

* Create the env: `virtualenv django_env` (set `django_env` to your preferred env name) 
* Start the env: `source django_env/bin/activate`
* Install all dependencies: `pip install -r requirements.txt`
* Exit the env: `deactivate` 

###### De Futuro (important):  

* **After installing new python libraries to your pipenv, you must update the `requirements.txt` file** 
* Do this by running `pip freeze > requirements.txt`

### Test Suite 

* Run the suite with `./manage.py test`

### Included Scripts 

###### Populate 

* `python manage.py populate`
* Creates an sow user (**is_staff**): User(username='sow', password='sow')
* And an admin (**is_superuser**): User(username='admin', password='admin')

###### Drop

* `python manage.py drop`
* Destroys created objects
