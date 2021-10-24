from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

with open('requirements.txt') as f:
    all_reqs = f.read().split('\n')
install_requires = [x.strip() for x in all_reqs]

setup(
    name="simframe",
    version="0.0.1",
    packages=['simframe'],
    install_requires = install_requires,
    description='Distributed Multi Agent Simulation Framework using Ray',
    long_description=readme,
    author='Rui Hirano',
    license='MIT',
)