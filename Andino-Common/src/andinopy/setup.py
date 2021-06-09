#       _              _ _
#      / \   _ __   __| (_)_ __   ___  _ __  _   _
#     / _ \ | '_ \ / _` | | '_ \ / _ \| '_ \| | | |
#    / ___ \| | | | (_| | | | | | (_) | |_) | |_| |
#   /_/   \_\_| |_|\__,_|_|_| |_|\___/| .__/ \__, |
#                                     |_|    |___/
# by Jakob Groß
from setuptools import find_packages, setup

setup(
    name="andinopy",
    packages=find_packages(include=['andinopy']),
    version='0.2',
    description="Library for Andino.Systems Products",
    author="Jakob Groß - Clear Systems GmbH",
    author_email="jakob.gross@clearsystems.de",
    maintainer_email="support@clearsystems.de",
    url="andino.systems",
    download_url="TODO",
    license='Apache-2.0',
    install_requires=['gpiozero', 'smbus2', 'pyserial', 'adafruit-circuitpython-ssd1306', 'Pillow', 'adafruit-blinka'],
    data_files=[('resources', ['andinopy/resources/FIRACODE.TTF'])],
    classifiers=["Development Status :: 4 - Beta",
                 "Operating System :: POSIX :: Linux",
                 "License :: OSI Approved :: Apache Software License",
                 "Topic :: System :: Operating System Kernels :: Linux",
                 "Topic :: System :: Networking",
                 "Topic :: System :: Hardware",
                 "Topic :: Home Automation"],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='pytest'
)
