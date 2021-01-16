from setuptools import setup

from mockthink.version import VERSION

setup(
    name="mockthink",
    zip_safe=True,
    version=VERSION,
    description="A pure-python in-memory mock of rethinkdb",
    url="http://github.com/scivey/mockthink",
    maintainer="Scott Ivey",
    maintainer_email="scott.ivey@gmail.com",
    packages=['mockthink'],
    package_dir={'mockthink': 'mockthink'},
    install_requires=['rethinkdb>=2.4.8', 'python-dateutil', 'future']
)
