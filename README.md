Naver blog backup
=======
[![PyPI version](https://badge.fury.io/py/NaverBlogBackup.svg)](https://badge.fury.io/py/NaverBlogBackup)

'Naver blog backup' Backups your Naver Blog Posts.  
네이버 블로그를 HTML로 백업해줍니다. 

Getting Started
---------
You can Install 'NaverBlogBackup' with pip.  
pip으로 설치하실 수 있습니다.

    $ pip install NaverBlogBackup
    $ pip3 install NaverBlogBackup


Usage
---------
You can backup your Naver blog with using python3 like this.  
네이버 블로그를 파이썬3을 사용하여 다음과 같이 백업할 수 있습니다.

    from NaverBlogCrawler import NaverBlogCrawler as nblog
    
    crawler = nblog.NaverBlogCrawler("your_naver_ID")
    crawler.run()

Results
---------
Files that crawled is in ./post/...  
크롤링 된 파일들은 post 폴더 내에 저장됩니다.  


Version Info
---------
##### ver 0.1.0
First Release, beta.
##### ver 0.1.1
Fix issue with Module name.