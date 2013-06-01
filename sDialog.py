import os
import http.cookiejar
import urllib.request
import setting
import json
from PyQt4 import QtGui,QtCore
# from opener import install_opener


class sDialog(QtGui.QDialog,setting.Ui_Dialog):
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        self.initUi()
        
    def initUi(self):
        self.setupUi(self)
        self.setFixedSize(QtCore.QSize(400,350))
        self.glink.setText("<a href = 'http://wwww.baidu.com' >baidu</a>")
        self.dlink.setText("<a href= 'http://www.douban.com/people/lxiaofeng/'>小峰</a>")
        self.captchaurl_id = None
        self.codeButton.clicked.connect(self.getCode)
        self.buttonBox.accepted.connect(self.getAuth)
        self.buttonBox.rejected.connect(self.close)
        self.glink.linkActivated.connect(self.openUrl)
        self.dlink.linkActivated.connect(self.openUrl)
    def openUrl(self,url):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))
        
    def getCode(self):
        captchaurl = "http://douban.fm/j/new_captcha"
        data = urllib.request.urlopen(captchaurl)
        self.captchaurl_id = data.read().decode('utf-8').split('"')[1]
        requrl = "http://douban.fm/misc/captcha?size=m&id={0}".format(self.captchaurl_id)
        urllib.request.urlretrieve(requrl,'chaptucha.jpg')
        self.codeImage.setPixmap(QtGui.QPixmap("chaptucha.jpg"))
        
    def getAuth(self):
        if self.captchaurl_id is None:
            QtGui.QMessageBox.information(self,"Groove","请先获取验证码")
        else:
            loginurl = "http://douban.fm/j/login"
            params = {
                      "source": "radio",
                      "alias": self.emailEdit.text(),
                      "form_password": self.passwordEdit.text(),
                      "captcha_solution":self.codeEdit.text(),
                      "captcha_id":self.captchaurl_id,
                      "task": "sync_channel_list"
                      }
            user_agent = 'Mozilla/5.0 (compatible; MSIE 5.5; Windows NT)'
            
            cookiefile = "cookies.txt"
            cookie = http.cookiejar.LWPCookieJar(cookiefile)
            if os.path.isfile(cookiefile):
                cookie.revert(cookiefile, ignore_discard=False, ignore_expires=False)
            else:
                cookie.save(cookiefile, ignore_discard=False, ignore_expires=False)
            opener= urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))
            data = urllib.parse.urlencode(params).encode('unicode_escape')
            opener.addheaders = [('User-Agent',user_agent)]
            response = opener.open(loginurl, data)
            ans = json.loads(response.read().decode('utf-8'))
            if 'err_no' in ans:
                error = ans['err_msg']
                if error == "验证码不正确":
                    error += ",请刷新验证码"
                QtGui.QMessageBox.information(self,"Groove",error)
                os.remove("cookies.txt")
            else:
                self.parent().likeButton.setEnabled(True)
                self.parent().notlikeButton.setEnabled(True)
                self.parent().redheartChannel.setEnabled(True)
                self.parent().privateChannel.setEnabled(True)
                self.parent().collectChannel.setEnabled(True)
                self.parent().username.setText(ans['user_info']['name'])
                self.parent().rednum.setText(str(ans['user_info']['play_record']['liked']))
                cookie.save(cookiefile, ignore_discard=True, ignore_expires=True)
                self.parent().install_opener("cookies.txt")
                self.parent().changeChannel("0")
                self.parent().currentChannel("私人兆赫")
                if not self.parent().get:
                    collect = self.parent().getcollect()
                    self.parent().tocollect(collect)
                self.close()