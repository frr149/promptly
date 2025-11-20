# Design Document - promptly

This document explains the design decisions, architecture, and technical considerations behind promptly.

## Table of Contents

1. [Design Decisions](#design-decisions)
2. [Alternatives Considered](#alternatives-considered)
3. [Technical Architecture](#technical-architecture)
4. [Migration to GitHub](#migration-to-github)
5. [Future Evolution](#future-evolution)
6. [Extension Patterns](#extension-patterns)
7. [Usage Patterns](#usage-patterns)
8. [Testing Strategy](#testing-strategy)
9. [Performance Considerations](#performance-considerations)
10. [Troubleshooting](#troubleshooting)

## Design Decisions

### Why Minimalism?

**Decision**: Keep the codebase minimal with only essential features.

**Rationale**:
- Less code means fewer bugs
- Easier to understand and maintain
- Lower cognitive load for users
- Faster to learn and adopt
- Reduces dependency hell

**Benefits**:
- Single file implementation (~150 lines)
- One runtime dependency (Jinja2)
- No complex configuration needed
- Easy to audit and understand

**Trade-offs**:
- Some advanced features require extending the loader
- Less "batteries included" than larger frameworks
- Users may need to add custom filters/functions

### Why NO Front-Matter YAML?

**Decision**: Prompts are plain Markdown/text files with only Jinja2 syntax. No YAML front-matter metadata.

**Rationale**:

Front-matter adds ceremony without sufficient benefit:

```markdown
---
name: "Code Review"
description: "Review code for quality"
variables:
  - name: "language"
    required: true
    type: "string"
  - name: "code"
    required: true
    type: "string"
---
Review this {{ language }} code: {{ code }}
```

vs. our approach:

```markdown
Review this {{ language }} code: {{ code }}
```

**Benefits**:
- No YAML parsing library needed
- No metadata validation complexity
- Variables detected automatically
- Prompts remain readable and clean
- No schema to learn or maintain

**When this might be limiting**:
- If you need strict validation of inputs (use Pydantic separately)
- If you want metadata like author, version (use Git for this)
- If you need complex type constraints (validate at call site)

**Why this works**:
- Jinja2's AST parser can extract variables automatically
- Defaults can be specified in templates: `{{ var|default("value") }}`
- Type validation should happen at the application level
- Git provides versioning and metadata

### Why Automatic Variable Detection?

**Decision**: Use `jinja2.meta.find_undeclared_variables()` to automatically detect template variables.

**Rationale**:
- Eliminates manual documentation of variables
- Variables are discovered from actual usage
- No risk of outdated documentation
- Less maintenance burden

**Implementation**:

```python
def variables(self, prompt_path: str) -> set[str]:
    template_source = self.env.loader.get_source(self.env, prompt_path)
    parsed_content = self.env.parse(template_source[0])
    return jinja2.meta.find_undeclared_variables(parsed_content)
```

**Benefits**:
- Zero configuration
- Always accurate
- Works with conditionals, loops, filters
- Supports introspection

### Why Callable Loader?

**Decision**: Make the loader callable via `__call__`, with `load` as an alias.

**Rationale**:
- More Pythonic and concise
- Reduces boilerplate
- Common pattern in Python (e.g., `functools.partial`)

**Example**:

```python
# Concise
prompt = loader("code_review.md", language="Python")

# Also works (for those who prefer explicit methods)
prompt = loader.load("code_review.md", language="Python")
```

**Benefits**:
- Less typing for common operation
- Callable objects are idiomatic Python
- Provides flexibility (both forms work)

### Why Only Jinja2?

**Decision**: Use Jinja2 as the sole templating engine, no alternatives.

**Rationale**:
- Jinja2 is mature, stable, and well-maintained
- Rich feature set (filters, conditionals, loops, includes)
- Excellent documentation
- Used by major projects (Flask, Ansible, etc.)
- Single dependency keeps things simple

**Benefits**:
- No need to abstract over multiple engines
- Users can leverage existing Jinja2 knowledge
- Full access to Jinja2's power
- Easy to extend with custom filters/functions

**What if users want another engine?**:
- They can fork and swap Jinja2 for their preferred engine
- The codebase is small enough to make this trivial
- Most users won't need this

### Why Convention Over Configuration?

**Decision**: No configuration files, use sensible defaults and conventions.

**Rationale**:
- Configuration is a form of technical debt
- Most projects have similar needs
- Conventions reduce decision fatigue
- Easier onboarding for new users

**Conventions**:
- Prompts are Markdown files (`.md`)
- Directory structure is flexible but suggested
- Templates use Jinja2 syntax
- Variables detected automatically
- Errors are raised, not silenced

**Benefits**:
- No `config.yaml` or `.promptrc` needed
- Works out of the box
- Easy to understand by reading code

## Alternatives Considered

### Alternative 1: Front-Matter YAML

**What**: Metadata in YAML front-matter.

```markdown
---
name: "Code Review"
variables: ["language", "code"]
---
Review this {{ language }} code: {{ code }}
```

**Why Rejected**:
- Adds YAML parsing dependency
- Requires schema definition and validation
- Metadata can get out of sync with template
- More boilerplate to write and maintain

**When to reconsider**:
- If strict validation becomes critical
- If metadata like versioning is needed per-prompt
- If complex type constraints are required

### Alternative 2: Pydantic Models for Validation

**What**: Use Pydantic to validate template variables.

```python
class CodeReviewPrompt(BaseModel):
    language: str
    code: str
    focus: Optional[str] = "best practices"

prompt = loader("code_review.md", **CodeReviewPrompt(...).dict())
```

**Why Rejected**:
- Adds dependency and complexity
- Validation should be at application level
- Makes the library opinionated about validation
- Users can add this themselves if needed

**When to reconsider**:
- If many users request built-in validation
- Could be added as optional extension

### Alternative 3: Complex CLI

**What**: Full CLI for managing prompts.

```bash
prompts list
prompts validate code_review.md
prompts render code_review.md --language=Python --code="..."
```

**Why Rejected**:
- YAGNI (You Aren't Gonna Need It)
- Adds complexity for limited benefit
- Users can build their own CLI if needed
- Keep it a library, not a framework

**When to reconsider**:
- If CLI usage becomes common
- Could be separate package: `promptly-cli`

### Alternative 4: Multiple Template Engines

**What**: Support Jinja2, Mustache, Handlebars, etc.

**Why Rejected**:
- Abstraction overhead
- More code to maintain
- Users rarely need multiple engines
- Jinja2 covers 99% of use cases

**When to reconsider**:
- If there's strong demand for specific engines
- Keep as separate packages instead

### Alternative 5: Built-in Prompt Repository

**What**: Pre-built prompts included with the library.

**Why Rejected**:
- Every project has unique needs
- Built-in prompts become outdated quickly
- Increases package size
- Better as separate package

**Alternative**:
- Community prompts in separate repo
- Users fork and customize as needed

## Technical Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────┐
│           promptly                       │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌────────────────────────────────────────┐    │
│  │        PromptLoader                    │    │
│  ├────────────────────────────────────────┤    │
│  │ - prompts_dir: Path                    │    │
│  │ - env: jinja2.Environment              │    │
│  ├────────────────────────────────────────┤    │
│  │ + __init__(prompts_dir)                │    │
│  │ + __call__(path, **vars) -> str        │    │
│  │ + load(path, **vars) -> str            │    │
│  │ + variables(path) -> set[str]          │    │
│  │ + list(pattern) -> list[str]           │    │
│  │ + prompts_dir: Path                    │    │
│  └────────────────────────────────────────┘    │
│                                                 │
│  Dependencies:                                  │
│  ┌────────────────────────────────────────┐    │
│  │         Jinja2                         │    │
│  ├────────────────────────────────────────┤    │
│  │ - Environment                          │    │
│  │ - FileSystemLoader                     │    │
│  │ - StrictUndefined                      │    │
│  │ - meta.find_undeclared_variables()     │    │
│  └────────────────────────────────────────┘    │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Rendering Flow

```
User Code
    │
    ├─> loader("code_review.md", language="Python", code="...")
    │
    v
PromptLoader.__call__()
    │
    ├─> env.get_template("code_review.md")
    │   │
    │   v
    │   FileSystemLoader
    │       │
    │       ├─> Read file from prompts_dir
    │       └─> Parse Jinja2 syntax
    │
    ├─> template.render(language="Python", code="...")
    │   │
    │   v
    │   Jinja2 Template Engine
    │       │
    │       ├─> Substitute variables
    │       ├─> Apply filters
    │       ├─> Evaluate conditionals
    │       ├─> Execute loops
    │       └─> Process includes
    │
    v
Rendered prompt (string)
    │
    v
Return to user
```

### Error Handling Flow

```
Error Scenarios:

1. Directory doesn't exist
   PromptLoader.__init__() -> ValueError
   Message: "Prompts directory does not exist: /path"

2. Template not found
   env.get_template() -> jinja2.TemplateNotFound
   Converted to -> FileNotFoundError
   Message: "Prompt template not found: code_review.md"

3. Missing variable
   template.render() -> jinja2.UndefinedError
   Enriched message: "Missing required variable in 'code_review.md': code"

4. Syntax error
   env.parse() -> jinja2.TemplateSyntaxError
   Passed through with full details
```

### Class Design

**Why single class?**
- Most use cases need only one loader per prompts directory
- Simple to understand and use
- Easy to extend if needed

**Key properties**:
- `prompts_dir`: Stored as `Path` for type safety and path operations
- `env`: Jinja2 environment configured once at initialization

**Key methods**:
- `__call__`: Primary interface, concise and Pythonic
- `load`: Explicit alias for those who prefer method calls
- `variables`: Introspection for understanding templates
- `list`: Discovery of available prompts

## Migration to GitHub

### Step-by-Step Migration

1. **Create GitHub Repository**
   ```bash
   # On GitHub: Create new repository "promptly"
   ```

2. **Initialize Local Git**
   ```bash
   cd promptly
   git init
   git add .
   git commit -m "Initial commit: Minimalist prompt template library"
   ```

3. **Connect to GitHub**
   ```bash
   git remote add origin git@github.com:username/promptly.git
   git branch -M main
   git push -u origin main
   ```

4. **Tag First Release**
   ```bash
   git tag -a v0.1.0 -m "Initial release"
   git push origin v0.1.0
   ```

### Installing from GitHub

After migration, users can install via:

```bash
# Latest from main branch
uv pip install git+https://github.com/username/promptly.git

# Specific tag
uv pip install git+https://github.com/username/promptly.git@v0.1.0

# Specific branch
uv pip install git+https://github.com/username/promptly.git@develop
```

### In pyproject.toml

```toml
[project]
dependencies = [
    "promptly @ git+https://github.com/username/promptly.git@main"
]

# Or with tag
[project]
dependencies = [
    "promptly @ git+https://github.com/username/promptly.git@v0.1.0"
]
```

### Publishing to PyPI (Future)

If you want to publish to PyPI:

```bash
# Build package
uv build

# Upload to PyPI
uv publish

# Then users can install with
pip install promptly
```

## Future Evolution

These features could be added without breaking simplicity:

### 1. Template Caching

**Problem**: Loading and parsing templates repeatedly is wasteful.

**Solution**:

```python
from functools import lru_cache

class CachedPromptLoader(PromptLoader):
    @lru_cache(maxsize=128)
    def load(self, prompt_path: str, **variables):
        # Variables must be hashable for caching
        return super().load(prompt_path, **variables)
```

**Trade-offs**:
- Only works with hashable variables
- Memory usage increases
- Good for high-volume applications

### 2. Optional Validation

**Problem**: Some users want strict validation.

**Solution**:

```python
class ValidatingPromptLoader(PromptLoader):
    def __init__(self, prompts_dir, schemas=None):
        super().__init__(prompts_dir)
        self.schemas = schemas or {}

    def load(self, prompt_path, **variables):
        if prompt_path in self.schemas:
            self.schemas[prompt_path].validate(variables)
        return super().load(prompt_path, **variables)
```

### 3. Prompt Composition

**Problem**: Want to compose prompts from multiple files.

**Solution**: Already supported via Jinja2's `{% include %}`:

```jinja2
{% include 'templates/header.md' %}
{{ main_content }}
{% include 'templates/footer.md' %}
```

### 4. Hot Reload

**Problem**: Template changes require restart during development.

**Solution**:

```python
class HotReloadLoader(PromptLoader):
    def __init__(self, prompts_dir):
        super().__init__(prompts_dir)
        # Disable Jinja2's cache
        self.env.cache = None
```

### 5. Async Support

**Problem**: Some users need async rendering.

**Solution**:

```python
class AsyncPromptLoader(PromptLoader):
    async def aload(self, prompt_path: str, **variables):
        # Implement async loading
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.load, prompt_path, **variables
        )
```

## Extension Patterns

### Custom Filters

Add domain-specific filters:

```python
from promptly import PromptLoader

loader = PromptLoader("prompts")

# Markdown code block filter
def markdown_code(text: str, language: str = "python") -> str:
    return f"```{language}\n{text}\n```"

loader.env.filters['mdcode'] = markdown_code

# JSON formatting filter
import json

def json_format(obj, indent=2):
    return json.dumps(obj, indent=indent)

loader.env.filters['json'] = json_format

# Use in templates:
# {{ code|mdcode("python") }}
# {{ config|json(4) }}
```

### Global Functions

Add utility functions available in all templates:

```python
import datetime

# Current timestamp
def now():
    return datetime.datetime.now().isoformat()

loader.env.globals['now'] = now

# UUID generation
import uuid

def generate_id():
    return str(uuid.uuid4())

loader.env.globals['uuid'] = generate_id

# Use in templates:
# Generated at: {{ now() }}
# ID: {{ uuid() }}
```

### Extending the Loader

Create specialized loaders:

```python
class ProjectPromptLoader(PromptLoader):
    """Loader with project-specific customizations."""

    def __init__(self, prompts_dir, project_name):
        super().__init__(prompts_dir)
        self.project_name = project_name

        # Add project name as global
        self.env.globals['project'] = project_name

        # Add custom filters
        self.env.filters['titlecase'] = str.title

    def load_for_user(self, prompt_path, user, **variables):
        """Load prompt with user context."""
        return self.load(
            prompt_path,
            user=user,
            project=self.project_name,
            **variables
        )
```

## Usage Patterns

### Pattern 1: Centralized Prompt Management

**Goal**: All prompts in one place, shared across team.

**Structure**:

```
company-prompts/         # Git repository
├── engineering/
│   ├── code_review.md
│   ├── architecture.md
│   └── testing.md
├── product/
│   ├── user_story.md
│   └── requirements.md
└── support/
    ├── bug_triage.md
    └── response.md
```

**Usage**:

```python
# Each team member installs
uv pip install git+https://github.com/company/company-prompts.git

# Use in any project
loader = PromptLoader("~/.prompts")  # Or wherever installed
prompt = loader("engineering/code_review.md", ...)
```

### Pattern 2: Project-Specific Prompts

**Goal**: Prompts tailored to specific project.

**Structure**:

```
my-project/
├── src/
├── tests/
├── prompts/              # Project-specific prompts
│   ├── system/
│   └── tasks/
└── pyproject.toml
```

**Usage**:

```python
# In project code
loader = PromptLoader("prompts")
prompt = loader("tasks/review.md", ...)
```

### Pattern 3: Hybrid Approach

**Goal**: Mix shared and project-specific prompts.

**Structure**:

```python
from promptly import PromptLoader

# Shared prompts
shared_loader = PromptLoader("~/.prompts")

# Project prompts
project_loader = PromptLoader("./prompts")

# Try project first, fall back to shared
def get_prompt(path, **variables):
    try:
        return project_loader(path, **variables)
    except FileNotFoundError:
        return shared_loader(path, **variables)
```

### Pattern 4: Prompt Versioning

**Goal**: Version prompts with code.

**Approach**:

```bash
# In your repo
prompts/
├── v1/
│   └── code_review.md
└── v2/
    └── code_review.md
```

```python
# Use specific version
loader = PromptLoader("prompts/v2")
```

### Pattern 5: Environment-Specific Prompts

**Goal**: Different prompts for dev/staging/prod.

**Structure**:

```
prompts/
├── base/
│   └── common.md
├── development/
│   └── debug_review.md
└── production/
    └── code_review.md
```

```python
import os

env = os.getenv("ENVIRONMENT", "development")
loader = PromptLoader(f"prompts/{env}")
```

## Testing Strategy

### Unit Tests

Test individual methods in isolation:

```python
def test_simple_rendering(tmp_path):
    """Test basic variable substitution."""
    prompt_file = tmp_path / "test.md"
    prompt_file.write_text("Hello {{ name }}!")

    loader = PromptLoader(tmp_path)
    result = loader("test.md", name="World")

    assert result == "Hello World!"
```

### Integration Tests

Test complete workflows:

```python
def test_complex_workflow(tmp_path):
    """Test real-world usage pattern."""
    # Create directory structure
    (tmp_path / "tasks").mkdir()

    # Create prompt with multiple features
    (tmp_path / "tasks" / "review.md").write_text("""
{% for issue in issues %}
- {{ issue|upper }}
{% endfor %}
    """)

    loader = PromptLoader(tmp_path)
    result = loader("tasks/review.md", issues=["bug", "typo"])

    assert "BUG" in result
    assert "TYPO" in result
```

### Coverage Goals

- **Unit tests**: All public methods
- **Edge cases**: Empty inputs, missing files, invalid syntax
- **Error paths**: All error conditions tested
- **Integration**: Complete user workflows
- **Target**: >90% code coverage

### Test Fixtures

Use `tmp_path` for isolation:

```python
def test_with_fixture(tmp_path):
    # Each test gets fresh temporary directory
    prompt = tmp_path / "test.md"
    prompt.write_text("content")
    # Automatically cleaned up
```

## Performance Considerations

### Jinja2 Performance

- **Template compilation**: Jinja2 compiles templates to Python bytecode
- **Caching**: FileSystemLoader caches compiled templates automatically
- **Cost**: First load is slower, subsequent loads are fast

### When to Optimize

For most use cases, performance is fine. Optimize if:

- Rendering >1000 prompts per second
- Templates are very large (>100KB)
- Using in hot path of web application

### Optimization Strategies

1. **Explicit caching**: Cache rendered results if variables don't change
2. **Disable cache**: For development, disable cache to see changes
3. **Precompile**: Compile templates at startup
4. **Reduce complexity**: Simpler templates render faster

### Benchmarks (Rough Estimates)

- Small template (<1KB): ~0.1ms first load, ~0.01ms cached
- Medium template (~10KB): ~1ms first load, ~0.1ms cached
- Large template (~100KB): ~10ms first load, ~1ms cached
- Variable detection: ~1-5ms per template

For 99% of use cases, this is fast enough.

## Troubleshooting

### Common Issues

#### Issue: TemplateNotFound

**Error**:
```
FileNotFoundError: Prompt template not found: code_review.md
```

**Causes**:
- File doesn't exist
- Wrong path (not relative to prompts_dir)
- Typo in filename

**Solutions**:
- Check file exists: `ls prompts/code_review.md`
- Use `loader.list()` to see available prompts
- Verify path is relative: `"tasks/review.md"` not `"/tasks/review.md"`

#### Issue: UndefinedError

**Error**:
```
jinja2.UndefinedError: 'code' is undefined
```

**Causes**:
- Missing required variable
- Typo in variable name
- Variable not passed to loader

**Solutions**:
- Use `loader.variables("template.md")` to see required vars
- Add default: `{{ code|default("") }}`
- Pass variable: `loader("template.md", code="...")`

#### Issue: Excessive Whitespace

**Problem**: Extra blank lines in output.

**Cause**: Jinja2 syntax creates whitespace.

**Solutions**:
- Use minus sign: `{%- if -%}`
- We already set `trim_blocks=True` and `lstrip_blocks=True`
- Add `.strip()` to final result

#### Issue: Paths Don't Work

**Error**: Prompts in subdirectories not found.

**Cause**: Using absolute path instead of relative.

**Solution**:
```python
# Wrong
loader("/absolute/path/prompts/tasks/review.md")

# Right
loader("tasks/review.md")
```

### Debug Helpers

**List all prompts**:

```python
print(loader.list())
```

**Check variables**:

```python
print(loader.variables("template.md"))
```

**Test template**:

```python
# Add to template for debugging
{# DEBUG: variables = {{ variables }} #}
```

**Check prompts directory**:

```python
print(loader.prompts_dir)
print(loader.prompts_dir.exists())
```

## Conclusion

promptly is intentionally minimal and focused. It does one thing well: load and render prompt templates using Jinja2.

The design prioritizes:
- **Simplicity** over features
- **Convention** over configuration
- **Clarity** over cleverness
- **Extensibility** over built-in options

If you need more features, extend the loader. If you want validation, add it at the application level. If you need a different template engine, fork and swap it out.

Keep it simple. Keep it focused. Let users build what they need on top.
