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

          ETegro Technologies

          .. class:: meine

          Россия, Москва, 111141

          .. class:: meine

          ул. Электродная, 2, #12-13-14

          .. class:: meine

          Тел/Факс: +7-495-380-0288

          .. class:: meine

          `sales@etegro.com <mailto:sales@etegro.com>`_

          .. class:: meine

          `www.etegro.com <http://www.etegro.com/>`_

        -
          .. class:: meine

          ©2005 ETegro Technologies. Все права защищены

          .. class:: meine

          ETegro Technologies и логотип ETegro Technologies являются
          зарегистрированными торговыми марками ЗАО ЕТегро Текнолоджис.
          
          .. class:: meine

          Примечание: упомянутые наименования сторонних продуктов
          являются торговыми марками их владельцев и приведены
          исключительно в целях идентификации. Цены и спецификации
          могут быть изменены без оповещения.

{% endautoescape %}
