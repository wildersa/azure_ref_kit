import sys
from .config import Settings, validate_user_input
from .adapter import FoundryAgentAdapter


def main() -> None:
    """CLI entrypoint for the Foundry Agent with MCP solution."""
    try:
        # Load and validate configuration
        settings = Settings.from_env()

        # Get user input from command line arguments or stdin
        if len(sys.argv) > 1:
            raw_input = " ".join(sys.argv[1:])
        else:
            print("Enter your prompt: ", end="", flush=True)
            raw_input = sys.stdin.readline()

        user_input = validate_user_input(raw_input)

        # Invoke the agent
        adapter = FoundryAgentAdapter(settings)
        response_text = adapter.get_chat_response(user_input)

        # Print only the final safe response text
        print(response_text)

    except ValueError as ve:
        # Configuration or input validation errors
        print(f"Configuration error: {ve}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as re:
        # Sanitized runtime/SDK errors
        print(f"Error: {re}", file=sys.stderr)
        sys.exit(1)
    except Exception:
        # Catch-all for unexpected errors, keeping them sanitized
        print("Error: An unexpected error occurred.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
