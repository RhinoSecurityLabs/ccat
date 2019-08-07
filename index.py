#!/usr/bin/env python3
import json
import sys


import boto3
import fire
from pyfiglet import figlet_format
from PyInquirer import (prompt, Separator)


import modules.ecr__enum_repos.main as ecr__enum_repos
import modules.ecr__pull_repos.main as ecr__pull_repos
import modules.docker__backdoor_reverse_shell.main as docker__backdoor
import modules.ecr__push_repos.main as ecr__push_repos


ENUMRATE_ECR = 'Enumrate ECR'
PULL_ECR_REPOSE = 'Pull Repos from ECR'
PUSH_ECR_REPOS = 'Push Repos to ECR'
DOCKER_BACKDOOR = 'Docker Backdoor'


class CLI(object):
    def __init__(self):
        aws = AWS(profile='cloudgoat')
        docker = Docker()

        print(aws.get_menu())

        self.extentions = {
            'aws': aws,
            'docker': docker
        }

    def print_title(self, text='Rhino\'s Docker Hacking CLI', font='slant'):
        print(figlet_format(text, font=font))

    def main_menu(self, menu_choices=[]):

        if not menu_choices:
            for extention in self.extentions.values():
                menu_choices += extention.get_menu()

            menu_choices += self.get_helpter_menu()

        questions = [
            {
                'type': 'list',
                'name': 'main_menu',
                'message': 'What do you want to do?',
                'choices': menu_choices
            }
        ]

        answers = prompt(questions)

        return answers

    def print_module_running(self, module_name):
        print('Running module {}...'.format(module_name))

    def print_module_summary(self, data, module):
        if data is not None:
            summary = module.summary(data)
            if len(summary) > 1000:
                raise ValueError('The {} module\'s summary is too long ({} characters). Reduce it to 1000 characters or fewer.'.format(module.module_info['name'], len(summary)))
            if not isinstance(summary, str):
                raise TypeError(' The {} module\'s summary is {}-type instead of str. Make summary return a string.'.format(module.module_info['name'], type(summary)))
            
            print('{} completed.\n'.format(module.module_info['name']))
            print('MODULE SUMMARY:\n\n{}\n'.format(summary.strip('\n')))  

    def run_module(self, answers):
        if ENUMRATE_ECR in answers['main_menu']:
            cli_answers = self.extentions['aws'].ask_ecr_enum_repos()
            self.print_module_running(ecr__enum_repos.module_info['name'])
            data = ecr__enum_repos.main(cli_answers)
            self.print_module_summary(data, ecr__enum_repos)

        elif PULL_ECR_REPOSE in answers['main_menu']:
            cli_answers = self.extentions['aws'].ask_ecr_pull_repos()
            self.print_module_running(ecr__pull_repos.module_info['name'])
            data = ecr__pull_repos.main(cli_answers)
            self.print_module_summary(data, ecr__pull_repos)

        elif PUSH_ECR_REPOS in answers['main_menu']:
            cli_answers = self.extentions['aws'].ask_ecr_push_repos()
            self.print_module_running(ecr__push_repos.module_info['name'])
            data = ecr__push_repos.main(cli_answers)
            self.print_module_summary(data, ecr__push_repos)

        elif DOCKER_BACKDOOR in answers['main_menu']:
            cli_answers = self.extentions['docker'].ask_docker_backdoor()
            self.print_module_running(docker__backdoor.module_info['name'])
            data = docker__backdoor.main(cli_answers)
            self.print_module_summary(data, docker__backdoor)

        else:
            self.exit_cli()

    def get_helpter_menu(self):
        return [
            Separator('= Exit CLI ='),
            'Exit'
        ]

    def exit_cli(self):
        print(figlet_format('Bye Bye', font='slant'))
        sys.exit()


class AWS(object):
    def __init__(self, profile, region='us-east-1'):
        self.configure = {
            'profile': profile,
            'region': region
        }

    def get_available_regions(self):
        aws_session = boto3.Session()
        regions = aws_session.get_available_regions('ec2')

        return regions

    def get_menu_choices_regions(self, aws_regions=[]):
        choices = []
        for region in aws_regions:
            choices.append({
                'name': region
            })

        return choices

    def get_menu(self):
        return [
            Separator('= AWS ='),
            ENUMRATE_ECR,
            PULL_ECR_REPOSE,
            PUSH_ECR_REPOS
        ]

    def ask_ecr_enum_repos(self):
        aws_regions = self.get_available_regions()

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
                'choices': self.get_menu_choices_regions(aws_regions)
            }
        ]

        answers = prompt(questions)
        
        return answers

    def ask_ecr_pull_repos(self):
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

    def ask_ecr_push_repos(self):
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
                'message': 'Enter Docker image that named after AWS ECR repository URI'
            },
            {
                'type': 'input',
                'name': 'aws_ecr_repository_tag',
                'message': 'Enter Docker image tag'
            }
        ]

        answers = prompt(questions)

        return answers

class Docker(object):
    def get_menu(self):
        return [
            Separator('= Docker ='),
            DOCKER_BACKDOOR,
        ]

    def ask_docker_backdoor(self):
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


def main():
    cli = CLI()
    cli.print_title()
    while True:
        answers = cli.main_menu()
        cli.run_module(answers)


if __name__ == "__main__":
    fire.Fire(main)
