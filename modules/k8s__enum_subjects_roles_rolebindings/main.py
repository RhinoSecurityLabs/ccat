#!/usr/bin/env python3
import os
import json
import sys


from kubernetes import client, config
from kubernetes.client.rest import ApiException
import fire


module_info = {
    'name': 'k8s__enum_subjects_roles_rolebindings',
    'author': 'Itgel Ganbold (Jack) of Rhino Security Labs',
    'category': 'Kubernets, Enumerate',
    'one_liner': 'Enumerate K8s subjects, (cluster)roles and (cluster)rolebindings.',
    'description': 'Enumerate K8s subjects, (cluster)roles and (cluster)rolebindings',
    'services': ['K8s'],
    'prerequisite_modules': [],
    'external_dependencies': [],
    'arguments_to_autocomplete': [],
    'data_saved': ''
}


def enum_service_accounts(coreV1Api, data):
    try:
        serviceAccounts = coreV1Api.list_service_account_for_all_namespaces(watch=False)
    except ApiException as e:
        print("Exception when calling CoreV1Api->list_service_account_for_all_namespaces: %s\n" % e)
    
    items = []
    for item in serviceAccounts.items:
        secrets = []
        for secret in item.secrets:
            cleanedSecret = {
                'name': secret.name
            }
            secrets.append(cleanedSecret)

        cleanedItem = {
            'metadata': {
                'name': item.metadata.name,
                'namespace': item.metadata.namespace
            },
            'secrets': secrets,
            'automount_service_account_token': item.automount_service_account_token,
            'image_pull_secrets': item.image_pull_secrets
        }
        items.append(cleanedItem)

    data['payload']['service_accounts']['items'] = items
    data['payload']['service_accounts']['count'] = len(serviceAccounts.items)


def enum_roles(rbacAuthorizationV1Api, data):
    try:
        roles = rbacAuthorizationV1Api.list_role_for_all_namespaces(watch=False)
    except ApiException as e:
        print("Exception when calling RbacAuthorizationV1Api->list_role_for_all_namespaces: %s\n" % e)

    items = []
    for item in roles.items:
        rules = []
        for rule in item.rules:
            apiGroups = [*rule.api_groups] if rule.api_groups else []
            resources = [*rule.resources] if rule.resources else []
            verbs = [*rule.verbs] if rule.verbs else []

            cleanedRule = {
                'api_groups': apiGroups,
                'resources': resources,
                'verbs': verbs
            }
            rules.append(cleanedRule)
        
        cleanedLabels = {}
        cleanedLabels.update(item.metadata.labels)

        cleanedItem = {
            'metadata': {
                'name': item.metadata.name,
                'namespace': item.metadata.namespace,
                'labels': cleanedLabels
            },
            'rules': rules
        }
        items.append(cleanedItem)

    data['payload']['roles']['items'] = items
    data['payload']['roles']['count'] = len(roles.items)


def enum_cluter_roles(rbacAuthorizationV1Api, data):
    try:
        clusterRoles = rbacAuthorizationV1Api.list_cluster_role(watch=False)
    except ApiException as e:
        print("Exception when calling rbacAuthorizationV1Api->list_cluster_role: %s\n" % e)

    items = []
    for item in clusterRoles.items:
        rules = []
        for rule in item.rules:
            apiGroups = [*rule.api_groups] if rule.api_groups else []
            resources = [*rule.resources] if rule.resources else []
            verbs = [*rule.verbs] if rule.verbs else []

            cleanedRule = {
                'api_groups': apiGroups,
                'resources': resources,
                'verbs': verbs
            }
            rules.append(cleanedRule)

        cleanedItem = {
            'metadata': {
                'name': item.metadata.name
            },
            'rules': rules
        }
        items.append(cleanedItem)

    data['payload']['cluster_roles']['items'] = items
    data['payload']['cluster_roles']['count'] = len(clusterRoles.items)


