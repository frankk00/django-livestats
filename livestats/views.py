# -*- coding: utf-8 -*-
'''
   Created by   prinkk
   Developer    Kristian Øllegaard
   Mail         kristian@prinkk.net
   www          http://www.prinkk.net

   License      Copyright 2011 prinkk
   Filename     views.py
'''
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
import datetime
from django.template.loader import render_to_string
from models import *
from utils import *
from operator import attrgetter
from forms import RegistrationForm
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from backends.db import DjangoOrmBackend


@login_required
def registration_form(request):
    entity = request.user.entities_set
    regtypes = request.user.userregistrationaccess.registrations.filter(manual=True)
    if request.POST:
        r = Registration(entity=entity, date=datetime.datetime.now())
        form = RegistrationForm(regtypes, request.POST, instance=r)
        if form.is_valid():
            object = form.save()
            form = RegistrationForm(regtypes)
            return render_to_response("livestats/registration_form.html", {'form': form, 'success': True, 'object': object, 'entity': entity},
                context_instance=RequestContext(request))
    else:
        form = RegistrationForm(regtypes)
    return render_to_response("livestats/registration_form.html", {'form': form, 'entity': entity},
        context_instance=RequestContext(request))

def monitor_detail(request, monitor_id=1, ajax=False, day=None, month=None, year=None):
    if not ajax:
        if day and month and year:
            live_update = False
        elif month and year:
            if int(month) == datetime.date.today().month and int(year) == datetime.date.today().year:
                live_update = True
            else:
                live_update = False
        else:
            live_update = True
        monitor = Monitor.objects.get(pk=monitor_id)
        return render_to_response("livestats/monitor_detail.html", {'live_update': live_update,
                                                                    'monitor': monitor,
                                                                    'boxes': MonitorBoxKPI.objects.filter(monitor=monitor).order_by('order'),
                                                                    'tablecolumns': MonitorTableKPI.objects.filter(monitor=monitor)},
            context_instance=RequestContext(request))

    if not request.GET.has_key('refresh'):
        d = DjangoOrmBackend(monitor_id, day, month, year).return_dict()
        return render_to_response("livestats/monitor_detail.json",
                d,
                context_instance=RequestContext(request))
    else:
        return HttpResponse("""
        {
            "projects" : []
        }
            """)


@cache_page(10)    
def overview_detail(request, overview_id, ajax=False, day=None, month=None, year=None):
    
    if day and month and year:
        live_update = False
        reg = Registration.objects.filter(date__day=day, date__month=month, date__year=year)
    elif month and year:
        live_update = False
        reg = Registration.objects.filter(date__month=month, date__year=year)
    else:
        day=datetime.date.today().day
        month=datetime.date.today().month
        year=datetime.date.today().year
        live_update = True
        reg = Registration.objects.filter(date__day=day, date__month=month, date__year=year)
    
    o = Overview.objects.get(pk=overview_id)
    kpis = []
    
    for monitor in o.monitors.all():
        regtypes = RegistrationType.objects.filter(kpi__monitorkpi__monitor=monitor)
        regs = reg.filter(entity__in=monitor.entities.all())
        stats = Stats([monitor.order_by,], regs, monitor.order_by)
        stats.monitor = monitor
        kpis.append(stats)
    
    if ajax:    
        return render_to_response("livestats/overview_detail.json",
            {'overview': o, 'kpis': kpis},
            context_instance=RequestContext(request))
    else:
        return render_to_response("livestats/overview_detail.html",
            {'overview': o, 'kpis': kpis, 'live_update': True},
            context_instance=RequestContext(request))
            
def monitor_list(request):
    day=datetime.date.today().day
    month=datetime.date.today().month
    year=datetime.date.today().year
    live_update = True
    reg = Registration.objects.filter(date__day=day, date__month=month, date__year=year)
    
    if request.GET.has_key("next"):
        next = request.GET["next"]
    else:
        next = reverse("livestats_monitor_list")

    kpis = []

    for monitor in Monitor.objects.all():
        regtypes = RegistrationType.objects.filter(kpi__monitorkpi__monitor=monitor)
        regs = reg.filter(entity__in=monitor.entities.all())
        stats = Stats([monitor.order_by,], regs, monitor.order_by)
        stats.monitor = monitor
        kpis.append(stats)

    return render_to_response("livestats/monitor_list.html",
        {'object_list': kpis, 'next': next},
        context_instance=RequestContext(request))