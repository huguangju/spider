# -*- coding: utf-8 -*-

import urllib2
import urllib
import os
import errno
import urlparse
from bs4 import BeautifulSoup
import socket
import time

class Spider:

    def __init__(self):
        self.base_url = ''
        self.save_path = 'downloads/'
        timeout = 25
		
		# 这里对整个socket层设置超时时间。后续文件中如果再使用到socket，不必再设置
        socket.setdefaulttimeout(timeout) 
        self.downloadSuccess = False
        self.index_page = 'index.html'

    def getContent(self, url):
        self.base_url = url
		
        # TODO:如果根路径就是首页则下载
        urllib.urlretrieve(url, self.save_path + self.index_page, self.download_callbackfunc)

        response = urllib2.urlopen(url)
        content = response.read().decode('utf-8')
        response.close()
        return content

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

    def download_callbackfunc(self,blocknum, blocksize, totalsize):
        '''回调函数
        @blocknum: 已经下载的数据块
        @blocksize: 数据块的大小
        @totalsize: 远程文件的大小
        '''
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
                try: # 外包一层try
                    time.sleep(sleep_time)
                    urllib.urlretrieve(absolute_url, save_path + url, self.download_callbackfunc)
                    print 'download file:' + absolute_url
                   # 只有正常执行方能退出。
                    if self.downloadSuccess:
                        break
                except : # 如果发生了10054或者IOError或者XXXError
                    sleep_time += 5 #多睡5秒，重新执行以上的download.因为做了检查点的缘故，上面的程序会从抛出异常的地方继续执行。防止了因为网络连接不稳定带来的程序中断。
                    print('enlarge sleep time:',sleep_time)




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
    content = spider.getContent('http://webapplayers.com/inspinia_admin-v1.6/Angular/#/dashboards/dashboard_1');
    spider.save_path = "test/"
    for href in {}.fromkeys(spider.getUrls(content)).keys():
        if not href.__contains__('https://maps.googleapis.com/maps/api'):
            spider.download(href, spider.save_path)


