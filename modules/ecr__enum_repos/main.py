#!/usr/bin/env python3
import os
import json
import sys

import boto3
import fire


#   TODO: Accept command line args

SAVE_TO_FILE_DIRECTORY = './data'
SAVE_TO_FILE_PATH = '{}/ecr__enum_repos_data.json'.format(SAVE_TO_FILE_DIRECTORY)


module_info = {
    'name': 'ecr__enum_repos',
    'author': 'Jack Ganbold of Rhino Security Labs',
    'category': 'ENUM',
    'one_liner': 'Enumerates ECR repositories.',
    'description': 'Enumerates ECR repositories.',
    'services': ['ECR'],
    'prerequisite_modules': [],
    'external_dependencies': [],
    'arguments_to_autocomplete': [],
    'data_saved': SAVE_TO_FILE_PATH
}


def get_aws_session(profile, region):
    return boto3.Session(profile_name=profile, region_name=region)


def get_ecr_repos(ecr_client):
    data = []
    nextToken = None

    try:
        while True:
            if nextToken is None:
                response = ecr_client.describe_repositories(maxResults=2)
            else:
                response = ecr_client.describe_repositories(maxResults=2, nextToken=nextToken)

            if response.get('repositories'):
                data.extend(response.get('repositories'))
            elif len(data) == 0:
                break

            if response.get('nextToken'):
                nextToken = response['nextToken']
            else:
                break

    except Exception as e:
        print(e, file=sys.stderr)

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


def save_to_file(data):
    os.makedirs(SAVE_TO_FILE_DIRECTORY, exist_ok=True)
    with open(SAVE_TO_FILE_PATH, 'w+') as json_file:
        json.dump(data, json_file, indent=4, default=str)  


def enum_repos(profile, aws_regions, data):
    total = 0

    try:
        for region in aws_regions:
            aws_session = get_aws_session(profile, region)
            ecr_client = aws_session.client('ecr')
            ecr_repos = get_ecr_repos(ecr_client)

            if len(ecr_repos) != 0:
                data['payload']['aws_regions'].append(region)
                data['payload']['repositories_by_region'].update({
                    region: ecr_repos
                })

                append_image_tags_to_repo(ecr_client, ecr_repos)

                count = len(ecr_repos)
                out = "Found {} repositories in {}".format(count, region)
                print(out)
                total += count
                
    except Exception as e:
        print(e, file=sys.stderr)

    data['count'] = total


def main(args):
    data  = {
        'count': 0,
        'payload': {
            'aws_regions': [],
            'repositories_by_region': {}
        }
    }

    enum_repos(args.get('aws_cli_profile'), args.get('aws_regions'), data)
    save_to_file(data)

    return data


def summary(data):
    out = ''
    out += 'Total {} ECR Repositories Enumerated\n'.format(data['count'])
    out += 'ECR recources saved under {}.\n'.format(module_info['data_saved'])

    return out

#python main.py cloudgoat "['us-east-1','us-west-2']"
def set_args(aws_cli_profile, aws_regions):
    print(aws_regions)
    if type(aws_regions) is list:
        args = {
            'aws_cli_profile': 'cloudgoat',
            'aws_regions': aws_regions
        }
    else:
        print('Regions must be a list.\n\tExample list format:\n\t\tpython main.py <aws-profile> \"[\'us-east-1\',\'us-west-2\']\"', file=sys.stderr)
        sys.exit(1)

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
        
        print('RESULT:')
        print(json.dumps(data, indent=4, default=str))         

        print('{} completed.\n'.format(module_info['name']))
        print('MODULE SUMMARY:\n\n{}\n'.format(summary.strip('\n')))       
