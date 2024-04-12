import os
import re
import json
from dotenv import load_dotenv
from anthropic import Anthropic
from tavily import TavilyClient
from rich.console import Console
from rich.panel import Panel
from datetime import datetime

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
client = Anthropic(api_key=api_key)

def calculate_subagent_cost(model, input_tokens, output_tokens):
    # Pricing information per model
    pricing = {
        "claude-3-opus-20240229": {"input_cost_per_mtok": 15.00, "output_cost_per_mtok": 75.00},
        "claude-3-haiku-20240307": {"input_cost_per_mtok": 0.25, "output_cost_per_mtok": 1.25},
    }
    # Calculate cost
    input_cost = (input_tokens / 1_000_000) * pricing[model]["input_cost_per_mtok"]
    output_cost = (output_tokens / 1_000_000) * pricing[model]["output_cost_per_mtok"]
    total_cost = input_cost + output_cost
    return total_cost

# Initialize the Rich Console
console = Console()

def opus_orchestrator(brand_info, previous_results=None, use_search=False):
    console.print(f"\n[bold]Calling Orchestrator for Brand OS[/bold]")
    previous_results_text = "\n".join(previous_results) if previous_results else "None"
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": f"Based on the following brand information and the previous sub-task results (if any), please break down the objective into the next sub-task, and create a concise and detailed prompt for a subagent so it can execute that task. The objective is to monitor, analyze, and suggest actions for the brand to maintain unique differentiation.\n\nBrand Information:\n{brand_info}\n\nPrevious sub-task results:\n{previous_results_text}"},
                {"type": "text", "text": "Please also generate a JSON object containing a single 'search_query' key, which represents a question that, when asked online, would yield important information for solving the subtask. The question should be specific and targeted to elicit the most relevant and helpful resources. Format your JSON like this, with no additional text before or after:\n{\"search_query\": \"<question>\"}\n"}
            ]
        }
    ]
    opus_response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=4096,
        messages=messages
    )
    response_text = opus_response.content[0].text
    console.print(f"Input Tokens: {opus_response.usage.input_tokens}, Output Tokens: {opus_response.usage.output_tokens}")
    total_cost = calculate_subagent_cost("claude-3-opus-20240229", opus_response.usage.input_tokens, opus_response.usage.output_tokens)
    console.print(f"Opus Orchestrator Cost: ${total_cost:.2f}")
    # Extract the JSON from the response
    json_match = re.search(r'{.*}', response_text, re.DOTALL)
    if json_match:
        json_string = json_match.group()
        try:
            search_query = json.loads(json_string)["search_query"]
            console.print(Panel(f"Search Query: {search_query}", title="[bold blue]Search Query[/bold blue]", title_align="left", border_style="blue"))
            response_text = response_text.replace(json_string, "").strip()
        except json.JSONDecodeError as e:
            console.print(Panel(f"Error parsing JSON: {e}", title="[bold red]JSON Parsing Error[/bold red]", title_align="left", border_style="red"))
            console.print(Panel(f"Skipping search query extraction.", title="[bold yellow]Search Query Extraction Skipped[/bold yellow]", title_align="left", border_style="yellow"))
            search_query = None
    else:
        search_query = None
    console.print(Panel(response_text, title=f"[bold green]Opus Orchestrator[/bold green]", title_align="left", border_style="green", subtitle="Sending task to Haiku 👇"))
    return response_text, search_query

def haiku_sub_agent(prompt, search_query=None, previous_haiku_tasks=None, continuation=False):
    if previous_haiku_tasks is None:
        previous_haiku_tasks = []
    continuation_prompt = "Continuing from the previous answer, please complete the response."
    system_message = "Previous Haiku tasks:\n" + "\n".join(f"Task: {task['task']}\nResult: {task['result']}" for task in previous_haiku_tasks)
    if continuation:
        prompt = continuation_prompt
    qna_response = None
    if search_query:
        # Initialize the Tavily client
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        tavily = TavilyClient(api_key=tavily_api_key)
        # Perform a QnA search based on the search query
        qna_response = tavily.qna_search(query=search_query)
        console.print(f"QnA response: {qna_response}", style="yellow")
    if not prompt.strip() and not qna_response:
        console.print("[bold yellow]Warning:[/bold yellow] Both prompt and search results are empty. Skipping API call.")
        return "I apologize, but I don't have enough information to provide a helpful response. Please provide more context or details."
    # Ensure that the prompt and qna_response are not empty before sending them to the API
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt.strip()} if prompt.strip() else None,
                {"type": "text", "text": f"\nSearch Results:\n{qna_response}" if qna_response else None}
            ]
        }
    ]
    # Filter out any None values from the content list
    messages[0]["content"] = [content for content in messages[0]["content"] if content is not None]
    haiku_response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=4096,
        messages=messages,
        system=system_message
    )
    response_text = haiku_response.content[0].text.strip()
    console.print(f"Input Tokens: {haiku_response.usage.input_tokens}, Output Tokens: {haiku_response.usage.output_tokens}")
    total_cost = calculate_subagent_cost("claude-3-haiku-20240307", haiku_response.usage.input_tokens, haiku_response.usage.output_tokens)
    console.print(f"Haiku Sub-agent Cost: ${total_cost:.2f}")
    if haiku_response.usage.output_tokens >= 4000 and not continuation:  # Threshold set to 4000 as a precaution
        console.print("[bold yellow]Warning:[/bold yellow] Output may be truncated. Attempting to continue the response.")
        continuation_response_text = haiku_sub_agent(continuation_prompt, search_query, previous_haiku_tasks + [{"task": prompt, "result": response_text}], continuation=True)
        response_text += "\n" + continuation_response_text
    console.print(Panel(response_text, title="[bold blue]Haiku Sub-agent Result[/bold blue]", title_align="left", border_style="blue", subtitle="Task completed, sending result to Opus 👇"))
    return response_text

