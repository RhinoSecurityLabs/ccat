#!/usr/bin/env python3
import os
import json
import sys
import base64


from kubernetes import client, config
from kubernetes.client.rest import ApiException
import fire


module_info = {
    'name': 'k8s__enum_secrets',
    'author': 'Itgel Ganbold (Jack) of Rhino Security Labs',
    'category': 'Kubernets, Enumerate',
    'one_liner': 'Enumerate K8s secrets',
    'description': 'Enumerate K8s secrets',
    'services': ['K8s'],
    'prerequisite_modules': [],
    'external_dependencies': [],
    'arguments_to_autocomplete': [],
    'data_saved': ''
}


def decodeBase64Secret(encodedBase64Str):
    decodedSecretBytes = base64.b64decode(encodedBase64Str)
    decodedSecretStr = str(decodedSecretBytes, "utf-8")
    
    return decodedSecretStr


def enum_secrets(coreV1Api, data):
    try:
        secrets = coreV1Api.list_secret_for_all_namespaces(watch=False)
    except ApiException as e:
        print("Exception when calling CoreV1Api->list_secret_for_all_namespaces: %s\n" % e)

    data['payload']['secrets']['items'] = secrets.items
    data['payload']['secrets']['count'] = len(secrets.items)

    # print(secrets.items[0])

    encodedSecretsData = secrets.items[0].data
    decodedSecretsData = {}
    for secret in encodedSecretsData:
        base64DecodedValue = decodeBase64Secret(encodedSecretsData[secret])
        base64DecodedKey = secret + "-base64Decoded"
        decodedSecretsData[base64DecodedKey] = base64DecodedValue
    
    # merge decode secrets with encoded secrets
    encodedSecretsData.update(decodedSecretsData)


def save_to_file(save_to_file_directory ,save_to_file_path ,data):
    os.makedirs(save_to_file_directory, exist_ok=True)
    with open(save_to_file_path, 'w+') as json_file:
        json.dump(data, json_file, indent=4, default=str)


def main(args):
    data  = {
        'count': 0,
        'payload': {
            'secrets': {
                'count': 0,
                'items': []
            }
        }
    }

    # Configure K8s context
    config.load_kube_config()

    # Congigure K8s Apis
    coreV1Api = client.CoreV1Api()

    # Enumerate
    enum_secrets(coreV1Api, data)

    # Save data
    current_context = config.list_kube_config_contexts()[1]
    save_to_file_directory = './data/k8s/{}'.format(current_context['name'])
    save_to_file_path = '{}/k8s__enum_secrets.json'.format(save_to_file_directory)
    save_to_file(save_to_file_directory, save_to_file_path, data)
    module_info['data_saved'] = save_to_file_path

    return data


def summary(data):
    out = ''
    out += 'Total {} K8s Secrets Enumerated\n'.format(data['payload']['secrets']['count'])
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
