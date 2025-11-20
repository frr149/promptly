"""Comprehensive test suite for PromptLoader."""

from __future__ import annotations

from pathlib import Path

import jinja2
import pytest

from promptly import PromptLoader

# ============================================================================
# Basic Tests
# ============================================================================


def test_init_with_valid_directory(tmp_path: Path) -> None:
    """Test PromptLoader initialization with valid directory."""
    loader = PromptLoader(tmp_path)
    assert loader.prompts_dir == tmp_path


def test_init_with_nonexistent_directory(tmp_path: Path) -> None:
    """Test PromptLoader initialization with nonexistent directory."""
    nonexistent = tmp_path / "does_not_exist"
    with pytest.raises(ValueError, match="does not exist"):
        PromptLoader(nonexistent)


def test_init_with_file_not_directory(tmp_path: Path) -> None:
    """Test PromptLoader initialization with file instead of directory."""
    file_path = tmp_path / "file.txt"
    file_path.write_text("content")
    with pytest.raises(ValueError, match="not a directory"):
        PromptLoader(file_path)


def test_simple_rendering_with_one_variable(tmp_path: Path) -> None:
    """Test rendering a simple template with one variable."""
    prompt_file = tmp_path / "simple.md"
    prompt_file.write_text("Hello {{ name }}!")

    loader = PromptLoader(tmp_path)
    result = loader("simple.md", name="World")

    assert result == "Hello World!"


def test_rendering_with_multiple_variables(tmp_path: Path) -> None:
    """Test rendering with multiple variables."""
    prompt_file = tmp_path / "multi.md"
    prompt_file.write_text("{{ greeting }} {{ name }}, you are {{ age }} years old.")

    loader = PromptLoader(tmp_path)
    result = loader("multi.md", greeting="Hello", name="Alice", age=30)

    assert result == "Hello Alice, you are 30 years old."


def test_rendering_static_text_no_variables(tmp_path: Path) -> None:
    """Test rendering a prompt with no variables (static text)."""
    prompt_file = tmp_path / "static.md"
    prompt_file.write_text("This is a static prompt without variables.")

    loader = PromptLoader(tmp_path)
    result = loader("static.md")

    assert result == "This is a static prompt without variables."


def test_error_when_prompt_does_not_exist(tmp_path: Path) -> None:
    """Test error when prompt file doesn't exist."""
    loader = PromptLoader(tmp_path)

    with pytest.raises(FileNotFoundError, match="nonexistent.md"):
        loader("nonexistent.md")


def test_load_alias_works_identically(tmp_path: Path) -> None:
    """Test that loader.load() works identically to loader()."""
    prompt_file = tmp_path / "test.md"
    prompt_file.write_text("Hello {{ name }}!")

    loader = PromptLoader(tmp_path)
    result1 = loader("test.md", name="World")
    result2 = loader.load("test.md", name="World")

    assert result1 == result2


# ============================================================================
# Variable Detection Tests
# ============================================================================


def test_detect_single_variable(tmp_path: Path) -> None:
    """Test detection of a single variable."""
    prompt_file = tmp_path / "single.md"
    prompt_file.write_text("Hello {{ name }}!")

    loader = PromptLoader(tmp_path)
    variables = loader.variables("single.md")

    assert variables == {"name"}


def test_detect_multiple_variables(tmp_path: Path) -> None:
    """Test detection of multiple variables."""
    prompt_file = tmp_path / "multi.md"
    prompt_file.write_text("{{ greeting }} {{ name }}, age {{ age }}")

    loader = PromptLoader(tmp_path)
    variables = loader.variables("multi.md")

    assert variables == {"greeting", "name", "age"}


def test_detect_variables_in_conditionals(tmp_path: Path) -> None:
    """Test detection of variables in conditionals."""
    prompt_file = tmp_path / "conditional.md"
    prompt_file.write_text("""
{% if language == "Python" %}
Use {{ framework }} for Python
{% else %}
Use {{ alternative }}
{% endif %}
    """)

    loader = PromptLoader(tmp_path)
    variables = loader.variables("conditional.md")

    assert variables == {"language", "framework", "alternative"}


