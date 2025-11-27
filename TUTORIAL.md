# Promptly Tutorial

A hands-on guide to building reusable prompt templates for LLM applications.

## What is Promptly?

Promptly is a minimalist Python library for managing prompt templates across your LLM projects. Instead of hardcoding prompts in your application code, you store them as reusable Markdown templates with variables.

**Key Features:**

- **Centralized prompt library**: All prompts included in the package, ready to use
- **Separation of concerns**: Prompts live in files, not scattered in code
- **Reusability**: Write once, use everywhere across all your projects
- **Version control**: Track prompt changes in Git like any other code
- **Composition**: Combine smaller prompts into complex ones
- **Full Jinja2 power**: Variables, conditionals, loops, filters

## Installation

### For a New Project

```bash
# Create a new project directory
mkdir my-llm-app
cd my-llm-app

# Add promptly as a dependency
uv add git+https://github.com/username/promptly.git

# Or if working locally
uv add --editable /path/to/promptly
```

### For Development

```bash
# Clone the repository
git clone https://github.com/username/promptly.git
cd promptly

# Install with development dependencies
uv pip install -e ".[dev]"

# Run tests
make test
```

## Quick Start

Promptly comes with built-in prompts ready to use. No need to create your own prompts directory!

### 1. Install Promptly

```bash
# Add promptly as a dependency
uv add git+https://github.com/frr149/promptly.git

# Or if working locally
uv add --editable /path/to/promptly
```

### 2. Use Built-in Prompts

```python
from promptly import PromptLoader

# Initialize the loader - uses built-in prompts from the package
loader = PromptLoader()

# Load a built-in prompt
prompt = loader("developers/n8n.md")

# Use it with your LLM
print(prompt)
```

### 3. See Available Prompts

```python
# List all available prompts
all_prompts = loader.list()
print(all_prompts)
# ['components/base_skills.md', 'developers/n8n.md', 'developers/airtable.md', ...]

# List specific patterns
dev_prompts = loader.list("developers/*.md")
print(dev_prompts)
```

### 4. (Optional) Use Custom Prompts

If you need project-specific prompts, you can still provide your own directory:

```python
# Use custom prompts directory
loader = PromptLoader("my_prompts")

# Or use custom prompts with fallback to built-in prompts
loader = PromptLoader("my_prompts", fallback_to_package=True)
```

## Built-in Prompts

Promptly includes these ready-to-use prompts:

- **`developers/n8n.md`** - n8n workflow automation specialist
- **`developers/airtable.md`** - Airtable database specialist
- **`developers/n8n_airtable.md`** - Combined n8n + Airtable integration expert
- **`components/base_skills.md`** - Base developer skills (reusable component)
- **`components/communication.md`** - Communication style guidelines (reusable component)
- **`tasks/code_review.md`** - Code review prompt template

## Adding New Prompts to the Library

To add new prompts to Promptly's central library, add them to `src/promptly/prompts/` in the Promptly repository.

### Example: Simple Prompt with Variables

Create `src/promptly/prompts/tools/code_review.md`:

```markdown
Review this {{ language }} code for:
- Code quality
- Best practices
- Potential bugs
- Security issues

Code to review:
```{{ language|lower }}
{{ code }}
```

Provide specific feedback with line numbers.
```

Use it:

```python
loader = PromptLoader("prompts")

prompt = loader(
    "tools/code_review.md",
    language="Python",
    code="def divide(a, b): return a / b"
)
```

### Prompt with Default Values

Create `prompts/tools/debug.md`:

```markdown
Help debug this {{ language|default("Python") }} issue:

{{ error_message }}

{% if stack_trace %}
Stack trace:
```
{{ stack_trace }}
```
{% endif %}

Suggest {{ num_solutions|default(3) }} possible solutions.
```

Use it:

```python
# With all parameters
prompt = loader(
    "tools/debug.md",
    language="JavaScript",
    error_message="TypeError: undefined is not a function",
    stack_trace="...",
    num_solutions=5
)

# Or with defaults
prompt = loader(
    "tools/debug.md",
    error_message="Index out of range"
)
# Uses defaults: language=Python, num_solutions=3
```

### Prompt with Conditionals

Create `prompts/developers/react.md`:

```markdown
You are an expert React developer specializing in:
- React 18+ with hooks
- TypeScript
- Modern state management

{% if use_nextjs %}
You are also experienced with Next.js 14+ including:
- App Router
- Server Components
- Server Actions
{% endif %}

{% if styling == "tailwind" %}
Use Tailwind CSS for styling.
{% elif styling == "css-modules" %}
Use CSS Modules for styling.
{% else %}
Use standard CSS for styling.
{% endif %}

Help the user build clean, performant React applications.
```

Use it:

```python
# Next.js with Tailwind
prompt = loader(
    "developers/react.md",
    use_nextjs=True,
    styling="tailwind"
)

# Plain React with CSS Modules
prompt = loader(
    "developers/react.md",
    use_nextjs=False,
    styling="css-modules"
)
```

### Prompt with Lists

Create `prompts/tools/test_plan.md`:

