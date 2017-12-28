Naver blog backup
=======
[![PyPI version](https://badge.fury.io/py/NaverBlogBackup.svg)](https://badge.fury.io/py/NaverBlogBackup)

'Naver blog backup' Backups your Naver blog posts.  
네이버 블로그를 HTML로 백업해주는 파이썬 크롤러입니다. 

Getting Started
---------
You can Install 'NaverBlogBackup' with `pip`.  
`pip`으로 설치하실 수 있습니다.

    $ pip install NaverBlogBackup
    $ pip3 install NaverBlogBackup


Usage
---------
You can backup your Naver blog with using python3 script like this.  
네이버 블로그를 파이썬3 스크립트를 사용하여 다음과 같이 백업할 수 있습니다.

    from NaverBlogCrawler import NaverBlogCrawler as nblog
    
    crawler = nblog.NaverBlogCrawler("your_naver_ID")
    crawler.run()

Examples
---------
![](https://lenir.github.io/img/NaverBlogBackup/usageScreenshot.png)  
This is screenshot when run above python script on Terminal.  
위의 파이썬 스크립트를 터미널에서 실행 시의 스크린샷 입니다.  

![](https://lenir.github.io/img/NaverBlogBackup/bakupDirScreenshot.png)  
Inside of  `post/` directory. It makes directory for each post's backup.  
`post/` 디렉토리 안입니다. 포스트 별로 디렉토리를 만들어 저장합니다.  

![](https://lenir.github.io/img/NaverBlogBackup/postFolder.png)  
Inside of posting directory. Html backup saved in `post.html` and image also saved with it.  
포스트 백업 디렉토리 내부입니다. Html 백업은 `post.html`로 저장되어 있고, 이미지도 따로 저장되어 있습니다.

![](https://lenir.github.io/img/NaverBlogBackup/backupedPost.png)  
This is capture of `post.html`. This backup's original page is like [this](https://blog.naver.com/1net1/221159842052). It looks pretty same.  
 `post.html`의 캡쳐입니다. 원본은 [다음](https://blog.naver.com/1net1/221159842052)과 같습니다. 내용은 원본과 같습니다.  

![](https://lenir.github.io/img/NaverBlogBackup/codeComponent.png)  
Code Component in above post. I use css file's code component part on Naver Blog's page code.  
위 포스트의 코드 컴포넌트 입니다. 네이버 블로그 css 소스코드의 코드 컴포넌트 부분을 가지고 와서 적용했습니다.  


Version Info
---------
##### ver 0.1.0
First Release, beta.
##### ver 0.1.1
Fix issue with Module name.
##### ver 0.1.2
Make 'console script'. TBD.
##### ver 0.1.3
Fix issue that cannot copy css file.