def test_detect_variables_in_loops(tmp_path: Path) -> None:
    """Test detection of variables in loops."""
    prompt_file = tmp_path / "loop.md"
    prompt_file.write_text("""
{% for item in items %}
- {{ item }}
{% endfor %}
    """)

    loader = PromptLoader(tmp_path)
    variables = loader.variables("loop.md")

    assert variables == {"items"}


def test_detect_no_variables(tmp_path: Path) -> None:
    """Test detection in prompt without variables."""
    prompt_file = tmp_path / "static.md"
    prompt_file.write_text("Static text with no variables.")

    loader = PromptLoader(tmp_path)
    variables = loader.variables("static.md")

    assert variables == set()


def test_variables_error_when_prompt_not_found(tmp_path: Path) -> None:
    """Test error when trying to detect variables in nonexistent prompt."""
    loader = PromptLoader(tmp_path)

    with pytest.raises(FileNotFoundError, match="nonexistent.md"):
        loader.variables("nonexistent.md")


# ============================================================================
# Default Values Tests
# ============================================================================


def test_default_value_when_variable_not_provided(tmp_path: Path) -> None:
    """Test using default value when variable is not provided."""
    prompt_file = tmp_path / "default.md"
    prompt_file.write_text('Hello {{ name|default("User") }}!')

    loader = PromptLoader(tmp_path)
    result = loader("default.md")

    assert result == "Hello User!"


def test_override_default_value(tmp_path: Path) -> None:
    """Test overriding default value when variable is provided."""
    prompt_file = tmp_path / "default.md"
    prompt_file.write_text('Hello {{ name|default("User") }}!')

    loader = PromptLoader(tmp_path)
    result = loader("default.md", name="Alice")

    assert result == "Hello Alice!"


def test_multiple_defaults_in_template(tmp_path: Path) -> None:
    """Test multiple defaults in the same template."""
    prompt_file = tmp_path / "multi_default.md"
    prompt_file.write_text('''
{{ greeting|default("Hello") }} {{ name|default("User") }}!
You are {{ age|default(18) }} years old.
    '''.strip())

    loader = PromptLoader(tmp_path)
    result = loader("multi_default.md")

    assert result == "Hello User!\nYou are 18 years old."


def test_partial_default_override(tmp_path: Path) -> None:
    """Test providing some variables while others use defaults."""
    prompt_file = tmp_path / "partial.md"
    prompt_file.write_text('{{ greeting|default("Hi") }} {{ name|default("User") }}!')

    loader = PromptLoader(tmp_path)
    result = loader("partial.md", name="Bob")

    assert result == "Hi Bob!"


# ============================================================================
# Jinja2 Filters Tests
# ============================================================================


def test_string_filters_upper_lower_title(tmp_path: Path) -> None:
    """Test basic string filters: upper, lower, title."""
    prompt_file = tmp_path / "filters.md"
    prompt_file.write_text("""
Upper: {{ name|upper }}
Lower: {{ name|lower }}
Title: {{ name|title }}
    """.strip())

    loader = PromptLoader(tmp_path)
    result = loader("filters.md", name="hElLo WoRlD")

    assert "Upper: HELLO WORLD" in result
    assert "Lower: hello world" in result
    assert "Title: Hello World" in result


def test_numeric_filters(tmp_path: Path) -> None:
    """Test numeric filters: round, abs."""
    prompt_file = tmp_path / "numeric.md"
    prompt_file.write_text("""
Rounded: {{ value|round }}
Absolute: {{ negative|abs }}
    """.strip())

    loader = PromptLoader(tmp_path)
    result = loader("numeric.md", value=3.7, negative=-5)

    assert "Rounded: 4" in result
    assert "Absolute: 5" in result


def test_list_filters(tmp_path: Path) -> None:
    """Test list filters: join, length."""
    prompt_file = tmp_path / "list.md"
    prompt_file.write_text("""
Joined: {{ items|join(", ") }}
Length: {{ items|length }}
    """.strip())

    loader = PromptLoader(tmp_path)
    result = loader("list.md", items=["Python", "Rust", "Go"])

    assert "Joined: Python, Rust, Go" in result
    assert "Length: 3" in result


