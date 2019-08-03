import boto3, docker, base64, json


DOCKER_LOGIN_SUCCEEDED = 'Login Succeeded'
DOCKER_PUSH_ERROR = 'errorDetail'


module_info = {
    'name': 'erc__push_repos',
    'author': 'Jack Ganbold of Rhino Security Labs',
    'category': 'Docker',
    'one_liner': 'Does this thing.',
    'description': 'Pushes docker images to ECR repositories.',
    'services': ['ECR'],
    'prerequisite_modules': [],
    'external_dependencies': [],
    'arguments_to_autocomplete': [],
}


def get_aws_session(profile, region):
    return boto3.session.Session(profile_name=profile, region_name=region)


def docker_login(docker_client, username, password, registry):
    login_response = docker_client.login(username, password, registry=registry)
    return login_response


def get_docker_username_password_registery(token):
    docker_username, docker_password = base64.b64decode(token['authorizationData'][0]['authorizationToken']).decode().split(':')
    docker_registry = token['authorizationData'][0]['proxyEndpoint']
    return (docker_username, docker_password, docker_registry)


def docker_push(docker_client, image, tag):
    for line in docker_client.images.push(image, tag=tag, stream=True, decode=True):
        print(line)
        if DOCKER_PUSH_ERROR in line:
            return False

    return True

def main(args):
    data  = {
        'count': 0,
        'payload': {}
    }

    aws_session = get_aws_session(args['profile'], args['region'])
    ecr_client = aws_session.client('ecr')
    docker_client = docker.DockerClient(base_url='unix://var/run/docker.sock')

    token = ecr_client.get_authorization_token()
    docker_username, docker_password, docker_registry = get_docker_username_password_registery(token)
    docker_login_response = docker_login(docker_client,docker_username, docker_password, docker_registry)
    
    if DOCKER_LOGIN_SUCCEEDED == docker_login_response.get('Status'): 
        docker_push_response = docker_push(docker_client, args['repository_uri'],args['tag'])
        if docker_push_response:
            data['count'] = 1
            data['payload'].update({
                'region': args['region'],
                'repository_uri': args['repository_uri'],
                'tag': args['tag']
            })
        else:
            data['count'] = 0
    
    return data

def summary(data):
    out = ''
    out += '{} ECR Repositories Pushed\n'.format(data['count'])
    out += 'ECR recources saved in memory databse.\n'
    return out


if __name__ == "__main__":
    print('Running module {}...'.format(module_info['name']))
    args = {
        'profile': 'cloudgoat',
        'region': 'us-east-1',
        'repository_uri': '216825089941.dkr.ecr.us-east-1.amazonaws.com/pacu',
        'tag': 'latest'
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