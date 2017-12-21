from NaverBlogPostCrawler import *
from bs4 import BeautifulSoup
import requests
import re

class NaverBlogCrawler:
    def __init__(self, naverId):
        self.naverId = naverId
        self.postUrlList = []

    def getPostList(self):
        pass

    def run(self):
        page = 1
        urlPrefix = "https://blog.naver.com/" + self.naverId + "/"
        try:
            while True:
                postNumList = self.getPostNumListViaPage(page)
                for postNum in postNumList:
                    postingCrawler = NaverBlogPostCrawler(urlPrefix + str(postNum))
                    postingCrawler.run()
                page += 1
        except NonePostListException:
            pass

    def getPostNumListViaPage(self, pageNum):
        getPostList = "https://blog.naver.com/" \
                      "PostList.nhn?from=postList&" \
                      "blogId={}&currentPage={}".format(self.naverId, pageNum)
        postListHtml = requests.get(getPostList).text
        postListSoup = BeautifulSoup(postListHtml, "html5lib")
        postNumTags = re.search("var tagParam .*\';", str(postListSoup)).group()
        postNumList = re.findall('[0-9]+', postNumTags)
        if postNumList == None:
            raise NonePostListException
        return postNumList

if __name__ == "__main__":
    crawler = NaverBlogCrawler("1net1")
    crawler.run()

class NonePostListException(Exception):
    pass