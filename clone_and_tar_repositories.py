
import os
import sys
import json
import subprocess
from base64 import b64decode
import tarfile

release_version = os.getenv('RELEASE_VERSION', '0.0.1')
destination_directory = os.getenv('DESTINATION_DIR', "brewpro")
destination_directory = f"{destination_directory}_{release_version}"
output_zip = f"{destination_directory}_archive"
output_tar = f"{destination_directory}_archive.tar.gz"
# brewpro_v0.0.1_archive.tar.gz
filename = os.getenv('DEPLOYMENT_FILENAME', 'deployment.json')


def create_tar_archive(source_dir, output_tar):
    with tarfile.open(output_tar, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def clone_repository(repo, target_version, destination_directory):
    token = os.getenv('GITHUB_TOKEN')
    github_organization = os.getenv('GITHUB_ORGANIZATION')
    repo_path = os.path.join(destination_directory, f"{repo}_")
    clone_url = f"https://x-access-token:{token}@github.com/{github_organization}/{repo}.git"

    subprocess.run(["git", "clone", "--depth", "1", "--branch",
                   target_version, clone_url, repo_path])


def main(json_data, destination_directory):
    repositories = json.loads(json_data)

    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    for repository in repositories:
        repo = repository["repository"]
        target_version = repository["target_version"]
        print(repo, target_version)
        clone_repository(repo, target_version, destination_directory)
    
    create_tar_archive(destination_directory, output_tar)


def flatten_json(data, flattened_data=[]):
    for key in data:
        for item in data[key]:

            if isinstance(item, dict):
                if item.get('target_version') == 'latest':
                    item['target_version'] = 'main'
            flattened_data.append(item)
    output_json = json.dumps(flattened_data, separators=(',', ':'))

    return output_json


if __name__ == '__main__':

    with open(filename, 'r') as data_file_ref:
        data = json.load(data_file_ref)

    json_data = flatten_json(data)

    main(json_data, destination_directory)
