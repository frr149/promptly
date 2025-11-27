# promptly

Minimalist reusable prompt templates for LLM applications.

A simple, elegant Python library for managing prompt templates across your LLM projects. No complex configuration, no heavy dependencies, just clean Jinja2 templates and an intuitive API.

## Features

- **Centralized Prompt Library**: All prompts included in the package, ready to use across all projects
- **Minimalist Design**: Single dependency (Jinja2), minimal code, maximum clarity
- **Jinja2 Templating**: Full power of Jinja2 - variables, filters, conditionals, loops
- **Automatic Variable Detection**: No manual configuration needed
- **Type Safe**: Complete type hints for better IDE support
- **Version Control Friendly**: Store prompts as plain markdown files in Git
- **Flexible**: Use built-in prompts, custom prompts, or both with fallback
- **Well Tested**: >90% test coverage with comprehensive test suite
- **Pythonic API**: Intuitive, callable loader with clean error messages

## Installation

### Local Development

Install in editable mode for local development:

```bash
cd promptly
uv pip install -e .
```

### Development with Tests

Install with development dependencies:

```bash
uv pip install -e ".[dev]"
```

### From Another Local Project

#### Option 1: Using uv add (recommended)

Add as editable dependency to your project:

```bash
# With absolute path
uv add --editable /path/to/promptly

# With relative path
uv add --editable ../promptly
```

This automatically adds it to your `pyproject.toml`:

```toml
[project]
dependencies = [
    "promptly @ file:///path/to/promptly",
]
```

#### Option 2: Using uv pip install

Install directly without modifying pyproject.toml:

```bash
# Absolute path
uv pip install -e /path/to/promptly

# Relative path
uv pip install -e ../promptly
```

### From Git Repository

Once published to GitHub:

#### Option 1: Using uv add

```bash
# Latest from main branch
uv add git+https://github.com/username/promptly.git

# Specific tag or branch
uv add git+https://github.com/username/promptly.git@v0.1.0
uv add git+https://github.com/username/promptly.git@develop
```

#### Option 2: Using uv pip install

```bash
uv pip install git+https://github.com/username/promptly.git

# Specific tag or branch
uv pip install git+https://github.com/username/promptly.git@v0.1.0
```

#### Option 3: Manual pyproject.toml

```toml
[project]
dependencies = [
    "promptly @ git+https://github.com/username/promptly.git@main"
]
```

## Quick Start

```python
from promptly import PromptLoader

# Create loader - uses built-in prompts from package by default
loader = PromptLoader()

# List available prompts
print(loader.list())
# ['components/base_skills.md', 'developers/n8n.md', 'developers/airtable.md', ...]

# Use a built-in prompt
prompt = loader("developers/n8n.md")
print(prompt)

# Use a prompt with variables
prompt = loader("tasks/code_review.md",
                language="Python",
                code="def divide(a, b): return a / b")
print(prompt)
```

## Basic Usage

### Create a Loader

```python
from promptly import PromptLoader

# Use built-in prompts from package (default)
loader = PromptLoader()

# Or use custom prompts directory
loader = PromptLoader("my_prompts")

# Or use custom prompts with fallback to built-in prompts
loader = PromptLoader("my_prompts", fallback_to_package=True)

# Or use absolute path
loader = PromptLoader("/absolute/path/to/prompts")
```

### Render Prompts

```python
# Both syntaxes work identically
prompt = loader("code_review.md", language="Python", code="...")
prompt = loader.load("code_review.md", language="Python", code="...")

# Prompts in subdirectories
prompt = loader("tasks/review.md", code="...")
prompt = loader("system/assistant.md", role="helpful")
```

### Detect Variables

```python
# Find out which variables a template uses
variables = loader.variables("code_review.md")
print(variables)  # {'language', 'code', 'focus'}
```

### List Available Prompts

```python
# List all prompts
all_prompts = loader.list()
print(all_prompts)  # ['components/base_skills.md', 'developers/n8n.md', ...]

# List with pattern
dev_prompts = loader.list("developers/*.md")
task_prompts = loader.list("tasks/*.md")
```

## Built-in Prompts

