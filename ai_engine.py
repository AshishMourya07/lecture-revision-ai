import os
from dotenv import load_dotenv
from google import genai
from models import LectureRevisionPack, AnswerEvaluation, RevisionQA

load_dotenv()

MODEL_NAME = "gemini-3.8-flash"

def get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found! Please check your .env file.")
    return genai.Client(api_key=api_key)

def generate_revision_pack(transcript_text: str) -> LectureRevisionPack:
    client = get_client()

    prompt = f"""
    You are an expert university professor and exam-prep coach.
    Analyze the timestamped lecture transcript below and create a high-yield Student Revision Pack.

    STRICT RULES:
    1. Generate 10-12 questions covering the entire lecture chronologically:
       - 3 MCQs (with 4 realistic options)
       - 3 Short_2_Marks questions (core definitions/facts)
       - 3 Deep_5_Marks questions (conceptual 'why/how' explanations)
       - 2 Viva_Question items (practical/interview oral questions)
    2. Every question MUST include a complete, exam-ready `model_answer` and 3-4 `key_points`.
    3. Use the EXACT `[MM:SS (seconds)]` from the transcript where that concept starts for `timestamp_str` and `timestamp_seconds`.

    LECTURE TRANSCRIPT:
    {transcript_text}
    """

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": LectureRevisionPack,
            "temperature": 0.25,
        },
    )
    return LectureRevisionPack.model_validate_json(response.text)

def evaluate_student_answer(qa: RevisionQA, student_answer: str) -> AnswerEvaluation:
    client = get_client()

    prompt = f"""
    You are a supportive but rigorous exam grader.
    Compare the student's written answer against the lecture's model answer and key points.

    Question ({qa.question_type}): {qa.question}
    Official Model Answer: {qa.model_answer}
    Required Key Points: {", ".join(qa.key_points)}

    Student's Written Answer:
    "{student_answer}"

    Grade the student fairly out of 10, highlight what they got right, and list which specific key points they missed.
    """

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": AnswerEvaluation,
            "temperature": 0.2,
        },
    )
    return AnswerEvaluation.model_validate_json(response.text)