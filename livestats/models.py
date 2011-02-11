# -*- coding: utf-8 -*-
'''
   Created by   prinkk
   Developer    Kristian Øllegaard
   Mail         kristian@prinkk.net
   www          http://www.prinkk.net

   License      Copyright 2011 prinkk
   Filename     models.py
'''

from django.db import models
from django.contrib.auth.models import User
from django.template import Template, Context
from django.db.models import Avg, Max, Min, Count, Sum
from decimal import Decimal
from django.utils.translation import ugettext_lazy as _


KPI_TYPES = (
    ('SUM', _('Sum')),
    ('AVG', _('Average')),
    ('COUNT', _('Count')),
)

COLORS = (
    ('green', _('Green')),
    ('yellow', _('Yellow')),
    ('red', _('Red')),
    ('orange', _('Orange')),
    ('grey', _('Grey'))
)

PERIODS = (
    ('DAILY', _('Daily')),
    ('WEEKLY', _('Weekly')),
    ('MONTHLY', _('Monthly')),
    ('YEARLY', _('Yearly')),
#    ('CUSTOM', 'Custom'), - Needs to be implemented in utils.py
)

class EntityType(models.Model):
    """
    Organising for Entities, e.g. "Agents", "Cars", "Shops"
    """
    name = models.CharField(max_length=128)
    
    def __unicode__(self):
        return self.name

class Entity(models.Model):
    """
    An entity which all registrations relates to,
    for instance an Agent in a callcenter.
    """
    type = models.ForeignKey(EntityType)
    user = models.OneToOneField(User, blank=True, null=True, related_name="entities_set")
    name = models.CharField(max_length=64, blank=True)
    class Meta:
        verbose_name = _("entity")
        verbose_name_plural = _("entities")
        ordering = ('name',)
                
    def __unicode__(self):
        return self.name

class RegistrationType(models.Model):
    """
    Types of registrations, used for calculating KPIs
    e.g. this pseudocode
    KPI = (RegistrationTypeA/RegistrationTypeB*100)
    In reality variable_name is rendered in the KPI.template, using utils.Stats
    """
    title = models.CharField(max_length=100)
    type = models.CharField(max_length=12, choices=KPI_TYPES)
    variable_name = models.CharField(max_length=64)
    manual = models.BooleanField()
    
    def __unicode__(self):
        return self.title
    
class Registration(models.Model):
    """
    A specific kind of registration related to an entity,
    the field value is used for sum() or uniqueness on manual
    registrations
    """
    value = models.DecimalField(decimal_places=4, max_digits=16)
    type = models.ForeignKey(RegistrationType)
    unique_id = models.CharField(max_length=128, blank=True)
    date = models.DateTimeField()
    entity = models.ForeignKey(Entity)
    
class KPI(models.Model):
    """
    Key Performance Indicator
    A formula based on one or more registrationtypes and using utils.Stats
    returning a value for a specific period of time
    """    
    title = models.CharField(max_length=128)
    tablecolumn_name = models.CharField(max_length=128, editable=False)
    registrationtypes = models.ManyToManyField(RegistrationType)
    
    template = models.TextField()
    subtitle_template = models.TextField(blank=True)
    
    prefix = models.CharField(max_length=12, blank=True)
    suffix = models.CharField(max_length=12, blank=True)
    
    decimal_places = models.IntegerField(default=0)
    
    # implement Empty value
    
    order = models.IntegerField(default="100", editable=False)
    
    def __unicode__(self):
        return self.title
    
    class Meta:
        ordering = ['title']
        
class KPIGoal(models.Model):
    """
    Enables colored KPIs
    
    value should be greter than or equal to the value where the color should apply
    e.g. KpiGoal(value=0, color="red"), KpiGoal(value=50, color="green")
    value = 31 -> color = red
    value = 51 -> color = green
    
    Caution! If there is only one color, even though it has a higher value, it will be picked
    """
    kpi = models.ForeignKey(KPI)
    value = models.DecimalField(decimal_places=4, max_digits=16)
    color = models.CharField(max_length=7, choices=COLORS)
    
class Monitor(models.Model):
    """
    A collection of entities, each showing selected KPIs (MonitorKPIs)
    and common stats (MonitorBoxKPI)
    
    Consider a monitor as a physical monitor hanging on the wall.
    """
    title = models.CharField(blank=True, max_length=100)
    show_kpis = models.BooleanField()
    show_table = models.BooleanField()
    
    order_by = models.ForeignKey(KPI, related_name="monitorsortby_set")
    entities = models.ManyToManyField(Entity)
    
    @models.permalink
    def url(self):
        return ('livestats_monitor_detail', (self.id, ))
    
    def __unicode__(self):
        return self.title
    class Meta:
        ordering = ['title']
        
class MonitorKPI(models.Model):
    """
    M2M Relation between Monitor and KPI with some extra details
    """
    monitor = models.ForeignKey(Monitor)
    kpi = models.ForeignKey(KPI)
    
    order = models.IntegerField(null=True)
    title = models.CharField(max_length=128)
    
    class Meta:
        ordering = ['order']

class MonitorTableKPI(MonitorKPI):
    pass
    
class MonitorBoxKPI(MonitorKPI):
    """
    Enables KPI boxes to define another default period than the current date.
    Currently not implemented in the table, since it could lead to very large
    SQL queries, not suited for "live updates".
    """
    default_period = models.CharField(blank=True, default="DAILY", max_length=64, choices=PERIODS) # DAILY, WEEKLY, MONTHLY, YEARLY, CUSTOM (date_start, date_end)
    date_start = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
        
class KPIHistory(models.Model):
    """
    KPI history
    """
    monitor = models.ForeignKey(Monitor)
    kpi = models.ForeignKey(KPI)
    value = models.DecimalField(decimal_places=4, max_digits=16)
    date_from = models.DateTimeField()
    date_to = models.DateTimeField()
    
    class Meta:
        ordering = ('date_to', 'date_from')
        
class UserRegistrationAccess(models.Model):
    """
    Gives custom access to register Regstration for certain RegistrationType manually
    """
    user = models.OneToOneField(User, unique=True)
    registrations = models.ManyToManyField(RegistrationType)
    def __unicode__(self):
        return self.user.username
        
class Overview(models.Model):
    """
    Makes an overview of several monitors, where it compares
    the monitors based on Monitor.order_by
    """
    title = models.CharField(max_length=100)
    monitors = models.ManyToManyField(Monitor)
    
    def __unicode__(self):
        return self.title
        
# Possibility to make two monitors compete, giving the results in the color of each monitors main KPI box
# Experimental

class MonitorCompetition(models.Model):
    title = models.CharField(max_length=100)
    monitors = models.ManyToManyField(Monitor)
    kpi = models.ForeignKey(KPI)

    def __unicode__(self):
        return self.title

class MonitorCompetitionGoal(models.Model):
    monitorcompetition = models.ForeignKey(MonitorCompetition)
    nr = models.IntegerField()
    color = models.CharField(max_length=7, choices=COLORS)
    class Meta:
        unique_together = ('nr', 'monitorcompetition')