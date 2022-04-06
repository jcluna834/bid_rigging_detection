# Bid Rigging Detection

1. Bid Rigging detection using ....
2. Input text will be matched against all the documents present in the DB(`document` table) to get the maximum similarity score.

### Requirements
Python 3.x, pip3, MySQL

### How to run?

1. Move to ```<project-dir>```, create virual environment and then activate it as

```sh
$ cd <project-dir>
$ virtualenv .environment
$ source .environment/bin/activate
```

2. Edit configuration under ```settings.py```. i.e. provide configuration/settings related to DB and other constants.

> If you are using PyCharm then environment variables can be specified under `run configuration`.

3. Add project to ```PYTHONPATH``` as 

```sh 
$ export PYTHONPATH="$PYTHONPATH:." # . corresponds to current directory(project-dir)
```

4. Under ```<project-dir>``` install requirements/dependencies as 

```sh 
$ pip3 install -r requirements.txt
```

5. Then run test cases as -

```sh
$ python -m unittest discover -s 'tests' -p '*.py'
```

```sh
$ python -m nltk.downloader stopwords
```


6. Run server as - 
```sh
$ python app.py 
```

> Now you can access the application by visiting ```{protocol}://{host}:{port}```. For localhost it is ```http://localhost:5000```.


### Applications & Endpoints

There are following three APIs -

### TODO - 
1. Use a wsgi server like Gunicorn.
2. Centralized logging.


### comandos PC personal
py -> python 3
py -m pip ...