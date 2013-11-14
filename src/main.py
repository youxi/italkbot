# -*- coding: utf-8 -*-
import logging
import re
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import mail
from google.appengine.api import xmpp
from google.appengine.api import urlfetch
from google.appengine.ext import db
from google.appengine.ext import ereporter
from google.appengine.runtime.apiproxy_errors import DeadlineExceededError 
from apptwitter import AppEngineTwitter
from django.utils import simplejson
import xml.sax.saxutils
import config
import datetime
from database import fxdb

OAUTH_KEY = config.OAUTH_KEY
OAUTH_SECRET = config.OAUTH_SECRET
BOT=config.ACCOUNT

HEADER='''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>TwiTalker - Tweet it Easy with your Gtalk</title>
<link href="/img/favicon.ico" rel="shortcut icon" type="image/x-icon">
<link rel="stylesheet" type="text/css" media="screen" href="/css/style.css" /> 
</head>

<body>
<div id="top"></div>
<div id="header">
<div id="header_box"><img style="float:left" src="img/logo.png" />
<ul id="navCircle">
<!-- CSS Tabs -->
<li><a href="/">首页</a></li>
<li><a href="faq">帮助</a></li>
<li><a href="about">关于</a></li>
<li><a href="http://twitalkerblog.appspot.com">BLOG</a></li>
</ul>
</div>
<div class="clean"></div>
</div>
<div id="header_bottom"></div>
'''

JS='''
<SCRIPT LANGUAGE="JavaScript">
<!-- Begin
function copyit(theField) {
var tempval=eval("document."+theField)
tempval.focus()
tempval.select()
therange=tempval.createTextRange()
therange.execCommand("Copy")
}
//  End -->
</script>
'''

FOOTER='''
<div id="footer">
Copyright (C) 2009-2010 TwiTalker | <a href="http://www.kavingray.com">Kavin</a> | <a href="http://code.google.com/p/twitalker/">Open Source</a> | Powered by <a href="http://code.google.com/appengine/">Google appengine</a>
</div>
</body>
</html>
'''
# ...

def getre(content):
    trs = re.findall(r'澳大利亚元.*?欧元', content, re.DOTALL)
    rows = []
    for tr in trs:
        x = re.findall(r'>([^<>]*)(?:</a>)?</td>', tr, re.DOTALL)
        x = map(lambda s: s.strip(), x)
        rows.append(x)
    result = rows[0]
    return result

def getfx():
    url = r'http://fx.cmbchina.com/hq/'
##    rows = html2table(urllib.urlopen(url).read())
    try:
        url_result = urlfetch.fetch(url)
        if url_result.status_code == 200:
            result = getre(url_result.content)
            return result
    except DeadlineExceededError:
        logging.debug('Ohh, deadline exceeded, call again')


class InitHandler(webapp.RequestHandler):
    
    
    def get(self):
        twitter = AppEngineTwitter()
        twitter.set_oauth(key=OAUTH_KEY, secret=OAUTH_SECRET)
        req_info = twitter.prepare_oauth_login()
        
        OAuthRequestToken(token=req_info['oauth_token'],
                          secret=req_info['oauth_token_secret']).put()
        
        # get the oauth url
        oauth_url=xml.sax.saxutils.escape(req_info['url'], {'"': "&quot;"})
        # oauth_url=h(req_info['url'])

        content='''
        <div id="container">
        <div id="intro"><h2>Tweet  It  Easy</h2>
        <p>TwiTalker是一款第三方应用，提供推特Gtalk机器人服务，通过添加TwiTalker在Gtalk上的帐号您可以方便地在Gtalk上更新自己的推特和接收好友消息。如果第一次使用TwiTalker请<a href="%s">登陆</a>验证获取验证码和密钥(<a href="faq">如何获取</a>)，以便Gtalk绑定推特帐号，具体验证绑定过程详见帮助。欢迎在推特上Follow <a href="https://twitter.com/Twi_Talker">@Twi_Talker</a>以获取最新消息和更新。<br /></p>
        <h2>TwiTalker 功能格式</h2>
        <p>你大爷，烦死了</p>
        </div>

        <div id="step">
        <h2>OAuth验证(需翻墙)</h2>
        <a href="%s"><img style="margin-bottom:0px" src="img/login.png" /></a><br />
        <h2>工作原理</h2>
        <p>TwiTalker利用Google appengine为平台架设，通过OAuth验证，用户不需提供密码就可以把自己的Gtalk帐号和推特绑定在一起，这样就可以通过Gtalk更新自己的推特消息，由于考虑服务器负载问题，每个TwiTalker机器人帐号好友上限是250人。TwiTalker已经开源，如果您对TwiTalker的原理和开发感兴趣，欢迎查看项目主页或联系开发者<a href="https://twitter.com/kavin_gray">@Kavin_Gray</a></p>
        <img style="margin-bottom:0px" src="img/tie.png" />
        </div>
        <div class="clean"></div>
        </div>
        '''%(oauth_url,oauth_url)
    
        # initing the pages    
