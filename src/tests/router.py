from statistics import mean

from tests.generate_dataset import generate_dataset
from tests.helpers import *


def router():
    # TODO: add cli option to regenerate dataset
    dataset = generate_dataset()

    results = []

    # generate test scenarios & evals
    for test in dataset:
        # run initial issue analysis
        ticket = run_test(test)

        # run model grade
        model = grade_by_llm(test, ticket)
        model_grade = model["score"]
        reasoning = model["reasoning"]
        strengths = model["strengths"]
        weaknesses = model["weaknesses"]

        # run syntax grade
        syntax_grade = grade_syntax(ticket)

        # average grade
        score = (model_grade + syntax_grade) / 2

        # generate test result output
        output = {
            "ticket": json.loads(ticket),
            "score": score,
            "test_issue": test["issue"],
            "grade_by_model": {
                "score": model_grade,
                "reasoning": reasoning,
                "strengths": strengths,
                "weaknesses": weaknesses
            },
            "grade_by_syntax": syntax_grade
        }

        results.append(output)

    # generate overall grade
    mean_score = mean([result["score"] for result in results])
    
    print(mean_score)

    with open("prompt_eval.json", "w") as f:
        results = json.dump(results, f, indent=2)

    return results

router()