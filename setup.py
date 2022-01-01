import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name="milp_imgcomp",
    version="0.0.1",
    author="Fedor Glazov",
    author_email="fedorglazov@gmail.com",
    description="A lossless image compressor which is based on a mixed integer linear program.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FGlazov/milp-image",
    packages=setuptools.find_packages(where="milp_imgcomp"),
    package_dir={"": "milp_imgcomp"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Eclipse Public License 2.0 (EPL-2.0)",
        "Operating System :: OS Independent",
    ],
    install_requires=required,
)
