from setuptools import setup, find_packages

setup(
    name="registers",
    version="0.1.0",
    licence="MIT",
    packages=find_packages(),
    package_data={'': ["LICENSE"], 'registers': ['data/_redirects']},
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=[
        "Click~=7.0",
    ],
    entry_points='''
        [console_scripts]
        registers=registers.cli:cli
    ''',
)