Promptly includes these ready-to-use prompts:

### Developers
- **`developers/n8n.md`** - n8n workflow automation specialist
- **`developers/airtable.md`** - Airtable database specialist
- **`developers/n8n_airtable.md`** - Combined n8n + Airtable integration expert

### Components
- **`components/base_skills.md`** - Base developer skills (reusable component)
- **`components/communication.md`** - Communication style guidelines (reusable component)

### Tasks
- **`tasks/code_review.md`** - Code review prompt template with variables

These prompts use template composition with `{% include %}` to combine reusable components. Check the [Tutorial](TUTORIAL.md) for detailed examples.

## Jinja2 Syntax Guide

### Variables

Use double curly braces for variables:

```jinja2
Hello {{ name }}!
Review this {{ language }} code: {{ code }}
```

### Default Values

Provide fallback values with the `default` filter:

```jinja2
Hello {{ name|default("User") }}!
Language: {{ language|default("Python") }}
```

### Filters

Transform variables with built-in filters:

```jinja2
{# String filters #}
{{ name|upper }}           {# FERNANDO #}
{{ name|lower }}           {# fernando #}
{{ name|title }}           {# Fernando #}

{# List filters #}
{{ items|join(", ") }}     {# Python, Rust, Go #}
{{ items|length }}         {# 3 #}

{# Numeric filters #}
{{ value|round }}          {# 4 #}
{{ negative|abs }}         {# 5 #}

{# Chain filters #}
{{ name|upper|reverse }}   {# ODNANREF #}
```

### Conditionals

Control flow with if/elif/else:

```jinja2
{% if language == "Python" %}
Use pylint for linting
{% elif language == "Rust" %}
Use clippy for linting
{% else %}
Use appropriate linter for {{ language }}
{% endif %}

{# Comparison operators: ==, !=, <, >, <=, >= #}
{% if age >= 18 %}Adult{% endif %}

{# Logical operators: and, or, not #}
{% if age >= 18 and has_license %}Can drive{% endif %}
{% if is_admin or is_moderator %}Has privileges{% endif %}
{% if not is_banned %}Can post{% endif %}
```

### Loops

Iterate over lists and dictionaries:

```jinja2
{# Loop over list #}
{% for item in items %}
- {{ item }}
{% endfor %}

{# Loop with index #}
{% for item in items %}
{{ loop.index }}. {{ item }}
{% endfor %}

{# Loop over dictionary #}
{% for key, value in config.items() %}
{{ key }}: {{ value }}
{% endfor %}
```

### Comments

Add comments that won't appear in output:

```jinja2
{# This is a comment and won't appear in the rendered prompt #}
Hello {{ name }}!
```

### Template Composition

Include other templates:

```jinja2
{% include 'templates/header.md' %}

Main content here...

{% include 'templates/footer.md' %}
```

## Organizing Your Prompts

### Recommended Directory Structure

```
prompts/
├── system/           # System prompts and roles
│   ├── assistant.md
│   └── expert.md
├── tasks/            # Task-specific prompts
│   ├── code_review.md
│   ├── documentation.md
│   └── testing.md
└── templates/        # Reusable components
    ├── header.md
    ├── footer.md
    └── common.md
```

### Naming Conventions

- Use snake_case: `code_review.md`, not `codeReview.md`
- Be descriptive: `detailed_security_review.md` over `review.md`
- Avoid generic names: `bug_analysis.md` over `prompt1.md`

### Example Prompt Template

```markdown
{# prompts/tasks/code_review.md #}

Review the following {{ language|default("Python") }} code for:

{% if focus %}
Focus areas:
{% for area in focus %}
- {{ area }}
{% endfor %}
{% else %}
- Code quality and best practices
- Potential bugs
- Performance issues
- Security vulnerabilities
{% endif %}

Code:
```{{ language|lower|default("python") }}
{{ code }}
```

Please provide:
1. Summary of findings
2. Specific issues with line numbers
3. Suggested improvements
```

## Testing

Run the test suite:

```bash
# Run all tests
make test

# Or directly with pytest
uv run pytest

# With verbose output
uv run pytest -v

# With coverage report
uv run pytest --cov=src/promptly --cov-report=html
```

