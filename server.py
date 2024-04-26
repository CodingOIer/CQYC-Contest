import string
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
import json


class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request(self.path)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        body = json.loads(post_data.decode('utf-8'))
        self.handle_request(self.path, body)

    def handle_request(self, url, body=None):
        result = deal(url, body)
        if result[1] == '!':
            self.send_response(200)
            self.send_header(
                'Content-type', 'text/html, text/html; charset=UTF-8')
            self.end_headers()
            self.wfile.write(result.encode('utf-8'))
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(result.encode('utf-8'))


def run(server_class=HTTPServer, handler_class=MyHTTPRequestHandler, port=80):
    server_address = ('127.0.0.1', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd on {server_address[0]}:{server_address[1]}')
    httpd.serve_forever()


judge = 0

data = {}

template = {}

tokens = []

player = []


def rs(l=8):
    all = string.ascii_lowercase
    result = ''.join(random.choices(all, k=l))
    return result


def deal(url, body):
    if url == '/':
        with open('./Web/index.html', 'r', encoding='utf-8') as f:
            temp = f.readlines()
            result = ''
            for x in temp:
                result += x
            return result
    try:
        mode = body['mode']
        if mode == 'get':
            result = ''
            for name in player:
                mi = 0x3f3f3f3f
                ma = -0x3f3f3f3f
                su = 0
                cnt = 0
                for i in range(judge):
                    result += str(data[name][i]) + '|'
                    if data[name][i] != -1:
                        mi = min(mi, data[name][i])
                        ma = max(ma, data[name][i])
                        su += data[name][i]
                        cnt += 1
                result += f'{cnt}|{mi}|{ma}|{su}|{name}'
                result += '&'
            return result[:-1]
        elif mode == 'post':
            token = body['token']
            if not token in tokens:
                return 'Wrong Token'
            judger = -1
            for k in tokens:
                judger += 1
                if k == token:
                    break
            if not (0 <= judger and judger < 11):
                return 'Can Not Find Judger'
            name = body['name']
            want = body['point']
            data[name][judger] = want
            return 'Success To Change Data'
        else:
            return 'Unknown Mode'
    except:
        return 'Unknown Error'


if __name__ == '__main__':
    player_data = []
    with open('./data.txt', 'r', encoding='utf-8') as f:
        temp = f.readline()
        if (temp[-1] == '\n'):
            temp = temp[:-1]
        judge = int(temp)
        player_data = f.readlines()
    for x in player_data:
        if len(x) == 1 and x[-1] == '\n':
            continue
        if (x[-1] == '\n'):
            player.append(x[:-1])
        else:
            player.append(x)
    for name in player:
        data[name] = {}
        for i in range(judge):
            data[name][i] = -1
    with open('key.txt', 'w') as f:
        for i in range(judge):
            k = rs()
            tokens.append(k)
            f.write(f'{k}\n')
            print(k)
    run()
