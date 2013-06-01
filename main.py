import sys
import os
import fm_ui
# import time
import urllib.request       #python3
import http.cookiejar       #python3
from PyQt4 import QtCore,QtGui
from songinfo import getSongInfo
from sDialog import sDialog
from bs4 import BeautifulSoup
        
class Widget(QtGui.QWidget,fm_ui.Ui_Form):
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.initUi()
        
    def initUi(self):
        self.setupUi(self)
#         http.client.HTTPConnection.debuglevel = 1
        url = '1'
        cookiefile = "cookies.txt"
        collectChannel = {}
        self.tochannel()                #QSignalMapper
        self.get = 0
        if os.path.isfile(cookiefile):               #cookie文件是否存在
            self.likeButton.setEnabled(True)
            self.notlikeButton.setEnabled(True)
            self.redheartChannel.setEnabled(True)
            self.privateChannel.setEnabled(True)
            self.collectChannel.setEnabled(True)
            self.install_opener(cookiefile)
            collectChannel=self.getcollect()
            self.tocollect(collectChannel)
            url = '0'
        if url == '0':
            self.current_channel.setText("私人兆赫")
        else:
            self.current_channel.setText("华语HMz")
        self.url = "http://douban.fm/j/mine/playlist?type=n&channel="+url+"&from=mainsite"
        
        self.sDialog = None
        self.songprocess = QtCore.QProcess()
        self.songprocess.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self.songprocess.started.connect(self.info)
        self.songprocess.finished[int].connect(self.finish)
        self.nextButton.clicked.connect(self.next)          #下一首     
        self.stopButton.toggled.connect(self.stop)          #暂停
        self.volumnSlider.valueChanged.connect(self.changeVolumn)       #改变音量
        self.volumn.clicked.connect(self.mute)                          #改变音量
        self.setting.clicked.connect(self.changeSetting)
        self.likeButton.clicked.connect(self.like)
        self.notlikeButton.clicked.connect(self.notlike)
        self.channel.mousemove.connect(self.showChannel)
        self.quitLabel.clicked.connect(self.clearCookie)
        
        if url == "1":
            self.cnum = 1
        else:
            self.cnum = -3
            
        self.songlist = getSongInfo(self.url)
        self.s = next(self.songlist)         
        song = self.s["url"]
        self.songprocess.start('mplayer',['-slave','-quiet',song])
        self.vnum = 50
        self.volumnSlider.setValue(self.vnum)
    
    def getcollect(self):
        indexurl = "http://fm.douban.com"
        r = urllib.request.urlopen(indexurl)
        soup = BeautifulSoup(r)
        self.username.setText(soup.find(id="user_name").get_text())
        self.rednum.setText(soup.find(id="rec_liked").get_text())
        if  not self.get:
            ul = soup.find(id="fav_chls")
            collect={}
            for li in ul.find_all('li'):
                if li.get('class') == ['channel']:
                    cid = li.get('cid')
                    cname = li.a.get_text()
                    action = QtGui.QAction(cname,self)
                    self.collectChannel.addAction(action)
                    collect[cid]=action
            self.get = 1
            return collect
    
    def tocollect(self,collectChannel):
        if len(collectChannel):
            for num,channel in collectChannel.items():
                text = channel.text()
    #             collectChannel
                self.sMapper = QtCore.QSignalMapper(self)
                self.tMapper = QtCore.QSignalMapper(self)
                self.sMapper.setMapping(channel,num)
                self.tMapper.setMapping(channel,text)
                channel.triggered.connect(self.sMapper.map)
                channel.triggered.connect(self.tMapper.map)
                self.sMapper.mapped[str].connect(self.changeChannel)
                self.tMapper.mapped[str].connect(self.currentChannel)
        
    def install_opener(self,cookiefile):
        cookie = http.cookiejar.LWPCookieJar(cookiefile)
        cookie.load(cookiefile, ignore_discard=True, ignore_expires=True) 
        opener= urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))
        urllib.request.install_opener(opener)
  
    def tochannel(self):            #QSignalMapper
        channellist = {'-3':self.redheartChannel,'0':self.privateChannel,'1':self.chineseChannel,'2':self.westernChannel, 
                       '3':self.seventyChannel,'4':self.eightyChannel,'5':self.nintyChannel,
                       '6':self.cantoneseChannel,'7':self.rockChannel,'8':self.folkChannel,
                       '9':self.lightmusicChannnel,'10':self.movieChannel,'13':self.jazzChannel,
                       '14':self.elecChannel,'15':self.rapChannel,'16':self.rnbChannel,'17':self.japanChannel,
                       '18':self.koreanChannel,'20':self.womenChannel,"22":self.franceChannel}
        for num,channel in channellist.items():
            text = channel.text()
            self.sMapper = QtCore.QSignalMapper(self)
            self.tMapper = QtCore.QSignalMapper(self)
            self.sMapper.setMapping(channel,num)
            self.tMapper.setMapping(channel,text)
            channel.triggered.connect(self.sMapper.map)
            channel.triggered.connect(self.tMapper.map)
            self.sMapper.mapped[str].connect(self.changeChannel)
            self.tMapper.mapped[str].connect(self.currentChannel)
            
    def song(self):                 #获取歌曲
        url = self.s["picture"].replace("mpic","lpic")
        picture = urllib.request.urlopen(url).read()
        with open("image/cover.jpg",mode="wb") as img_file:
            img_file.write(picture)
        title = self.s["title"]
        artist = self.s["artist"]
        if len(title)>25:
            title = title[0:25]+'...'
        if len(artist)>25:
            artist = artist[0:25]+'...'
        self.cover.setPixmap(QtGui.QPixmap("image/cover.jpg"))
        self.artist.setText('<p><span style=" font-size:10pt; font-weight:600;">'+artist+'</span></p>')
        self.title.setText('<p><span style=" font-size:12pt; font-weight:600; color:#55aaff;">'+title+'</span></p>')
        self.sid = self.s['sid']
        if self.s["like"] == 1:
            self.likeButton.setPixmap(QtGui.QPixmap("image/redheart.png"))
            self.like = 1
        else:
            self.likeButton.setPixmap(QtGui.QPixmap("image/grepheart.png"))
            self.like = 0
    
    def nextsong(self):
        try:
            self.s = next(self.songlist)
        except StopIteration:
            self.songlist = getSongInfo(self.url)
            self.s = next(self.songlist)
    
    @QtCore.pyqtSlot()
    def like(self):             #加心或去掉加心
        num = int(self.rednum.text())
        if self.like:
            t = "u"
            self.likeButton.setPixmap(QtGui.QPixmap("image/grepheart.png"))
            self.like = 0
            num = num -1
        else:
            t = "r"
            self.likeButton.setPixmap(QtGui.QPixmap("image/redheart.png"))
            self.like = 1
            num = num + 1
        self.rednum.setText(str(num)) 
        url = "http://douban.fm/j/mine/playlist?type=" + t +"&sid=" + self.sid +"&channel=" + str(self.cnum) + "&from=mainsite"
        urllib.request.urlopen(url)
        
    @QtCore.pyqtSlot()      #不再收听
    def notlike(self):
        url = "http://douban.fm/j/mine/playlist?type=b&sid=" + self.sid +"&channel=" + str(self.cnum) + "&from=mainsite"
        urllib.request.urlopen(url)
        if self.like:
            num = int(self.rednum.text()) - 1
            self.rednum.setText(str(num))
        self.next()
        
    @QtCore.pyqtSlot()
    def changeSetting(self):        #打开设置
        if self.sDialog is None:
            self.sDialog = sDialog(self)
        self.sDialog.show()
        self.sDialog.raise_()
        self.sDialog.activateWindow()
            
    @QtCore.pyqtSlot()    
    def info(self):   
        self.song()
         
    @QtCore.pyqtSlot(bool)  
    def stop(self,stop):         #暂停
        if stop:
            self.stopButton.setPixmap(QtGui.QPixmap("image/splay.png"))
        else:
            self.stopButton.setPixmap(QtGui.QPixmap("image/Selection_005"))
        self.songprocess.write("pause\n")
        
    @QtCore.pyqtSlot(int)
    def changeVolumn(self,num):     #更改音量
        self.songprocess.write("volume {0} 1\n".format(num))
        if not num:
            self.volumn.setPixmap(QtGui.QPixmap('image/mute.png'))
        else:
            self.volumn.setPixmap(QtGui.QPixmap('image/volumnbutton.png'))
    @QtCore.pyqtSlot()
    def mute(self):         #静音
        num = self.volumnSlider.value()
        if(num):
            self.volumnSlider.setValue(0)
            self.vnum = num
            self.volumn.setPixmap(QtGui.QPixmap('image/mute.png'))
        else:
            self.volumnSlider.setValue(self.vnum)
            self.volumn.setPixmap(QtGui.QPixmap('image/volumnbutton.png'))