def test_chained_filters(tmp_path: Path) -> None:
    """Test chaining multiple filters."""
    prompt_file = tmp_path / "chain.md"
    prompt_file.write_text("Result: {{ name|upper|reverse }}")

    loader = PromptLoader(tmp_path)
    result = loader("chain.md", name="hello")

    assert result == "Result: OLLEH"


# ============================================================================
# Conditionals Tests
# ============================================================================


def test_if_else_basic(tmp_path: Path) -> None:
    """Test basic if/else conditional."""
    prompt_file = tmp_path / "condition.md"
    prompt_file.write_text("""
{% if user_type == "admin" %}
Admin access granted
{% else %}
Regular user access
{% endif %}
    """.strip())

    loader = PromptLoader(tmp_path)

    admin_result = loader("condition.md", user_type="admin")
    assert "Admin access granted" in admin_result

    user_result = loader("condition.md", user_type="user")
    assert "Regular user access" in user_result


def test_elif_multiple_conditions(tmp_path: Path) -> None:
    """Test elif with multiple conditions."""
    prompt_file = tmp_path / "elif.md"
    prompt_file.write_text("""
{% if score >= 90 %}
Grade: A
{% elif score >= 80 %}
Grade: B
{% elif score >= 70 %}
Grade: C
{% else %}
Grade: F
{% endif %}
    """.strip())

    loader = PromptLoader(tmp_path)

    assert "Grade: A" in loader("elif.md", score=95)
    assert "Grade: B" in loader("elif.md", score=85)
    assert "Grade: C" in loader("elif.md", score=75)
    assert "Grade: F" in loader("elif.md", score=65)


def test_comparison_operators(tmp_path: Path) -> None:
    """Test comparison operators in conditionals."""
    prompt_file = tmp_path / "compare.md"
    prompt_file.write_text("""
{% if age > 18 %}Adult{% endif %}
{% if age == 18 %}Exactly 18{% endif %}
{% if age < 18 %}Minor{% endif %}
    """.strip())

    loader = PromptLoader(tmp_path)

    assert "Adult" in loader("compare.md", age=25)
    assert "Exactly 18" in loader("compare.md", age=18)
    assert "Minor" in loader("compare.md", age=15)


def test_logical_operators(tmp_path: Path) -> None:
    """Test logical operators: and, or, not."""
    prompt_file = tmp_path / "logical.md"
    prompt_file.write_text("""
{% if age >= 18 and has_license %}Can drive{% endif %}
{% if is_admin or is_moderator %}Has privileges{% endif %}
{% if not is_banned %}Can post{% endif %}
    """.strip())

    loader = PromptLoader(tmp_path)

    result1 = loader("logical.md", age=20, has_license=True, is_admin=False,
                     is_moderator=True, is_banned=False)
    assert "Can drive" in result1
    assert "Has privileges" in result1
    assert "Can post" in result1


# ============================================================================
# Loops Tests
# ============================================================================


def test_basic_loop_over_list(tmp_path: Path) -> None:
    """Test basic loop over a list."""
    prompt_file = tmp_path / "loop.md"
    prompt_file.write_text("""
{% for item in items %}
- {{ item }}
{% endfor %}
    """.strip())

    loader = PromptLoader(tmp_path)
    result = loader("loop.md", items=["Python", "Rust", "Go"])

    assert "- Python" in result
    assert "- Rust" in result
    assert "- Go" in result


def test_loop_with_index(tmp_path: Path) -> None:
    """Test loop with index access."""
    prompt_file = tmp_path / "indexed.md"
    prompt_file.write_text("""
{% for item in items %}
{{ loop.index }}. {{ item }}
{% endfor %}
    """.strip())

    loader = PromptLoader(tmp_path)
    result = loader("indexed.md", items=["First", "Second", "Third"])

    assert "1. First" in result
    assert "2. Second" in result
    assert "3. Third" in result


