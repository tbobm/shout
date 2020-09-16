from setuptools import setup


deps = ['requests', 'etnawrapper>=2.1.1', 'click']

setup(
    name="etna-shout",
    version="1.1.1",
    description="Command line tool to interact with ETNA's APIs",
    url="https://github.com/tbobm/shout",
    author='Theo "Bob" Massard',
    author_email="massar_t@etna-alternance.net",
    license="Apache License 2.0",
    packages=['shout'],
    install_requires=deps,
    entry_points={"console_scripts": ["shout=shout:main"]},
)
