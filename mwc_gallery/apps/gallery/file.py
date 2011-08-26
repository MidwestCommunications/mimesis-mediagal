import re
from zipfile import ZipFile

def _check_zip_file(zipped_file_name):
    """
    Checks a zip file for malicious or malformed filenames.

    Returns the clean filenames.
    """
    clean_files = []
    zipped_file = ZipFile(zipped_file_name, "r")
    for f in zipped_file.filelist:
        if (f.filename.startswith("/")
                or "/.." in f.filename
                or "../" in f.filename
        ):
            continue
        else:
            clean_files += [f.filename]

    return clean_files

def extract_files(f):
    """
    Extracts images from a zip file.
    """
    pass
    
