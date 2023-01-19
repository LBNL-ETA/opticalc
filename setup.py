from setuptools import setup, find_packages

setup(
    name='opticalc',
    version='0.0.10',
    long_description='',
    # tell setuptools to look for any packages under 'src'
    packages=find_packages(where='src'),
    # tell setuptools that all packages will be under the 'src' directory
    # and nowhere else
    package_dir={'': 'src'},
    install_requires=['pydantic>=1.9.0',
                      'py_igsdb_base_data@git+https://github.com/LBNL-ETA/py_igsdb_base_data@main',
                      'pywincalc==v2.4.3'],
    test_suite='tests',
    zip_safe=False,
)
