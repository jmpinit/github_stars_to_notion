#!/usr/bin/env python3

import sys
import os.path
import requests
import yaml
import json
from notion.client import NotionClient

# For testing use star cache to avoid GitHub rate limit
DEBUG_USE_CACHE = False


def gh_query(query, token):
    """Run a GraphQL query against the GitHub API using the given access token"""
    headers = {'Authorization': f'Bearer {token}'}
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)

    if request.status_code == 200:
        return request.json()
    else:
        raise Exception('Query failed to run by returning code of {}. {}'.format(request.status_code, query))


def get_stars(user, token):
    """Return a list of the name, description, and URL for each star of the given user"""
    stars = []

    end_cursor = None
    while True:
        after_clause = ''

        if end_cursor:
            after_clause = f', after: "{end_cursor}"'

        result = gh_query(f"""
        {{
            user(login: "{user}") {{
                starredRepositories(first: 100{after_clause}) {{
                    pageInfo {{
                        hasNextPage
                        endCursor
                    }}
                    edges {{
                        node {{
                            name
                            url
                            description
                        }}
                    }}
                }}
            }}
        }}
        """, token)

        edges = result['data']['user']['starredRepositories']['edges']

        for node in edges:
            stars.append(node['node'])

        page_info = result['data']['user']['starredRepositories']['pageInfo']
        if not page_info['hasNextPage']:
            # No more data to retrieve
            break

        end_cursor = page_info['endCursor']

    return stars


def sync_star_table(url, token, stars, delete=False, name_col_name='Name', url_col_name='URL', description_col_name='Description'):
    """Sync the list of stars with name, description, and URL to the given Notion table

    - If delete is True then rows in the Notion table which do not correspond to a star will be removed
    - The names of the columns can optionally be specified
    """
    client = NotionClient(token_v2=token)
    cv = client.get_collection_view(url)

    rows_by_url = {}
    for row in cv.collection.get_rows():
        if len(getattr(row, url_col_name)) == 0:
            print('Warning: skipping row with empty URL')
            continue

        if getattr(row, url_col_name) in rows_by_url:
            print(f'Warning: found duplicate row for {getattr(row, url_col_name)}')
            continue

        rows_by_url[row.url] = row

    for star in stars:
        if star['url'] not in rows_by_url:
            new_row = cv.collection.add_row()
            setattr(new_row, name_col_name, star['name'])
            setattr(new_row, description_col_name, star['description'])
            setattr(new_row, url_col_name, star['url'])

            print(f'Added new row for {star["name"]}')

    if delete:
        stars_by_url = {}
        for star in stars:
            stars_by_url[star['url']] = star

        for url, row in rows_by_url.items():
            if url not in stars_by_url:
                row.remove()
                print(f'Deleted row for {row[name_col_name]}')


def load_config(config_file_path):
    """Load and validate a configuration file containing user information"""
    if not os.path.isfile(config_file_path):
        raise Exception('config.yml file missing')

    config = yaml.safe_load(open(config_file_path, 'r'))

    # Validate configuration

    if 'github' not in config:
        raise Exception('Missing GitHub section in config')

    if 'username' not in config['github']:
        raise Exception('Missing GitHub username in config')

    if 'token' not in config['github']:
        raise Exception('Missing GitHub token in config')

    if 'notion' not in config:
        raise Exception('Missing Notion section in config')

    if 'token_v2' not in config['notion']:
        raise Exception('Missing Notion token_v2 in config')

    if 'table_url' not in config['notion']:
        raise Exception('Missing Notion table_url in config')

    return config


def main():
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} config.yml')
        sys.exit(1)

    config_path = sys.argv[1]
    config = load_config(config_path)

    gh_username = config['github']['username']
    gh_token = config['github']['token']

    print('Retrieving stars for GitHub user {}'.format(gh_username))

    if not DEBUG_USE_CACHE:
        stars = get_stars(gh_username, gh_token)
    else:
        # Load stars from cache file if available,
        # otherwise retrieve from GitHub and write to cache
        if os.path.isfile('stars.json'):
            with open('stars.json', 'r') as stars_file:
                stars = json.load(stars_file)

            print('Loaded stars from cache')
        else:
            stars = get_stars(gh_username, gh_token)

            with open('stars.json', 'w') as stars_file:
                json.dump(stars, stars_file)

            print('Cached stars')

    print('Syncing stars to Notion table')
    n_table = config['notion']['table_url']
    n_token = config['notion']['token_v2']
    sync_star_table(n_table, n_token, stars)


if __name__ == '__main__':
    main()