```markdown
Create a test plan for this {{ feature_name }} feature.

Requirements:
{% for req in requirements %}
- {{ req }}
{% endfor %}

Test cases should cover:
{% for area in test_areas|default(["happy path", "edge cases", "error handling"]) %}
{{ loop.index }}. {{ area|title }}
{% endfor %}

Target: {{ coverage_target|default(80) }}% code coverage
```

Use it:

```python
prompt = loader(
    "tools/test_plan.md",
    feature_name="User Authentication",
    requirements=[
        "Users can sign up with email",
        "Users can log in",
        "Passwords are hashed"
    ],
    test_areas=["unit tests", "integration tests", "security tests"],
    coverage_target=90
)
```

## Combining Prompts

This is where Promptly really shines! You can compose complex prompts from smaller, reusable pieces.

### Example: Creating Specialized Developer Prompts

Let's create prompts for an n8n developer, an Airtable developer, and then combine them.

#### 1. Create Base Components

**`prompts/components/base_skills.md`:**
```markdown
You are a helpful developer assistant with expertise in:
- Clean code principles
- API design and integration
- Debugging and troubleshooting
- Best practices
```

**`prompts/components/communication.md`:**
```markdown

Communication style:
- Be clear and concise
- Provide code examples
- Explain your reasoning
- Ask clarifying questions when needed
```

#### 2. Create Tool-Specific Prompts

**`prompts/developers/n8n.md`:**
```markdown
{% include 'components/base_skills.md' %}

**n8n Specialization:**
- n8n workflow automation platform
- Node creation and customization
- HTTP requests and webhooks
- Error handling in workflows
- Credentials and authentication
- Function and Code nodes
- Workflow optimization

{% include 'components/communication.md' %}

Focus on helping users build reliable, efficient n8n workflows.
```

**`prompts/developers/airtable.md`:**
```markdown
{% include 'components/base_skills.md' %}

**Airtable Specialization:**
- Airtable API and base structure
- Formula fields and computations
- Automations and scripting
- Views, filters, and sorting
- Linked records and relationships
- Airtable integrations
- Data modeling in Airtable

{% include 'components/communication.md' %}

Focus on helping users design effective Airtable bases and automations.
```

#### 3. Create Combined Prompt

**`prompts/developers/n8n_airtable.md`:**
```markdown
{% include 'components/base_skills.md' %}

**n8n + Airtable Integration Specialist:**

You combine deep expertise in both platforms:

n8n Skills:
- n8n workflow automation
- HTTP requests and webhooks
- Error handling and retry logic
- Credentials management
- Function/Code nodes

Airtable Skills:
- Airtable API operations (CRUD)
- Base structure and relationships
- Formula fields
- Views and filters
- Automation capabilities

**Integration Expertise:**
- Connecting n8n workflows to Airtable
- Efficient data synchronization
- Handling Airtable rate limits
- Error handling for API operations
- Webhook-based triggers
- Batch operations and pagination
- Keeping data in sync between systems

{% include 'components/communication.md' %}

Help users build robust n8n workflows that integrate seamlessly with Airtable.
```

#### 4. Use Them

```python
from promptly import PromptLoader

loader = PromptLoader("prompts")

# Pure n8n developer
n8n_prompt = loader("developers/n8n.md")

# Pure Airtable developer
airtable_prompt = loader("developers/airtable.md")

# Combined n8n + Airtable specialist
integration_prompt = loader("developers/n8n_airtable.md")

# Use with your LLM
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4.5",
    max_tokens=4096,
    system=integration_prompt,  # Set as system prompt
    messages=[{
        "role": "user",
        "content": "How do I sync new Airtable records to an n8n workflow?"
    }]
)

print(response.content[0].text)
```

### Advanced: Dynamic Prompt Combination

You can also combine prompts dynamically based on user needs:

**`prompts/developers/multi_tool.md`:**
```markdown
{% include 'components/base_skills.md' %}

**Specialized Skills:**

{% if tools.n8n %}
**n8n Workflow Automation:**
- Building and optimizing workflows
- Custom node development
- Webhook and HTTP integrations
{% endif %}

{% if tools.airtable %}
**Airtable Database:**
- Base design and relationships
- Formula fields and computations
- API integration
{% endif %}

{% if tools.n8n and tools.airtable %}
**Integration Expertise:**
- Connecting n8n workflows to Airtable
- Real-time data synchronization
- Error handling and retries
{% endif %}

{% if tools.zapier %}
**Zapier Automation:**
- Zap creation and optimization
- Multi-step workflows
- Filter and path logic
{% endif %}

{% include 'components/communication.md' %}

Focus on {{ focus_area|default("building reliable automations") }}.
```

Use it dynamically:

```python
# n8n only
prompt = loader(
    "developers/multi_tool.md",
    tools={"n8n": True}
)

# n8n + Airtable integration
prompt = loader(
    "developers/multi_tool.md",
    tools={"n8n": True, "airtable": True},
    focus_area="building data sync workflows"
)

# All tools
prompt = loader(
    "developers/multi_tool.md",
    tools={"n8n": True, "airtable": True, "zapier": True},
    focus_area="comparing automation platforms"
)
```

