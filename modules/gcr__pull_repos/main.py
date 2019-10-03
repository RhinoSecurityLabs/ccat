#!/usr/bin/env python3
import json
import sys
import pathlib

import fire
import docker


DOCKER_BASE_URL = 'unix:///var/run/docker.sock'
DOCKER_LOGIN_SUCCEEDED = 'Login Succeeded'
DOCKER_USERNAME_JSON_KEY = '_json_key'
DOCKER_USERNAME_ACCESS_TOKEN = 'oauth2accesstoken'


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


def docker_pull(docker_client,repo):
    docker_pull_response = docker_client.images.pull(repo)
    out = 'Pulled {}'.format(docker_pull_response)
    print(out)


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


def gcr_pull_all(args, data):
    try:
        docker_client = docker.DockerClient(base_url=DOCKER_BASE_URL)
        
        count = 0
        registry_previous = ''
        for repo in args.get('repositories'):
            try:                
                registry_current = repo.split('/')[0]

                if registry_previous != registry_current:
                    docker_registry = get_registry(repo)
                    docker_login_response = docker_login(docker_client, args.get('docker_username'), args.get('docker_password'), docker_registry)
                
                if registry_previous == registry_current or DOCKER_LOGIN_SUCCEEDED == docker_login_response.get('Status'):
                    docker_pull(docker_client, repo)
                    data['payload']['repositories'].append(repo)
                    count += 1
                else:
                    print('login failed')

                registry_previous = registry_current
            except Exception as e:
                print(e, file=sys.stderr)

        data['count'] = count
        data['payload']['registry'] = docker_registry

    except Exception as e:
        print(e, file=sys.stderr)


def gcr_pull(args, data):
    try:
        docker_client = docker.DockerClient(base_url=DOCKER_BASE_URL)
        docker_registry = get_registry(args.get('repositories')[0])
        docker_login_response = docker_login(docker_client, args.get('docker_username'), args.get('docker_password'), docker_registry)

        if DOCKER_LOGIN_SUCCEEDED == docker_login_response.get('Status'):
            count = 0
            if args.get('repository_tags'):
                # pull provided tags
                for tag in args.get('repository_tags'):
                    repo = args.get('repositories')[0] + ':' + tag
                    try:
                        docker_pull(docker_client, repo)
                        data['payload']['repository_tags'].append(tag)
                        count += 1
                    except Exception as e:
                       print(e, file=sys.stderr)
            else:
                # pull all tags
                try:
                    repo = args.get('repositories')[0]
                    docker_pull(docker_client, repo)
                    count += 1
                except Exception as e:
                    print(e, file=sys.stderr)
        else:
            print('login failed')

        data['count'] = count
        data['payload']['repositories'] = args.get('repositories')

    except Exception as e:
        print(e, file=sys.stderr)


def set_args(service_account_json_file_path=None, access_token=None, repositories=[], repository_tags=[]):
    if service_account_json_file_path is not None:
        # check the existence of service account json file
        path = pathlib.Path(service_account_json_file_path)
        if path.exists() is False:
            print("Service account json file does not exist")
            sys.exit(1)

    args = {
        'service_account_json_file_path': service_account_json_file_path,
        'access_token': access_token,
        'repositories': repositories,
        'repository_tags': repository_tags
    }

    return args


def main(args):
    data  = {
        'count': 0,
        'payload': {
            'repositories': [],
            'repository_tags': []
        }
    }

    docker_configure_username_password(args)
    if len(args.get('repositories')) > 1:
        gcr_pull_all(args, data)
    else:
        gcr_pull(args, data)

    return data


def summary(data):
    out = ''
    out += '{} GCR Repositories Pulled\n'.format(data['count']) 
    out += 'GCR resource saved. Use the \'docker images\' command to check the result.\n'
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
