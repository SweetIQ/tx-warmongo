import setuptools


def parse_requirements():
    reqs = open('requirements.txt', 'r')
    raw_req = reqs.read()
    reqs.close()
    return raw_req.split('\n')


setuptools.setup(
    name='tx-warmongo',
    version='0.1.0',
    description='JSON-Schema-based ORM for MongoDB',
    author='Rob Britton',
    author_email='rob@robbritton.com',
    url='http://github.com/SweetiQ/tx-warmongo',
    keywords=["mongodb", "jsonschema", "twisted"],
    packages=['txwarmongo'],
    package_data={"tx-warmongo": ["requirements.txt"]},
    include_package_data=True,
    install_requires=parse_requirements(),
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Database :: Front-Ends"
    ],
    long_description="""\
  JSON-Schema-based ORM for MongoDB
  ---------------------------------

  Allows you to build models validated against a JSON-schema file, and save
  them to MongoDB. This version is built off of Twisted for performance.
""",
)
