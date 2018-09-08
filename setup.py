from setuptools import setup

#http://docs.python.org/2/distutils/setupscript.html

setup(
    name='kuankr-utils',
    version='0.3.3',

    author='dev',
    author_email='dev@agutong.com',
    url='https://github.com/kkyt/kuankr-utils-py',

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
        "six==1.9.0",
        "enum34==1.0.4",
        "simplejson==3.6.5",
        "namedlist==1.6",

        #datetime
        "pytz==2015.2",
        "tzlocal==1.1.3",
        "aniso8601==0.92",
        "python-dateutil==2.4.2",

        #test
        "pytest==2.6.4",
        "colorlog==2.6.0",
        "colorama==0.3.3",

        #flask
        "blinker==1.3",
        "flask==0.10.1",
        "Flask-API==0.6.2",
        "Flask-MongoEngine==0.7.1",

        #http
        "requests==2.7.0",

        #mongodb
        "mongokit==0.9.1.1",
        "pymongo<3.0",

        #log
        "python-logstash==0.4.2",
        "raven==5.3.1",

        #debug
        "faulthandler==2.4",
        "Dozer==0.4",

        #gevent
        "gevent>=1.0",
        "gunicorn==19.1.1",

        #yaml
        "PyYAML==3.11",
        "ujson==1.33",

        #string
        "inflection==0.3.1",

        #network
        "netifaces==0.10.7",

        #redis
        "redis==2.10.3",
        
        'msgpack==0.5.6'
    ],

    dependency_links=[
        #zip/tar urls
    ]
)
