"""Minimalist prompt loader with Jinja2 templating support."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import jinja2
import jinja2.meta


class PromptLoader:
    """Load and render prompt templates with Jinja2.

    This loader provides a simple interface for managing reusable prompt templates.
    It supports variable substitution, filters, conditionals, and loops through Jinja2.

    Attributes:
        _prompts_dir: Directory containing prompt templates.
        env: Jinja2 environment for template rendering.

    Example:
        >>> loader = PromptLoader("prompts")
        >>> prompt = loader("code_review.md", language="Python", code="def foo(): pass")
        >>> variables = loader.variables("code_review.md")
        >>> all_prompts = loader.list()
    """

    def __init__(self, prompts_dir: Path | str) -> None:
        """Initialize the prompt loader.

        Args:
            prompts_dir: Directory containing prompt templates.

        Raises:
            ValueError: If prompts_dir doesn't exist.
        """
        self._prompts_dir = Path(prompts_dir)

        if not self._prompts_dir.exists():
            raise ValueError(
                f"Prompts directory does not exist: {self._prompts_dir.absolute()}"
            )

        if not self._prompts_dir.is_dir():
            raise ValueError(
                f"Path is not a directory: {self._prompts_dir.absolute()}"
            )

        # Configure Jinja2 environment with clean formatting
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self._prompts_dir),
            trim_blocks=True,
            lstrip_blocks=True,
            undefined=jinja2.StrictUndefined,  # Raise errors for missing variables
        )

    def __call__(self, prompt_path: str, **variables: Any) -> str:
        """Load and render a prompt template.

        Args:
            prompt_path: Path to prompt file relative to prompts_dir.
            **variables: Variables to render the template with.

        Returns:
            Rendered prompt as string.

        Raises:
            FileNotFoundError: If prompt file doesn't exist.
            jinja2.TemplateNotFound: If template cannot be found.
            jinja2.UndefinedError: If required variables are missing.
            jinja2.TemplateSyntaxError: If template has syntax errors.

        Example:
            >>> loader = PromptLoader("prompts")
            >>> prompt = loader("code_review.md", language="Python", code="def foo(): pass")
        """
        try:
            template = self.env.get_template(prompt_path)
            return template.render(**variables)
        except jinja2.TemplateNotFound as e:
            # Convert to FileNotFoundError for more pythonic error handling
            full_path = self._prompts_dir / prompt_path
            raise FileNotFoundError(
                f"Prompt template not found: {prompt_path}\n"
                f"Expected location: {full_path.absolute()}"
            ) from e
        except jinja2.UndefinedError as e:
            # Add context to undefined variable errors
            raise jinja2.UndefinedError(
                f"Missing required variable in template '{prompt_path}': {e}"
            ) from e

    # Allow both syntaxes: loader(...) and loader.load(...)
    load = __call__

    def variables(self, prompt_path: str) -> set[str]:
        """Detect variables used in a prompt template.

        This method uses Jinja2's AST parser to find all undeclared variables
        in the template. This includes variables used in expressions, conditionals,
        loops, and filters.

        Args:
            prompt_path: Path to prompt file relative to prompts_dir.

        Returns:
            Set of variable names used in the template.

        Raises:
            FileNotFoundError: If prompt file doesn't exist.
            jinja2.TemplateSyntaxError: If template has syntax errors.

        Example:
            >>> loader = PromptLoader("prompts")
            >>> vars = loader.variables("code_review.md")
            >>> print(vars)
            {'language', 'code', 'focus'}
        """
        try:
            template_source = self.env.loader.get_source(self.env, prompt_path)
            parsed_content = self.env.parse(template_source[0])
            return jinja2.meta.find_undeclared_variables(parsed_content)
        except jinja2.TemplateNotFound as e:
            full_path = self._prompts_dir / prompt_path
            raise FileNotFoundError(
                f"Prompt template not found: {prompt_path}\n"
                f"Expected location: {full_path.absolute()}"
            ) from e

    def list(self, pattern: str = "**/*.md") -> list[str]:
        """List all available prompts matching a pattern.

        Args:
            pattern: Glob pattern for matching files (default: all .md files).

        Returns:
            List of prompt paths relative to prompts_dir, sorted alphabetically.

        Example:
            >>> loader = PromptLoader("prompts")
            >>> loader.list()
            ['system/assistant.md', 'tasks/code_review.md']
            >>> loader.list("tasks/*.md")
            ['tasks/code_review.md', 'tasks/documentation.md']
        """
        matches = self._prompts_dir.glob(pattern)
        # Convert to relative paths and sort
        relative_paths = [
            str(path.relative_to(self._prompts_dir))
            for path in matches
            if path.is_file()
        ]
        return sorted(relative_paths)

    @property
    def prompts_dir(self) -> Path:
        """Return the prompts directory path.

        Returns:
            Path object pointing to the prompts directory.
        """
        return self._prompts_dir