##        self.response.out.write(HEADER)    
##        self.response.out.write(content)
##        self.response.out.write(FOOTER)
        
        datefrom = str(int((datetime.datetime.utcnow()+datetime.timedelta(hours=+8)).strftime("%Y%m%d")) - 1) + '000000'
        dateto   = (datetime.datetime.utcnow()+datetime.timedelta(hours=+8)).strftime("%Y%m%d%H%M%S")
        fxtest = fxdb.all()
        fxtest.filter('indexTime >=', datefrom).filter('indexTime <=', dateto)
        fxtest.order('indexTime')
        hello=[]
        hello = fxtest.fetch(limit=310)
        self.response.out.write(HEADER)
        dd=[]
        for helloline in hello:
            dd.append(str(helloline.audOfferRate))
        datastr = ",".join(dd)
        maxmin = [str(float(min(dd)) - 0.2), str(float(max(dd)) + 0.2)]
        maxminstr = ",".join(maxmin)
        
        fxHist = fxdb.all()
        fxtest.filter('indexTime >=', datefrom).filter('indexTime <=', dateto)
        fxHist.order('-audOfferRate')
        maxRateTime = fxHist.get().audUpdateTime
        
        fxHist = fxdb.all()
        fxtest.filter('indexTime >=', datefrom).filter('indexTime <=', dateto)
        fxHist.order('audOfferRate')
        minRateTime = fxHist.get().audUpdateTime
        logging.debug('datefrom: %s  dateto: %s' %(datefrom,dateto))  
        logging.debug('minRate: %s  maxRate: %s' %(str(float(min(dd))),str(float(max(dd)))))
        logging.debug('minTime: %s  maxTime: %s' %(str(minRateTime),str(maxRateTime))) 
        logging.debug('maxminstr: %s' %(maxminstr))     
        
        img='''
        <img src="//chart.googleapis.com/chart?chs=400x150&cht=lc&chds=%s&chd=t:%s&chls=1" width="400" height="150" alt="" />'''%(maxminstr,datastr)
        cons='''
        <div id="container">
        <div id="intro"><h2>Tweet  It  Easy</h2>
        <p>%s<br /></p>
        <h2>TwiTalker 功能格式</h2>
        <p>你大爷，烦死了</p>
        今日最低点: %s 时间: %s
        今日最高点: %s 时间: %s
        </div>
        '''%(img,str(float(min(dd))),str(minRateTime),str(float(max(dd))),str(maxRateTime))
        self.response.out.write(cons)