def test_loop_over_dictionary(tmp_path: Path) -> None:
    """Test loop over dictionary items."""
    prompt_file = tmp_path / "dict_loop.md"
    prompt_file.write_text("""
{% for key, value in config.items() %}
{{ key }}: {{ value }}
{% endfor %}
    """.strip())

    loader = PromptLoader(tmp_path)
    result = loader("dict_loop.md", config={"name": "Alice", "age": 30})

    assert "name: Alice" in result
    assert "age: 30" in result


def test_nested_loops(tmp_path: Path) -> None:
    """Test nested loops."""
    prompt_file = tmp_path / "nested.md"
    prompt_file.write_text("""
{% for category in categories %}
{{ category.name }}:
{% for item in category.elements %}
  - {{ item }}
{% endfor %}
{% endfor %}
    """.strip())

    loader = PromptLoader(tmp_path)
    result = loader("nested.md", categories=[
        {"name": "Languages", "elements": ["Python", "Rust"]},
        {"name": "Frameworks", "elements": ["Django", "FastAPI"]},
    ])

    assert "Languages:" in result
    assert "  - Python" in result
    assert "Frameworks:" in result
    assert "  - Django" in result


# ============================================================================
# Listing Prompts Tests
# ============================================================================


def test_list_all_prompts(tmp_path: Path) -> None:
    """Test listing all prompts."""
    (tmp_path / "prompt1.md").write_text("Content 1")
    (tmp_path / "prompt2.md").write_text("Content 2")

    loader = PromptLoader(tmp_path)
    prompts = loader.list()

    assert sorted(prompts) == ["prompt1.md", "prompt2.md"]


def test_list_with_specific_pattern(tmp_path: Path) -> None:
    """Test listing with specific glob pattern."""
    (tmp_path / "code_review.md").write_text("Content")
    (tmp_path / "test_plan.md").write_text("Content")
    (tmp_path / "readme.txt").write_text("Content")

    loader = PromptLoader(tmp_path)
    prompts = loader.list("test_*.md")

    assert prompts == ["test_plan.md"]


def test_list_in_subdirectories(tmp_path: Path) -> None:
    """Test listing prompts in subdirectories."""
    tasks_dir = tmp_path / "tasks"
    system_dir = tmp_path / "system"
    tasks_dir.mkdir()
    system_dir.mkdir()

    (tasks_dir / "review.md").write_text("Content")
    (system_dir / "assistant.md").write_text("Content")

    loader = PromptLoader(tmp_path)
    prompts = loader.list()

    assert sorted(prompts) == ["system/assistant.md", "tasks/review.md"]


def test_list_specific_subdirectory_pattern(tmp_path: Path) -> None:
    """Test listing with subdirectory pattern."""
    tasks_dir = tmp_path / "tasks"
    system_dir = tmp_path / "system"
    tasks_dir.mkdir()
    system_dir.mkdir()

    (tasks_dir / "review.md").write_text("Content")
    (tasks_dir / "test.md").write_text("Content")
    (system_dir / "assistant.md").write_text("Content")

    loader = PromptLoader(tmp_path)
    prompts = loader.list("tasks/*.md")

    assert sorted(prompts) == ["tasks/review.md", "tasks/test.md"]


def test_list_empty_directory(tmp_path: Path) -> None:
    """Test listing prompts in empty directory."""
    loader = PromptLoader(tmp_path)
    prompts = loader.list()

    assert prompts == []


# ============================================================================
# Paths Tests
# ============================================================================


def test_prompt_in_subdirectory(tmp_path: Path) -> None:
    """Test loading prompt from subdirectory."""
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir()

    (tasks_dir / "review.md").write_text("Review this {{ code }}")

    loader = PromptLoader(tmp_path)
    result = loader("tasks/review.md", code="function() {}")

    assert result == "Review this function() {}"


