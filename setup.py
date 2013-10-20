from setuptools import setup, find_packages

setup(
    name='logging-fancyformatter',
    version='0.1.0',
    description='A pluggable logging.Formatter that can vary formatting based on the logger name.',
    author='Nathan Wright',
    author_email='thatnateguy@gmail.com',
    url='http://github.com/natedub/logging-fancyformatter',
    license='BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
    ],
    packages=find_packages(),
)