def opus_refine(brand_info, sub_task_results, filename, continuation=False):
    print("\nCalling Opus to provide the refined final output for Brand OS:")
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Brand Information:\n" + brand_info + "\n\nSub-task results:\n" + "\n".join(sub_task_results) + "\n\nPlease review and refine the sub-task results into a cohesive final output. Add any missing information or details as needed. Provide a list of competitors, keyword search terms to monitor, and suggested actions for the brand to maintain unique differentiation."}
            ]
        }
    ]
    opus_response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=4096,
        messages=messages
    )
    response_text = opus_response.content[0].text.strip()
    console.print(f"Input Tokens: {opus_response.usage.input_tokens}, Output Tokens: {opus_response.usage.output_tokens}")
    total_cost = calculate_subagent_cost("claude-3-opus-20240229", opus_response.usage.input_tokens, opus_response.usage.output_tokens)
    console.print(f"Opus Refine Cost: ${total_cost:.2f}")
    if opus_response.usage.output_tokens >= 4000 and not continuation:  # Threshold set to 4000 as a precaution
        console.print("[bold yellow]Warning:[/bold yellow] Output may be truncated. Attempting to continue the response.")
        continuation_response_text = opus_refine(brand_info, sub_task_results + [response_text], filename, continuation=True)
        response_text += "\n" + continuation_response_text
    console.print(Panel(response_text, title="[bold green]Final Output[/bold green]", title_align="left", border_style="green"))
    return response_text

# Get the brand information from user input
brand_url = input("Please enter the brand URL: ")
mission = input("Please enter the brand mission: ")
vision = input("Please enter the brand vision: ")
values = input("Please enter the brand values: ")

brand_info = f"Brand URL: {brand_url}\nMission: {mission}\nVision: {vision}\nValues: {values}"

# Ask the user if they want to use search
use_search = input("Do you want to use search? (y/n): ").lower() == 'y'

task_exchanges = []
haiku_tasks = []

while True:
    # Call Orchestrator to break down the objective into the next sub-task or provide the final output
    previous_results = [result for _, result in task_exchanges]
    opus_result, search_query = opus_orchestrator(brand_info, previous_results, use_search)
    if "The task is complete:" in opus_result:
        # If Opus indicates the task is complete, exit the loop
        final_output = opus_result.replace("The task is complete:", "").strip()
        break
    else:
        sub_task_prompt = opus_result
        # Call haiku_sub_agent with the prepared prompt, search query, and record the result
        sub_task_result = haiku_sub_agent(sub_task_prompt, search_query, haiku_tasks)
        # Log the task and its result for future reference
        haiku_tasks.append({"task": sub_task_prompt, "result": sub_task_result})
        # Record the exchange for processing and output generation
        task_exchanges.append((sub_task_prompt, sub_task_result))

# Create the .md filename
sanitized_brand_name = re.sub(r'\W+', '_', brand_url)
timestamp = datetime.now().strftime("%H-%M-%S")

# Call Opus to review and refine the sub-task results
refined_output = opus_refine(brand_info, [result for _, result in task_exchanges], timestamp)

# Truncate the sanitized_brand_name to a maximum of 50 characters
max_length = 25
truncated_brand_name = sanitized_brand_name[:max_length] if len(sanitized_brand_name) > max_length else sanitized_brand_name

# Update the filename to include the brand name
filename = f"{timestamp}_{truncated_brand_name}.md"

# Prepare the full exchange log
exchange_log = f"Brand Information:\n{brand_info}\n\n"
exchange_log += "=" * 40 + " Task Breakdown " + "=" * 40 + "\n\n"
for i, (prompt, result) in enumerate(task_exchanges, start=1):
    exchange_log += f"Task {i}:\n"
    exchange_log += f"Prompt: {prompt}\n"
    exchange_log += f"Result: {result}\n\n"
exchange_log += "=" * 40 + " Refined Final Output " + "=" * 40 + "\n\n"
exchange_log += refined_output

console.print(f"\n[bold]Refined Final output:[/bold]\n{refined_output}")

with open(filename, 'w') as file:
    file.write(exchange_log)

print(f"\nFull exchange log saved to {filename}")