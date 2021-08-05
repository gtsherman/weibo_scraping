import argparse
import json
import re


def parse_args():
    opts = argparse.ArgumentParser(
        description='Create configuration file from list of URLs.')
    opts.add_argument('url_file', description='Requires one URL per line')
    opts.add_argument('config_template',
                      description='A JSON configuration template, fully filled out except'
                      ' for the user ID list (existing user ID list will be '
                      ' replaced)')
    return opts.parse_args()


def load_config(config_template):
    with open(config_template) as f:
        return json.load(f)


def load_urls(url_file):
    urls = []
    with open(url_file) as f:
        for url in f:
            urls.append(url)
    return urls


def url_to_id(url):
    id = re.search(r'(?:u|profile)/([A-Za-z0-9]+)', url)
    try:
        return id.group(1)
    except IndexError:
        return id.group(0)
    except AttributeError:
        return id


def generate_config(config, urls):
    ids = [url_to_id(url) for url in urls]
    config['user_id_list'] = ids
    return config


def main():
    args = parse_args()

    urls = load_urls(args.url_file)
    config = load_config(args.config_template)

    new_config = generate_config(config, urls)
    print(new_config)
