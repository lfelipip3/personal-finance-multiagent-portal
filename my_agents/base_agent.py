from openai import OpenAI

class BaseAgent:
    def __init__(self, client: OpenAI, name: str, description: str, model: str):
        self.client = client
        self.name = name
        self.description = description
        self.tools = {}
        self.agents = {}  # Reference to other agents
        self.model = model

    def register_tool(self, tool_name: str, tool_function):
        self.tools[tool_name] = tool_function

    def set_agents(self, agents: dict):
        """Provide a registry of all available agents (including self)."""
        self.agents = agents

    def reason_and_select_tool(self, user_input: str) -> str:
        available_tools = ", ".join(self.tools.keys())

        system_prompt = f"""You are an intelligent agent.
        You can use the following tools: {available_tools}

        ONLY respond with the name of the tool to use.

        If no available tool fits, and another agent would be better suited, respond exactly with:
        'delegate to [agent name]'
        where agent names are: spend, investment, project.
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ]
        )

        choice = response.choices[0].message.content.strip().lower()

        return choice

    def handle(self, user_input: str) -> str:
        """Main method to handle user input (must be overridden)."""
        raise NotImplementedError("Subclasses must implement this.")

    def reason_with_chain_of_thought(self, user_input: str) -> dict:
        """Use LLM to think step-by-step before picking a tool or delegating."""
        available_tools = ", ".join(self.tools.keys())
        available_agents = ", ".join(["spend", "investment", "project"])

        system_prompt = f"""You are an intelligent financial agent.

    You must perform step-by-step reasoning to decide the final action to handle the user's request.

    Available tools you can use: {available_tools}
    Available agents you can delegate to: {available_agents}

    Follow this process strictly:
    1. Think step-by-step what the user's goal is.
    2. Think what sub-tasks would solve it.
    3. Decide whether you can solve it yourself or if another agent is needed.

    Output ONLY a JSON object like this:

    {{
      "reasoning": "<your reasoning>",
      "final_action": "<tool_name>"  # (must match exactly from available tools) 
    }}
    OR, if delegating:

    {{
      "reasoning": "<your reasoning>",
      "final_action": "delegate to <agent_name>"  # (agent name only: spend, investment, or project)
    }}

    No free text. No explanations outside the JSON.

    If you cannot understand, delegate to spend.
    """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ]
        )

        import json
        reasoning_text = response.choices[0].message.content.strip()
        try:
            parsed = json.loads(reasoning_text)
        except Exception as e:
            print("[Agent] Failed to parse reasoning JSON:", e)
            print("[Agent] Raw LLM output:", reasoning_text)
            parsed = {"reasoning": "Could not parse reasoning", "final_action": "delegate to spend"}

        return parsed

    def generate_response(self, context: str) -> str:
        """Use LLM to generate a natural conversational response based on tool output."""
        system_prompt = """You are a friendly financial assistant. 
        Given some internal context (like tool results), you must generate a polite, natural, and helpful response to the user.

        Always be brief (1-3 sentences), helpful, and clear.

        Do not repeat the user's input. Just explain the result nicely."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print("[Agent] Failed to generate nice response. Returning raw output.", e)
            return context  # fallback if API fails