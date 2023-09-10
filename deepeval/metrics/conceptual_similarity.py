"""Asserting conceptual similarity
"""
from typing import Optional

from ..singleton import Singleton
from ..test_case import LLMTestCase
from ..utils import cosine_similarity
from .metric import Metric


class ConceptualSimilarityMetric(Metric, metaclass=Singleton):
    """basic implementation of BertScoreMetric"""

    def __init__(
        self,
        model_name: Optional[str] = "sentence-transformers/all-mpnet-base-v2",
        minimum_score: float = 0.7,
    ):
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self.model = SentenceTransformer(self.model_name).eval()
        self.minimum_score = minimum_score

    def _vectorize(self, text_a: str, text_b: str):
        vectors = self.model.encode([text_a, text_b])
        return vectors

    def measure(self, test_case: LLMTestCase) -> float:
        if test_case.output is None or test_case.expected_output is None:
            raise ValueError("Output or expected_output cannot be None")

        vectors = self._vectorize(test_case.output, test_case.expected_output)
        self.score = cosine_similarity(vectors[0], vectors[1])
        self.log(
            success=self.is_successful(),
            score=self.score,
            metric_name="Conceptual Similarity With Ground Truth",
            output=test_case.output,
            expected_output=test_case.expected_output,
        )
        return float(self.score)

    def is_successful(self) -> bool:
        return bool(self.score >= self.minimum_score)


def assert_conceptual_similarity(
    output: str, expected_output: str, minimum_score=0.3
):
    metric = ConceptualSimilarityMetric(minimum_score=minimum_score)
    test_case = LLMTestCase(output=output, expected_output=expected_output)
    score = metric.measure(test_case)
    assert (
        metric.is_successful()
    ), f"Metric is not conceptually similar - got {score}"
