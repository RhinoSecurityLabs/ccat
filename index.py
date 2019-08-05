import json
import sys


from pyfiglet import figlet_format
from PyInquirer import (prompt, Separator)


import modules.ecr__enum_repos.main as ecr__enum_repos
import modules.ecr__pull_repos.main as ecr__pull_repos
import modules.docker__backdoor_reverse_shell.main as docker__backdoor


ENUMRATE_ECR = 'Enumrate ECR'
PULL_ECR_REPOSE = 'Pull Repos from ECR'
PUSH_ECR_REPOS = 'Push Repos to ECR'
DOCKER_BACKDOOR = 'Docker Backdoor'
AWS_REGIONS_ALL = 'ALL'


def title(text='Rhino Container Hack CLI', font='slant'):
    print(figlet_format(text, font=font))


def ask_ecr_enum_repos_input():
    questions= [
        {
            'type': 'input',
            'name': 'aws_cli_profile',
            'message': 'Enter AWS profile name'
        },
        {
            'type': 'checkbox',
            'name': 'aws_regions',
            'message': 'Select AWS regions',
            'choices': [
                Separator('= Select ALL ='),
                {
                    'name': AWS_REGIONS_ALL
                },
                Separator('= United States ='),
                {
                    'name': 'us-east-1'
                },
                {
                    'name': 'us-east-2'
                },
                {
                    'name': 'us-west-1'
                },
                {
                    'name': 'us-west-2'
                },
                Separator('= Asia Pacific ='),
                {
                    'name': 'ap-east-1'
                },
                {
                    'name': 'ap-south-1'
                },
                {
                    'name': 'ap-northeast-1'
                },
                {
                    'name': 'ap-northeast-2'
                },
                {
                    'name': 'ap-southeast-1'
                },
                {
                    'name': 'ap-southeast-2'
                },
                Separator('= China ='),
                {
                    'name': 'cn-north-1'
                },
                {
                    'name': 'cn-northwest-1'
                },
                Separator('= European Union ='),
                {
                    'name': 'eu-central-1'
                },
                {
                    'name': 'eu-west-1'
                },
                {
                    'name': 'eu-west-2'
                },
                {
                    'name': 'eu-west-3'
                },
                {
                    'name': 'eu-north-1'
                },
                Separator('= Middle East ='),
                {
                    'name': 'me-south-1'
                },
                Separator('= South America ='),
                {
                    'name': 'sa-east-1'
                },
                Separator('= AWS GovCloud ='),
                {
                    'name': 'us-gov-east-1'
                },
                {
                    'name': 'us-gov-west-1'
                }
            ]
        }
    ]

    answers = prompt(questions)

    if AWS_REGIONS_ALL in answers['aws_regions']:
        answers['aws_regions'] = get_all_aws_regions()
    
    return answers


def ask_ecr_pull_repos_input():
    questions = [
        {
            'type': 'input',
            'name': 'aws_cli_profile',
            'message': 'Enter AWS profile name'
        },
        {
            'type': 'input',
            'name': 'aws_region',
            'message': 'Enter AWS region name'
        },
        {
            'type': 'input',
            'name': 'aws_ecr_repository_uri',
            'message': 'Enter AWS ECR repository URI'
        },
        {
            'type': 'input',
            'name': 'aws_ecr_repository_tags',
            'message': 'Enter AWS ECR repository tags seperate by comma'
        },
    ]

    answers = prompt(questions)

    # strip(',') remove leading or trailing (,)
    # replace(' ', '') remove spaces
    # split by comma to generate a list of tags
    answers['aws_ecr_repository_tags'] = answers['aws_ecr_repository_tags'].strip(',').replace(' ', '').split(',')

    return answers


def ask_docker_backdoor_input():
    questions = [
        {
            'type': 'input',
            'name': 'repository_uri',
            'message': 'Enter Docker image name'
        },
        {
            'type': 'input',
            'name': 'target_image_tag',
            'message': 'Enter Docker image tag'
        },
        {
            'type': 'input',
            'name': 'build_image_tag',
            'message': 'Enter Docker image new build tag'
        },
        {
            'type': 'input',
            'name': 'injection',
            'message': 'Enter Docker injection'
        }
    ]

    answers = prompt(questions)

    return answers

def print_summary(data, module):
    if data is not None:
        summary = module.summary(data)
        if len(summary) > 1000:
            raise ValueError('The {} module\'s summary is too long ({} characters). Reduce it to 1000 characters or fewer.'.format(module.module_info['name'], len(summary)))
        if not isinstance(summary, str):
            raise TypeError(' The {} module\'s summary is {}-type instead of str. Make summary return a string.'.format(module.module_info['name'], type(summary)))
        
        print('{} completed.\n'.format(module.module_info['name']))
        print('MODULE SUMMARY:\n\n{}\n'.format(summary.strip('\n')))  


def exit_cli():
    print(figlet_format('Bye Bye', font='slant'))
    sys.exit()


def run_module(answers):
    if ENUMRATE_ECR in answers['main_menu']:
        cli_answers = ask_ecr_enum_repos_input()
        data = ecr__enum_repos.main(cli_answers)
        print_summary(data, ecr__enum_repos)

    elif PULL_ECR_REPOSE in answers['main_menu']:
        cli_answers = ask_ecr_pull_repos_input()
        data = ecr__pull_repos.main(cli_answers)
        print_summary(data, ecr__pull_repos)

    elif PUSH_ECR_REPOS in answers['main_menu']:
        pass

    elif DOCKER_BACKDOOR in answers['main_menu']:
        cli_answers = ask_docker_backdoor_input()
        data = docker__backdoor.main(cli_answers)
        print_summary(data, docker__backdoor)
        
    else:
        exit_cli()


def get_all_aws_regions():
    return [
        'us-east-1','us-east-2','us-west-1','us-west-2','ap-east-1',
        'ap-south-1','ap-northeast-3','ap-northeast-2','ap-southeast-1',
        'ap-southeast-2','ap-northeast-1','ca-central-1','cn-north-1',
        'cn-northwest-1','eu-central-1','eu-west-1','eu-west-2','eu-west-3',
        'eu-north-1','me-south-1','sa-east-1','us-gov-east-1','us-gov-west-1'
    ]


def main_menu():
    questions = [
        {
            'type': 'list',
            'name': 'main_menu',
            'message': 'What do you want to do?',
            'choices': [
                Separator('= AWS ='),
                ENUMRATE_ECR,
                PULL_ECR_REPOSE,
                PUSH_ECR_REPOS,
                Separator('= AZURE ='),
                Separator('Coming Soon'),
                Separator('= GCP ='),
                Separator('Coming Soon='),
                Separator('= Docker ='),
                DOCKER_BACKDOOR,
                Separator('= Kubernets ='),
                Separator('Coming Soon'),
                Separator('= Exit CLI ='),
                'Exit'
            ]
        }
    ]

    answers = prompt(questions)
    return answers


def main():
    title()
    main_menu_answers = main_menu()
    run_module(main_menu_answers)


if __name__ == "__main__":
    main()
