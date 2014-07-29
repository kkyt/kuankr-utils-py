from setuptools import setup

#http://docs.python.org/2/distutils/setupscript.html

setup(
    name='kuankr-utils',
    version='0.0.1',

    author='dev',
    author_email='dev@agutong.com',
    url='http://git.agutong.com/dev/kuankr-utils',

    license='LICENSE',
    description='kuankr utils',
    long_description=open('README.md').read(),

    packages=[
      'kuankr_utils',
    ],

    package_data = {
        #'kuankr_utils': ['config/*.yml'],
    },

    data_files=[
        #('/etc/init.d', ['bin/init-kuankr-utils'])
    ],

    scripts=[
    ],

    install_requires=[
        #basic
        "six",
        "simplejson",

        #datetime
        "pytz",
        "tzlocal",
        "aniso8601",

        #test
        "pytest",
        "colorlog",
        "colorama",

        #flask
        "blinker",
        "flask",
        "Flask-API",
        "Flask-MongoEngine",

        #http
        "requests",

        #mongodb
        "mongokit",
        "pymongo",

        #log
        "python-logstash",

        #gevent
        "gevent>=1.0",
    ],

    dependency_links=[
        #zip/tar urls
    ]
)
