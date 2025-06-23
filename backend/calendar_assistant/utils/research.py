from smolagents import tool, LiteLLMModel, LogLevel
from langchain_google_community import GoogleSearchAPIWrapper
from smolagents import CodeAgent

@tool
def google_search(query: str) -> str:
    """
    Busca en Google los principales 3 resultados para una consulta.

    Args:
        query: Texto de búsqueda.

    Returns:
        str: Resultados concatenados.
    """
    search = GoogleSearchAPIWrapper(k=3)
    return search.run(query)

def research_week_plan(event_summary: str, general_info: str, user_requirements: str) -> str:
    model = LiteLLMModel(model_id="gpt-4.1")
    agent = CodeAgent(
        tools=[google_search],
        model=model,
        add_base_tools=True,
        stream_outputs=True,
        use_structured_outputs_internally=True,
        verbosity_level=LogLevel.DEBUG
    )
    prompt = f"""
Find tips and structure for a 1‑week training plan to prepare for the next fitness event: '{event_summary}'.\n
Here is some general information about the user's profile: {general_info}\n
Also, consider and prioritize the following user requirements (only if provided): {user_requirements}\n
The plan must only focus on the training events. Don't include the main event in the plan.
Then produce a daily schedule with lines like:\n
sunday: ..., monday: ..., ..., saturday: ...\n
You must use the google search tool to answer\n
"""
    result = agent.run(prompt)
    output_str = result.to_string() if hasattr(result, "to_string") else str(result)
    # Guarda el resultado
    path = "weekly_training_plan.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"Event summary: {event_summary}\n\n")
        f.write("Weekly Training Plan:\n")
        f.write(output_str)
    return path
