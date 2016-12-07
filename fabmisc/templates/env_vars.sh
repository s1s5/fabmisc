# -*- mode:shell-script -*-

{% for key, value in items %}export {{ prefix }}{{ key }}={{ value }}
{% endfor %}
