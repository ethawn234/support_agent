import json
from tests.helpers import add_assistant_message, add_user_message, chat

def generate_dataset():
    prompt = """
Generate example user issue data for prompt evaluation. The dataset will be used to evaluate user IT Support requests
that LLMs handle. Generate an array of three objects, each a human request that is low, medium, and 
high priority issues. Each object should also contain a solution criteria. Respond only with the dataset array. 
Do not provide commentary.

"priority": "An integer from 1 to 5 indicating the severity in which an incident needs to be resolved: 1 - Critical, 2 - High, 3 - Moderate, 4 - Low, 5 - Planning"

Example output:
        ```json
        [
            {
                "issue": "the user's issue",
                "solution_criteria: "Characteristics the solution must have. Include the expected priority."
            },
            ...additional
        ]
        ```
"""
    messages = []
    
    add_user_message(messages, prompt)
    add_assistant_message(messages, "```json")

    response = chat(messages, stop_sequences=["```"])
    response = json.loads(response)

    with open("dataset.json", "w") as f:
        json.dump(response, f, indent=2)
        # TODO: Validate dataset structure. If invalid, re-prompt
    return response