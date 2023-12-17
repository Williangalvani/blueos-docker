#!/usr/bin/env python3

import setuptools

setuptools.setup(
    name="pardal",
    version="0.1.0",
    description="Web service to help with speed and latency tests",
    license="MIT",
    install_requires=[
        "aiohttp == 3.7.4",
        "chardet==3.0.4",
        "commonwealth == 0.1.0",
        "chardet==3.0.4",
        "loguru == 0.5.3",
    ],
)
