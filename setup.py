from setuptools import setup


setup(
    name="rethinkdb_mock",
    zip_safe=True,
    version='0.10.1',
    description="A pure-python in-memory mock of rethinkdb (formerly MockThink)",
    url="https://github.com/Inveracity/rethinkdb-mock",
    maintainer="Christopher Baklid",
    maintainer_email="cbaklid@gmail.com",
    packages=['rethinkdb_mock'],
    package_dir={'rethinkdb_mock': 'rethinkdb_mock'},
    install_requires=['rethinkdb>=2.4.8', 'python-dateutil', 'future'],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Database",
        "Topic :: Software Development :: Testing :: Mocking",
    ],
    python_requires='>=3.7',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
