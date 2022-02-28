
from setuptools import find_packages, setup

setup(
    name='django-native-call',
    version='0.0.3',
    packages=find_packages(),
    package_data={'': ['native_call/templates/native_call/*.html']},
    include_package_data=True,
    url='',
    license='apache',
    author='jraylan',
    author_email='jeffersonraylan@gmail.com',
    description='Allow web pages to call functions in django\'s backend',
    install_requires=[
        'django>=1.11.29'
    ]
)
