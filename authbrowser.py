from PyQt4 import QtCore, QtGui, QtWebKit
from bs4 import BeautifulSoup


class AuthBrowser(QtWebKit.QWebView):
    def __init__(self, parent):
        self.parent = parent
        QtWebKit.QWebView.__init__(self)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.loadFinished.connect(self._result_available)
        self.loadStarted.connect(self._starttimer)
        self.timer = QtCore.QTimeLine()
        self.pageloads = 0

    def _result_available(self, ok):
        frame = self.page().mainFrame()
        soup = BeautifulSoup(unicode(frame.toHtml()).encode('utf-8'))
        doc = self.page().mainFrame().documentElement()

        #IF ON THE LOGIN FORM PAGE
        if(self.pageloads == 0):
            #fill out the form here
            user = doc.findFirst("input[id=id_login]")
            passwd = doc.findFirst("input[id=id_password]")
            #####this should read from the configuration file
            self.parent.parent.configuration.read()
            user.evaluateJavaScript("this.value = '" + self.parent.parent.configuration.get('Login', 'username') + "'")
            passwd.evaluateJavaScript("this.value = '" + self.parent.parent.configuration.get('Login', 'password') + "'")

            button = doc.findFirst("button[type=button]")
            button.evaluateJavaScript("this.click()")
            #end filling out the form

        #if on the second page, this should be verifier submit page
        if(self.pageloads == 1):
            verify = doc.findFirst("button[type=submit]")
            verify.evaluateJavaScript("this.click()")

            if(soup.find(text='You are currently logged in as:') is None):
                #bad username or password, failure
                self.parent.badloginerror()

        #if on the third page or higher, get the verifier
        if(self.pageloads >= 2):
            try:
                verifierlocal = soup.find(id="id_verifier").get("value")
            except:
                #bad username or password, failure
                self.parent.badloginerror()
            else:
                #logged in successfully, now verify the key...
                try:
                    self.parent.parent.smartfile.get_access_token(None, verifierlocal)
                except:
                    #something happened after logging in successfully, and is not sucessful now
                    self.parent.badloginerror()
                else:
                    #logged in successfully
                    self.parent.success()

        self.pageloads = self.pageloads + 1
        self.timer.stop()

    def _starttimer(self):
        self.pagetimer()

    def pagetimer(self):
        #starts up a page timer, so after 30 seconds, we can give a network error
        self.timer.valueChanged.connect(self.netwatch)
        self.timer.setDuration(int(self.parent.parent.configuration.get('LocalSettings', 'network-timeout')) * 1000)
        self.timer.start()

    def netwatch(self, value):
        if (value == 1.0):
            self.stop()
            self.parent.networkerror()
