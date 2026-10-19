from typing import List, Literal
from pydantic import BaseModel, Field

class RevisionQA(BaseModel):
    topic: str = Field(description="Concept or sub-topic name")
    question_type: Literal["MCQ", "Short_2_Marks", "Deep_5_Marks", "Viva_Question"]
    difficulty: Literal["Easy", "Medium", "Hard"]
    question: str = Field(description="The exam or revision question")
    options: List[str] = Field(
        default=[],
        description="Provide 4 options ONLY if question_type is MCQ, else empty list []"
    )
    model_answer: str = Field(description="Complete, well-structured exam answer")
    key_points: List[str] = Field(description="3 to 4 bullet points the student must remember")
    timestamp_str: str = Field(description="Exact MM:SS where the lecturer explains this")
    timestamp_seconds: int = Field(description="Exact start time in integer seconds")

class LectureRevisionPack(BaseModel):
    lecture_title: str = Field(description="Inferred title/topic of the lecture")
    executive_summary: List[str] = Field(description="5 high-impact summary bullet points")
    formulas_and_definitions: List[str] = Field(description="Key formulas, dates, or definitions")
    questions_and_answers: List[RevisionQA] = Field(description="10 to 12 diverse exam questions")

class AnswerEvaluation(BaseModel):
    score_out_of_10: int = Field(description="Score from 0 to 10")
    verdict: Literal["Excellent", "Good - Missing Details", "Needs Revision"]
    what_you_got_right: str
    what_you_missed: List[str] = Field(description="Specific points from the model answer missed by the student")
    improved_answer_tip: str = Field(description="1-sentence tip to write a better answer in the exam")