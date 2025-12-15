Revisa el siguiente código en {{ language|default("Python") }}:

```{{ language|lower|default("python") }}
{{ code }}
```

{% if focus %}
Céntrate en:
{% for area in focus %}
- {{ area }}
{% endfor %}
{% else %}
Céntrate en:
- Calidad del código y buenas prácticas
- Posibles bugs
- Problemas de rendimiento
- Vulnerabilidades de seguridad
{% endif %}

Por favor, proporciona:
1. Resumen de hallazgos
2. Problemas específicos con números de línea
3. Mejoras sugeridas
