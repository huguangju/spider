# -*- coding: utf-8 -*-

import urllib2
import urllib
import os
import errno
import urlparse
from bs4 import BeautifulSoup


class Spider:

    def __init__(self):
        self.index_filename = 'index.html'
        self.base_url = 'http://webapplayers.com/inspinia_admin-v1.5/'
        self.save_path = 'downloads/'

    def getContent(self, url):
        response = urllib2.urlopen('http://webapplayers.com/inspinia_admin-v1.5/')
        return response.read().decode('utf-8')

    def getUrls(self, content):
        soup = BeautifulSoup(''.join(content))
        result = []

        #images
        links = soup.findAll('img')
        for link in links:
            try:
                temp = link['src']
                result.append(temp)
            except KeyError:
                pass # or some other fallback action

        return result

    def getdirc(self, url):
        idx = url.rfind('/')
        return url[:idx]

    # 下载到本地
    def download(self, url, save_path):
        # TODO:是否基路径就是首页
        if len(save_path) == 0:
            save_path = self.save_path

        if not os.path.exists(save_path):
            self.mkdir_p(save_path)

        absolute_url = urlparse.urljoin(self.base_url, url)
        dirs = self.getdirc(save_path + url)
        if not os.path.exists(dirs):
            self.mkdir_p(dirs)
            print 'create directory:' + dirs

        if not os.path.exists(save_path + url):
            urllib.urlretrieve(absolute_url, save_path + url)
            print 'download file:' + absolute_url

    # 递归创建文件夹
    def mkdir_p(self, path):
        try:
            if not path.__contains__('.'):
                os.makedirs(path)
        except OSError as exc: # Python >2.5 (except OSError, exc: for Python <2.5)
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    def isAbsolute(self, link):
        for item in ['http://', 'https://']:
            try:
                if link.index(item) >= 0:
                    return True
            except:
                pass
        return False

if __name__ == "__main__":
    spider = Spider()
    content = spider.getContent('http://webapplayers.com/inspinia_admin-v1.5/');
    for href in {}.fromkeys(spider.getUrls(content)).keys():
        spider.download(href, 'temp/')


