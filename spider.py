# -*- coding: utf-8 -*-

import urllib2
import urllib
import os
import errno
import urlparse
from bs4 import BeautifulSoup
import socket
import time
import re

class Spider:

    def __init__(self):
        self.base_url = ''
        self.save_path = 'downloads/'
        timeout = 25

        # 这里对整个socket层设置超时时间。后续文件中如果再使用到socket，不必再设置
        socket.setdefaulttimeout(timeout)
        self.downloadSuccess = False
        self.index_page = 'index.html'

    def getContent(self, url, save_path):
        self.base_url = url

        # TODO:如果根路径就是首页则下载
        if not os.path.exists(save_path):
            self.mkdir_p(save_path)

        urllib.urlretrieve(url, save_path + self.index_page, self.download_callbackfunc)

        response = urllib2.urlopen(url)
        content = response.read().decode('utf-8')
        response.close()
        return content

    def get_img_in_css(self, url):
        request = urllib2.Request(url)
        html = urllib2.urlopen(request).read().decode('utf-8')

        # background: url("../images/arrow.png") no-repeat scroll right 14px top 18px rgba(0, 0, 0, 0);
        re_string = r'background.*url\("(.*)"\)'
        match = re.compile(re_string)
        img_links = re.findall(match, html)
        img_result = []

        for img in img_links:
            # TODO:只有一层相对目录的情况，考虑多层或无限层解析相对目录
            if img.count('../') == 1:
                img_result.append(url[:url.rfind('/')+1] + img.replace('../', ''))
                #print img, img.count('../'), url.rfind('/'), url[:url.rfind('/')]

        return img_result

    def getUrls(self, content):
        soup = BeautifulSoup(''.join(content))
        result = []

        #a
        links = soup.findAll('a')
        for link in links:
            try:
                temp = link['src']
                result.append(temp)
            except KeyError:
                pass # or some other fallback action

        #css
        links = soup.findAll('link')
        for link in links:
            try:
                temp = link['href']
                result.append(temp)
            except KeyError:
                pass # or some other fallback action

        #js
        links = soup.findAll('script')
        for link in links:
            try:
                temp = link['src']
                result.append(temp)
            except KeyError:
                pass # or some other fallback action

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

    '''下载文件的回调函数
    @blocknum: 已经下载的数据块
    @blocksize: 数据块的大小
    @totalsize: 远程文件的大小
    '''
    def download_callbackfunc(self,blocknum, blocksize, totalsize):
        percent = 100.0 * blocknum * blocksize / totalsize
        if percent > 100:
            percent = 100
            self.downloadSuccess = True

        print "%.2f%%"% percent

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
            sleep_time = 1
            while True:
                try:
                    time.sleep(sleep_time)

                    print 'downloading file:' + absolute_url
                    urllib.urlretrieve(absolute_url, save_path + url, self.download_callbackfunc)

                    # 只有下载成功方能退出
                    if self.downloadSuccess:
                        break

                # 如果发生了10054或者IOError或者XXXError
                except:
                    # 多睡5秒，重新执行以上的download.因为做了检查点的缘故，上面的程序会从抛出异常的地方继续执行。
                    # 防止了因为网络连接不稳定带来的程序中断
                    sleep_time += 5
                    print('enlarge sleep time:', sleep_time)

    # 递归创建文件夹
    def mkdir_p(self, path):
        try:
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
    base_url = 'http://foxythemes.net/cleanzone2/'
    save_path = "test/"
    #content = spider.getContent(base_url, "test/");
    for href in {}.fromkeys(spider.getUrls(content)).keys():
        if not href.__contains__('googleapis'):
            spider.download(href, save_path)

     # 单独下载css中的背景图
    '''imgs = spider.get_img_in_css('http://foxythemes.net/cleanzone2/css/style.css')
    for img in imgs:
        temp = img.replace(base_url, '')
        dirs = save_path + temp[:temp.rfind('/')]
        if not os.path.exists(dirs):
            spider.mkdir_p(dirs)

        urllib.urlretrieve(img, save_path + temp)
        print 'downloading img: ', img'''