#         self.volumn.repaint()    
        
    @QtCore.pyqtSlot() 
    def next(self):
        self.nextsong()         
        song = self.s["url"]  
        self.songprocess.write("loadfile {0}\n".format(song))
        self.song()
#         self.repaint()
    @QtCore.pyqtSlot(int)
    def finish(self,error):
        if not error:
            self.nextsong()        
            song = self.s["url"] 
            self.songprocess.start('mplayer',['-slave','-quiet',song])   
            
    @QtCore.pyqtSlot(QtGui.QMouseEvent)
    def showChannel(self,event):        #显示兆赫选择菜单
        pos = QtCore.QPoint(250,478)
        self.menu.exec_(self.mapToParent(pos)) 
                      
    @QtCore.pyqtSlot(str)
    def changeChannel(self,num):
        self.url = "http://douban.fm/j/mine/playlist?type=n&sid=&pt=0.0&channel="+ num + "&from=mainsite"
        self.cnum = num
        self.songlist = getSongInfo(self.url)
        self.s = next(self.songlist)
        song = self.s["url"]      
        self.songprocess.write("loadfile {0}\n".format(song))
        self.song() 
        
    @QtCore.pyqtSlot(str)
    def currentChannel(self,text):
        self.current_channel.setText(text)
    @QtCore.pyqtSlot()
    def clearCookie(self):
        if os.path.isfile("cookies.txt"):
            r = QtGui.QMessageBox.warning(self,"Groove","退出登录？", buttons=QtGui.QMessageBox.Yes|QtGui.QMessageBox.No, defaultButton=QtGui.QMessageBox.No)
            if r == QtGui.QMessageBox.Yes:
                os.remove("cookies.txt")
                self.likeButton.setEnabled(False)
                self.notlikeButton.setEnabled(False)
                self.redheartChannel.setEnabled(False)
                self.privateChannel.setEnabled(False)
                self.collectChannel.setEnabled(False)
                self.username.setText("未登录")
                self.rednum.setText("0")
                self.changeChannel('1')
                self.currentChannel("华语HMz")
    def closeEvent(self,ev):
        self.songprocess.write("quit\n")
        self.songprocess.waitForFinished(msecs=30000)
        ev.accept() 
            
def main():
    app = QtGui.QApplication(sys.argv)
    widget = Widget()
    widget.show()
    app.lastWindowClosed.connect(app.quit)
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()


