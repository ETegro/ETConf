{% load i18n %}
{% autoescape off %}

{{ main_header }}

.. header::

   .. list-table::
      :widths: 50 50
      :header-rows: 0

      * - .. image:: {{ images_path }}/design/logo-gif.gif
             :width: 90%
        - 
          .. class:: meine

          {{ slogan }}

{{ description }}

.. image:: {{ images_path }}/{{ main_image.0 }}/{{ main_image.1 }}/big/0.jpg
   :width: 70%

{% if specifications %}
.. list-table::
   :widths: 30 70
   :header-rows: 0

   {% for row in specifications %}
   * - {{ row.skey }}
     - 
       {% for svalue in row.svalues %}{{ svalue }}
       {% endfor %}
   {% endfor %}
{% endif %}

.. footer::

   .. list-table::
      :widths: 30 70
      :header-rows: 0
      :class: hell

      * -
          .. class:: meine

          Your Company

        -
          .. class:: meine

          ©2005 Your Company

{% endautoescape %}
