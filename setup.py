
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fstreemap",
    version="0.0.2",
    author="Or Barzilay",
    author_email="turchy@gmail.com",
    description="Interactive filesystem treemaps",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "jinja2",
        "tqdm",
        "plotly",
        "pywebview",
    ],

    entry_points={
        "console_scripts": [
            "fstreemap = fstreemap.__main__:main",
        ],
    }
)
