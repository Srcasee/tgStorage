from app.metadata.classifier import ResourceClassifier


def test_resolution_tokens_do_not_classify_video_as_anime():
    classifier = ResourceClassifier()
    assert classifier.classify("Interstellar.2014.1080p.mkv", "video", ["2014", "1080p"]) == "视频"


def test_explicit_anime_keyword_classifies_as_anime():
    classifier = ResourceClassifier()
    assert classifier.classify("One.Piece.anime.1080p.mkv", "video", ["1080p"]) == "动漫"


def test_resolution_is_only_a_tag_when_no_explicit_category_matches():
    classifier = ResourceClassifier(rules=[])
    assert classifier.classify("movie.1080p.mkv", "unknown", ["1080p"]) is None
