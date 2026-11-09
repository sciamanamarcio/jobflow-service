from app.analysis import analyze_text


def test_counts_words_sentences_and_characters():
    result = analyze_text("Hello world. Hello again!")

    assert result["words"] == 4
    assert result["unique_words"] == 3
    assert result["sentences"] == 2
    assert result["characters"] == 25


def test_top_words_sorted_by_frequency_then_alphabetically():
    result = analyze_text("b a b a c", top_n=2)

    assert result["top_words"] == [{"word": "a", "count": 2}, {"word": "b", "count": 2}]


def test_is_case_insensitive():
    result = analyze_text("Python python PYTHON")

    assert result["unique_words"] == 1
    assert result["top_words"][0] == {"word": "python", "count": 3}


def test_reading_time_uses_200_words_per_minute():
    result = analyze_text("word " * 200)

    assert result["reading_time_seconds"] == 60