def test_deeply_nested_prompt(tmp_path: Path) -> None:
    """Test loading deeply nested prompt."""
    deep_dir = tmp_path / "level1" / "level2" / "level3"
    deep_dir.mkdir(parents=True)

    (deep_dir / "prompt.md").write_text("Hello {{ name }}")

    loader = PromptLoader(tmp_path)
    result = loader("level1/level2/level3/prompt.md", name="World")

    assert result == "Hello World"


def test_different_file_extensions(tmp_path: Path) -> None:
    """Test that loader works with different file extensions."""
    (tmp_path / "prompt.txt").write_text("Hello {{ name }}")
    (tmp_path / "prompt.md").write_text("Hi {{ name }}")

    loader = PromptLoader(tmp_path)

    assert loader("prompt.txt", name="Alice") == "Hello Alice"
    assert loader("prompt.md", name="Bob") == "Hi Bob"


# ============================================================================
# Error Handling Tests
# ============================================================================


def test_missing_required_variable_error(tmp_path: Path) -> None:
    """Test error when required variable is missing (no default)."""
    prompt_file = tmp_path / "required.md"
    prompt_file.write_text("Hello {{ name }}!")

    loader = PromptLoader(tmp_path)

    with pytest.raises(jinja2.UndefinedError, match="name"):
        loader("required.md")


def test_invalid_jinja2_syntax_error(tmp_path: Path) -> None:
    """Test error with invalid Jinja2 syntax."""
    prompt_file = tmp_path / "invalid.md"
    prompt_file.write_text("Hello {{ name")  # Missing closing braces

    loader = PromptLoader(tmp_path)

    with pytest.raises(jinja2.TemplateSyntaxError):
        loader("invalid.md", name="World")


def test_template_not_found_error(tmp_path: Path) -> None:
    """Test FileNotFoundError for nonexistent template."""
    loader = PromptLoader(tmp_path)

    with pytest.raises(FileNotFoundError, match="does_not_exist.md"):
        loader("does_not_exist.md")


def test_syntax_error_in_variables_detection(tmp_path: Path) -> None:
    """Test syntax error when detecting variables."""
    prompt_file = tmp_path / "invalid.md"
    prompt_file.write_text("Hello {{ name")

    loader = PromptLoader(tmp_path)

    with pytest.raises(jinja2.TemplateSyntaxError):
        loader.variables("invalid.md")


# ============================================================================
# Additional Features Tests
# ============================================================================


def test_prompts_dir_property(tmp_path: Path) -> None:
    """Test prompts_dir property returns correct path."""
    loader = PromptLoader(tmp_path)
    assert loader.prompts_dir == tmp_path
    assert isinstance(loader.prompts_dir, Path)


def test_string_path_initialization(tmp_path: Path) -> None:
    """Test initialization with string path."""
    loader = PromptLoader(str(tmp_path))
    assert loader.prompts_dir == tmp_path


def test_whitespace_handling(tmp_path: Path) -> None:
    """Test that trim_blocks and lstrip_blocks work correctly."""
    prompt_file = tmp_path / "whitespace.md"
    prompt_file.write_text("""
{% if True %}
Line with content
{% endif %}
    """)

    loader = PromptLoader(tmp_path)
    result = loader("whitespace.md")

    # Should have clean whitespace, not excessive blank lines
    assert result.strip() == "Line with content"


def test_include_directive(tmp_path: Path) -> None:
    """Test Jinja2 include directive for composing prompts."""
    (tmp_path / "header.md").write_text("# Header\n")
    (tmp_path / "main.md").write_text("""
{% include 'header.md' %}
Main content here
    """.strip())

    loader = PromptLoader(tmp_path)
    result = loader("main.md")

    assert "# Header" in result
    assert "Main content here" in result


def test_comment_blocks_ignored(tmp_path: Path) -> None:
    """Test that Jinja2 comments are ignored in output."""
    prompt_file = tmp_path / "comments.md"
    prompt_file.write_text("""
Line 1
{# This is a comment and should not appear #}
Line 2
    """.strip())

    loader = PromptLoader(tmp_path)
    result = loader("comments.md")

    assert "Line 1" in result
    assert "Line 2" in result
    assert "comment" not in result.lower()
