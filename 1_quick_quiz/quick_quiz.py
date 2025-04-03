# quiz game where the script interactively asks the user questions
# the questions may be open-ended or multiple choice
# a final score is presented with the number of correct answers

# basic oop principles, encapsulation, and input validation makes
# this code more robust, maintainable, and scalable than
# the inspiration:
# https://github.com/techwithtim/5-Python-Projects-For-Beginners/blob/main/quiz_game.py

from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class ResponseSettings:
    correct_reponse: Optional[str] = "Correct!"
    incorrect_response: Optional[str] = "Incorrect."
    max_attempts: Optional[int] = 1
    correct_points: Optional[int] = 1


@dataclass
class QuizQuestion:
    question: str
    correct_answer: str
    answer: str = field(init=False)
    transformation_name: Optional[str] = "title"
    transformation: Callable[[str], str] = field(init=False)
    response_settings: ResponseSettings = field(default_factory=ResponseSettings)

    def __post_init__(self) -> None:
        self.set_transformation(self.transformation_name)
        self._attempt_count = 0
        self.answer = None

    def prompt_question(self) -> None:
        self.answer = input(f"{self.question}\n> ")

    @property
    def is_correct_answer(self) -> bool:
        return self.transform(self.answer) == self.transform(self.correct_answer)

    @property
    def attempt_count(self) -> int:
        return self._attempt_count

    def increment_attempts(self):
        self._attempt_count += 1

    def set_transformation(self, transformation_name: str) -> None:
        """Set the transformation function based on a string identifier."""
        transformations = {
            "title": str.title,
            "upper": str.upper,
            "lower": str.lower,
            "capitalize": str.capitalize,
            "swapcase": str.swapcase,
        }
        if transformation_name in transformations:
            self.transformation_name = transformation_name
            self.transformation = transformations[transformation_name]
        else:
            raise ValueError(f"Invalid transformation: {transformation_name}")

    def transform(self, text: str) -> str:
        """Apply the selected transformation to the input text."""
        return self.transformation(text)

    def validate_response(self):
        if not self.correct_answer:
            raise ValueError(f"No correct answer provided for {self.question}")
        if not self.answer:
            raise ValueError(f"No answer provided for {self.question}")
        return True

    def print_question_header(self, question_number: int = None):
        if self.attempt_count == 0:
            question_header = ""
            if question_number:
                self.question = f"{question_number}. {self.question}"
            print(f"{question_header}")

    def handle_question_and_answer(self, question_number: int = None) -> None:
        self.print_question_header(question_number)
        self.prompt_question()
        self.increment_attempts()
        is_valid_response = self.validate_response()
        max_attempts = self.response_settings.max_attempts
        while not is_valid_response and self.attempt_count < max_attempts:
            self.prompt_question()
            self.increment_attempts()
            is_valid_response = self.validate_response()
        if not is_valid_response and self.attempt_count == max_attempts:
            print(
                f"Maximum number of attempts ({max_attempts}) reached for this question"
            )
        if self.is_correct_answer:
            print(f"{self.response_settings.correct_reponse}")
        else:
            print(f"{self.response_settings.incorrect_response}")


@dataclass
class MultipleChoiceQuizQuestion(QuizQuestion):
    options: Optional[list[tuple[str, str]]] = field(default=None)

    def __post_init__(self):
        self.response_settings.max_attempts = 3
        return super().__post_init__()

    @property
    def valid_possible_answers(self):
        return [self.transform(option[0]) for option in self.options]

    def add_option(self, option_item: tuple[str, str]) -> None:
        if not self.options:
            self.options = []
        self.options.append((option_item[0], option_item[1]))

    def prompt_question(self) -> None:
        if not self.options:
            super().prompt_question()
        question_with_options = f"{self.question}\n" + "\n".join(
            [f"  {item[0]}: {item[1]}" for item in self.options]
        )
        self.answer = input(f"{question_with_options}\n> ")

    def validate_response(self) -> bool:
        if not self.correct_answer:
            raise ValueError(f"No correct answer provided for {self.question}")
        if not self.answer:
            raise ValueError(f"No answer provided for {self.question}")
        if not self.options:
            super().validate_response()
        if self.correct_answer not in self.valid_possible_answers:
            raise ValueError("Correct answer is not available")
        if self.transform(self.answer) not in self.valid_possible_answers:
            print(
                f"'{self.answer}' is not a valid answer. Expecting one of the following: {self.valid_possible_answers}. {self.response_settings.max_attempts - self.attempt_count} attempts remaining."
            )
            return False
        return True


@dataclass
class SimpleQuiz:
    score: int = 0
    _questions = None

    def startup(self) -> bool:
        print("Welcome to my computer quiz!")

        response_settings = ResponseSettings(
            correct_reponse="Great! Let's play :)",
            incorrect_response="Another time then! Goodbye :)",
            max_attempts=2,
            correct_points=0,
        )
        question = MultipleChoiceQuizQuestion(
            "Do you want to play?", "Y", response_settings=response_settings
        )
        question.add_option(("Y", "Yes"))
        question.add_option(("N", "No"))
        question.handle_question_and_answer()

        return question.is_correct_answer

    @property
    def questions(self) -> list[QuizQuestion]:
        return self.get_list_of_questions()

    def get_list_of_questions(self) -> list[QuizQuestion]:
        return [
            QuizQuestion(
                question="What does CPU stand for?",
                correct_answer="Central Processing Unit",
            ),
            QuizQuestion(
                question="What does RAM stand for?",
                correct_answer="Random Access Memory",
            ),
            QuizQuestion(
                question="What does GPU stand for?",
                correct_answer="Graphics Processing Unit",
            ),
            MultipleChoiceQuizQuestion(
                question="Which answer is A?",
                correct_answer="A",
                options=[("A", "Answer A"), ("B", "Answer B")],
            ),
        ]

    def start_quiz(self):
        for num, question in enumerate(self.questions):
            question.handle_question_and_answer(num + 1)
            self.update_score(question=question)

    def update_score(self, question):
        if question.is_correct_answer:
            self.score += question.response_settings.correct_points

    def display_score(self) -> None:
        print(f"\nScore: {self.score} / {len(self.questions)}")


def main():
    quiz = SimpleQuiz()
    if quiz.startup():
        quiz.start_quiz()
        quiz.display_score()


if __name__ == "__main__":
    main()
