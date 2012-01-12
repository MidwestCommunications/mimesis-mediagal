from setuptools import setup


setup(
    name = "mediagal",
    version = "0.1-dev1",
    author = "Midwest Communications",
    url = "https://github.com/MidwestCommunications/mimesis-mediagal",
    description = "A gallery app for Django, using Mimesis and Mediaman.",
    license = "BSD",
    packages = ['mediagal'],
    install_requires =[
        "Django>=1.2",
        "celery>=2.3.3",
        "django-celery>=2.3.3",
        "PIL>=1.1.7",
        "easy-thumbnails>=1.0-alpha-18",
        "django-taggit>=0.9.3",
    ]
)
