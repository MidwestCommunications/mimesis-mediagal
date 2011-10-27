from os import mkdir
from shutil import rmtree
from zipfile import ZipFile

from django.test import TestCase

from gallery.file import _check_zip_file, extract_files



SCRATCH_DIR = "./tmp/"

class ZipFileTest(TestCase):
    file_names = ["f1.jpg","f2.png","f3.gif"]
    def setUp(self):
        mkdir(SCRATCH_DIR)
        z = ZipFile(SCRATCH_DIR + "ztest.zip", "w")
        # Create files to be zipped.
        for f_name in self.file_names:
            f = open(SCRATCH_DIR + f_name, "w")
            f.write("")
            f.close()
            z.write(SCRATCH_DIR + f_name)
        z.close()
        
    def tearDown(self):
        rmtree(SCRATCH_DIR)
        
class ZipFileCheckTest(ZipFileTest):
    
    def test_check_zip_file(self):
        names = _check_zip_file(SCRATCH_DIR + "ztest.zip")
        self.assertTrue("tmp/f1.jpg" in names)
        self.assertTrue("tmp/f2.png" in names)



