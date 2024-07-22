import pytest
from pandas import DataFrame
from fuzzywuzzy import fuzz
from unittest.mock import MagicMock

# Assuming the class containing match_columns is named CSVRewriter
from CSVRewriter.CSVRewriter import CSVRewriter

@pytest.mark.parametrize(
    "headers_from_file, correct_headers, expected_output, expected_prints",
    [
        # Happy path tests
        (["name", "age"], ["name", "age"], ["name", "age"], ["name : Valid", "age : Valid"]),
        (["Name", "Age"], ["name", "age"], ["name", "age"], ["Name >> name", "Age >> age"]),
        
        # Edge cases
        (["nme", "ag"], ["name", "age"], ["name", "age"], ["nme >> name", "ag >> age"]),
        ([""], ["name", "age"], [""], []),
        (["name", "age", "gender"], ["name", "age"], ["name", "age", "gender"], ["name : Valid", "age : Valid"]),
        
        # Error cases
        (["unknown"], ["name", "age"], ["unknown"], []),
        (["name", "unknown"], ["name", "age"], ["name", "unknown"], ["name : Valid"]),
    ],
    ids=[
        "exact_match",
        "case_insensitive_match",
        "fuzzy_match",
        "empty_header",
        "extra_header",
        "no_match",
        "partial_match"
    ]
)
def test_match_columns(headers_from_file, correct_headers, expected_output, expected_prints, capsys):
    
    # Arrange
    csv_rewriter = CSVRewriter("imput.csv", ["1","2","3"])
    csv_rewriter.get_and_clean_headers = MagicMock(return_value=headers_from_file)
    csv_rewriter.correct_headers = correct_headers

    # Act
    result = csv_rewriter.match_columns()

    # Assert
    assert result == expected_output
    captured = capsys.readouterr()
    for expected_print in expected_prints:
        assert expected_print in captured.out