## Best Practices

### 1. Organize by Purpose

```
prompts/
├── components/         # Reusable pieces
│   ├── base_skills.md
│   └── communication.md
├── developers/         # Role-specific prompts
│   ├── n8n.md
│   ├── airtable.md
│   └── n8n_airtable.md
├── tools/             # Task-specific prompts
│   ├── code_review.md
│   └── debug.md
└── system/            # System-level prompts
    └── assistant.md
```

### 2. Use Descriptive Names

```python
# Good
loader("developers/n8n_airtable_integration.md")
loader("tools/security_code_review.md")

# Avoid
loader("prompt1.md")
loader("dev.md")
```

### 3. Document Your Variables

Add comments at the top of templates:

```markdown
{# Variables:
   - language: str - Programming language name
   - code: str - Code to review
   - focus: list[str] (optional) - Specific areas to focus on
#}

Review this {{ language }} code...
```

### 4. Use Defaults Wisely

```markdown
{# Provide sensible defaults for optional parameters #}
Language: {{ language|default("Python") }}
Max suggestions: {{ max_suggestions|default(5) }}
Strictness: {{ strictness|default("moderate") }}
```

### 5. Version Your Prompts

Keep prompts in Git and use meaningful commit messages:

```bash
git add prompts/developers/n8n_airtable.md
git commit -m "Add n8n + Airtable integration specialist prompt"
```

## Discovering Available Prompts

```python
loader = PromptLoader("prompts")

# List all prompts
all_prompts = loader.list()
print(all_prompts)
# ['developers/n8n.md', 'developers/airtable.md', ...]

# List specific patterns
dev_prompts = loader.list("developers/*.md")
print(dev_prompts)
# ['developers/n8n.md', 'developers/airtable.md', ...]

# Check what variables a prompt needs
variables = loader.variables("tools/code_review.md")
print(variables)
# {'language', 'code'}
```

## Real-World Example: Complete Workflow

Here's a complete example of using promptly in an n8n + Airtable integration project:

```python
from promptly import PromptLoader
import anthropic

# Initialize
loader = PromptLoader("prompts")
client = anthropic.Anthropic()

# Load the integration specialist prompt
system_prompt = loader("developers/n8n_airtable.md")

# User's question
user_question = """
I need to create an n8n workflow that:
1. Triggers when a new record is added to my Airtable "Leads" table
2. Enriches the lead data with an API call
3. Updates the record in Airtable with the enriched data
4. Handles errors gracefully

Can you help me design this?
"""

# Get AI response
response = client.messages.create(
    model="claude-sonnet-4.5",
    max_tokens=4096,
    system=system_prompt,
    messages=[{"role": "user", "content": user_question}]
)

print(response.content[0].text)

# Later, need to review the generated n8n workflow code
code_review_prompt = loader(
    "tools/code_review.md",
    language="JSON",
    code=workflow_json
)

review_response = client.messages.create(
    model="claude-sonnet-4.5",
    max_tokens=2048,
    messages=[{"role": "user", "content": code_review_prompt}]
)

print(review_response.content[0].text)
```

## Next Steps

- Explore the [README](README.md) for complete API documentation
- Check out [DESIGN.md](DESIGN.md) for design philosophy
- Look at the `examples/` directory for more code samples
- Read about [Jinja2 templates](https://jinja.palletsprojects.com/) for advanced features

## Tips & Tricks

### Tip 1: Use Filters for Formatting

```markdown
Language: {{ language|upper }}
Timestamp: {{ timestamp|default(now()) }}
Items: {{ items|join(", ") }}
```

### Tip 2: Nested Includes

Components can include other components:

```markdown
{# components/expert_base.md #}
{% include 'components/base_skills.md' %}
{% include 'components/communication.md' %}
```

### Tip 3: Template Inheritance Alternative

While Jinja2 supports template inheritance, includes are simpler for most cases:

```markdown
{# Instead of complex inheritance, use includes #}
{% include 'components/header.md' %}
{{ custom_content }}
{% include 'components/footer.md' %}
```

### Tip 4: Debugging Templates

```python
# Check what variables a template needs
print(loader.variables("my_prompt.md"))

# Test rendering with dummy data
prompt = loader("my_prompt.md", language="Python", code="print('test')")
print(prompt)
```

## Troubleshooting

### "No module named 'promptly'"

```bash
# Make sure it's installed
uv pip list | grep promptly

# Reinstall if needed
uv pip install -e ".[dev]"
```

### "Template not found"

```python
# Check available prompts
loader = PromptLoader("prompts")
print(loader.list())

# Make sure path is relative to prompts directory
# ✓ Correct: loader("developers/n8n.md")
# ✗ Wrong: loader("prompts/developers/n8n.md")
```

### "Variable not defined"

```python
# Check required variables
print(loader.variables("my_prompt.md"))

# Provide all required variables
prompt = loader("my_prompt.md", required_var="value")
```

Happy prompting! 🚀
