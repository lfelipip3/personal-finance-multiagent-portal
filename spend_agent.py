from .base_agent import BaseAgent
from tools.expense_classifier import classify_expense
from tools.budget_tracker import check_budget
from tools.bill_reminder import remind_upcoming_bills

class SpendManagementAgent(BaseAgent):
    def __init__(self, client, model, session_memory):
        super().__init__(
            client=client,
            name="Spend Management Agent",
            description="Manages user spending, budgets, and alerts.",
            model=model
        )
        
        self.session_memory = session_memory
        self.register_tool("expense_classifier", classify_expense)
        self.register_tool("budget_tracker", check_budget)
        self.register_tool("bill_reminder", remind_upcoming_bills)

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

        if final_action == "expense_classifier":
            expense_description = input("[Spend Agent] Please describe your expense: ")
            result = self.tools[final_action](expense_description)
            return self.generate_response(f"Result of {final_action}: {result}")

        elif final_action == "budget_tracker":
            spent = float(input("[Spend Agent] How much did you spend? "))
            budget = float(input("[Spend Agent] What is your budget? "))
            result = self.tools[final_action](spent, budget)
            return self.generate_response(f"Result of {final_action}: {result}")

        elif final_action == "bill_reminder":
            bills = [
                {"name": "Electricity Bill", "due_date": "2025-05-10"},
                {"name": "Water Bill", "due_date": "2025-05-12"},
                ]
            result = self.tools[final_action](bills)
            return self.generate_response(f"Result of {final_action}: {result}")

        else:
            return f"[{self.name}] Selected an unknown tool."