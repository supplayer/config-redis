import setuptools

with open("README.md") as fh:
    long_description = fh.read()

setuptools.setup(
    name="proj-config",
    version="0.0.7",
    author="RoyXing",
    author_email="x254724521@hotmail.com",
    description="get proj config args from redis",
    license='BSD',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="gitlab.com",
    packages=setuptools.find_packages(exclude=('tests',)),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=['redis==3.4.1']
)