##        chart.googleapis.com/chart?chs=160x79&cht=lc&chds=645,666&chd=t:657,658,661,654,655&chls=1
##        <img src="//chart.googleapis.com/chart?chs=160x79&cht=lc&chds=645,666&chd=t:654,655,661,654,655&chls=1" width="160" height="79" alt="" />
##        xmppmessage = "chart.googleapis.com/chart?chs=1000x200&cht=lc&chds=" + maxminstr + "&chd=t:" + datastr + "&chls=1"
##        xmpp.send_message('maming622@gmail.com', xmppmessage)
#        haha = getfx()
##        mailBody = '澳元卖出价:'+ haha[3] + '\n' + '澳元现汇买入价:' + haha[4] + '\n' + '时间:' + haha[6] + '\n\n' + '美元卖出价:' + haha[12] + '\n' + '美元现汇买入价:' + haha[13] + '\n' + '时间:' + haha[15]
##        mailBody += '\n'
##        htlmBody = '''
##        <html><head></head><body>
##        <p>澳元卖出价: %s
##        澳元现汇买入价: %s
##        时间: %s</p><br>
##        <p>美元卖出价: %s
##        美元现汇买入价: %s
##        时间: %s</p>
##        %s
##        '''%(haha[3],haha[4],haha[6],haha[12],haha[13],haha[15],img)
##        mail.send_mail(sender="AUD Rate Trend <audtrend@italkbot.appspotmail.com>",
##                      to=["Ming MA <maming622@gmail.com>", "Ming MA <neilma@hotmail.com>"],
##                      subject='测试邮件',
##                      body=mailBody,
##                      html=htlmBody)

class CallbackHandler(webapp.RequestHandler):
 
    def get(self, mode=''):
        
        if mode == '':
            twitter = AppEngineTwitter()
            twitter.set_oauth(OAUTH_KEY, OAUTH_SECRET)
            req_token = self.request.get('oauth_token')
     
            query = OAuthRequestToken.all()
            query.filter('token = ', req_token)
            req_tokens = query.fetch(1)
     
            acc_token = twitter.exchange_oauth_tokens(req_token, req_tokens[0].secret)
            if (twitter.verify()==200):
                name = simplejson.loads(twitter.last_response.content)['screen_name']
                OAuthAccessToken( acc_token=acc_token['oauth_token'],
                                  acc_secret=acc_token['oauth_token_secret'],
                                  username=name.encode("utf-8")).put()            
                
                self.response.out.write(HEADER)
                self.response.out.write(JS)
                con_begin='''
                <div id="container">
                <div id="content">
                <h2>验证成功:)</h2>
                <P>恭喜你，%s，你已经成功授权TwiTalker并获取验证码和密钥，请<strong>务必首先保管好它们</strong></p>'''%(name.encode("utf-8"))
                self.response.out.write(con_begin)
                self.response.out.write("验证码: ")
                self.response.out.write(acc_token['oauth_token'])
                self.response.out.write("<br />密钥: ")
                self.response.out.write(acc_token['oauth_token_secret'])
                con_copy='''
                <form name="it">
                <textarea name="select1" rows="2" cols="120">-v '''+acc_token['oauth_token']+" "+acc_token['oauth_token_secret']+'''</textarea>
                <input onclick="copyit('it.select1')" type="button" value="复制绑定信息" name="cpy"></input>
                </form>
                '''
                self.response.out.write(con_copy)
    ##            db_ser = DBService()            
    ##            db_ser.setQuery('TwiCount')
    ##            twiNum=db_ser.getQuery()
    ##            num=twiNum.count()
    ##            if(num<250):
    ##                con_foot='<p>下一步: 推荐在GTalk添加'+ BOT +'为好友，并向该帐号发送以下格式绑定信息完成绑定:<br /><b>-v 空格 验证码 空格 密钥</b> (也可以直接复制框中信息并向机器人帐号发送)'+'</p>'
    ##            else:
    ##                con_foot='<p>目前没有可用机器人</p> '
            
    ##            self.response.out.write(con_foot)
                self.response.out.write('<p>如果你对验证过程仍有疑问，请参考<a href="faq">帮助页面</a></p>')
                
                self.response.out.write(FOOTER)
            
class OAuthRequestToken(db.Model):
    token = db.StringProperty()
    secret = db.StringProperty()

class OAuthAccessToken(db.Model):
    token = db.StringProperty()
    secret = db.StringProperty()    
    username = db.StringProperty()

routing = [('/', InitHandler),
           ('/oauth/(.*)', CallbackHandler)]

logging.getLogger().setLevel(logging.DEBUG)
ereporter.register_logger()

application = webapp.WSGIApplication(routing, debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
