from setuptools import setup

setup(
    name='django-native-call',
    version='0.1.1',
    packages=['native_call', 'native_call.migrations'],
    url='',
    license='apache',
    author='jraylan',
    author_email='jeffersonraylan@gmail.com',
    description='Allow web pages to call functions in django\'s backend',
    install_requires=[
        'django>=1.11.29'
    ]
)
