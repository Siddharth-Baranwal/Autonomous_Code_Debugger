from __future__ import annotations

# Prompt template used to ask the LLM for debugging guidance.
DEBUG_PROMPT = """
You are an autonomous debugging assistant.
Review the error and the retrieved code.
Error: {error}
Relevant code:
{code}
Explain the likely bug and recommend the next debugging step.
"""
