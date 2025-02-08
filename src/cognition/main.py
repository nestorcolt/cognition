#!/usr/bin/env python
from cognition.crew import Cognition
from datetime import datetime
import asyncio
import warnings
import sys


warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information


def run():
    """Run the crew."""
    inputs = {"topic": "AI LLMs", "current_year": str(datetime.now().year)}

    try:
        cognition = Cognition()
        # Use asyncio.run for setup
        asyncio.run(cognition.setup())
        crew = cognition.crew()

        # Debug information before execution
        print("\nCrew Configuration:")
        print(
            f"Available Tools: {crew.tools_handler.get_tools(crew.tool_service.list_tools()) if crew.tools_handler else 'No tools'}"
        )

        for agent in crew.agents:
            print(f"\nAgent: {agent.role}")
            print(f"Tools assigned: {agent.tools}")
            print(f"Tool names: {agent.tool_names}")

        # Use kickoff (not kickoff_async) as it handles the async internally
        result = crew.kickoff(inputs=inputs)
        return result

    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {"topic": "AI LLMs"}
    try:
        Cognition().crew().train(
            n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs
        )

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Cognition().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {"topic": "AI LLMs"}
    try:
        Cognition().crew().test(
            n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs
        )

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


if __name__ == "__main__":
    result = run()  # No asyncio.run needed here
    print(f"Result: {result}")
