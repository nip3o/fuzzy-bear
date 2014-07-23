from __future__ import division

import re
import pytz
import datetime
import sys

import requests
import dateutil.parser

GITHUB_URL = re.compile(r'(?:https?)://(?:www\.)?github\.com/(\w+)/([\w-]+)/?')


def get_info(name):
    pypi_data = requests.get('https://pypi.python.org/pypi/%s/json' % name).json()

    package_info = pypi_data['info']
    homepage = package_info['home_page']
    summary = package_info['summary']
    description = package_info['description']

    releases = pypi_data['releases'].values()
    total_downloads = 0

    for release in releases:
        for release_type in release:
            total_downloads += release_type['downloads']

    print '========== %s - %s ==========' % (name, summary)
    print '%d downloads in total' % total_downloads

    github_url_match = GITHUB_URL.findall(homepage) or GITHUB_URL.findall(description)

    if github_url_match:
        github_user, github_repo = github_url_match[0]
        repo_name = '%s/%s' % (github_user, github_repo)
        repo_data = requests.get('https://api.github.com/repos/%s' % repo_name).json()

        stars = repo_data['stargazers_count']
        watchers = repo_data['subscribers_count']
        print '%d stars, %d watchers' % (stars, watchers)

        commit_list = requests.get('https://api.github.com/repos/%s/commits' % repo_name).json()
        recent_commits = 0
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)

        for commit_data in commit_list:
            date_string = commit_data['commit']['committer']['date']
            dt = dateutil.parser.parse(date_string)

            if now - dt < datetime.timedelta(days=30):
                recent_commits += 1

        print '%d out of the latest %d commits are within the last month.' % (recent_commits, len(commit_list))


def main():
    get_info(sys.argv[1])
    print


if __name__ == '__main__':
    main()
