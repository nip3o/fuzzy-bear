import pytest

from pypi_package_info import Github, Bitbucket


@pytest.fixture
def github():
    return Github()


@pytest.fixture
def bitbucket():
    return Bitbucket()


class Test_Github:
    class Test_match_string:
        @pytest.mark.parametrize(['string'], [
            ['http://github.com/user/repo/'],
            ['https://github.com/user/repo'],
            ['https://www.github.com/user/repo/'],
            ['foo\nhttp://github.com/user/repo/bar.\n'],
        ])
        def test_should_match(self, github, string):
            assert github.match_string(string) == [('user', 'repo')]

        def test_should_not_match(self, github):
            assert github.match_string('http://github.com/user/') == []

        def test_hyphens(self, github):
            assert github.match_string('https://github.com/some-user/some-repo') == [('some-user',
                                                                                      'some-repo')]


class Test_Bitbucket:
    class Test_match_string:
        @pytest.mark.parametrize(['string'], [
            ['https://bitbucket.org/user/repo/'],
            ['http://bitbucket.com/user/repo'],
            ['https://bitbucket.org/user/repo/'],
            ['foo\nhttps://bitbucket.org/user/repo/bar.\n'],
        ])
        def test_should_match(self, bitbucket, string):
            assert bitbucket.match_string(string) == [('user', 'repo')]

        def test_should_not_match(self, bitbucket):
            assert bitbucket.match_string('https://bitbucket.org/user') == []

        def test_hyphens(self, bitbucket):
            assert bitbucket.match_string('http://bitbucket.org/some-user/some-repo') == [('some-user',
                                                                                           'some-repo')]

    class Test_match:
        def test_match_in_homepage(self, bitbucket):
            result = bitbucket.match(homepage='http://bitbucket.org/user/repo/',
                                     description='')
            assert result is True
            assert bitbucket.repo_name == 'user/repo'

        def test_match_in_description(self, bitbucket):
            result = bitbucket.match(homepage='',
                                     description='Repo: http://bitbucket.org/user/repo/issues.')
            assert result is True
            assert bitbucket.repo_name == 'user/repo'
