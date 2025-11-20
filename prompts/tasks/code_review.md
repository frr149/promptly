Review the following {{ language|default("Python") }} code:

```{{ language|lower|default("python") }}
{{ code }}
```

{% if focus %}
Focus on:
{% for area in focus %}
- {{ area }}
{% endfor %}
{% else %}
Focus on:
- Code quality and best practices
- Potential bugs
- Performance issues
- Security vulnerabilities
{% endif %}

Please provide:
1. Summary of findings
2. Specific issues with line numbers
3. Suggested improvements
