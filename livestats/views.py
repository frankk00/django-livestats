# -*- coding: utf-8 -*-
'''
   Created by   prinkk
   Developer    Kristian Øllegaard
   Mail         kristian@prinkk.net
   www          http://www.prinkk.net

   License      Copyright 2011 prinkk
   Filename     views.py
'''

from django.shortcuts import render_to_response
from django.template import RequestContext
import datetime
from models import *
from utils import *
from operator import attrgetter
from forms import RegistrationForm
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required

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

@cache_page(10)
def monitor_detail(request, monitor_id=1, ajax=False, day=None, month=None, year=None):
    # Get current monitor from url
    monitor = Monitor.objects.get(pk=monitor_id)
    # Get all entities for current monitor
    reg_entities = monitor.entities.all()
    # Get RegistrationType objects from monitor
    regtypes = RegistrationType.objects.filter(kpi__monitorkpi__monitor=monitor)
    # Get tablecolumns for monitor
    tablecolumns = MonitorTableKPI.objects.filter(monitor=monitor)
    # Get KPI Boxes for monitor
    boxes = MonitorBoxKPI.objects.filter(monitor=monitor).order_by('order')
    # Assume the date is given manually, if set to false later, it will make
    # the KPI boxes make their own date interval, based in the current date
    manual_date= True
    
    # Check if the page should live update and generate a Registraion queryset,
    # based on the date from the url and use it as a manual date
    
    if day and month and year:
        live_update = False
        reg = Registration.objects.filter(date__day=day, date__month=month, date__year=year)
    elif month and year:
        if int(month) == datetime.date.today().month and int(year) == datetime.date.today().year:
            live_update = True
        else:
            live_update = False
        reg = Registration.objects.filter(date__month=month, date__year=year)
    else:
        date = datetime.date.today()
        reg = Registration.objects.filter(date__day=date.day, date__month=date.month, date__year=date.year)
        live_update = True
        manual_date = False
    # Return hostpage
    if not ajax:
        last_week_range = DateInterval(date=datetime.date.today()).lastweek()
        kpi_history = KPIHistory.objects.filter(monitor=monitor, kpi=monitor.order_by, date_from__range=last_week_range, date_to__range=last_week_range)
        return render_to_response("livestats/monitor_detail.html", {'live_update': live_update,
        'monitor': monitor, 'kpi_history': kpi_history, 'boxes': boxes, 'tablecolumns': tablecolumns},
            context_instance=RequestContext(request))
        
    # Create KPI boxes
    if manual_date:
        stats = Stats(MonitorBoxKPI.objects.filter(monitor=monitor).order_by('-order'), reg.filter(entity__in=reg_entities), manual_date=manual_date)
    else:
        stats = Stats(MonitorBoxKPI.objects.filter(monitor=monitor).order_by('-order'), Registration.objects.filter(entity__in=reg_entities))
    stats.monitor = monitor
    
    
    
    
    # Competition // # KPI Competition status
    
    m = MonitorCompetition.objects.filter(monitors=monitor)
    c = []
    mcdict = {}
    if m.count() > 0:
        for mc in m:
            for mon in mc.monitors.all():
                mstats = Stats([mc.kpi], reg.filter(entity__in=mon.entities.all()), mc.kpi)
                mstats.monitor = mon
                mstats.competition = mc
                c.append(mstats)
        c = sorted(c, key=attrgetter('order_by'), reverse=True)
        i = 0
        for mc in c:
            i = i +1
            if mc.monitor == monitor:
                try:
                    stats.competition = i
                    stats.competition_css_class = MonitorCompetitionGoal.objects.filter(monitorcompetition=mc.competition, nr=i).get().color
                except:
                    stats.competition = i
                    stats.competition_css_class = "grey"
        
    # Create data for table
    entities = []
    if monitor.show_table:
        for entity in reg_entities:
            entity_reg = reg.filter(entity=entity, type__in=regtypes)
            if entity_reg:
                agstats = Stats(tablecolumns, entity_reg, monitor.order_by, manual_date=manual_date)
                agstats.entity = entity
                entities.append(agstats)
        entities = sorted(entities, key=attrgetter('order_by'), reverse=True)
        
    # Provide an <html> and <body> tag if not ajax, to make compatible with django debug toolbar
    if request.is_ajax():
        return render_to_response("livestats/monitor_detail.json",
            {'summary': stats, 'entities': entities, 'html': False},
            context_instance=RequestContext(request))
    else:
        return render_to_response("livestats/monitor_detail.json",
            {'summary': stats, 'entities': entities, 'html': True},
            context_instance=RequestContext(request))
        

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
            
            
@cache_page(1)    
def monitor_list(request):
    day=datetime.date.today().day
    month=datetime.date.today().month
    year=datetime.date.today().year
    live_update = True
    reg = Registration.objects.filter(date__day=day, date__month=month, date__year=year)

    kpis = []

    for monitor in Monitor.objects.all():
        regtypes = RegistrationType.objects.filter(kpi__monitorkpi__monitor=monitor)
        regs = reg.filter(entity__in=monitor.entities.all())
        stats = Stats([monitor.order_by,], regs, monitor.order_by)
        stats.monitor = monitor
        kpis.append(stats)

    return render_to_response("livestats/monitor_list.html",
        {'object_list': kpis,},
        context_instance=RequestContext(request))