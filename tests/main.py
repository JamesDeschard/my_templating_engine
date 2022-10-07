import unittest

from tests.test_document import TestDocument

from .test_document import TestDocument
from .test_engine import TestEngine
from .test_evaluate import TestEvaluate

from.test_utils import TestUtils


def main():
    document = unittest.TestLoader().loadTestsFromTestCase(TestDocument)
    engine = unittest.TestLoader().loadTestsFromTestCase(TestEngine)
    evaluate = unittest.TestLoader().loadTestsFromTestCase(TestEvaluate)
    utils = unittest.TestLoader().loadTestsFromTestCase(TestUtils)
    
    suite = unittest.TestSuite([document, engine, evaluate, utils])
    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == '__main__':
    main()
