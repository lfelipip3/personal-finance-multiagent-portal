from openai import OpenAI
from dotenv import load_dotenv
import os

from my_agents.spend_agent import SpendManagementAgent
from my_agents.investment_agent import InvestmentManagementAgent
from my_agents.project_agent import ProjectManagementAgent

class SessionMemory:
    def __init__(self):
        self.data = {}

    def update(self, key: str, value):
        self.data[key] = value

    def get(self, key: str, default=None):
        return self.data.get(key, default)

def select_model():
    available_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4.1-2025-04-14"]
    print("Available models:")
    for idx, model in enumerate(available_models, 1):
        print(f"{idx}. {model}")

    choice = input("Select the model number you want to use (default 4 for gpt-4.1-2025-04-14): ").strip()

    if choice.isdigit():
        idx = int(choice)
        if 1 <= idx <= len(available_models):
            return available_models[idx - 1]

    print("Using default model gpt-4.1-2025-04-14.\n")
    return "gpt-4.1-2025-04-14"

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
selected_model = select_model()
client = OpenAI(api_key=api_key)

def classify_user_request_with_llm(client, user_input: str) -> str:
    """Use LLM to classify user input into Spend, Investment, or Project."""
    system_prompt = """You are a router assistant. 
    Given a user's message, decide if it should go to:
    - Spend Management Agent
    - Investment Management Agent
    - Project Management Agent

    Only answer with one word: 'spend', 'investment', or 'project'.

    If unclear, guess the most likely option."""
    
    response = client.chat.completions.create(
        model=selected_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ]
    )

    choice = response.choices[0].message.content.lower().strip()

    if choice not in ["spend", "investment", "project"]:
        choice = "spend"  # default fallback

    return choice

# Initialize all agents
session_memory = SessionMemory()

agents = {
    "spend": SpendManagementAgent(client, selected_model, session_memory),
    "investment": InvestmentManagementAgent(client, selected_model, session_memory),
    "project": ProjectManagementAgent(client, selected_model, session_memory),
}

# After all agents are created, set their access to each other
for agent in agents.values():
    agent.set_agents(agents)

def route_input(user_input: str):
    """Route using LLM classification instead of keyword matching."""
    agent_key = classify_user_request_with_llm(client, user_input)

    agent = agents.get(agent_key)

    if agent:
        return agent.handle(user_input)
    else:
        return "Sorry, I could not determine the right agent for your request."


# Main console loop
if __name__ == "__main__":
    print("Welcome to your Personal Finance Multi-Agent Portal!")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        response = route_input(user_input)
        print(response)