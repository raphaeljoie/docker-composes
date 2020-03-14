import argparse
import logging
import os

import yaml


def prepend_relative_path(parent, path):
    if path[0:2] == './':
        path = path[2:]

    return f"./{parent}/{path}"


def check_version(docker_compose, version):
    if 'version' not in docker_compose:
        raise BaseException('Missing version')

    if version is None:
        version = docker_compose['version']

    if version != docker_compose['version']:
        raise BaseException(f"Version mismatch: found {docker_compose['version']} instead of {version}")

    return version


def find_docker_compose_file_path(path):
    if path[0] == '/':
        raise BaseException('only relative path accepted')

    if path[0:2] == './':
        path = path[2:]

    if os.path.isdir(f"{path}"):
        if path[-1] == '/':
            path = path[:-1]
        path = f"{path}/docker-compose.yml"

    if not os.path.isfile(path):
        raise BaseException(f'{path} is not a file')

    return path


def append(dc1, dc2):
    pass


def prepend_build_path(definition, dir_path):
    if 'build' in definition:
        if isinstance(definition['build'], str):
            definition['build'] = prepend_relative_path(dir_path, definition['build'])
        else:
            raise BaseException('NOT YET IMPLEMENTED: volume as object. Only string accepted')


def prepend_volumes_paths(definition, dir_path):
    if 'volumes' in definition:
        for i in range(len(definition['volumes'])):
            volume = definition['volumes'][i]
            if isinstance(volume, str):
                volume_comp = volume.split(':')
                volume_comp[0] = prepend_relative_path(dir_path, volume_comp[0])
                volume = ':'.join(volume_comp)
            else:
                raise BaseException('NOT YET IMPLEMENTED: volume as object. Only string accepted')
            definition['volumes'][i] = volume


def solve_port_conflicts(service, service_definition, ports_used):
    if 'ports' in service_definition:
        for i in range(len(service_definition['ports'])):
            port = service_definition['ports'][i]

            if isinstance(port, str):
                port_comp = port.split(':')
                port_comp[0] = int(port_comp[0])
                while port_comp[0] in ports_used:
                    port_comp[0] += 1
                ports_used[port_comp[0]] = service
                port_comp[0] = str(port_comp[0])
                port = ':'.join(port_comp)
            else:
                raise BaseException('NOT YET IMPLEMENTED: volume as object. Only string accepted')

            service_definition['ports'][i] = port


def combine(paths):
    version = None
    services = {}
    ports = {}
    counter = 0

    for path in paths:
        path = find_docker_compose_file_path(path)
        dir_path = os.path.dirname(path)

        docker_compose = yaml.load(open(path), Loader=yaml.FullLoader)

        # VERSION
        version = check_version(docker_compose, version)

        # SERVICES
        if 'services' in docker_compose:
            for service, service_definition in docker_compose['services'].items():
                service = f'{counter}-{service}'
                prepend_build_path(service_definition, dir_path)
                prepend_volumes_paths(service_definition, dir_path)
                solve_port_conflicts(service, service_definition, ports)

                services[service] = service_definition

        counter += 1

    return {
        'version': version,
        'services': services
    }


parser = argparse.ArgumentParser(description='Combine Docker compose files.')
parser.add_argument('paths', metavar='path', type=str, nargs='+',
                    help='a relative path to a docker-compose file, or a directory containing such a file')

args = parser.parse_args()

paths = args.paths
destination = 'docker-compose.yml'

docker_composes = combine(paths)

# TODO allow other destination, but without sub directory (+ must be yaml?)
if os.path.exists(destination):
    overwrite = input(f"overwrite '{destination}'? [y/n]: ")

    if overwrite != 'y':
        logging.info(f"{destination} not updated")
        exit(0)

with open(destination, 'w') as outfile:
    yaml.dump(docker_composes, outfile, default_flow_style=False)
