"""Basic usage examples for promptly."""

from promptly import PromptLoader


def main() -> None:
    """Run basic usage examples."""
    # Create loader - uses built-in prompts from package by default
    loader = PromptLoader()

    # Example 1: Simple rendering
    print("=== Example 1: Simple Rendering ===")
    print("This example assumes prompts/system/assistant.md exists")
    print("Template: You are {{ name }}, an AI {{ expertise }} assistant.")
    print()
    try:
        prompt = loader("system/assistant.md", name="Code Assistant", expertise="Python")
        print("Rendered:")
        print(prompt)
    except FileNotFoundError:
        print("Note: prompts/system/assistant.md not found. Create it to run this example.")
    print()

    # Example 2: Using defaults
    print("=== Example 2: Using Defaults ===")
    print('Template: Hello {{ name|default("User") }}!')
    print()
    try:
        # Uses default
        prompt = loader("templates/greeting.md")
        print(f"Without providing name: {prompt}")

        # Override default
        prompt = loader("templates/greeting.md", name="Fernando")
        print(f"With name='Fernando': {prompt}")
    except FileNotFoundError:
        print("Note: prompts/templates/greeting.md not found. Create it to run this example.")
    print()

    # Example 3: Detect variables
    print("=== Example 3: Detect Variables ===")
    print("This detects which variables a template uses")
    print()
    try:
        variables = loader.variables("tasks/code_review.md")
        print(f"Variables in tasks/code_review.md: {variables}")
    except FileNotFoundError:
        print("Note: prompts/tasks/code_review.md not found. Create it to run this example.")
    print()

    # Example 4: List prompts
    print("=== Example 4: List Available Prompts ===")
    all_prompts = loader.list()
    print(f"All prompts: {all_prompts}")
    print()

    task_prompts = loader.list("tasks/*.md")
    print(f"Task prompts: {task_prompts}")
    print()

    # Example 5: Both calling syntaxes
    print("=== Example 5: Equivalent Calling Syntaxes ===")
    print("loader(...) and loader.load(...) work identically")
    try:
        # Both syntaxes work
        result1 = loader("system/assistant.md", name="Helper", expertise="general")
        result2 = loader.load("system/assistant.md", name="Helper", expertise="general")
        print(f"Results are identical: {result1 == result2}")
    except FileNotFoundError:
        print("Note: Create prompts to test this example")
    print()


if __name__ == "__main__":
    main()
