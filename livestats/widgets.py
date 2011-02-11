# -*- coding: utf-8 -*-
'''
   Created by   prinkk
   Developer    Kristian Øllegaard
   Mail         kristian@prinkk.net
   www          http://www.prinkk.net

   License      Copyright 2011 prinkk
   Filename     widgets.py
'''

from django import forms
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
import textwrap

# Mainly taken from on http://www.djangosnippets.org/snippets/951/ and changed to fit this application

class SubmitButton(forms.Widget):
    """
    A widget that handles a submit button.
    """
    def __init__(self, name, value, label, attrs):
        self.name, self.value, self.label = name, value, label
        self.attrs = attrs
        
    def __unicode__(self):
        
        final_attrs = self.build_attrs(
            self.attrs,
            type="submit",
            id=self.label.replace(" ", "_"),
            name=self.name,
            value="\n".join(textwrap.TextWrapper(width=11, drop_whitespace=False).wrap(self.label)), # Create \r\n if width is to wide
            )
        return mark_safe(u'<input%s />' % (
            forms.widgets.flatatt(final_attrs),

            ))

class MultipleSubmitButton(forms.Select):
    """
    A widget that handles a list of submit buttons.
    """
    def __init__(self, attrs={'class': 'multiplesubmit'}, choices=()):
        self.attrs = attrs
        self.choices = choices

    def __iter__(self):
        for value, label in self.choices:
            yield SubmitButton(self.name, value, label, self.attrs.copy())

    def __unicode__(self):
        return '<input type="submit" />'
        
    def render(self, name, value, attrs=None, choices=()):
        """Outputs a <ul> for this set of submit buttons."""
        self.name = name
        return mark_safe(u'\n%s' % u'\n'.join(
            [u'%s' % force_unicode(w) for w in self],
            ))
    def value_from_datadict(self, data, files, name):
        """
        returns the value of the widget: IE posts inner HTML of the button
        instead of the value.
        """
        value = data.get(name, None)
        value = "".join(value.split("\r\n")) # Assemble from \r\n
        print value
        if value in dict(self.choices):
            return value
        else:
            inside_out_choices = dict([(v, k) for (k, v) in self.choices])
            if value in inside_out_choices:
                return inside_out_choices[value]
        return None