import json


def generate_proxies(proxies_path):
    with open(f"{proxies_path}", "r") as proxies_file:
        try:
            proxies_input = json.load(proxies_file)
        except Exception as exception:
            print(exception)
        for key, value in proxies_input[0].items():
            if key == 'proxy':
                port = str(value['port'])
                host = value['ip']
            elif key == 'provider':
                user = value['credentials']['username']
                password = value['credentials']['password']
    return host, port, user, password


IP, PORT, USER, PASS = generate_proxies('proxy.json')
