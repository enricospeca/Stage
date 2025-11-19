from agno.agent import Agent
from agno.models.ollama import Ollama

agent = Agent(
    model=Ollama(id="gpt-oss:20b"),
    markdown=True
)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story.")