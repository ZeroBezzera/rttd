import socket
import os
import json

HOST = '0.0.0.0'
PORT = 8080
ROOT = os.getcwd()

def guess_type(path):
    if path.endswith('.html'):
        return 'text/html'
    if path.endswith('.css'):
        return 'text/css'
    if path.endswith('.js'):
        return 'application/javascript'
    if path.endswith('.json'):
        return 'application/json'
    return 'application/octet-stream'

def read_http_request(conn):
    data = ''
    conn.settimeout(5)
    try:
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            data += chunk
            if '\r\n\r\n' in data:
                headers_part, _, rest = data.partition('\r\n\r\n')
                header_lines = headers_part.split('\r\n')
                content_length = 0
                for h in header_lines:
                    if h.lower().startswith('content-length:'):
                        content_length = int(h.split(':', 1)[1].strip())
                while len(rest) < content_length:
                    more = conn.recv(4096)
                    if not more:
                        break
                    rest += more
                return headers_part, rest
    except socket.timeout:
        pass
    return data, ''

def send_response(conn, status, body, content_type='text/plain'):
    if isinstance(body, unicode):
        body = body.encode('utf-8')
    header = 'HTTP/1.1 %s\r\nContent-Length: %d\r\nContent-Type: %s\r\nConnection: close\r\nAccess-Control-Allow-Origin: *\r\n\r\n' % (status, len(body), content_type)
    conn.sendall(header)
    conn.sendall(body)

def handle_exec(conn, body):
    try:
        req = json.loads(body)
    except Exception:
        send_response(conn, '400 Bad Request', json.dumps({'error': 'invalid json'}), 'application/json')
        return

    cmd = req.get('cmd', '')
    cwd = req.get('cwd', '/tmp')

    if not os.path.isdir(cwd):
        cwd = '/tmp'

    # Handle cd specially so cwd persists per-tab
    stripped = cmd.strip()
    if stripped == 'cd' or stripped.startswith('cd '):
        target = stripped[2:].strip()
        if target == '':
            new_cwd = '/root'
        elif target.startswith('/'):
            new_cwd = target
        else:
            new_cwd = os.path.normpath(os.path.join(cwd, target))

        if os.path.isdir(new_cwd):
            result = {'output': '', 'error': '', 'cwd': new_cwd}
        else:
            result = {'output': '', 'error': 'cd: no such directory: %s' % target, 'cwd': cwd}

        send_response(conn, '200 OK', json.dumps(result), 'application/json')
        return

    full_cmd = 'cd %s 2>/dev/null; %s' % (cwd, cmd)

    try:
        p = os.popen(full_cmd + ' 2>&1')
        output = p.read()
        p.close()
    except Exception as e:
        output = ''
        result = {'output': '', 'error': str(e), 'cwd': cwd}
        send_response(conn, '200 OK', json.dumps(result), 'application/json')
        return

    result = {'output': output, 'error': '', 'cwd': cwd}
    send_response(conn, '200 OK', json.dumps(result), 'application/json')

def handle_ls(conn, path):
    if not path:
        path = '/'
    if not os.path.isdir(path):
        send_response(conn, '404 Not Found', json.dumps({'error': 'not a directory'}), 'application/json')
        return

    entries = []
    try:
        names = os.listdir(path)
    except Exception as e:
        send_response(conn, '500 Error', json.dumps({'error': str(e)}), 'application/json')
        return

    names.sort()
    for name in names:
        full = os.path.join(path, name)
        is_dir = os.path.isdir(full)
        entries.append({'name': name, 'is_dir': is_dir})

    entries.sort(key=lambda e: (not e['is_dir'], e['name'].lower()))

    result = {'path': path, 'entries': entries}
    send_response(conn, '200 OK', json.dumps(result), 'application/json')

def handle_static(conn, path):
    if path == '/':
        path = '/terminal.html'
    safe_path = os.path.normpath(path).lstrip('/')
    full_path = os.path.join(ROOT, safe_path)

    if not full_path.startswith(ROOT):
        send_response(conn, '403 Forbidden', 'Forbidden')
        return

    if os.path.isfile(full_path):
        f = open(full_path, 'rb')
        data = f.read()
        f.close()
        send_response(conn, '200 OK', data, guess_type(full_path))
    else:
        send_response(conn, '404 Not Found', 'Not Found')

def parse_query(path):
    if '?' not in path:
        return path, {}
    base, qs = path.split('?', 1)
    params = {}
    for pair in qs.split('&'):
        if '=' in pair:
            k, v = pair.split('=', 1)
            params[k] = v.replace('%2F', '/').replace('%20', ' ')
        else:
            params[pair] = ''
    return base, params

def handle_connection(conn):
    try:
        headers_part, body = read_http_request(conn)
        if not headers_part:
            conn.close()
            return

        request_line = headers_part.split('\r\n')[0]
        parts = request_line.split(' ')
        if len(parts) < 2:
            conn.close()
            return

        method = parts[0]
        raw_path = parts[1]
        base_path, params = parse_query(raw_path)

        if method == 'OPTIONS':
            send_response(conn, '200 OK', '')
        elif base_path == '/exec' and method == 'POST':
            handle_exec(conn, body)
        elif base_path == '/ls':
            handle_ls(conn, params.get('path', '/'))
        else:
            handle_static(conn, base_path)

    except Exception as e:
        try:
            send_response(conn, '500 Internal Server Error', 'error: %s' % str(e))
        except Exception:
            pass
    finally:
        try:
            conn.close()
        except Exception:
            pass

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
    print 'TV Terminal serving on http://%s:%d/' % (HOST, PORT)

    while True:
        conn, addr = s.accept()
        handle_connection(conn)

if __name__ == '__main__':
    main()
