# -*- coding: utf-8 -*-
import re
import logging
import config
import datetime
from google.appengine.ext import webapp
from google.appengine.ext import ereporter
from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.api import xmpp
from google.appengine.api.backends import backends
from google.appengine.api.urlfetch_errors import DeadlineExceededError
from google.appengine.api.urlfetch_errors import DownloadError 
from google.appengine.ext.webapp.util import run_wsgi_app
from main import OAuthAccessToken
from apptwitter import AppEngineTwitter
from database import fxdb

_max_fetch_count = 9

def getfx():
    urlget = r'http://fx.cmbchina.com/hq/'
##    rows = html2table(urllib.urlopen(url).read())
    for count in range(_max_fetch_count):
        try:
            url_result = urlfetch.fetch(url=urlget,deadline=5)
            break
        except DeadlineExceededError:
            logging.debug('Ohh, deadline exceeded, kao!')
        except DownloadError:
            logging.debug('Ohh, download error, kao!')
        
    if url_result.status_code == 200:
        trs = re.findall(r'澳大利亚元.*?欧元', url_result.content, re.DOTALL)
        rows = []
        for tr in trs:
            x = re.findall(r'>([^<>]*)(?:</a>)?</td>', tr, re.DOTALL)
            x = map(lambda s: s.strip(), x)
            rows.append(x)
        return rows[0]

# ...

class CRONServiceHandler(webapp.RequestHandler):
    def get(self):
#        backend_url = '%s/backend/fetch/%s' % (backends.get_url('fetchbackend'), 'GET')
#        result = urlfetch.fetch(backend_url,method='POST')
#        logging.debug('Backend URL: %s' %(backend_url))
#        logging.debug('Result: %s' %result.content)
 
        if (datetime.datetime.utcnow()+datetime.timedelta(hours=+8)).strftime("%H%M%S") >= '080000' and \
           (datetime.datetime.utcnow()+datetime.timedelta(hours=+8)).strftime("%H%M%S") <= '220000':
            haha = getfx()
    ##        messageBody = '澳元卖出价:'+ haha[3] + ' 更新时间:' + haha[6]
    ##        query = OAuthAccessToken.all()
    ##        username = 'wanyouxi'
    ##        query.filter('username = ', username)
    ##        acc_key = query.fetch(1)
    ##        twitter = AppEngineTwitter()
    ##        twitter.set_oauth(config.OAUTH_KEY, config.OAUTH_SECRET, acc_key[0].token,acc_key[0].secret)
    ##        if (twitter.verify() == 200):
    ##            twitter.update(messageBody)
    ##        else:
    ##            logging.debug('twitter.sent shit')
            
            fxHist = fxdb.all()
            fxHist.order('-indexTime')
            lastfx = fxHist.get().audOfferRate       
            logging.debug(lastfx)
            logging.debug(haha[3])
            if lastfx > haha[3]:
                logging.debug('⬇')
            elif lastfx < haha[3]:
                logging.debug('⬆')
            else:
                logging.debug('-')

##            datefrom = (datetime.datetime.utcnow()+datetime.timedelta(hours=+8)).strftime("%Y%m%d") + '080000'
##            dateto   = (datetime.datetime.utcnow()+datetime.timedelta(hours=+8)).strftime("%Y%m%d%H%M%S")
##            fxtest = fxdb.all()
##            fxtest.filter('indexTime >=', datefrom).filter('indexTime <=', dateto)
##            fxtest.order('indexTime')
##            hello = fxtest.fetch(limit=300)
            
    ##        chartdata = hello.audOfferRate
    ##        chart.googleapis.com/chart?chs=160x79&cht=lc&chds=645,666&chd=t:657,658,661,654,655&chls=1
    ##        xmppmessage = "chart.googleapis.com/chart?chs=160x79&cht=lc&chds=645,666&chd=t:657,658,661,654,655&chls=1"
    ##        xmpp.send_message('maming622@gmail.com', xmppmessage)

            datestring = (datetime.datetime.utcnow()+datetime.timedelta(hours=+8)).strftime("%Y%m%d%H%M%S")
     
            fxdb(indexTime=datestring,
                 audOfferRate=haha[3],
                 audBillBidRate=haha[4],
                 audUpdateTime=haha[6],
                 usdOfferRate=haha[12],
                 usdBillBidRate=haha[13],
                 usdUpdateTime=haha[15]).put()

logging.getLogger().setLevel(logging.DEBUG)
ereporter.register_logger()
application = webapp.WSGIApplication([('/cron_service', CRONServiceHandler)],debug=True)                                      

def main():

    run_wsgi_app(application)

if __name__ == "__main__":
    main()  
