"""
demo.py

Christopher Jones, 10 Sep 2020

Demo of using flask with Oracle Database

Before running, set these environment variables:

    PYTHON_USERNAME       - your DB username
    PYTHON_PASSWORD       - your DB password
    PYTHON_CONNECTSTRING  - the connection string to the DB, e.g. "example.com/XEPDB1"
    PORT                  - port the web server will listen on.  The default in 8080

"""

import os
import sys
import cx_Oracle
from flask import Flask

################################################################################
#
# On macOS tell cx_Oracle 8 where the Instant Client libraries are.  You can do
# the same on Windows, or add the directories to PATH.  On Linux, use ldconfig
# or LD_LIBRARY_PATH.  cx_Oracle installation instructions are at:
# https://cx-oracle.readthedocs.io/en/latest/user_guide/installation.html
if sys.platform.startswith("darwin"):
    cx_Oracle.init_oracle_client(lib_dir=os.environ.get("HOME")+"/instantclient_19_3")
elif sys.platform.startswith("win32"):
    cx_Oracle.init_oracle_client(lib_dir=r"c:\oracle\instantclient_19_8")

################################################################################
#
# Start a connection pool.
#
# Connection pools allow multiple, concurrent web requests to be efficiently
# handled.  The alternative would be to open a new connection for each use
# which would be very slow, inefficient, and not scalable.  Connection pools
# support Oracle high availability features.
#
# Doc link: https://cx-oracle.readthedocs.io/en/latest/user_guide/connection_handling.html#connection-pooling


# init_session(): a 'session callback' to efficiently set any initial state
# that each connection should have.
#
# If you have multiple SQL statements, then put them all in a PL/SQL anonymous
# block with BEGIN/END so you only call execute() once.  This is shown later in
# create_schema().
#
# This particular demo doesn't use dates, so sessionCallback could be omitted,
# but it does show settings many apps would use.
#
# Note there is no explicit 'close cursor' or 'close connection'.  At the
# end-of-scope when init_session() finishes, the cursor and connection will be
# closed automatically.  In real apps with a bigger code base, you will want to
# close each connection as early as possible so another web request can use it.
#
# Doc link: https://cx-oracle.readthedocs.io/en/latest/user_guide/connection_handling.html#session-callbacks-for-setting-pooled-connection-state
#
def init_session(connection, requestedTag_ignored):
    cursor = connection.cursor()
    cursor.execute("""
        ALTER SESSION SET
          TIME_ZONE = 'UTC'
          NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI'""")

# start_pool(): starts the connection pool
def start_pool():

    # Generally a fixed-size pool is recommended, i.e. pool_min=pool_max.
    # Here the pool contains 4 connections, which is fine for 4 concurrent
    # users.
    #
    # The "get mode" is chosen so that if all connections are already in use, any
    # subsequent acquire() will wait for one to become available.

    pool_min = 4
    pool_max = 4
    pool_inc = 0
    pool_gmd = cx_Oracle.SPOOL_ATTRVAL_WAIT

    print("Connecting to", "192.168.122.105:1521/ORCLCDB")

    pool = cx_Oracle.SessionPool(user="roberto",
                                 password="roberto",
                                 dsn="192.168.122.105:1521/ORCLCDB",
                                 min=pool_min,
                                 max=pool_max,
                                 increment=pool_inc,
                                 threaded=True,
                                 getmode=pool_gmd,
                                 sessionCallback=init_session)

    return pool

################################################################################
#
# create_schema(): drop and create the demo table, and add a row


################################################################################
#
# Specify some routes
#
# The default route will display a welcome message:
#   http://127.0.0.1:8080/
#
# To insert a new user 'fred' you can call:
#    http://127.0.0.1:8080/post/fred
#
# To find a username you can pass an id, for example 1:
#   http://127.0.0.1:8080/user/1
#

app = Flask(__name__)

# Display a welcome message on the 'home' page
@app.route('/')
def index():
    return "Welcome to the demo app"


# Show the username for a given id
@app.route('/emp/<int:id>')
def show_username(id):
    connection = pool.acquire()
    cursor = connection.cursor()
    cursor.execute("select * from emp where id = :idbv", [id])
    r = cursor.fetchone()
    return (r[0] if r else "Unknown user id")

################################################################################
#
# Initialization is done once at startup time
#
if __name__ == '__main__':

    # Start a pool of connections
    pool = start_pool()

    # Create a demo table
    create_schema()

    # Start a webserver
    app.run(port=int(os.environ.get('PORT', '8080')))