from setuptools import setup, find_packages

setup(
    name='opticalc',
    version='0.0.7',
    long_description='',
    # tell setuptools to look for any packages under 'src'
    packages=find_packages(where='src'),
    # tell setuptools that all packages will be under the 'src' directory
    # and nowhere else
    package_dir={'': 'src'},
    install_requires=['pydantic>=1.9.0',
                      'py_igsdb_optical_data @ git+https://github.com/LBNL-ETA/py_igsdb_optical_data@main',
                      'pywincalc @ git+https://github.com/LBNL-ETA/pywincalc@v2.4.2'],
    test_suite='tests',
    zip_safe=False,
)
