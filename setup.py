import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Roadster",
    version="0.0.1",
    author="Pablo Duboue",
    author_email="pablo.duboue@gmail.com",
    description="Feature server for distance to closest road feature",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Textualization/Roadster",
    packages=setuptools.find_packages(),
    keywords="GIS feature engineering osm openstreetmap road data science",
    install_requires=[
        "Shapely>=1.8.0",
        "PyKrige>=1.6.1",
        "Fiona>=1.8.20",
        "numpy>=1.21.4",
        "scikit-image>=0.19.1",
        "Flask>=2.0",
    ],
    extras_require={},
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "roadster-one-tile=roadster.cli:one_tile",
            "roadster-one-coord=roadster.cli:one_coord",
            "list-layers=roadster.cli:list_layers",
        ],
    },
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: Web",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
    ],
    python_requires=">=3.9",
)
