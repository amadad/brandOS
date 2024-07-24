import os
from typing import List, Dict, Union
from dotenv import load_dotenv
from chain.chain import MinimalChainable, FusionChain
import llm
import json


def build_models():
    load_dotenv()

    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

    sonnet_3_5_model: llm.Model = llm.get_model("claude-3.5-sonnet")
    sonnet_3_5_model.key = ANTHROPIC_API_KEY

    # Add more models here for FusionChain
    sonnet_3_model: llm.Model = llm.get_model("claude-3-sonnet")
    sonnet_3_model.key = ANTHROPIC_API_KEY

    haiku_3_model: llm.Model = llm.get_model("claude-3-haiku")
    haiku_3_model.key = ANTHROPIC_API_KEY

    return [sonnet_3_5_model, sonnet_3_model, haiku_3_model]


def prompt(model: llm.Model, prompt: str):
    res = model.prompt(
        prompt,
        temperature=0.5,
    )
    return res.text()


def prompt_chainable_poc():

    sonnet_3_5_model, _, _ = build_models()

    result, context_filled_prompts = MinimalChainable.run(
        context={"topic": "AI Agents"},
        model=sonnet_3_5_model,
        callable=prompt,
        prompts=[
            # prompt #1
            "Generate one blog post title about: {{topic}}. Respond in strictly in JSON in this format: {'title': '<title>'}",
            # prompt #2
            "Generate one hook for the blog post title: {{output[-1].title}}",
            # prompt #3
            """Based on the BLOG_TITLE and BLOG_HOOK, generate the first paragraph of the blog post.
BLOG_TITLE:
{{output[-2].title}}
BLOG_HOOK:
{{output[-1]}}""",
        ],
    )

    chained_prompts = MinimalChainable.to_delim_text_file(
        "poc_context_filled_prompts", context_filled_prompts
    )
    chainable_result = MinimalChainable.to_delim_text_file("poc_prompt_results", result)

    print(f"\n\n📖 Prompts~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ \n\n{chained_prompts}")
    print(f"\n\n📊 Results~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ \n\n{chainable_result}")

    pass


def fusion_chain_poc():
    sonnet_3_5_model, sonnet_3_model, haiku_3_model = build_models()

    def evaluator(outputs: List[str]) -> tuple[str, List[float]]:
        # Simple evaluator that chooses the longest output as the top response
        scores = [len(output) for output in outputs]
        max_score = max(scores)
        normalized_scores = [score / max_score for score in scores]
        top_response = outputs[scores.index(max_score)]
        return top_response, normalized_scores

    result = FusionChain.run(
        context={"topic": "AI Agents"},
        models=[sonnet_3_5_model, sonnet_3_model, haiku_3_model],
        callable=prompt,
        prompts=[
            # prompt #1
            "Generate one blog post title about: {{topic}}. Respond in strictly in JSON in this format: {'title': '<title>'}",
            # prompt #2
            "Generate one hook for the blog post title: {{output[-1].title}}",
            # prompt #3
            """Based on the BLOG_TITLE and BLOG_HOOK, generate the first paragraph of the blog post.
BLOG_TITLE:
{{output[-2].title}}
BLOG_HOOK:
{{output[-1]}}""",
        ],
        evaluator=evaluator,
        get_model_name=lambda model: model.model_id,
    )

    result_dump = result.dict()

    print("\n\n📊 FusionChain Results~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(json.dumps(result_dump, indent=4))

    # Write the result to a JSON file
    with open("poc_fusion_chain_result.json", "w") as json_file:
        json.dump(result_dump, json_file, indent=4)


def main():

    prompt_chainable_poc()

    # fusion_chain_poc()


if __name__ == "__main__":
    main()