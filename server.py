import string
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, SquareModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask, SquareGradiantColorMask
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
pub_judge = 0

data = {}
pub_data = {}

tokens = []
pub_tokens = []

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
    elif url[:8] == '/teacher':
        with open('./Web/mobile/teacher.html', 'r', encoding='utf-8') as f:
            temp = f.readlines()
            result = ''
            for x in temp:
                result += x
            return result
    elif url[:8] == '/student':
        with open('./Web/mobile/student.html', 'r', encoding='utf-8') as f:
            temp = f.readlines()
            result = ''
            for x in temp:
                result += x
            return result
    elif url[:8] == '/players':
        result = ''
        for name in player:
            result += name + '&'
        result = result[:-1]
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
                pub = -1
                pmi = 0x3f3f3f3f
                pma = -0x3f3f3f3f
                psu = 0
                pnt = 0
                for i in range(judge):
                    result += str(data[name][i]) + '|'
                    if data[name][i] != -1:
                        mi = min(mi, int(data[name][i]))
                        ma = max(ma, int(data[name][i]))
                        su += int(data[name][i])
                        cnt += 1
                for i in range(pub_judge):
                    if pub_data[name][i] != -1:
                        pmi = min(pmi, int(pub_data[name][i]))
                        pma = max(pma, int(pub_data[name][i]))
                        psu += int(pub_data[name][i])
                        pnt += 1
                if (pnt >= 3):
                    pub = (psu - pmi - pma) / (pnt - 2)
                result += f'{pub}|{cnt}|{mi}|{ma}|{su}|{name}'
                result += '&'
            result += str(judge)
            return result
        elif mode == 'post':
            who = body['who']
            if who == 'teacher':
                token = body['token']
                if not token in tokens:
                    return 'Token 错误，请确保您通过二维码进入'
                judger = -1
                for k in tokens:
                    judger += 1
                    if k == token:
                        break
                if not (0 <= judger and judger < judge):
                    return '无法找到此评委'
                name = body['name']
                want = body['point']
                data[name][judger] = want
                return '提交成功'
            elif who == 'student':
                token = body['token']
                if not token in pub_tokens:
                    return 'Token 错误，请确保您通过二维码进入'
                judger = -1
                for k in pub_tokens:
                    judger += 1
                    if k == token:
                        break
                if not (0 <= judger and judger < pub_judge):
                    return '无法找到此评委'
                name = body['name']
                want = body['point']
                pub_data[name][judger] = want
                return '提交成功'
            else:
                return '未知角色'
        else:
            return '未知请求'
    except:
        return '未知错误（发送邮件到 codingoier-project@outlook.com）'


def mkQRCode(url, filename):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(url)
    img = qr.make_image(image_factory=StyledPilImage,
                        module_drawer=RoundedModuleDrawer())
    img.save(f'./{filename}')


if __name__ == '__main__':
    url = input('Input your URL\n')
    player_data = []
    with open('./data.txt', 'r', encoding='utf-8') as f:
        temp = f.readline()
        if (temp[-1] == '\n'):
            temp = temp[:-1]
        temp = temp.split(' ')
        judge = int(temp[0])
        pub_judge = int(temp[1])
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
    for name in player:
        pub_data[name] = {}
        for i in range(pub_judge):
            pub_data[name][i] = -1
    with open('key.txt', 'w') as f:
        for i in range(judge):
            k = rs()
            tokens.append(k)
            mk = f'{url}/teacher?{k}\n'
            f.write(mk)
            mkQRCode(mk, f'./qrcode/tea_{i}')
            print(k)
    with open('pub_key.txt', 'w') as f:
        for i in range(pub_judge):
            k = rs()
            pub_tokens.append(k)
            mk = f'{url}/student?{k}\n'
            f.write(mk)
            mkQRCode(mk, f'./qrcode/stu_{i}')
            print(k)
    run()
