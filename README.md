rsu
===
rsu is an open source version of shorten url, written in python.

rsu is licensed under the GNU/GPLv3
(http://www.gnu.org/licenses/).

Description
===========
rsu is written in python, using package gevent, redis and simplejson.
Shorten URL algorithm is using auto_increment (redis) start from 130892
(you can modify) end on sign int 64 (2^64 -1)
so the maximum url that can be shortened is 2^64 -1 - start_number
9223372036854775807 - 130892 = 9223372036854644915

Instalation
===========
rsu has been tested on Python 2.7. To use rsu,
you need to have redis, gevent and simplejson installed.

On Ubuntu Linux, you can install the packages with:

    $ sudo easy_install redis
    $ sudo easy_install simplejson

Also you need to install gevent package version >= 1.0a3
    $ wget http://gevent.googlecode.com/files/gevent-1.0xx.tar.gz
    $ tar xzf gevent-1.0xx.tar.gz
    $ cd gevent-1.0xx
    $ sudo python setup.py install

where xx is a version (a3)

Running the application
=======================

redis-server
------------
    $ mkdir /opt/redis-db
    $ redis-server [your-rsu-dir]/redis.conf

rsu-server
----------
    $ python server.py --port [port] --config-file [your-ini-config-file]

It's very recommended to running rsu behind nginx reverse proxy.

Sample nginx.conf
-----------------
View nginx_example.conf

Bug Reports
===========
Send your report and feature request to Rizky Abdilah rizky.abdilah.mail@gmail.com
