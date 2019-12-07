# Simple Bidding Application
It's Simple Bidding Application build using Python Flask Framework, Bootstrap.


#### Requirements and Specifications -
* Python 3.6.5 and grater
* Flask 1.1.1

And database used MySQL.

#### Setup and Run -
* First create virtual environment and activate:
<pre>
$ virtualenv venv
$ source venv/bin/activate
</pre>

* Install requirements:
<pre>
(venv) $ pip3 install -r requirements.txt
</pre>

* Configure database in config.py file:
<pre>
USERNAME = 'username'
PASSWORD = 'password'
HOST = 'host'
DATABASE = 'bidding_database'
</pre>

* Set environment variables:
<pre>
(venv) $ export EMAIL_USER='email'
(venv) $ export EMAIL_PASSWORD='password'
</pre>

* Run project:
<pre>
(venv) $ python3 run.py
</pre>

Now, you can visit [here](http://127.0.0.1:5000/) or search directly in browser http://127.0.0.1:5000/.
