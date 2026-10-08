from __future__ import annotations

from typing import NamedTuple
from assets.wordle.logic import evaluate_guess, STATUS_CORRECT

class TurnAnalysis(NamedTuple):
    guess: str
    possibilities_before: int
    possibilities_after: int
    words_eliminated: int
    elimination_pct: float
    remaining_candidates: list[str]
    skill_rating: str
    
    def to_list(self) -> list[str | int | float]:
        return [
            self.guess,
            self.possibilities_before,
            self.possibilities_after,
            self.words_eliminated,
            self.elimination_pct,
            self.skill_rating
        ]
    
    @staticmethod
    def get_headers() -> list[str]:
        return [
            "Guess",
            "Possibilities Before",
            "Possibilities After",
            "Words Eliminated",
            "Elimination Percentage",
            "Skill Rating"
        ]

class WordleAnalytics:
    """UI-Agnostic engine that tracks remaining candidate words after each guess."""
    
    def __init__(self, target_words: list[str]):
        self.all_targets = set(target_words)
        self.possible_words = list(target_words)
        self.history: list[TurnAnalysis] = []
        
    def reset(self):
        self.possible_words = list(self.all_targets)

    def analyze_turn(self, guess: str, target: str) -> TurnAnalysis:
        before_count = len(self.possible_words)
        statuses = evaluate_guess(guess, target)

        # Filter candidates: keep only words that would yield the exact same pattern
        new_possible = [
            word for word in self.possible_words
            if evaluate_guess(guess, word) == statuses
        ]

        after_count = len(new_possible)
        eliminated = before_count - after_count
        elimination_pct = (eliminated / before_count * 100) if before_count > 0 else 100.0

        # Assess guess strength
        if guess == target:
            rating = "Solution!"
        elif after_count == 1:
            rating = "Pinpointed!"
        elif elimination_pct >= 90.0:
            rating = "Excellent"
        elif elimination_pct >= 70.0:
            rating = "Solid"
        else:
            rating = "Risky"

        analysis = TurnAnalysis(
            guess=guess,
            possibilities_before=before_count,
            possibilities_after=after_count,
            words_eliminated=eliminated,
            elimination_pct=elimination_pct,
            remaining_candidates=new_possible,
            skill_rating=rating
        )

        self.possible_words = new_possible
        self.history.append(analysis)
        return analysis
    
    def analyze(self, all_guesses: list[str], target: str) -> list[TurnAnalysis]:
        all_analyses: list[TurnAnalysis] = []
        for i in range(len(all_guesses)):
            analysis: TurnAnalysis = self.analyze_turn(all_guesses[i], target)
            self.possible_words = analysis.remaining_candidates
            all_analyses.append(analysis)
        return all_analyses