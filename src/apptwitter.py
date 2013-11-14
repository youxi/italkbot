#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
AppEngine-Base-Twitter
 
Twitter API wrapper for applications on Google App Engine
 
See: http://0-oo.net/sbox/python-box/appengine-twitter
License: http://0-oo.net/pryn/MIT_license.txt (The MIT license)
Modified by Kavin Gray
'''
__author__ = 'dgbadmin@gmail.com'
__edit__ = 'grayseason@gmail.com'
 
 
import base64
from google.appengine.api import xmpp
import urllib,urllib2,re
from appoauth import AppEngineOAuth
from django.utils import simplejson
from google.appengine.api import urlfetch
import wordhandler
 
 
class AppEngineTwitter(object):
  
  def __init__(self, tw_name='', tw_pswd=''):
    '''
    Note: Some actions require password or OAuth.
    '''
    self._oauth_api_url = 'https://twitter.com'
    self._api_url='http://api.twitter.com/1'
    self._search_url = 'http://search.twitter.com'
    self.tw_name = tw_name
    self._oauth = None
    self._headers = {}
    if tw_pswd != '':
      auth = base64.encodestring(tw_name + ':' + tw_pswd)[:-1]
      self._headers['Authorization'] = 'Basic ' + auth
 
 
  # ========= Status Methods ===========
 
  def update(self, msg, rid='0'):
    '''
    Post a tweet
    Sucess => Retrun 200
    Fialed => Return other HTTP status
    '''
    
    if(rid=='0'):        
        return self._post('/statuses/update.json', {'status': msg})
    else:
        return self._post('/statuses/update.json', {'status': msg, 'in_reply_to_status_id': long(rid)})


  def delMsg(self, msgid):
    '''
    delete a msg 
    Sucess => Retrun 200
    Fialed => Return other HTTP status
    '''
    url="/statuses/destroy/%s.json"%(msgid) 
    return self._post(url, {}) 



  def getContent(self):
    '''
    return the content
    '''
    return self.content




  # ========= Timeline Methods =========

  def user_timeline(self, page=0,user_name=''):
    '''
    get user Timeline 
    Sucess => Return contents of user timeline /
    Fialed => Return error HTTP status
    '''
    param={}
    if(user_name<>''):
        param['screen_name']=user_name   
    if(page==0):
        param['count']=10
    else:
        param['page']=page
    status = self._get('/statuses/user_timeline.json', param)
    
    if(status==200):
        self.content=self.last_response.content
    return status  


  def home_timeline(self, msgid=0, page=0):
    '''
    save and get home timeline
    Sucess => Return contents of home timeline
    Failed => Return other HTTP status
    '''
    if(msgid==0):
        if(page==0):
            status = self._get('/statuses/home_timeline.json', {"count":10})
        elif(page==-1):
            status = self._get('/statuses/home_timeline.json', {"count":3})
        else:
            status = self._get('/statuses/home_timeline.json', {"page":page})
    else:
        status = self._get('/statuses/home_timeline.json', {"since_id":msgid})
    if status == 200:
      self.content=self.last_response.content
    return status


      
  def friends_timeline(self , msgid=0):
    '''
    save and get friends timeline
    Sucess => Return contents of friends timeline
    Failed => Return other HTTP status
    '''
    if(msgid==0):
        count=10
        status = self._get('/statuses/friends_timeline.json', {"count":count})
    elif(msgid==1):
        count=20
        status = self._get('/statuses/friends_timeline.json', {"count":count})
    else:
        status = self._get('/statuses/friends_timeline.json', {"since_id":msgid})
    if status == 200:
      self.content=self.last_response.content
    return status


  def mentions(self, msgid=0,page=0):
    '''
    get and save Mention messages
    Sucess => Return content of mentions
    Fialed => Return other HTTP status
    '''
    if(msgid==0):
        if(page==0):
            status = self._get('/statuses/mentions.json', {"count":10})
        else:
            status = self._get('/statuses/mentions.json', {"page":page})
    else:
        status = self._get('/statuses/mentions.json', {"page":page})
    if(status==200):
        self.content=self.last_response.content
    return status


  def list_timeline(self, params, msgid=0,page=0):
    '''
    get and save list messages
    Sucess => Return content of list timeline
    Fialed => Return other HTTP status
    '''
    list_url='/lists/statuses.json'
    if(msgid==0):
        if(page==0):
			params['per_page']=10
        elif(page==-1):
			params['per_page']=3
        else:
			params['page']=page
    else:
		params['since_id']=msgid
    status = self._get(list_url, params)
    if(status==200):
        self.content=self.last_response.content
    return status


  def getRt2Me(self,page=0):
    if(page==0):
        count=10
        status = self._get('/statuses/retweeted_to_me.json', {"count":count})
    else:
        status = self._get('/statuses/retweeted_to_me.json', {"page":page})
    if status == 200:
        self.content=self.last_response.content
    return status


  def getListInfo(self,target_name,list_id):
    url='/%s/lists/%s.json'%(target_name,list_id)
    status = self._get(url,{})
    if status == 200:
        self.content=self.last_response.content
    return status
      
      


 
  # ========= Friendship Methods =========
  
  def follow(self, target_name):
    '''
    follow a user
    Sucess => Return 200 /
    Fialed => Return other HTTP status
    '''
    return self._post('/friendships/create.json', {'screen_name': target_name})



  def unfollow(self, target_name):
    '''
    unfollow a user
    Sucess => Return 200 / 
    Fialed => Return other HTTP status
    '''
    return self._post('/friendships/destroy.json', {'screen_name': target_name})


  def is_following(self, target_name):
    '''
    Yes => Return True / No => Return False /
    Fialed => Return HTTP status except 200
    '''
    if self.tw_name == '':
      # With OAuth, screen_name is not required.
      self.verify()
      user_info = simplejson.loads(self.last_response.content)
      self.tw_name = user_info['screen_name'] 
    status = self._get('/friendships/exists.json',
                       {'user_a':target_name , 'user_b': self.tw_name})
    if status == 200:
      return (self.last_response.content == 'true')
    else:
      return status



  def block(self, target_name):
    '''
    block a user
    Sucess => Return 200 /
    Fialed => Return other HTTP status
    '''
    return self._post('/blocks/create.json', {'screen_name': target_name})


  # ========= Direct Message Methods =========
  
  def getDMessage(self,dmid=0,page=0):
    '''
    get and save Direct Messages
    Sucess => Return content of Direct Message
    Fialed => Return other HTTP status
    '''
    if(dmid==0):
      if(page==0):
        status = self._get('/direct_messages.json', {"count":10})
      else:
        status = self._get('/direct_messages.json', {"page":page}) 
    elif(dmid==1):
      status = self._get('/direct_messages.json', {"count":1})
    else:
      status = self._get('/direct_messages.json', {"since_id":dmid})
    if(status==200):
        self.content=self.last_response.content
    return status



  def sentDMessage(self, name ,text):
    '''
    Sent a Direct Messages
    Sucess => Retrun 200
    Fialed => Return other HTTP status
    '''
    return self._post('/direct_messages/new.json', {'screen_name': name,'text': text})




  # ========= Favorite Methods ========  

  def addFav(self, msgid):
    '''
    add a msg as fav
    Sucess => Retrun 200
    Fialed => Return other HTTP status
    '''
    url="/favorites/create/%s.json"%(msgid)
    status=self._post(url, {})    
    return status



  def unFav(self, msgid):
    '''
    destroy a favorite tweets
    Sucess => Retrun 200
    Fialed => Return other HTTP status
    '''
    url="/favorites/destroy/%s.json"%(msgid)
    status=self._post(url, {})    
    return status



  def getFav(self , page=0):
    '''
    get and save your fav messages
    Sucess => Return 200 / Fialed => Return other HTTP status
    '''
    if(page==0):
        status = self._get('/favorites.json', {"count":10})
    else:
        status = self._get('/favorites.json', {"page":page})
    if(status==200):
        self.content=self.last_response.content
    return status



  def rtMsg(self,msgid):
    '''
    get and save the messages
    Sucess => Return 200
    Fialed => Return other HTTP status
    '''
    url="/statuses/show/%s.json"%(msgid)
    status = self._get(url, {})
    if(status==200):
        self.content=self.last_response.content
    return status


  def newRTMsg(self,msgid):
    '''
    get and save the messages
    Sucess => Return 200
    Fialed => Return other HTTP status
    '''
    url="/statuses/retweet/%s.json"%(msgid)
    status = self._post(url, {})
    if(status==200):
        self.content=self.last_response.content
    return status


  def getRtMsg(self):
    '''
    return the message
    '''
    return self.rtmsg  



  # ========= User Methods =========

  def getName(self):
    self.verify()
    user_info = simplejson.loads(self.last_response.content)
    return user_info['screen_name']


  def getUserInfo(self,name):
    '''
    return the info of the user
    '''
    status = self._get('/users/show.json', {"screen_name":name})
    if(status==200):
        self.content=self.last_response.content
    return status


  def verify(self):
    '''
    Verify user_name and password, and get user info
    Sucess => Return 200 / Fialed => Return other HTTP status
    '''
    status = self._get('/account/verify_credentials.json', {})
    if(status==200):
        self.content=self.last_response.content
    return status
 



  # ========= List Methods =========
  def getLists(self,name,cursor):
    url="/%s/lists.json"%(name)
    status = self._get(url, {'cursor':cursor})
    if(status==200):
        self.content=self.last_response.content
    return status


  def getSubscriptions(self,name,cursor):
    url="/%s/lists/subscriptions.json"%(name)
    status = self._get(url, {'cursor':cursor})
    if(status==200):
        self.content=self.last_response.content
    return status


  def getMemberships(self,name,cursor):
    url="/%s/lists/memberships.json"%(name)
    status = self._get(url, {'cursor':cursor})
    if(status==200):
        self.content=self.last_response.content
    return status



  def searchTweet(self,word,page):
    
    params={}
    params['q'] = wordhandler.getString(unicode(word.encode("utf-8"),'utf-8')).encode("utf-8")
    if(page<>0):
        params['page'] = page
    status = self._search('/search.json', params)
    if(status==200):
        self.content=self.last_response.content
    return status

 
  # =========  OAuth methods ==========
  # (See http://0-oo.net/sbox/python-box/appengine-oauth )
 
  def set_oauth(self, key, secret, acs_token='', acs_token_secret=''):
    '''
    Set OAuth parameters
    '''
    self._oauth = AppEngineOAuth(key, secret, acs_token, acs_token_secret)
 
 
  def prepare_oauth_login(self):
    '''
    Get request token, request token secret and login URL
    '''
    dic = self._oauth.prepare_login(self._oauth_api_url + '/oauth/request_token/')
    dic['url'] = self._oauth_api_url + '/oauth/authorize?' + dic['params']
    return dic
 
 
  def exchange_oauth_tokens(self, req_token, req_token_secret):
    '''
    Exchange request token for access token
    '''
    return self._oauth.exchange_tokens(self._oauth_api_url + '/oauth/access_token/',
                                       req_token,
                                       req_token_secret)
 
 
  # =========  Private methods  =========  
 
  def _post(self, path, params):
    url = self._api_url + path
    if self._oauth != None:
      params = self._oauth.get_oauth_params(url, params, 'POST')     
      #self.smessage=type(params["status"])
      #smessage=urllib.urlencode(params)
    res = urlfetch.fetch(url=url,
                         payload=urllib.urlencode(params),
                         method='POST',
                         headers=self._headers)
    self.last_response = res
    return res.status_code


    
  def _get(self, path, params):
    url = self._api_url + path
    if self._oauth != None:
      params = self._oauth.get_oauth_params(url, params, 'GET')
    url += '?' + urllib.urlencode(params)
    res = urlfetch.fetch(url=url, method='GET', headers=self._headers)
    self.last_response = res
    return res.status_code
 
 
  def _search(self, path, params):
    '''
    FYI http://apiwiki.twitter.com/Rate-limiting (Especially 503 error)
    '''

    url = self._search_url + path + '?' + urllib.urlencode(params)
    res = urlfetch.fetch(url=url, method='GET')
    self.last_response = res
    return res.status_code

    if res.status_code == 200:  
      return simplejson.loads(res.content)['results']
    elif res.status_code == 503:
      err_msg = 'Rate Limiting: Retry After ' + res.headers['Retry-After']
    else:
      err_msg = 'Error: HTTP Status is ' + str(res.status_code)
 
    raise Exception('Twitter Search API ' + err_msg)

