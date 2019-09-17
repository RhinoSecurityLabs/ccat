#!/usr/bin/env python3
import json
import sys
import pathlib

import fire
import docker


DOCKER_BASE_URL = 'unix:///var/run/docker.sock'
DOCKER_LOGIN_SUCCEEDED = 'Login Succeeded'
DOCKER_USERNAME = '_json_key'


module_info = {
    'name': 'gcr__pull_repos',
    'author': 'Jack Ganbold of Rhino Security Labs',
    'category': 'Container',
    'one_liner': 'Pulls GCR repositories.',
    'description': 'Pulls GCR repositories.',
    'services': ['GCR'],
    'prerequisite_modules': [],
    'external_dependencies': [],
    'arguments_to_autocomplete': [],
}


def get_sa_key(path):
    with open(path) as json_file:
        sa_key_json = json.load(json_file)

    return json.dumps(sa_key_json, default=str)


def get_registry(repository_uri):
    print(repository_uri)
    registry_split= repository_uri.split('/')
    docker_registry = 'https://' + registry_split[0]
    return docker_registry


def docker_login(docker_client ,username, password, docker_registry):
    login_response = docker_client.login(username, password, registry=docker_registry)
    return login_response

def docker_pull_all(args, data):
    try:
        docker_client = docker.DockerClient(base_url=DOCKER_BASE_URL)
        docker_password = get_sa_key(args.get('service_account_json_file_path'))
        
        count = 0
        for repo in args.get('repositories'):
            try:
                docker_registry = get_registry(repo)
                docker_login_response = docker_login(docker_client, DOCKER_USERNAME, docker_password, docker_registry)
                if DOCKER_LOGIN_SUCCEEDED == docker_login_response.get('Status'):
                    for line in docker_client.images.pull(repo, stream=True)
                        print(json.dumps(json.loads(line), indent=4, default=str))
                    
                    data['payload']['repositories'].append(repo)
                    count += 1
                    print(out)
                else:
                    print('login failed')
            except Exception as e:
                print(e, file=sys.stderr)

        data['count'] = count
        data['payload']['registry'] = docker_registry

    except Exception as e:
        print(e, file=sys.stderr)


def gcr_pull(docker_client,repo, data):
        docker_pull_response = docker_client.images.pull(repo)
        out = 'Pulled {}'.format(docker_pull_response)
        print(out)

def docker_pull(args, data):
    try:
        docker_client = docker.DockerClient(base_url=DOCKER_BASE_URL)
        docker_password = get_sa_key(args.get('service_account_json_file_path'))
        docker_registry = get_registry(args.get('repositories')[0])
        docker_login_response = docker_login(docker_client, DOCKER_USERNAME, docker_password, docker_registry)

        if DOCKER_LOGIN_SUCCEEDED == docker_login_response.get('Status'):
            count = 0
            if args.get('repository_tags') is not None and len(args.get('repository_tags')) >= 1:
                for tag in args.get('repository_tags'):
                    repo = args.get('repositories')[0] + ':' + tag
                    try:
                        gcr_pull(docker_client, repo, data)
                        data['payload']['repository_tags'].append(tag)
                        count += 1
                    except Exception as e:
                        print(e, file=sys.stderr)
            else:
                try:
                    repo = args.get('repositories')[0]
                    gcr_pull(docker_client, repo, data)
                    count += 1
                 except Exception as e:
                    print(e, file=sys.stderr)

        data['count'] = count
        data['payload']['repositories'] = args.get('repositories')
        data['payload']['registry'] = docker_registry

    except Exception as e:
        print(e, file=sys.stderr)


def main(args):
    data  = {
        'count': 0,
        'payload': {
            'registry': None,
            'repositories': [],
            'repository_tags': []
        }
    }
    
    docker_pull(args, data)

    return data


def set_args(service_account_json_file_path, repositories, repository_tags=None):
    # check the existence of service account json file
    path = pathlib.Path(service_account_json_file_path)
    if path.exists() is False:
        print("Service account json file does not exist")
        sys.exit(1)

    args = {
        'service_account_json_file_path': service_account_json_file_path,
        'repositories': repositories,
        'repository_tags': repository_tags
    }

    return args


def summary(data):
    out = ''
    out += '{} GCR Repositories Pulled\n'.format(data['count']) 
    out += 'GCR resources saved and use \'docker images\' command to check the result.\n'
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
        
        print('RESULT:')
        print(json.dumps(data, indent=4, default=str))        

        print('{} completed.\n'.format(module_info['name']))
        print('MODULE SUMMARY:\n\n{}\n'.format(summary.strip('\n')))