## Linting

Check code quality:

```bash
make lint

# Or directly
uv run ruff check src/ tests/ examples/
```

## Using in Other Projects

### 1. Install the Package

In your project directory:

```bash
# Recommended: Add as dependency with uv add
uv add --editable ../promptly

# Or from Git
uv add git+https://github.com/username/promptly.git

# Alternative: Install with uv pip (doesn't modify pyproject.toml)
uv pip install -e ../promptly
uv pip install git+https://github.com/username/promptly.git
```

### 2. Create Your Prompts Directory

```bash
mkdir -p prompts/system prompts/tasks prompts/templates
```

### 3. Add Prompts

Create `prompts/tasks/code_review.md`:

```markdown
Review this {{ language }} code:

{{ code }}

Focus on {{ focus|default("best practices and potential bugs") }}.
```

### 4. Use in Your Code

```python
from promptly import PromptLoader

loader = PromptLoader("prompts")

# Generate prompts for your LLM
prompt = loader(
    "tasks/code_review.md",
    language="Python",
    code="def divide(a, b): return a / b"
)

# Use with your favorite LLM library
# response = openai.ChatCompletion.create(
#     messages=[{"role": "user", "content": prompt}]
# )
```

## Advanced Usage

### Custom Filters

Add your own Jinja2 filters:

```python
from promptly import PromptLoader

loader = PromptLoader("prompts")

# Add custom filter
def markdown_code(text, language="python"):
    return f"```{language}\n{text}\n```"

loader.env.filters['mdcode'] = markdown_code

# Use in template: {{ code|mdcode("python") }}
```

### Global Functions

Add global functions to templates:

```python
import datetime

def now():
    return datetime.datetime.now().isoformat()

loader.env.globals['now'] = now

# Use in template: Generated at {{ now() }}
```

### Extending the Loader

Create a custom loader class:

```python
from promptly import PromptLoader

class CachedPromptLoader(PromptLoader):
    def __init__(self, prompts_dir):
        super().__init__(prompts_dir)
        self.cache = {}

    def load(self, prompt_path, **variables):
        cache_key = (prompt_path, tuple(sorted(variables.items())))
        if cache_key not in self.cache:
            self.cache[cache_key] = super().load(prompt_path, **variables)
        return self.cache[cache_key]
```

## Examples

The `examples/` directory contains runnable examples:

```bash
# Run basic examples
uv run python examples/basic_usage.py

# Run advanced examples
uv run python examples/advanced_usage.py

# Or use make
make examples
```

## Error Handling

The library provides clear error messages:

```python
# FileNotFoundError: Prompt template not found
try:
    loader("nonexistent.md")
except FileNotFoundError as e:
    print(e)  # Shows expected location

# UndefinedError: Missing required variable
try:
    loader("code_review.md")  # Missing 'code' variable
except jinja2.UndefinedError as e:
    print(e)  # Shows which variable is missing

# TemplateSyntaxError: Invalid Jinja2 syntax
try:
    loader("broken.md")  # Has syntax errors
except jinja2.TemplateSyntaxError as e:
    print(e)  # Shows syntax error details
```

## Design Philosophy

This library follows these principles:

- **Minimalism**: Less code is better code. No unnecessary abstractions.
- **Convention over Configuration**: Sensible defaults, no config files needed.
- **Developer Experience**: Intuitive API, clear errors, great tooling support.
- **No Magic**: Straightforward implementation, easy to understand and extend.

See [DESIGN.md](DESIGN.md) for detailed design decisions and architecture.

## Contributing

Contributions welcome! Please ensure:

- Tests pass: `make test`
- Linting passes: `make lint`
- Coverage stays >90%
- Type hints on all public functions
- Docstrings in Google Style format

## License

MIT License - see LICENSE file for details.

## Requirements

- Python 3.11+
- Jinja2 3.1.0+

## Credits

Built with:
- [Jinja2](https://jinja.palletsprojects.com/) - Template engine
- [pytest](https://pytest.org/) - Testing framework
- [ruff](https://github.com/astral-sh/ruff) - Fast Python linter
