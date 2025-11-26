"""Tutorial demo: Using combined prompts for n8n + Airtable integration."""

from promptly import PromptLoader


def main():
    # Initialize loader
    loader = PromptLoader("prompts")

    print("=" * 70)
    print("Promptly Tutorial Demo: n8n + Airtable Integration")
    print("=" * 70)

    # Demo 1: Pure n8n developer
    print("\n1. Pure n8n Developer Prompt:")
    print("-" * 70)
    n8n_prompt = loader("developers/n8n.md")
    print(n8n_prompt)

    # Demo 2: Pure Airtable developer
    print("\n2. Pure Airtable Developer Prompt:")
    print("-" * 70)
    airtable_prompt = loader("developers/airtable.md")
    print(airtable_prompt)

    # Demo 3: Combined n8n + Airtable specialist
    print("\n3. Combined n8n + Airtable Integration Specialist:")
    print("-" * 70)
    integration_prompt = loader("developers/n8n_airtable.md")
    print(integration_prompt)

    # Demo 4: Show available prompts
    print("\n4. Available Prompts:")
    print("-" * 70)
    all_prompts = loader.list()
    for prompt in sorted(all_prompts):
        print(f"  - {prompt}")

    # Demo 5: List just developer prompts
    print("\n5. Developer Prompts Only:")
    print("-" * 70)
    dev_prompts = loader.list("developers/*.md")
    for prompt in sorted(dev_prompts):
        print(f"  - {prompt}")

    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print("\nTry using these prompts with your favorite LLM:")
    print("  - Anthropic Claude")
    print("  - OpenAI GPT")
    print("  - Or any other LLM API")
    print("\nSee TUTORIAL.md for detailed examples with code!")


if __name__ == "__main__":
    main()
