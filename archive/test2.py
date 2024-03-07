import os
from phi.assistant import Assistant
from dotenv import load_dotenv
from typing import List
from pydantic import BaseModel, Field
from rich.pretty import pprint
from phi.llm.openai.like import OpenAILike

load_dotenv()
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

class Policy(BaseModel):
    name: str
    date: int
    fact: List[str] = Field(..., description="A list of facts about the policy")
    recommendations: List[str] = Field(..., description="A list of recommendations")
    stakeholders: List[str] = Field(..., description="A list of stakeholders")
    challenges: List[str] = Field(..., description="A list of challenges")
    objectives: List[str] = Field(..., description="The goals or objectives that the policy aims to achieve")
    expected_outcomes: List[str] = Field(..., description="The anticipated results of implementing the policy")
    legal_context: List[str] = Field(..., description="Legal and regulatory considerations relevant to the policy")
    impact: List[str] = Field(..., description="Potential positive and negative impacts of the policy")
    evaluation_criteria: List[str] = Field(..., description="Criteria for monitoring and evaluating the policy's effectiveness")
    funding_sources: List[str] = Field(..., description="Sources of funding for the policy's implementation")
    implementation_timeline: List[str] = Field(None, description="The timeline over which the policy is expected to be implemented")
    policy_instruments: List[str] = Field(..., description="The tools and methods used to implement the policy")
    prior_examples: List[str] = Field(..., description="Examples of similar policies implemented in other contexts")
    feedback_mechanisms: List[str] = Field(..., description="Mechanisms for collecting feedback from stakeholders and the public")

policy_assistant = Assistant(
    description="You are an expert policy researcher and analyst.",
    llm=OpenAILike(
        model="sonar-small-online",
        api_key=os.getenv("PERPLEXITY_API_KEY"),
        base_url="https://api.perplexity.ai",
    ),
    output_model=Policy,
)

pprint(policy_assistant.run('Marijuana Legalisation in Michigan', markdown=True))




