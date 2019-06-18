from setuptools import setup, find_packages
from registers.core import __version__


setup(
    name="registers",
    version=__version__,
    license="MIT",
    packages=find_packages(),
    package_data={
        '': ["LICENSE"],
        'registers': ['data/_redirects', 'data/openapi.json']
    },
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=[
        "Click~=7.0",
        "PyYAML~=5.1",
        "Jinja2~=2.10",
    ],
    entry_points="""
        [console_scripts]
        registers=registers.cli:cli
    """,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development",
    ],
)
