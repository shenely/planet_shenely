Planet Shenely
===================

Welcome to Planet Shenely!

Installation
---------------------

Go to the planet_shenely directory and create a source distribution:
```bash
cd ./planet_shenely
python setup.py sdist
```
The distribution will be packaged as a *.tar.gz (.zip on Windodes) by default.

Go to the dist/ directory and use pip to install the package:
```bash
sudo ./dist/
sudo pip install planet_shenely-0.1.tar.gz
```
Prompts may appear to install dependencies.

From anywhere, run the planet_shenely module in python:
```bash
sudo python -m planet_shenely
```
By default be reached at http://localhost:8080.

Hit it! The REST API should now be active.
