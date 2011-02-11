REQUIRES
========

- jQuery
http://jquery.com/

- jquery.tableSort.js
http://mitya.co.uk/scripts/Animated-table-sort-REGEXP-friendly-111

The templates tries to find them in /media/js/


INSTALL
=======

- Add to INSTALLED_APPS
- Add to urls.py (e.g. (r'^', include('livestats.urls')), )
- Create a base.html in root template directory
- Add jquery to base.html
- Create appropriate styles for the table and KPI boxes