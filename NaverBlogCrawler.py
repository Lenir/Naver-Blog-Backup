from NaverBlogPostCrawler import *
from bs4 import BeautifulSoup
import requests
import re
import time
from multiprocessing import Process, Queue
import threading

class NaverBlogCrawler:
    def __init__(self, naverId):
        self.naverId = naverId
        self.postUrlList = []
        self.postsNum = 0
        self.curPost = 1

    def getPostList(self):
        pass

    def run(self):
        initTime = time.time()
        startPage = 1
        urlPrefix = "https://blog.naver.com/" + self.naverId + "/"
        postIdList = self.getEntirePostIdList(startPage)
        self.postsNum = len(postIdList)
        print("[ Getting post address list in {0:0.2f}s ]".format((time.time() - initTime)))
        print("[ Total posts : {}posts. Backup begins... ]".format(self.postsNum))
        half = self.postsNum // 2
        list1 = list(postIdList[0:half])
        list2 = list(postIdList[half:])
        process1 = Process(target= self.postBackupProcess, args=list1)
        process2 = Process(target= self.postBackupProcess, args=list2)
        process1.start()
        process2.start()
        process1.join()
        process2.join()

        # for postId in postIdList:
        #     print("{}/{}".format(self.curPost, self.postsNum), end=' ')
        #     postingCrawler = NaverBlogPostCrawler(urlPrefix + str(postId))
        #     postingCrawler.run()
        #     self.curPost += 1
        print("[ {0} Posts backup complete in {1:0.2f}s ]".format(self.postsNum, time.time() - initTime))

    def postBackupProcess(self, postList):
        for postUrl in postList:
            print("{}/{}".format(self.curPost, self.postsNum), end=' ')
            self.curPost += 1
            postingCrawler = NaverBlogPostCrawler(postUrl)
            postingCrawler.run()


    def getEntirePostIdList(self, startPage):
        page = startPage
        postIdList = []
        pastIdList = []
        while True:
            try:
                partialList = self.getPostIdListViaPage(page)
                if page == 1 or page % 20 == 0:
                    print("Getting post number list in page {}...".format(page))
                if partialList == [] or self.isDuplicateList(pastIdList, partialList):
                    return postIdList
                postIdList.extend(partialList)
                pastIdList = partialList
                page += 1
            except NonePostListException:
                return postIdList

    def isDuplicateList(self, postNumList1, postNumList2):
        if len(postNumList1) == len(postNumList2):
            for index in range(len(postNumList1)):
                if postNumList1[index] != postNumList2[index]:
                    return False
            return True
        else:
            return False

    def getPostIdListViaPage(self, pageNum):
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