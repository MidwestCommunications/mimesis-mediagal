#!/usr/bin/env python
from os.path import dirname, abspath
from os import environ
import sys

environ["DJANGO_SETTINGS_MODULE"] = "example_project.settings"

from django.conf import settings as django_settings

django_settings.DATABASES["default"]["ENGINE"] = "sqlite3"
def runtests(*test_args):
    if not test_args:
        test_args = ["gallery"]
    parent = dirname(abspath(__file__))
    sys.path.insert(0, parent)
    from django.test.simple import run_tests
    failures = run_tests(test_args, verbosity=1, interactive=True)
    sys.exit(failures)
    
if __name__ == "__main__":
    runtests(*sys.argv[1:])
