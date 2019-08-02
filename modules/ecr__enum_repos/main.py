#!/usr/bin/env python3
import boto3
import json


#   TODO: Accept command line args


module_info = {
    'name': 'erc__enum_repos',
    'author': 'Jack Ganbold of Rhino Security Labs',
    'category': 'ENUM',
    'one_liner': 'Does this thing.',
    'description': 'Enumerates ECR repositories.',
    'services': ['ECR'],
    'prerequisite_modules': [],
    'external_dependencies': [],
    'arguments_to_autocomplete': [],
}


def get_all_aws_regions():
    return [
        'us-east-1','us-east-2','us-west-1','us-west-2','ap-east-1',
        'ap-south-1','ap-northeast-3','ap-northeast-2','ap-southeast-1',
        'ap-southeast-2','ap-northeast-1','ca-central-1','cn-north-1',
        'cn-northwest-1','eu-central-1','eu-west-1','eu-west-2','eu-west-3',
        'eu-north-1','me-south-1','sa-east-1','us-gov-east-1','us-gov-west-1'
    ]

def get_aws_session(profile, region):
    return boto3.session.Session(profile_name=profile, region_name=region)


def get_ecr_repos(ecr_client):
    data = None

    try:
        response = ecr_client.describe_repositories()
        if not response['repositories']:
            pass
        else:
            data = response['repositories']
    except:
        pass

    return data


def get_ecr_repo_image_tags(ecr_client, repository_name, tag_status):
    data = None

    try:
        response = ecr_client.list_images(repositoryName=repository_name, filter={
            'tagStatus': tag_status
        })

        if not response['imageIds']:
            pass
        else:
            data = response['imageIds']
    except:
        pass

    return data


def append_image_tags_to_repo(ecr_client, ecr_repos):
    for repo in ecr_repos:
        image_ids = get_ecr_repo_image_tags(ecr_client, repo['repositoryName'], 'ANY')
        if image_ids is not None:
            repo.update({'image_ids': image_ids})


def enum_repos(profile, data):
    sum = 0
    regions = get_all_aws_regions()

    for region in regions:
        aws_session = get_aws_session(profile, region)
        ecr_client = aws_session.client('ecr')
        ecr_repos = get_ecr_repos(ecr_client)

        if ecr_repos is not None:
            data['payload']['regions'].append(region)
            data['payload']['repositories_by_region'].update({
                region: ecr_repos
            })

            append_image_tags_to_repo(ecr_client, ecr_repos)

            count = len(ecr_repos)
            out = "Found {} repositories in {}".format(count, region)
            print(out)
            sum += count

    data['count'] = sum

def main(args):
    data  = {
        'count': 0,
        'payload': {
            'regions':[],
            'repositories_by_region': {}
        }
    }

    enum_repos(args.get('profile'), data)

    print('Result:')
    print(json.dumps(data, indent=4, default=str)) 
    return data


def summary(data):
    out = ''
    out += 'Total {} ECR Repositories Enumrated\n'.format(data['count'])
    out += 'ECR recources saved in memory databse.\n'

    return out


if __name__ == "__main__":
    print('Running module {}...'.format(module_info['name']))
    args = {'profile': 'cloudgoat'}
    data = main(args) 

    if data is not None:
        summary = summary(data)
        if len(summary) > 1000:
            raise ValueError('The {} module\'s summary is too long ({} characters). Reduce it to 1000 characters or fewer.'.format(module_info['name'], len(summary)))
        if not isinstance(summary, str):
            raise TypeError(' The {} module\'s summary is {}-type instead of str. Make summary return a string.'.format(module_info['name'], type(summary)))
        
        print('{} completed.\n'.format(module_info['name']))
        print('MODULE SUMMARY:\n\n{}\n'.format(summary.strip('\n')))       
