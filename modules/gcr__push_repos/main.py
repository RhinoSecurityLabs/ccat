#!/usr/bin/env python3
import json
import sys
import pathlib


import fire
import docker


module_info = {
    'name': 'grc__push_repos',
    'author': 'Jack Ganbold of Rhino Security Labs',
    'category': 'Docker',
    'one_liner': 'Pushes docker images to GCR repositories.',
    'description': 'Pushes docker images to GCR repositories.',
    'services': ['GCR'],
    'prerequisite_modules': [],
    'external_dependencies': [],
    'arguments_to_autocomplete': [],
}


DOCKER_LOGIN_SUCCEEDED = 'Login Succeeded'
DOCKER_USERNAME_JSON_KEY = '_json_key'
DOCKER_USERNAME_ACCESS_TOKEN = 'oauth2accesstoken'
DOCKER_PUSH_ERROR = 'errorDetail'
DOCKER_BASE_URL = 'unix:///var/run/docker.sock'


def get_sa_key(path):
    with open(path) as json_file:
        sa_key_json = json.load(json_file)

    return json.dumps(sa_key_json, default=str)


def get_registry(repository_uri):
    print(repository_uri)
    registry_split= repository_uri.split('/')
    docker_registry = 'https://' + registry_split[0]
    return docker_registry


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


def docker_login(docker_client ,username, password, docker_registry):
    login_response = docker_client.login(username, password, registry=docker_registry)
    return login_response


def docker_push(docker_client, image, repository_tag):
    for line in docker_client.images.push(image, tag=repository_tag, stream=True, decode=True):
        if DOCKER_PUSH_ERROR in line:
            print(line, file=sys.stderr)
            return False

        print(line)

    return True


def set_args(service_account_json_file_path=None, access_token=None, repository_uri=None, repository_tag=None):
    if service_account_json_file_path is not None:
        # check the existence of service account json file
        path = pathlib.Path(service_account_json_file_path)
        if path.exists() is False:
            print("Service account json file does not exist")
            sys.exit(1)

    args = {
        'service_account_json_file_path': service_account_json_file_path,
        'repository_uri': repository_uri,
        'repository_tag': repository_tag,
        'access_token': access_token
    }

    return args


def main(args):
    data  = {
        'count': 0,
        'payload': {}
    }

    docker_configure_username_password(args)

    try:
        docker_client = docker.DockerClient(base_url=DOCKER_BASE_URL)
        docker_registry = get_registry(args.get('repository_uri'))
        docker_login_response = docker_login(docker_client, args.get('docker_username'), args.get('docker_password'), docker_registry)
        
        if DOCKER_LOGIN_SUCCEEDED == docker_login_response.get('Status'): 
            docker_push_response = docker_push(docker_client, args['repository_uri'],args['repository_tag'])
            if docker_push_response:
                data['count'] = 1
                data['payload'].update({
                    'repository_uri': args['repository_uri'],
                    'repository_tag': args['repository_tag']
                })
            else:
                data['count'] = 0
    except Exception as e:
        print(e, file=sys.stderr)
    
    return data

def summary(data):
    out = ''
    out += '{} GCR Repositories Pushed\n'.format(data['count'])
    out += 'Pushed the image. Check the Container Registry to get info about the pushed image.\n'
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
