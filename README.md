# <a href="http://newera412.com/" target="_blank">NewERA412 Platform</a>

* Organization: ReEntry412
* Client Contact: <a href="mailto:bvbaseball42@gmail.com">`Taili Thompson`</a>
* Student Consultants: <a href="https://github.com/brentthongg">`Brent Hong`</a>, <a href="">`Max Kornyev`</a>, and <a href="https://github.com/epiccrash">`Joseph Perrino`</a>
* `See the GitHub Wiki for more important information`

### Application Versions

* `Python 3.6.6`
* `Django 3.0.2 final`
* `Twilio 6.38.0`
* See `requirements.txt` for a complete enumaration of package dependencies

***

### Dependency Setup (DEVELOPMENT)

###### First Time: 

The following will set up a python environment for the cloned project. This allows you to keep all your project dependencies (or `pip modules`) in isolation, and running their correct versions. 

* Create the env: `virtualenv django_env` (set `django_env` to your preferred env name) 
* Start the env: `source django_env/bin/activate`
* Install all dependencies: `pip install -r requirements.txt`
* Exit the env: `deactivate` or exit terminal 

###### De Futuro (important):  

* **After installing new python libraries to your pipenv, you must update the `requirements.txt` file**
* Do this by running `pip freeze > requirements.txt`

### Test Suite 

* Run the suite with `./manage.py test` (Only model tests are incuded)

### Included Scripts 

###### Populate (DEPRECATED)

* `python manage.py populate`
* Creates an sow user (**is_staff**): User(username='sow', password='sow')
* And an admin (**is_superuser**): User(username='admin', password='admin')

###### Drop (DEPRECATED)

* `python manage.py drop`
* Destroys all user objects

###### Load Tags and Resources

* `python manage.py load_tags_and_resources`
* Loads the values and initial sets of tags and resources from a CSV ("Northside PD Service Providers.csv" in the root directory)
	* Loads a resource with a name, tag, website, contact name, contact position, phone number, fax number, contact email, address, city, state, zip code, second address line, and/or description, should they be provided
	* Tags are loaded with the resources
