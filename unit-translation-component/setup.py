from setuptools import setup

setup(name='unit_translation_component',
      version='1.0',
      description='',
      url='https://gitlab.tue.nl/sep-group-10/sep-2020-group-10.git',
      author='Stefan Friptu',
      author_email='p.friptu@student.tue.nl',
      license='MIT',
	  classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      python_requires='>=3.6',
      packages=['unit_translation_component'],
	  install_requires=[
	      'rdflib==5.0.0',
		  'requests==2.22.0',
		  'SPARQLWrapper==1.8.5',
          'redis==3.5.3',
		  'progress==1.5',
		  'pyspellchecker==0.5.4'
	  ],
	  include_package_data = True,
      zip_safe=False)
