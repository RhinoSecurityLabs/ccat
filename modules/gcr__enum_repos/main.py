import fire

SAVE_TO_FILE_DIRECTORY = './data'
SAVE_TO_FILE_PATH = '{}/gcr__enum_repos_data.json'.format(SAVE_TO_FILE_DIRECTORY)

module_info = {
    'name': 'gcr__enum_repos',
    'author': 'Jack Ganbold of Rhino Security Labs',
    'category': 'ENUM',
    'one_liner': 'Enumerates GCR repositories.',
    'description': 'Enumerates GCR repositories.',
    'services': ['GCR'],
    'prerequisite_modules': [],
    'external_dependencies': [],
    'arguments_to_autocomplete': [],
    'data_saved': SAVE_TO_FILE_PATH
}

def set_args():
    return ''

def main(args):
    data  = {
        'count': 0
    }
    return data

def summary(data):
    out = ''
    out += '{} GCR Repositories Pushed\n'.format(data['count'])
    out += 'GCR recources saved under the {} path.\n'.format(SAVE_TO_FILE_PATH)
    return out

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
        
        print('{} completed.\n'.format(module_info['name']))
        print('MODULE SUMMARY:\n\n{}\n'.format(summary.strip('\n')))  