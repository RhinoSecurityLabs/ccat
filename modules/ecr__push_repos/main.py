import base64
import json
import sys


import fire
import boto3
import docker


module_info = {
    'name': 'erc__push_repos',
    'author': 'Jack Ganbold of Rhino Security Labs',
    'category': 'Docker',
    'one_liner': 'Pushes docker images to ECR repositories.',
    'description': 'Pushes docker images to ECR repositories.',
    'services': ['ECR'],
    'prerequisite_modules': [],
    'external_dependencies': [],
    'arguments_to_autocomplete': [],
}


DOCKER_LOGIN_SUCCEEDED = 'Login Succeeded'
DOCKER_PUSH_ERROR = 'errorDetail'
DOCKER_BASE_URL = 'unix:///var/run/docker.sock'


def get_aws_session(aws_cli_profile, aws_region):
    return boto3.session.Session(profile_name=aws_cli_profile, region_name=aws_region)


def docker_login(docker_client, username, password, registry):
    login_response = docker_client.login(username, password, registry=registry)
    return login_response


def get_docker_username_password_registry(token):
    docker_username, docker_password = base64.b64decode(token['authorizationData'][0]['authorizationToken']).decode().split(':')
    docker_registry = token['authorizationData'][0]['proxyEndpoint']
    return (docker_username, docker_password, docker_registry)


def docker_push(docker_client, image, aws_ecr_repository_tag):
    for line in docker_client.images.push(image, tag=aws_ecr_repository_tag, stream=True, decode=True):
        if DOCKER_PUSH_ERROR in line:
            print(line, file=sys.stderr)
            return False

        print(line)

    return True

def main(args):
    data  = {
        'count': 0,
        'payload': {}
    }
    try:
        aws_session = get_aws_session(args['aws_cli_profile'], args['aws_region'])
        ecr_client = aws_session.client('ecr')
        docker_client = docker.DockerClient(base_url=DOCKER_BASE_URL)

        token = ecr_client.get_authorization_token()
        docker_username, docker_password, docker_registry = get_docker_username_password_registry(token)
        docker_login_response = docker_login(docker_client,docker_username, docker_password, docker_registry)
        
        if DOCKER_LOGIN_SUCCEEDED == docker_login_response.get('Status'): 
            docker_push_response = docker_push(docker_client, args['aws_ecr_repository_uri'],args['aws_ecr_repository_tag'])
            if docker_push_response:
                data['count'] = 1
                data['payload'].update({
                    'aws_region': args['aws_region'],
                    'aws_ecr_repository_uri': args['aws_ecr_repository_uri'],
                    'aws_ecr_repository_tag': args['aws_ecr_repository_tag']
                })
            else:
                data['count'] = 0
    except Exception as e:
        print(e, file=sys.stderr)
    
    return data

def summary(data):
    out = ''
    out += '{} ECR Repositories Pushed\n'.format(data['count'])
    out += 'ECR recources saved in memory database.\n'
    return out


def set_args(aws_cli_profile, aws_region, aws_ecr_repository_uri, aws_ecr_repository_tag):
    args = {
        'aws_cli_profile': aws_cli_profile,
        'aws_region': aws_region,
        'aws_ecr_repository_uri': aws_ecr_repository_uri,
        'aws_ecr_repository_tag': aws_ecr_repository_tag
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