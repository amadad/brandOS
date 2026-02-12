from brand_os.eval.rubric import parse_rubric


def test_parse_rubric_without_score_anchors_defaults_empty() -> None:
    rubric = parse_rubric(
        {
            "name": "test",
            "dimensions": [
                {
                    "name": "brand_voice",
                    "description": "Does it match the brand voice?",
                    "weight": 1.0,
                    "threshold": 0.7,
                    "criteria": ["Consistent tone"],
                }
            ],
        }
    )

    assert len(rubric.dimensions) == 1
    assert rubric.dimensions[0].name == "brand_voice"
    assert rubric.dimensions[0].score_anchors == {}


def test_parse_rubric_with_score_anchors_preserved() -> None:
    rubric = parse_rubric(
        {
            "name": "test",
            "dimensions": [
                {
                    "name": "brand_voice",
                    "description": "Does it match the brand voice?",
                    "score_anchors": {
                        "1": "Bad",
                        3: "OK",
                        "5": "Great",
                    },
                }
            ],
        }
    )

    assert len(rubric.dimensions) == 1
    assert rubric.dimensions[0].name == "brand_voice"
    assert rubric.dimensions[0].score_anchors == {1: "Bad", 3: "OK", 5: "Great"}
