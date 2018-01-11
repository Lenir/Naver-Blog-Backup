from NaverBlogCrawler import NaverBlogPostCrawler as postCrawler
import unittest

class NaverBlogPostCrawlerTest(unittest.TestCase):
    def setUp(self):
        se3testPostURL = "http://blog.naver.com/1net1/221182904428"
        se2testPostURL = "http://blog.naver.com/1net1/221182912148"
        self.se3postCrawler = postCrawler.NaverBlogPostCrawler(se3testPostURL)
        self.se2postCrawler = postCrawler.NaverBlogPostCrawler(se2testPostURL)

        self.se3postCrawler.postSetup()
        self.se2postCrawler.postSetup()

    def tearDown(self):
        self.se3postCrawler.backupFile.close()
        self.se2postCrawler.backupFile.close()

        del self.se3postCrawler
        del self.se2postCrawler

    def test_getEditorVersion3(self):
        self.assertEqual(self.se3postCrawler.getEditorVersion(), 3)

    def test_getEditorVersion2(self):
        self.assertEqual(self.se2postCrawler.getEditorVersion(), 2)

    def test_getPostFrameURL(self):
        se3postFrameURL = "https://blog.naver.com/PostView.nhn?" \
                          "blogId=1net1&" \
                          "logNo=221182904428"
        isFrameUrl = se3postFrameURL in self.se3postCrawler.postFrameUrl
        self.assertTrue(isFrameUrl)

    def test_getNaverID(self):
        naverID = "1net1"
        self.assertEqual(self.se3postCrawler.getNaverID(), naverID)

    def test_getPostTitle(self):
        postTitle = "[SE3]NaverBlogPostCrawlerTestCase"
        self.assertEqual(self.se3postCrawler.getPostTitle(), postTitle)

    def test_getSE3Component(self):
        se3Components = self.se3postCrawler.getSE3Components()
        self.assertTrue(se3Components is not None)

    def test_getSE2(self):
        se2PostViewArea = self.se2postCrawler.getSE2PostViewArea()
        self.assertTrue(se2PostViewArea is not None)


if __name__ == "__main__":
    unittest.main()