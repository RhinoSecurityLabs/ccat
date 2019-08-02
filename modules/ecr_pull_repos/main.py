import boto3, docker, base64, json

#   TODO: Implement a better error handling
#   TODO: Pull multiple repos with different tags

module_info = {
    'name': 'ecr_pull_repos',
    'author': 'Jack Ganbold of Rhino Security Labs',
    'category': 'Container',
    'one_liner': 'Does this thing.',
    'description': 'Pulls ECR repositories.',
    'services': ['ECR'],
    'prerequisite_modules': [],
    'external_dependencies': [],
    'arguments_to_autocomplete': [],
}


DOCKER_LOGIN_SUCCEEDED = 'Login Succeeded'


def get_aws_session(profile, region):
    return boto3.session.Session(profile_name=profile, region_name=region)


def docker_login(docker_client ,username, password, registry):
    login_response = docker_client.login(username, password, registry=registry)
    return login_response


def get_docker_username_password_registery(token):
    docker_username, docker_password = base64.b64decode(token['authorizationData'][0]['authorizationToken']).decode().split(':')
    docker_registry = token['authorizationData'][0]['proxyEndpoint']
    return (docker_username, docker_password, docker_registry)


def docker_pull(docker_client, repo):
    docker_pull_response = docker_client.images.pull(repo)
    return docker_pull_response

def ecr_pull(args, data):
    aws_session = get_aws_session(args['profile'], args['region'])
    ecr_client = aws_session.client('ecr')
    token = ecr_client.get_authorization_token()

    docker_client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    docker_username, docker_password, docker_registry = get_docker_username_password_registery(token)
    docker_login_response = docker_login(docker_client, docker_username, docker_password, docker_registry)

    if DOCKER_LOGIN_SUCCEEDED == docker_login_response.get('Status'):
        count = 0
        for tag in args['tags']:
            repo_tag = args['repository_uri'] + ":" + tag
            try:
                docker_pull_response = docker_pull(docker_client, repo_tag)
                out = 'Pulled {}'.format(docker_pull_response)
                count += 1
                data['payload']['tags'].append(tag)
                print(out)
            except Exception as e:
                print(e)

        data['count'] = count
        data['payload']['repository_uri'] = args['repository_uri']
        data['payload']['region'] = args['region']
         
        print('Result:')
        print(json.dumps(data, indent=4, default=str))

def main(args):
    data  = {
        'count': 0,
        'payload': {
            'region': None,
            'repository_uri': None,
            'tags': []
        }
    }

    ecr_pull(args, data)

    return data


def summary(data):
    out = ''
    out += '{} ECR Repositories Pulled\n'.format(data['count']) 
    out += 'ECR resources saved in memory databse.\n'
    return out


if __name__ == "__main__":
    print('Running module {}...'.format(module_info['name']))
    args = {
        'profile':'cloudgoat',
        'region':'us-east-1',
        'repository_uri': '216825089941.dkr.ecr.us-east-1.amazonaws.com/pacu',
        'tags': ['latest', 'hahah']
    }
    
    data = main(args)

    if data is not None:
        summary = summary(data)
        if len(summary) > 1000:
            raise ValueError('The {} module\'s summary is too long ({} characters). Reduce it to 1000 characters or fewer.'.format(module_info['name'], len(summary)))
        if not isinstance(summary, str):
            raise TypeError(' The {} module\'s summary is {}-type instead of str. Make summary return a string.'.format(module_info['name'], type(summary)))
        
        print('{} completed.\n'.format(module_info['name']))
        print('MODULE SUMMARY:\n\n{}\n'.format(summary.strip('\n')))   
