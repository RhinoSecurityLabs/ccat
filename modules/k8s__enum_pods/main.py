#!/usr/bin/env python3
import os
import json
import sys


from kubernetes import client, config
from kubernetes.client.rest import ApiException
import fire


module_info = {
    'name': 'k8s__enum_pods',
    'author': 'Itgel Ganbold (Jack) of Rhino Security Labs',
    'category': 'Kubernets, Enumerate',
    'one_liner': 'Enumerate K8s Pods',
    'description': 'Enumerate K8s Pods',
    'services': ['K8s'],
    'prerequisite_modules': [],
    'external_dependencies': [],
    'arguments_to_autocomplete': [],
    'data_saved': ''
}


def enum_pods(coreV1Api, data):
    try:
        pods = coreV1Api.list_pod_for_all_namespaces(watch=False)
    except ApiException as e:
        print("Exception when calling CoreV1Api->list_pod_for_all_namespaces: %s\n" % e)

    data['payload']['pods']['items'] = pods.items
    data['payload']['pods']['count'] = len(pods.items)


def save_to_file(save_to_file_directory ,save_to_file_path ,data):
    os.makedirs(save_to_file_directory, exist_ok=True)
    with open(save_to_file_path, 'w+') as json_file:
        json.dump(data, json_file, indent=4, default=str)


def main(args):
    data  = {
        'count': 0,
        'payload': {
            'pods': {
                'count': 0,
                'items': [],
            }
        }
    }

    # Configure K8s context
    config.load_kube_config()

    # Congigure K8s Apis
    coreV1Api = client.CoreV1Api()

    # Enumerate
    enum_pods(coreV1Api, data)

    # Save data
    current_context = config.list_kube_config_contexts()[1]
    save_to_file_directory = './data/k8s/{}'.format(current_context['name'])
    save_to_file_path = '{}/k8s__enum_pods.json'.format(save_to_file_directory)
    save_to_file(save_to_file_directory, save_to_file_path, data)
    module_info['data_saved'] = save_to_file_path

    return data


def summary(data):
    out = ''
    out += 'Total {} K8s Pods Enumerated\n'.format(data['payload']['pods']['count'])
    out += 'K8s recources saved under {}.\n'.format(module_info['data_saved'])

    return out


def set_args():
    args = {}

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
        
        # print('RESULT:')
        # print(json.dumps(data, indent=4, default=str))

        print('{} completed.\n'.format(module_info['name']))
        print('MODULE SUMMARY:\n\n{}\n'.format(summary.strip('\n')))
