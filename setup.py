# -*- coding: utf-8 -*-


from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='Edt',
    version='0.1.0',
    description="Package du back-end de l'emploie du temps",
    long_description=readme,
    url='https://github.com/DUT-Info-Montreuil/SAE-5.A-Back-EDT-APP.git',
    license=license,
    packages=find_packages("src")
)






