#!/bin/sh
sudo pip3 uninstall -y andinopy
sudo python3 setup.py bdist_wheel
sudo pip3 install dist/andinopy-0.2-py3-none-any.whl
