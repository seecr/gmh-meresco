from meresco.dans.storagesplit import Md5HashDistributeStrategy, md5Split, md5Join


def test_split():
    for split_function in [Md5HashDistributeStrategy.split, md5Split]:
        result = split_function(("identifier", "partname"))
        assert result == ["identifier", "partname"]
        result = split_function(("identifier:subpart", "partname"))
        assert result == ["identifier", "81", "ed", "subpart", "partname"]

        result = split_function((b"identifier:subpart", "partname"))
        assert result == ["identifier", "81", "ed", "subpart", "partname"]
        result = split_function(("identifier:subpart", b"partname"))
        assert result == ["identifier", "81", "ed", "subpart", "partname"]
        result = split_function((b"identifier:subpart", b"partname"))
        assert result == ["identifier", "81", "ed", "subpart", "partname"]

        assert split_function(("tue:oai:library.tue.nl:692605", "metadata")) == [
            "tue",
            "ff",
            "fa",
            "oai:library.tue.nl:692605",
            "metadata",
        ]


def test_join():
    for join_function in [Md5HashDistributeStrategy.join, md5Join]:
        assert join_function(
            ["tue", "ff", "fa", "oai:library.tue.nl:692605", "metadata"]
        ) == ("tue:oai:library.tue.nl:692605", "metadata")
