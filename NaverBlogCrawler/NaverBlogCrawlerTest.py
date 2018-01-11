import unittest
from NaverBlogCrawler import NaverBlogCrawler as nbcrawler

class NaverBlogCrawlerTest(unittest.TestCase):
    def setUp(self):
        self.crawler = nbcrawler.NaverBlogCrawler("1net1")

    def tearDown(self):
        del self.crawler

    def test_getPostIdListViaPage(self):
        postIdList = self.crawler.getPostIdListViaPage(1)
        self.assertTrue(postIdList is not None)


if __name__ == "__main__":
    unittest.main()