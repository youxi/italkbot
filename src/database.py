# -*- coding: utf-8 -*-
from google.appengine.ext import db

class fxdb(db.Model):
    indexTime       = db.StringProperty()
    audOfferRate    = db.StringProperty()
    audBillBidRate  = db.StringProperty()
    audUpdateTime   = db.StringProperty()
    usdOfferRate    = db.StringProperty()
    usdBillBidRate  = db.StringProperty()
    usdUpdateTime   = db.StringProperty()
    when            = db.DateTimeProperty(auto_now_add=True)
