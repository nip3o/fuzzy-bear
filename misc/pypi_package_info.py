from __future__ import division

import locale
locale.setlocale(locale.LC_ALL, '')

import re
import pytz
import datetime
import sys

import requests
import dateutil.parser

FRESH_LIMIT = datetime.timedelta(days=30)


class Matcher(object):
    def match(self, homepage, description):
        url_match = self.match_string(homepage) or self.match_string(description)

        if not url_match:
            return False

        self.repo_name = '{}/{}'.format(*url_match[0])
        return True


class Github(Matcher):
    name = 'Github'
    url_regex = re.compile(r'(?:https?)://(?:www\.)?github\.com/([\w-]+)/([\w-]+)/?')

    def match_string(self, string):
        return self.url_regex.findall(string)

    def get_features(self):
        repo_data = requests.get('https://api.github.com/repos/%s' % self.repo_name).json()

        return {
            'stars': repo_data['stargazers_count'],
            'watchers': repo_data['subscribers_count'],
        }

    def get_freshness(self):
        commit_list = requests.get('https://api.github.com/repos/%s/commits' %
                                   self.repo_name).json()
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)

        recent = sum(now - dateutil.parser.parse(entry['commit']['committer']['date']) < FRESH_LIMIT
                     for entry in commit_list)

        return (recent, len(commit_list))


class Bitbucket(Matcher):
    name = 'Bitbucket'
    url_regex = re.compile(r'(?:https?)://(?:www\.)?bitbucket\.(?:org|com)/([\w-]+)/([\w-]+)/?')

    def match_string(self, string):
        return self.url_regex.findall(string)

    def get_features(self):
        repo_data = requests.get('https://bitbucket.org/api/2.0/repositories/%s' %
                                 self.repo_name).json()
        watchers_url = repo_data['links']['watchers']['href']
        watchers_data = requests.get(watchers_url).json()

        return {'watchers': watchers_data['size']}

    def get_freshness(self):
        commit_data = requests.get('https://bitbucket.org/api/2.0/repositories/%s/commits' %
                                   self.repo_name).json()

        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        recent = sum(now - dateutil.parser.parse(commit['date']) < FRESH_LIMIT
                     for commit in commit_data['values'])

        return (recent, commit_data['pagelen'])


def get_info(package_name):
    pypi_response = requests.get('https://pypi.python.org/pypi/%s/json' % package_name)
    if pypi_response.status_code == 404:
        print ('Could not find package "{}". Note that package names are case-sensitive.'
               .format(package_name))
        return

    pypi_data = pypi_response.json()
    package_info = pypi_data['info']
    homepage = package_info['home_page']
    summary = package_info['summary']
    description = package_info['description']

    releases = pypi_data['releases'].values()
    total_downloads = 0

    for release in releases:
        for release_type in release:
            total_downloads += release_type['downloads']

    print '========== {} - {} =========='.format(package_name, summary)
    print '{:n} downloads in total'.format(total_downloads)

    for matcher in [Github(), Bitbucket()]:
        if matcher.match(homepage, description):
            features = ['{} {}'.format(value, feature_name)
                        for feature_name, value in matcher.get_features().items()]

            print '{} on {}'.format(', '.join(features), matcher.name)

            recent, total = matcher.get_freshness()
            print '{} out of the latest {} commits are within the last month.'.format(recent, total)


if __name__ == '__main__':
    print
    get_info(sys.argv[1])
    print
