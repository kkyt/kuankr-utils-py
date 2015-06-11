from setuptools import setup

#http://docs.python.org/2/distutils/setupscript.html

setup(
    name='kuankr-utils',
    version='0.3.0',

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

    entry_points='''
        [console_scripts]
        kuankr-api=kuankr_utils.api_cli:main
    ''',

    install_requires=[
        #basic
        "six",
        "enum34",
        "simplejson",
        "namedlist",

        #datetime
        "pytz",
        "tzlocal",
        "aniso8601",
        "python-dateutil",

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
        "pymongo<3.0",

        #log
        "python-logstash",
        "raven",

        #debug
        "faulthandler",
        "Dozer",

        #gevent
        "gevent>=1.0",
        "gunicorn",

        #yaml
        "PyYAML",
        "ujson",

        #string
        "inflection",

        #network
        "netifaces"
    ],

    dependency_links=[
        #zip/tar urls
    ]
)
