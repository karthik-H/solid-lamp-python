import os

from crewai import Agent, Crew, LLM, Process, Task

from app.tools.wiki_search import wiki_search_tool


def _get_llm() -> LLM:
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    model = os.environ.get("OPENAI_MODEL")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not configured")
    if not model:
        raise ValueError("OPENAI_MODEL is not configured")
    return LLM(
        model=f"openai/{model}",
        api_key=api_key,
        base_url=base_url,
        api_base=base_url,
    )


def run_deep_analysis(question: str) -> dict:
    llm = _get_llm()

    answer_agent = Agent(
        role="Research Analyst",
        goal="Research and answer user questions accurately using Wikipedia",
        backstory=(
            "You are an expert researcher who gathers facts from Wikipedia "
            "before forming clear, well-supported answers."
        ),
        tools=[wiki_search_tool],
        llm=llm,
        verbose=False,
    )

    reviewer_agent = Agent(
        role="Answer Reviewer",
        goal="Review answers for accuracy, completeness, and clarity",
        backstory=(
            "You are a critical reviewer who verifies claims against Wikipedia "
            "and improves answers before they are delivered."
        ),
        tools=[wiki_search_tool],
        llm=llm,
        verbose=False,
    )

    answer_task = Task(
        description=(
            f"Answer this user question using Wikipedia research: {question}\n"
            "Use the Wikipedia Search tool with search_query set to relevant topics."
        ),
        expected_output=(
            "A thorough answer with key facts and the Wikipedia sources used."
        ),
        agent=answer_agent,
    )

    review_task = Task(
        description=(
            f"Review the answer to this user question: {question}\n"
            "Verify facts with Wikipedia when needed. Note any gaps or inaccuracies "
            "and provide a polished final answer."
        ),
        expected_output=(
            "A review with verified facts, issues found (if any), "
            "and a polished final answer."
        ),
        agent=reviewer_agent,
        context=[answer_task],
    )

    crew = Crew(
        agents=[answer_agent, reviewer_agent],
        tasks=[answer_task, review_task],
        process=Process.sequential,
        verbose=False,
    )

    result = crew.kickoff()
    tasks_output = result.tasks_output

    return {
        "question": question,
        "answer": tasks_output[0].raw if len(tasks_output) > 0 else None,
        "review": tasks_output[1].raw if len(tasks_output) > 1 else None,
        "final": result.raw,
    }
