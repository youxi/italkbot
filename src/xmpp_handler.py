# -*- coding: utf-8 -*-
import re
import urllib
import smtplib
import logging
from google.appengine.api import mail
from google.appengine.api import xmpp
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import ereporter
from main import OAuthAccessToken
from apptwitter import AppEngineTwitter
import config

def html2table(html):
    trs = re.findall(r'澳大利亚元.*?欧元', html, re.DOTALL)
    rows = []
    for tr in trs:
        x = re.findall(r'>([^<>]*)(?:</a>)?</td>', tr, re.DOTALL)
        x = map(lambda s: s.strip(), x)
        rows.append(x)
    return rows
# ...
class XMPPHandler(webapp.RequestHandler):
    def post(self):
        message = xmpp.Message(self.request.POST)
        if message.body[0:2].lower() == 'fx':
            url = r'http://fx.cmbchina.com/hq/'
            message.reply(url)
            rows = html2table(urllib.urlopen(url).read())
            haha = rows[0]
            messageBody = '澳元卖出价:'+ haha[3] + ' 更新时间:' + haha[6]
            logging.debug(messageBody)
            message.reply(messageBody)
            
##            query = OAuthAccessToken.all()
##            username = 'wanyouxi'
##            query.filter('username = ', username)
##            acc_key = query.fetch(1)
##            twitter = AppEngineTwitter()
##            twitter.set_oauth(config.OAUTH_KEY, config.OAUTH_SECRET, acc_key[0].token,acc_key[0].secret)
##            if (twitter.verify() == 200):
##                twitter.update(messageBody+' 手动更新')
##            else:
##                logging.debug('twitter.sent shit')
        else:
            message.reply("嗯，然后呢？哈哈哈哈哈哈1")
            
logging.getLogger().setLevel(logging.DEBUG)
ereporter.register_logger()
application = webapp.WSGIApplication([('/_ah/xmpp/message/chat/', XMPPHandler)],debug=True)

def main():

    run_wsgi_app(application)

if __name__ == "__main__":
    main()
# ...
