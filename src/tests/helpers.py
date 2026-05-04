import json
from tests.client import create_client

client = create_client()
messages = []
# Helper functions
def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)


def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)


def chat(messages, system=None, temperature=1.0, stop_sequences=[]):
    params = {
        "model": "@aws-bedrock-use2/us.anthropic.claude-3-haiku-20240307-v1:0",
        "max_tokens": 1000,
        "messages": messages,
        "temperature": temperature,
        "stop_sequences": stop_sequences
    }

    if system:
        params["system"] = system

    message = client.messages.create(**params)
    return message.content[0].text

def grade_syntax(ticket):
    try:
        if json.loads(ticket.strip()) and ("intent" and "urgency" and "category" and "summary" and "analysis" in ticket):
            return 10
    except SyntaxError:
        # handle IsValidJson
        return 0


def grade_by_llm(test, ticket):
    prompt = f"""
        You are an expert IT Support Technician. Your task is to evaluate the following user's issue.

        Original Issue:
        <issue>{test["issue"]}</issue>

        Ticket:
        <ticket>{ticket}</ticket>

        Solution Criteria:
        <criteria>{test["solution_criteria"]}</criteria>

        Output Format:
        Provide your evaluation as a structured JSON object with the following fields:
        - "strengths": An array of 1-3 key strengths
        - "weaknesses": An array of 1-3 key areas for improvement
        - "reasoning": A concise explanation of your overall assessment
        - "score": A number between 1-10

        Respond with JSON. Keep your response concise and direct.
        Example response shape:
        {{
            "strengths": string[],
            "weaknesses": string[],
            "reasoning": string,
            "score": number
        }}

        * Ensure key metrics as found the ServiceNow Incident ticket schema are accurate and justified.
"""
    messages = []
    add_user_message(messages, prompt)
    add_assistant_message(messages, "```json")
    eval = chat(messages, stop_sequences=["```"])
    return json.loads(eval)

def run_test(test):
    prompt = f"""
    Classify the following support request into one of the following categories: 1) password_issue, 2) hardware_issue, 3) software_issue 4) general_inquiry. 
        
        Request: {test["issue"]}

        Analyze this IT request and provide the classification, including intent, urgency, category, and summary.

        Example output:
        ```json
        [
            {{
                "intent": "The intent of the email (e.g., password reset, software issue, hardware issue)",
                "urgency": "The extent to which resolution of an incident can bear delay (1 for high delay, 3 for low delay)",
                "category": "Category of the issue: ["network", "software", "hardware", "password_reset", "inquiry", "database"]",
                "analysis": "Agent's analysis and recommendation",
                "priority": "An integer from 1 to 5 indicating the severity in which an incident needs to be resolved: 1 - Critical, 2 - High, 3 - Moderate, 4 - Low, 5 - Planning"
            }}
        ]
        ```
    """
    add_user_message(messages, prompt)
    add_assistant_message(messages, "```json")
    response = chat(messages, stop_sequences=["```"])
    return response