from setuptools import setup, find_packages
setup(
    name = "django-fbgraph",
    version = "0.0",
    packages = find_packages(),
    scripts = [],
    
    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = ['docutils>=0.3'],
    
    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'fbgraph' package, too:
        'fbgraph': ['*.msg'],
        },

    # metadata for upload to PyPI
    author = "Bradley Young",
    author_email = "young.bradley@gmail.com",
    description = "Django integration with Facebook graph libraries",
    license = "BSD",
    keywords = "django facebook graph",
    url = "http://consciou.us/fbgraph",   # project home page, if any

    # could also include long_description, download_url, classifiers, etc.
)
