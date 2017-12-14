from bs4 import BeautifulSoup
import requests
from urllib import request
import os
import re

class NaverBlogCrawler:
    def __init__(self, url):
        self.url = url
        self.postFrameUrl = ""
        self.postTitle = ""
        self.postNumber = ""
        self.postSoup = None
        self.postFrameSoup = None
        self.backupDir = ""
        self.backupFile = None
        self.imageCount = 0
        self.postSetup()

    def isSmartEditor3Posting(self, postFrameUrl):
        pass

    def postSetup(self):
        postHtmlSource = requests.get(self.url).text
        self.postSoup = BeautifulSoup(postHtmlSource, "html5lib")
        self.postFrameUrl = self.getPostFrameUrl()
        self.postNumber = self.getPostNumber()


        postFrameHttpResponse = requests.get(self.postFrameUrl).text
        self.postFrameSoup = BeautifulSoup(postFrameHttpResponse, "html5lib")
        self.postTitle = self.getPostTitle()

        self.backupDir = self.getBackupDirName()

        self.makeBackupDir()
        self.backupFile = open(self.backupDir+"/post.html", 'w', encoding='utf-8')
        self.setupHtml()

    def getPostFrameUrl(self):
        mainFrameTag = self.postSoup.find('frame', {'id': 'mainFrame'})
        mainFrameAttr = str(mainFrameTag).split(' ')

        postUrlSuffix = ""
        for attribute in mainFrameAttr:
            if attribute.startswith("src="):
                postUrlSuffix = str(attribute)[5:len(attribute) - 3]

        postUrlSuffix = postUrlSuffix.replace("amp;", "")
        postFrameUrl = "https://blog.naver.com" + postUrlSuffix

        return postFrameUrl

    def getPostNumber(self):
        postNum = re.sub(".*naver.com/.*/", '', self.url)
        return postNum

    def makeBackupDir(self):
        os.makedirs(self.backupDir, exist_ok=True)

    # post backup will save in ./posts/{postnumber+posttitle}
    # eg. 221156999402[자료구조] 트라이(Trie)
    def getBackupDirName(self):
        dirName = "posts/"
        return dirName + self.postNumber + self.postTitle

    def getPostTitle(self):
        titleTag = self.postFrameSoup.find('title')
        title = re.sub("<title>", '', str(titleTag))
        title = re.sub(" : 네이버 블로그</title>", '', title)
        return title

    def getPostEditAreas(self):
        if self.postFrameUrl is None:
            raise InvalidUrl
        else:
            editAreas = self.postFrameSoup.find_all('div', {'class': {'se_component se_paragraph default',
                                                                      'se_component se_image default',
                                                                      'se_component se_oglink default'}})
            return editAreas

    def getViewAreas(self, editArea):
        result = []


    def writeAreasToFile(self):
        editAreas = self.getPostEditAreas()
        for editArea in editAreas:
            self.backupFile.write("\n")
            if self.isTextEditArea(editArea):
                print("TEXT")
                self.backupFile.write(str(editArea))
            elif self.isLinkEditArea(editArea):
                print("LINK")
                # TODO : implement backup link block
                pass
            elif self.isImageEditArea(editArea):
                strEditArea = str(editArea)
                print("IMAGE")
                imgSrc = re.search("src=\".*(png|jpg|gif)?type=.[0-9]*", strEditArea).group()
                imgUrl = imgSrc[5:]
                print("imgURL = " + imgUrl)
                self.saveImage(imgUrl)

                saveImgName = self.getSaveImageName(imgUrl)
                print("Save img name : "+saveImgName)
                # strEditArea = re.sub("src=\".*(png|jpg|gif)?type=.[0-9]*\"", "src=\"" + saveImgName + "\"", strEditArea)
                strEditArea = re.sub("src=\".*(png|jpg|gif)?type=.[0-9]*\"", "src=\"" + saveImgName + "\"", strEditArea)
                self.backupFile.write(strEditArea)
                self.imageCount += 1
                pass
            self.backupFile.write("\n")
        self.prepareCloseHtml()
        self.backupFile.close()

    def setupHtml(self):
        headers = \
            "<html>\n" \
            "   <head>\n" \
            "       <meta http-equiv=\"content-type\" content=\"text/html;charset=UTF-8\"/>\n" \
            "   </head>\n"
        self.backupFile.write(headers)

    def prepareCloseHtml(self):
        tagClosers = "</html>"
        self.backupFile.write(tagClosers)

    def isTextEditArea(self, editArea):
        if "se_component se_paragraph" in str(editArea):
            return True
        else:
            return False

    def isLinkEditArea(self, editArea):
        if "se_component se_oglink" in str(editArea):
            return True
        else:
            return False

    def isImageEditArea(self, editArea):
        if "se_component se_image" in str(editArea):
            return True
        else:
            return False

    def saveImage(self, imageUrl):
        saveLoc = self.backupDir
        saveName = self.getSaveImageName(imageUrl)
        request.urlretrieve(imageUrl, "./" + saveLoc + "/" + str(saveName))

    def getSaveImageName(self, imageUrl):
        return str(self.imageCount) + "." + re.search('(png|jpg|gif)', imageUrl).group()

class InvalidUrl(Exception):
    pass

class EditArea:
    # EditArea is class that based on str, found on soup(= HTML TAG)
    def __init__(self, editArea):
        self.area = editArea

    def isTextEditArea(self):
        if "se_component se_paragraph" in str(self.area):
            return True
        else:
            return False

    def isLinkEditArea(self):
        if "se_component se_oglink" in str(self.area):
            return True
        else:
            return False

    def isImageEditArea(self):
        if "se_component se_image" in str(self.area):
            return True
        else:
            return False

    def isCenterAlignedArea(self):
        if "se_align-center" in str(self.area):
            return True
        else:
            return False

    def isRightAlignedArea(self):
        if "se_align-right" in str(self.area):
            return True
        else:
            return False