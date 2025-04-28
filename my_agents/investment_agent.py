from .base_agent import BaseAgent
from tools.investment_calculator import calculate_investment_return
from tools.portfolio_analyzer import analyze_portfolio

class InvestmentManagementAgent(BaseAgent):
    def __init__(self, client, model, session_memory):
        super().__init__(
            client=client,
            name="Investment Management Agent",
            description="Manages user investments, returns, and reallocations.",
            model=model
        )

        self.session_memory = session_memory
        self.register_tool("investment_return_calculator", calculate_investment_return)
        self.register_tool("portfolio_analyzer", analyze_portfolio)

    def handle(self, user_input: str) -> str:
        reasoning = self.reason_with_chain_of_thought(user_input)
        print(f"[{self.name}] Chain of Thought Reasoning:\n{reasoning['reasoning']}\n")

        final_action = reasoning['final_action'].lower()

        if final_action.startswith("delegate to"):
            _, agent_key = final_action.split("delegate to")
            agent_key = agent_key.strip()

            if agent_key == self.name.lower().split()[0]:
                print(f"[{self.name}] I am already the correct agent. Proceeding internally...")
                # Do not delegate, proceed with final_action
            else:
                if agent_key in self.agents:
                    print(f"[{self.name}] Delegating task to {agent_key.capitalize()} Agent...")
                    return self.agents[agent_key].handle(user_input)
                else:
                    return f"[{self.name}] Unknown delegation target."

        if final_action not in self.tools:
            return f"[{self.name}] Sorry, I could not find the right tool."

        if final_action == "investment_return_calculator":
            try:
                initial = float(input("[Investment Agent] Enter your initial investment amount: "))
                final = float(input("[Investment Agent] Enter your final investment value: "))
                result = self.tools[final_action](initial, final)
                return self.generate_response(f"Result of {final_action}: {result}")
            except ValueError:
                return "[Investment Agent] Invalid number entered."

        elif final_action == "portfolio_analyzer":
            try:
                returns_input = input("[Investment Agent] Enter individual investment returns separated by commas: ")
                returns = [float(x.strip()) for x in returns_input.split(",")]
                result = self.tools[final_action](returns)
                return self.generate_response(f"Result of {final_action}: {result}")
            except ValueError:
                return "[Investment Agent] Invalid input."

        else:
            return f"[{self.name}] Selected an unknown tool."