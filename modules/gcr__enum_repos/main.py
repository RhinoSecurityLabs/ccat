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
DOCKER_USERNAME_JSON_KEY = '_json_key'
DOCKER_USERNAME_ACCESS_TOKEN = 'oauth2accesstoken'
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

    return json.dumps(sa_key_json, default=str)


def docker_configure_username_password(args):
    if args.get('service_account_json_file_path'):
        service_account_json_file_path = args.get('service_account_json_file_path')
        docker_password = get_sa_key(service_account_json_file_path)
        args.update({
            'docker_username': DOCKER_USERNAME_JSON_KEY,
            'docker_password': docker_password
        })
    elif args.get('access_token'):
        args.update({
            'docker_username': DOCKER_USERNAME_ACCESS_TOKEN,
            'docker_password': args.get('access_token')
        })


def save_to_file(data):
    os.makedirs(SAVE_TO_FILE_DIRECTORY, exist_ok=True)
    with open(SAVE_TO_FILE_PATH, 'w+') as json_file:
        json.dump(data, json_file, indent=4, default=str)  


def enum_repos(args, data):
    total = 0

    docker_username = args.get('docker_username')
    docker_password = args.get('docker_password')
    registries = args.get('gcp_registries')

    try:

        for registry in registries:
            url_repos = DOCKER_REGISTRY_REPOS_URL.format(registry)
            url_repos_response = requests.get(url_repos, auth=(docker_username, docker_password))
            if(url_repos_response.status_code == 401):
                print('401 Unauthorized')
                continue
            
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
                    url_repo_tags_reponse = requests.get(url_repo_tags, auth=(docker_username, docker_password))
                    tags = json.loads(url_repo_tags_reponse.text).get('tags')
                    
                    if len(tags) != 0:
                        repos_temp.append({
                            'repositoryName': repo,
                            'repositoryUri': '{}/{}'.format(registry,repo),
                            'tags': tags,
                        })

                count = len(repos)
                out = "Found {} repositories in {}".format(count, registry)
                print(out)
                total += count

    except Exception as e:
        print(e, file=sys.stderr)

    data['count'] = total


#python main.py path_to_service_account_json_file
def set_args(service_account_json_file_path=None, access_token=None, gcp_registries=[]):

    if service_account_json_file_path is not None:
        # check the existence of service account json file
        path = pathlib.Path(service_account_json_file_path)
        if path.exists() is False:
            print("Service account json file does not exist")
            sys.exit(1)

    args = {
        'service_account_json_file_path': service_account_json_file_path,
        'access_token': access_token,
        'gcp_registries': gcp_registries
    }

    return args


def main(args):
    data  = {
        'count': 0,
        'payload': {
            'gcp_registries': [],
            'repositories_by_registry': {}
        }
    }

    docker_configure_username_password(args)
    enum_repos(args, data)
    save_to_file(data)

    return data


def summary(data):
    out = ''
    out += '{} GCR Repositories Enumerated\n'.format(data['count'])
    out += 'GCR recources saved under the {} path.\n'.format(SAVE_TO_FILE_PATH)
    return out


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