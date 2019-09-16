#!/usr/bin/env python3
import os
import json
import sys
import requests
import pathlib


import fire
import docker


# TODO: Get docker registries dynamicly

SAVE_TO_FILE_DIRECTORY = './data'
SAVE_TO_FILE_PATH = '{}/gcr__enum_repos_data.json'.format(SAVE_TO_FILE_DIRECTORY)
DOCKER_BASE_URL = 'unix:///var/run/docker.sock'
DOCKER_LOGIN_SUCCEEDED = 'Login Succeeded'
DOCKER_USERNAME = '_json_key'
DOCKER_REGISTRY_REPOS_URL = 'https://{}/v2/_catalog'
DOCKER_REGISTRY_REPOS_TAGS_URL = 'https://{}/v2/{}/tags/list'


module_info = {
    'name': 'gcr__enum_repos',
    'author': 'Jack Ganbold of Rhino Security Labs',
    'category': 'ENUM',
    'one_liner': 'Enumerates GCR repositories.',
    'description': 'Enumerates GCR repositories.',
    'services': ['GCR'],
    'prerequisite_modules': [],
    'external_dependencies': [],
    'arguments_to_autocomplete': [],
    'data_saved': SAVE_TO_FILE_PATH
}


def get_sa_key(path):
    with open(path) as json_file:
        sa_key_json = json.load(json_file)

    return sa_key_json


def save_to_file(data):
    os.makedirs(SAVE_TO_FILE_DIRECTORY, exist_ok=True)
    with open(SAVE_TO_FILE_PATH, 'w+') as json_file:
        json.dump(data, json_file, indent=4, default=str)  


def enum_repos(service_account_json_file_path, registries, data):
    total = 0

    try:
        docker_password = json.dumps(get_sa_key(service_account_json_file_path))

        for registry in registries:
            url_repos = DOCKER_REGISTRY_REPOS_URL.format(registry)
            url_repos_response = requests.get(url_repos, auth=(DOCKER_USERNAME, docker_password))
        
            repos = json.loads(url_repos_response.text).get('repositories')
            repos_temp = []

            if len(repos) != 0:
                data['payload']['gcp_registries'].append(registry)
                data['payload']['repositories_by_registry'].update({
                    registry: repos_temp
                })

                # append tags
                for repo in repos:
                    url_repo_tags = DOCKER_REGISTRY_REPOS_TAGS_URL.format(registry, repo)
                    url_repo_tags_reponse = requests.get(url_repo_tags, auth=(DOCKER_USERNAME, docker_password))
                    tags = json.loads(url_repo_tags_reponse.text).get('tags')
                    
                    if len(tags) != 0:
                        repos_temp.append({
                            'repositoryName': repo,
                            'repositoryUri': 'https://{}/{}'.format(registry,repo),
                            'tags': tags,
                        })

                count = len(repos)
                out = "Found {} repositories in {}".format(count, registry)
                print(out)
                total += count

    except Exception as e:
        print(e, file=sys.stderr)

    data['count'] = total


def main(args):
    data  = {
        'count': 0,
        'payload': {
            'gcp_registries': [],
            'repositories_by_registry': {}
        }
    }
    
    enum_repos(args.get('service_account_json_file_path'), args.get('gcp_registries'),data)
    save_to_file(data)
    # print(json.dumps(data, indent=4, default=str))

    return data


def summary(data):
    out = ''
    out += '{} GCR Repositories Enumerated\n'.format(data['count'])
    out += 'GCR recources saved under the {} path.\n'.format(SAVE_TO_FILE_PATH)
    return out


#python main.py path_to_service_account_json_file
def set_args(service_account_json_file_path):
    # check the existence of service account json file
    path = pathlib.Path(service_account_json_file_path)
    if path.exists() is False:
        print("Service account json file does not exist")
        sys.exit(1)

    args = {
        'service_account_json_file_path': service_account_json_file_path
    }

    return args


if __name__ == "__main__":
    print('Running module {}...'.format(module_info['name']))

    args = fire.Fire(set_args)
    data = main(args)

    if data is not None:
        summary = summary(data)
        if len(summary) > 1000:
            raise ValueError('The {} module\'s summary is too long ({} characters). Reduce it to 1000 characters or fewer.'.format(module_info['name'], len(summary)))
        if not isinstance(summary, str):
            raise TypeError(' The {} module\'s summary is {}-type instead of str. Make summary return a string.'.format(module_info['name'], type(summary)))
        
        print('{} completed.\n'.format(module_info['name']))
        print('MODULE SUMMARY:\n\n{}\n'.format(summary.strip('\n')))  