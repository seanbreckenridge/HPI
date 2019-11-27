#!/usr/bin/env python3
from setuptools import setup, find_packages

def main():
    setup(
        name='my',
        version='0.5',
        description='A Python interface to my life',
        url='https://github.com/karlicoss/my',
        author='Dmitrii Gerasimov',
        author_email='karlicoss@gmail.com',

        classifiers=[
            'Programming Language :: Python :: 3 :: Only',
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: End Users/Desktop',
            'Topic :: Scientific/Engineering :: Information Analysis',
        ],
        keywords=["pkm", "pim", "quantified-self"],

        # TODO eh, perhaps should use 'src'...
        # package_dir={'': ''},
        packages=find_packages(),
        package_data={
            'my': ['py.typed'],
        },

        python_requires='>=3.5', # depends on the modules though..
    )

if __name__ == '__main__':
    main()