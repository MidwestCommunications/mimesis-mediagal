from setuptools import setup, find_packages


setup(
    name = "mwc_gallery",
    version = "0.1-dev1",
    author = "Eldarion",
    author_email = "development@eldarion.com",
    description = "Gallery app",
    license = "Commerical",
    packages = find_packages(),
    zip_safe = False,
    install_requires =[
        "Django>=1.2",
        "celery>=2.3.3",
        "django-celery>=2.3.3",
        "PIL>=1.1.7",
        "easy-thumbnails>=1.0-alpha-18",
        "django-taggit>=0.9.3",
    ]
)
