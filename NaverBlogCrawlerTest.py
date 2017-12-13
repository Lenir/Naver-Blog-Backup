import unittest
from NaverBlogCrawler import *

class NaverBlogCrawlerTest(unittest.TestCase):
    def setUp(self):
        self.crawler = NaverBlogCrawler("http://blog.naver.com/1net1/221156999402")

    def tearDown(self):
        del self.crawler

    def test_getPostTestUrl(self):
        postFrameUrl = self.crawler.getPostFrameUrl()
        postFrameUrlAnswer = "https://blog.naver.com/PostView.nhn?blogId=1net1&logNo=221156999402&redirect=Dlog&widgetTypeCall=true&directAccess=false"
        self.assertEqual(postFrameUrl, postFrameUrlAnswer)

    def test_getEditAreas(self):
        editAreas = self.crawler.getPostEditAreas()
        for editArea in editAreas:
            print(editArea)
        self.assertTrue(editAreas is not None)

    def test_isTextArea(self):
        editAreas = self.crawler.getPostEditAreas()
        targetArea = editAreas[1]
        self.assertTrue(NaverBlogCrawler.isTextEditArea(targetArea))

if __name__ == "__main__":
    unittest.main()