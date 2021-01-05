# -*- coding: utf-8 -*-
from gstomd.corpus import Corpus
import unittest
import sys
from gstomd.my_init import setup_logging
import logging
setup_logging()
logger = logging.getLogger(__name__)


class CorpusTest(unittest.TestCase):
    """Tests operations of corpus class.
    """
    # ga = GoogleAuth('settings/test1.yaml')
    # ga.LocalWebserverAuth()
    # drive = GoogleDrive(ga)

    def test_01(self):
        logger.debug("Begin")

        corpus = Corpus()
        corpus.get_source(drive_id="0AIZGD5MSHiIcUk9PVA",
                                   root_folder_id="1ldIISbxYSv_s_GTPX7FhrVc_ytVpGHgT")
        logger.info(corpus.gscontent)
        corpus.gscontent.create_folders()
        corpus.gscontent.create_files()
        self.assertEqual(True, True)
        logger.debug("end")


if __name__ == '__main__':
    unittest.main()
