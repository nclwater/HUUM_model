import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="huum_model-SBerendsen",
    version="1.0.0",
    author="Sven Berendsen",
    author_email="s.berendsen2@newcastle.ac.uk",
    description="Household Utility Usage Model system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nclwater/HUUM_model/",
    project_urls={
        "Bug Tracker": "https://github.com/nclwater/HUUM_model/-/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache 2.0 License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
