import unittest
from NaverBlogCrawler import NaverBlogCrawler, NaverBlogPostCrawler

class NaverBlogCrawlerTest(unittest.TestCase):
    def setUp(self):
        self.crawler = NaverBlogPostCrawler("http://blog.naver.com/1net1/221156999402")
        self.crawler.postSetup()

    def tearDown(self):
        self.crawler.backupFile.close()
        del self.crawler

    def test_getPostTestUrl(self):
        postFrameUrl = self.crawler.postFrameUrl
        postFrameUrlAnswer = "https://blog.naver.com/PostView.nhn?blogId=1net1&logNo=221156999402&redirect=Dlog&widgetTypeCall=true&directAccess=false"
        self.assertEqual(postFrameUrl, postFrameUrlAnswer)


    def test_getEditAreas(self):
        editAreas = self.crawler.getSE3Components()
        # for editArea in editAreas:
        #     print(editArea)
        self.assertTrue(editAreas is not None)

    def test_isTextArea(self):
        editAreas = self.crawler.getSE3Components()
        targetArea = editAreas[1]
        self.assertTrue(self.crawler.isTextEditArea(targetArea))

    def test_getPostNumber(self):
        answerPostNumber = "221156999402"
        postNumber = self.crawler.getPostNumber()
        self.assertEqual(answerPostNumber, postNumber)

    def test_getPostTitle(self):
        answerTitle = "[자료구조] 트라이 (Trie)"
        self.assertEqual(answerTitle, self.crawler.postTitle)

    def test_writeBackup(self):
        self.crawler.run()
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()