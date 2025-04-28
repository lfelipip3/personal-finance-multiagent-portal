from .base_agent import BaseAgent
from tools.project_evaluator import build_cash_flows, calculate_project_npv
from tools.debt_optimizer import suggest_debt_payoff
import json

class ProjectManagementAgent(BaseAgent):
    def __init__(self, client, model, session_memory):
        super().__init__(
            client=client,
            model=model,
            name="Project Management Agent",
            description="Manages user projects, evaluates risk, and optimizes debt."
        )
        self.session_memory = session_memory

        self.register_tool("project_npv_calculator", None)
        self.register_tool("debt_payoff_optimizer", None)

    def handle(self, user_input: str) -> str:
        # STEP 1: Classify if debt or project task
        task_type = self.classify_task_type(user_input)

        if task_type == "debt":
            return self.optimize_debt(user_input)

        # Else continue normal project task
        reasoning = self.reason_with_chain_of_thought(user_input)
        print(f"[{self.name}] Chain of Thought Reasoning:\n{reasoning['reasoning']}\n")

        final_action = reasoning['final_action'].lower()

        if final_action.startswith("delegate to"):
            _, agent_key = final_action.split("delegate to")
            agent_key = agent_key.strip()

            if agent_key == self.name.lower().split()[0]:
                print(f"[{self.name}] I am already the correct agent. Reasoning internally...")
            else:
                if agent_key in self.agents:
                    print(f"[{self.name}] Delegating task to {agent_key.capitalize()} Agent...")
                    return self.agents[agent_key].handle(user_input)
                else:
                    return f"[{self.name}] Unknown delegation target."

        if final_action not in self.tools:
            return f"[{self.name}] Sorry, I could not find the right tool."

        if final_action == "project_npv_calculator":
            return self.evaluate_projects(user_input)

        else:
            return f"[{self.name}] Selected an unknown tool."

    def classify_task_type(self, user_input: str) -> str:
        """Classify if the user input is about debt or project evaluation."""
        system_prompt = """You are a classification assistant. 

        Classify the following user input as either:
        - "debt" (if about loans, payments, debts, payoff)
        - "project" (if about investments, projects, cash flows, returns)

        Only reply with one word: "debt" or "project"."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )

        classification = response.choices[0].message.content.strip().lower()
        return classification

    def get_discount_rate(self):
        """Ask user for a custom discount rate."""
        try:
            rate = input("[Project Agent] Enter discount rate as decimal (default 0.10 for 10%): ").strip()
            if not rate:
                return 0.10
            return float(rate)
        except ValueError:
            print("Invalid input. Using default 10% discount rate.")
            return 0.10

    def extract_projects_from_text(self, user_input: str) -> dict:
        """Use LLM to extract structured project data."""
        system_prompt = """You are a project extraction assistant.

        From the user's description, extract a list of projects. For each project, identify:

        - name (string)
        - initial_investment (float)
        - periods (int)
        - base_income (float)
        - growth_rate (float, optional, default 0 if not mentioned)
        - expenses (float, optional, default 0 if not mentioned)
        - unexpected_costs (dictionary where keys are periods as strings and values are amounts)

        Output STRICTLY as JSON:
        {
            "projects": [ 
                { project 1 },
                { project 2 },
                ...
            ]
        }
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )

        try:
            projects_data = json.loads(response.choices[0].message.content.strip())
            return projects_data
        except Exception as e:
            print("[Project Agent] Failed to parse project JSON:", e)
            print("[Project Agent] Raw LLM output:", response.choices[0].message.content.strip())
            return {"projects": []}

    def evaluate_projects(self, user_input: str) -> str:
        """Evaluate multiple projects and summarize the best option."""
        projects_info = self.extract_projects_from_text(user_input)
        projects = projects_info.get("projects", [])

        if not projects:
            return "Sorry, I could not understand the project details. Could you describe them again mentioning investment amount, expected cash inflows, periods, and unexpected costs?"

        evaluated_projects = []
        discount_rate = self.get_discount_rate()

        # === Collect results ===
        for project in projects:
            cash_flows = build_cash_flows(project)
            npv = calculate_project_npv(project["initial_investment"], cash_flows, discount_rate)
            evaluated_projects.append({
                "name": project["name"],
                "npv": npv,
                "cash_flows": cash_flows
            })

        # === Sort and Save ===
        ranked_projects = sorted(evaluated_projects, key=lambda x: x["npv"], reverse=True)
        self.session_memory.update("last_evaluated_projects", ranked_projects)

        # === STEP 1: Print the detailed NPV and Cash Flow Tables NOW ===
        print("\n📊 Project Evaluation Results:")
        for proj in ranked_projects:
            print(f"- {proj['name']}: NPV = ${proj['npv']:.2f}")
            print(self.build_cash_flow_table(proj["cash_flows"]))
            print()

        # === STEP 2: Prepare a small context only for final summary ===
        best_project = ranked_projects[0]
        context = f"The project with the highest NPV is {best_project['name']}."

        # === STEP 3: Ask LLM to generate a final user-friendly summary ===
        return self.generate_response(context)

    def optimize_debt(self, user_input: str) -> str:
        """Help user optimize debt payment based on budget and monthly payments."""
        try:
            budget = float(input("[Project Agent] Enter your available budget for extra payments: "))
            monthly_payment = float(input("[Project Agent] Enter your current monthly debt payment: "))
            suggestion = suggest_debt_payoff(budget, monthly_payment)
            return self.generate_response(f"Debt payoff suggestion: {suggestion}")
        except ValueError:
            return "Invalid input. Please enter valid numeric values."

    def build_cash_flow_table(self, cash_flows: list) -> str:
        """Build a neat cash flow table."""
        table = "Period | Cash Flow\n"
        table += "-------|----------\n"
        for i, flow in enumerate(cash_flows, start=1):
            table += f"{i:^7}| ${flow:,.2f}\n"
        return table