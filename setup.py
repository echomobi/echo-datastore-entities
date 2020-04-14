import setuptools


with open("requirements.txt", "r") as requirements:
    install_requires = requirements.read().strip().split("\n")

with open("README.md", "r") as readme:
    long_description = readme.read()

with open("RELEASE", "r") as release:
    version = release.read().strip()

setuptools.setup(
    name="echo-datastore-entities",
    version=version,
    author="Echo Mobile",
    author_email="engineering@echomobile.io",
    description="Client library for use with Google Cloud Datastore to provide an entities concept",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/echomobi/echo-datastore-entities",
    packages=['echo'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=install_requires
)
