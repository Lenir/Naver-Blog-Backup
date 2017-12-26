from setuptools import setup

setup(
    name='NaverBlogBackup',
    description='Python Crawler for Backup Naver blog posts.',
    version='0.1.0',
    author='Lenir',
    author_email='1net1@naver.com',
    url='https://github.com/Lenir/Naver-Blog-Backup',
    license='BSD License',
    keywords=['Naver', 'NaverBlog', 'Naver-Blog-Backup'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    install_requires=[
        'BeautifulSoup4',
        'progressbar2',
    ],
    packages=['NaverBlogCrawler'],
    data_files=['NaverBlogCrawler/blogstyle.css'],
)