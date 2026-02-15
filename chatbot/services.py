import time


def generate_subject_response(subject_name, question):
    """
    Rule-based chatbot.
    Replace with OpenAI / ML model later.
    """

    print(f"[CHATBOT LOG] Subject: {subject_name}")
    print(f"[CHATBOT LOG] Question: {question}")

    question_lower = question.lower()

    # Simulated response delay
    time.sleep(0.3)

    if "area" in question_lower and subject_name.lower() == "mathematics":
        return "The area of a circle is calculated using πr²."

    if "force" in question_lower:
        return "Force is calculated using Newton's Second Law: F = m × a."

    if "cell" in question_lower:
        return "Cells are the fundamental structural and functional units of life."

    if "logic" in question_lower:
        return "Logical reasoning involves identifying structured patterns and relationships."

    return "That is a thoughtful question. Continue practicing and reviewing the concept for mastery."
