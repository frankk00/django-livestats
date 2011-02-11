# -*- coding: utf-8 -*-
'''
   Created by   prinkk
   Developer    Kristian Øllegaard
   Mail         kristian@prinkk.net
   www          http://www.prinkk.net

   Date         23 10 2010

   License      Copyright 2010 prinkk
   Filename     urls.py
'''

from django.conf.urls.defaults import *
from django.conf import settings
from models import Monitor

urlpatterns = patterns('',    
    ### Manual registrations
    
    (r'^registration/$', 'livestats.views.registration_form', {}, 'livestats_registration_form'),
    
    ### Monitor displays
    
    # List
    #(r'^$', 'django.views.generic.list_detail.object_list', {'queryset': Monitor.objects.all(),}, 'livestats_monitor_list'),
    (r'^$', 'livestats.views.monitor_list', {}, 'livestats_monitor_list'),
    
    # Today
    (r'^(?P<monitor_id>\d+)/$', 'livestats.views.monitor_detail', {}, 'livestats_monitor_detail'),
    (r'^(?P<monitor_id>\d+)/ajax/$', 'livestats.views.monitor_detail', {'ajax': True}, 'livestats_monitor_ajax'),
    
    # A specified month
    (r'^(?P<monitor_id>\d+)/(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'livestats.views.monitor_detail', {}, 'livestats_monitor_detail_month'),
    (r'^(?P<monitor_id>\d+)/(?P<year>\d{4})/(?P<month>\d{1,2})/ajax/$', 'livestats.views.monitor_detail', {'ajax': True}, 'livestats_monitor_ajax_month'),
    
    # A specified day
    (r'^(?P<monitor_id>\d+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', 'livestats.views.monitor_detail', {}, 'livestats_monitor_detail_day'),
    (r'^(?P<monitor_id>\d+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/ajax/$', 'livestats.views.monitor_detail', {'ajax': True}, 'livestats_monitor_ajax_day'),
    
    ### Overview displays
    
    # Today
    (r'^overview/(?P<overview_id>\d+)/$', 'livestats.views.overview_detail', {}, 'livestats_overview_detail'),
    (r'^overview/(?P<overview_id>\d+)/ajax/$', 'livestats.views.overview_detail', {'ajax': True}, 'livestats_overview_detail'),
)