#!/usr/bin/env python3
import base64
import json
import sys


import fire
import boto3
import docker


module_info = {
    'name': 'ecr__pull_repos',
    'author': 'Jack Ganbold of Rhino Security Labs',
    'category': 'Container',
    'one_liner': 'Pulls ECR repositories.',
    'description': 'Pulls ECR repositories.',
    'services': ['ECR'],
    'prerequisite_modules': [],
    'external_dependencies': [],
    'arguments_to_autocomplete': [],
}


DOCKER_LOGIN_SUCCEEDED = 'Login Succeeded'
DOCKER_BASE_URL = 'unix:///var/run/docker.sock'


def get_aws_session(aws_cli_profile, aws_region):
    return boto3.session.Session(profile_name=aws_cli_profile, region_name=aws_region)


def docker_login(docker_client ,username, password, registry):
    login_response = docker_client.login(username, password, registry=registry)
    return login_response


def get_docker_username_password_registry(token):
    docker_username, docker_password = base64.b64decode(token['authorizationData'][0]['authorizationToken']).decode().split(':')
    docker_registry = token['authorizationData'][0]['proxyEndpoint']
    return (docker_username, docker_password, docker_registry)


def docker_pull(docker_client, repo):
    docker_pull_response = docker_client.images.pull(repo)
    return docker_pull_response



def ecr_pull_all_repos(args, data):
    ecr_repos = args.get('ecr_repos')
    count = 0
    
    try:
        if ecr_repos.get('aws_regions'):
            for region in ecr_repos.get('aws_regions'):
                aws_session = get_aws_session(args['aws_cli_profile'], region)
                ecr_client = aws_session.client('ecr')
                token = ecr_client.get_authorization_token()
        
                docker_client = docker.DockerClient(base_url=DOCKER_BASE_URL)
                docker_username, docker_password, docker_registry = get_docker_username_password_registry(token)
                docker_login_response = docker_login(docker_client, docker_username, docker_password, docker_registry)
    
                if ecr_repos.get('repositories_by_region'):
                    for repo in ecr_repos.get('repositories_by_region').get(region):
                        if repo.get('repositoryUri'):
                            docker_pull_response = docker_pull(docker_client, repo.get('repositoryUri'))
                            out = 'Pulled {}'.format(docker_pull_response)
                            count += 1
                            print(out)

        data['count'] = count
    except Exception as e:
        print(e, file=sys.stderr)
    

def ecr_pull(args, data):
    try:
        aws_session = get_aws_session(args['aws_cli_profile'], args['aws_region'])
        ecr_client = aws_session.client('ecr')
        token = ecr_client.get_authorization_token()

        docker_client = docker.DockerClient(base_url=DOCKER_BASE_URL)
        docker_username, docker_password, docker_registry = get_docker_username_password_registry(token)
        docker_login_response = docker_login(docker_client, docker_username, docker_password, docker_registry)

        if DOCKER_LOGIN_SUCCEEDED == docker_login_response.get('Status'):
            count = 0
            for tag in args['aws_ecr_repository_tags']:
                repo_tag = args['aws_ecr_repository_uri'] + ":" + tag
                try:
                    docker_pull_response = docker_pull(docker_client, repo_tag)
                    out = 'Pulled {}'.format(docker_pull_response)
                    count += 1
                    data['payload']['aws_ecr_repository_tags'].append(tag)
                    print(out)
                except Exception as e:
                    print(e, file=sys.stderr)

            data['count'] = count
            data['payload']['aws_ecr_repository_uri'] = args['aws_ecr_repository_uri']
            data['payload']['aws_region'] = args['aws_region'] 
    except Exception as e:
        print(e, file=sys.stderr)

def main(args):
    data  = {
        'count': 0,
        'payload': {
            'aws_region': None,
            'aws_ecr_repository_uri': None,
            'aws_ecr_repository_tags': []
        }
    }

    if args.get('ecr_repos'):
        ecr_pull_all_repos(args, data)
    else:
        ecr_pull(args, data)

    return data


def summary(data):
    out = ''
    out += '{} ECR Repositories Pulled\n'.format(data['count']) 
    out += 'ECR resources saved and use \'docker images\' command to check the result.\n'
    return out


def set_args(aws_cli_profile, aws_region, aws_ecr_repository_uri, aws_ecr_repository_tags):
    args = {
        'aws_cli_profile': aws_cli_profile,
        'aws_region': aws_region,
        'aws_ecr_repository_uri': aws_ecr_repository_uri,
        'aws_ecr_repository_tags': aws_ecr_repository_tags
    }

    return args

# Run it with sdtin, sdtout, sdterr
#   standard input	0>
#   standard output	1>
#   standard error	2>
#
#   Example:
        # python ./modules/ecr__pull_repos/main.py \
        #   0> read cloudgoat us-east-1 999999999.dkr.ecr.us-east-1.amazonaws.com/nginx "['tag1','tag2']" \
        #   2> pull_err.txt \
        #   1> pull_out.txt
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
