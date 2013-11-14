#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# TwiTalker - Tweet it easy with your GTalk
# Copyright 2009-2010 Kavin Gray
# See LICENSE for details.
# 
#

# =====================   twitter app settting      ======================

# Change the OAUTH_KEY below to the match the consumer key of your twitter app.
# 将你在twitter创建的应用的consumer key替换到下面OAUTH_KEY参数
OAUTH_KEY = 't7OvJHSoly5EzZjUW9KEQ'

# Change the OAUTH_SECRET below to the match the consumer secret of your twitter app.
# 将你在twitter创建的应用的consumer secret替换到下面OAUTH_SECRET参数
OAUTH_SECRET = 'dCuUTsJ3RTm3JrEV7HicdkLt9XTZ7MCTNXsuHd1E'

# Be aware to change the callback setting to this url on your twitter app: http://your gae app id.appspot.com/oauth
# 注意要在Twitter应用的设置里把callback参数设置为 http://你的gae app id名称.appspot.com/oauth

# =====================   gae  settting      ======================

# Change the APP_ID account below to your GAE Application Identifier.
# 机器人的地址，将下面参数改为你在GAE创建的应用ID，
APP_ID='italkbot'

# Initing the bot account.Do not Change this expression
# 不要修改这个参数
ACCOUNT = APP_ID+'@appspot.com'

# http://italkbot.appspot.com/oauth/?oauth_token=uDPyWhZMSsGp0nM7eC1MaP6ExOQoLTIcX14UoGGK6lU&oauth_verifier=DGvzpK6NYmSds3TCGhoBAziYLV10ODLX9cqbEJDjs
# oauth_token 1g3ASCehW2F5urScX0BjOob0lEgQve9iIqGQo7q5Rmw
# oauth_verifier tOIVFYR2LiJkdxhW32LFrv7yKP9RXlhe0U1Y4hvc
