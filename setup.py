from setuptools import setup

setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='json-python-push',
    url='https://github.com/coveo-labs/json-python-push',
    author='Wim Nijmeijer',
    author_email='wnijmeijer@coveo.com',
    packages=['json-python-push'],
    version='0.2',
    description='Coveo JSON Push client',
)