def enum_role_bindings(rbacAuthorizationV1Api, data):
    try:
        roleBindings = rbacAuthorizationV1Api.list_role_binding_for_all_namespaces(watch=False)
    except ApiException as e:
        print("Exception when calling rbacAuthorizationV1Api->list_role_binding_for_all_namespaces: %s\n" % e)
    
    items = []
    for item in roleBindings.items:

        cleanedLabels = {}
        cleanedLabels.update(item.metadata.labels)

        cleanedRoleRef = {
            'apiGroup': item.role_ref.api_group,
            'kind': item.role_ref.kind,
            'name': item.role_ref.name
        }

        subjects = []
        for subject in item.subjects:
            cleanedSubject = {
                'kind': subject.kind,
                'name': subject.name,
                'namespace': subject.namespace
            }
            subjects.append(cleanedSubject)

        cleanedItem = {
            'metadata': {
                'name': item.metadata.name,
                'namespace': item.metadata.namespace,
                'labels': cleanedLabels
            },
            'roleRef': cleanedRoleRef,
            'subjects': subjects
        }
        items.append(cleanedItem)

    data['payload']['role_bindings']['items'] = items
    data['payload']['role_bindings']['count'] = len(roleBindings.items)


def enum_cluster_role_bindings(rbacAuthorizationV1Api, data):
    try:
        clusterRoleBindings = rbacAuthorizationV1Api.list_cluster_role_binding(watch=False)
    except ApiException as e:
        print("Exception when calling rbacAuthorizationV1Api->list_cluster_role_binding: %s\n" % e)

    items = []
    for item in clusterRoleBindings.items:
        cleanedLabels = {}
        cleanedLabels.update(item.metadata.labels)

        cleanedRoleRef = {
            'apiGroup': item.role_ref.api_group,
            'kind': item.role_ref.kind,
            'name': item.role_ref.name
        }

        subjects = []
        if item.subjects:
            for subject in item.subjects:
                cleanedSubject = {
                    'kind': subject.kind,
                    'name': subject.name,
                    'namespace': subject.namespace
                }
                subjects.append(cleanedSubject)

        cleanedItem = {
            'metadata': {
                'name': item.metadata.name,
                'namespace': item.metadata.namespace,
                'labels': cleanedLabels
            },
            'roleRef': cleanedRoleRef,
            'subjects': subjects
        }
        items.append(cleanedItem)


    data['payload']['cluster_role_bindings']['items'] = items
    data['payload']['cluster_role_bindings']['count'] = len(clusterRoleBindings.items)


def save_to_file(save_to_file_directory ,save_to_file_path ,data):
    os.makedirs(save_to_file_directory, exist_ok=True)
    with open(save_to_file_path, 'w+') as json_file:
        json.dump(data, json_file, indent=4, default=str)


def main(args):
    data  = {
        'count': 0,
        'payload': {
            'service_accounts': {
                'count': 0,
                'items': []
            },
            'roles': {
                'count': 0,
                'items': []
            },
            'cluster_roles': {
                'count': 0,
                'items': []
            },
            'role_bindings': {
                'count': 0,
                'items': []
            },
            'cluster_role_bindings': {
                'count': 0,
                'items': []
            }
        }
    }

    # Configure K8s context
    config.load_kube_config()

    current_context = config.list_kube_config_contexts()[1]

    # Congigure K8s Apis
    coreV1Api = client.CoreV1Api()
    rbacAuthorizationV1Api = client.RbacAuthorizationV1Api()

    # Enumerate
    enum_service_accounts(coreV1Api, data)
    enum_roles(rbacAuthorizationV1Api, data)
    enum_cluter_roles(rbacAuthorizationV1Api, data)
    enum_role_bindings(rbacAuthorizationV1Api, data)
    enum_cluster_role_bindings(rbacAuthorizationV1Api, data)

    # Save data
    save_to_file_directory = './data/k8s/{}'.format(current_context['name'])
    save_to_file_path = '{}/k8s__enum_subjects_roles_rolebindings.json'.format(save_to_file_directory)
    save_to_file(save_to_file_directory, save_to_file_path, data)
    module_info['data_saved'] = save_to_file_path

    return data


def summary(data):
    out = ''
    out += 'Total {} K8s Service Accounts Enumerated\n'.format(data['payload']['service_accounts']['count'])
    out += 'Total {} K8s Roles Enumerated\n'.format(data['payload']['roles']['count'])
    out += 'Total {} K8s Cluster Roles Enumerated\n'.format(data['payload']['cluster_roles']['count'])
    out += 'Total {} K8s Role Bindings Enumerated\n'.format(data['payload']['role_bindings']['count'])
    out += 'Total {} K8s Cluster Role Bindings Enumerated\n'.format(data['payload']['cluster_role_bindings']['count'])
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