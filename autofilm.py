from webdav3.client import Client
import argparse, os, requests, time

'''
遍历Webdav服务器函数
如果depth为None，则会递归遍历整个WebDAV服务器
如果depth为正整数，则会递归遍历到指定深度
如果depth为0，则只会遍历当前文件夹中的文件和文件夹，不会继续递归遍历下一级文件夹。
'''
def list_files(webdav_url, username, password, depth=None, path=''):
    options = {
        'webdav_hostname': webdav_url,
        'webdav_login': username,
        'webdav_password': password
    }

    client = Client(options)
    directory = []
    files = []
    q = 1
    while q < 15:
        try:
            items = client.list()
        except:
            print(f'第{q}次连接失败，{q+1}秒后重试...')
            q += 1
            time.sleep(q)
        else:
            if q > 1:
                print('重连成功...')
            break

    if q == 15:
        print('连接失败，请检查网络设置！')
        exit()

    for item in items[1:]:
        if item[-1] == '/':
            if depth is None or depth > 0:
                subdirectory, subfiles = list_files(webdav_url + item, username, password, depth=None if depth is None else depth - 1, path=path+item)
                directory += [item + subitem for subitem in subdirectory]
                files += [item + subitem for subitem in subfiles]
            else:
                directory.append(item)
        else:
            files.append(item)
    if path:
        print(f'当前文件夹路径：{path}')
    return directory, files

'''
下载函数
用于'ASS', 'SRT', 'SSA','NFO','JPG', 'PNG'文件的下载
'''   
def download_file(url, local_path, filename):
    p = 1
    while p < 10:
        try:
            print('正在下载：' + filename)
            r = requests.get(url.replace('/dav', '/d'))
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'wb') as f:
                f.write(r.content)
                f.close
        except:
            print(f'第{p}次下载失败，{p + 1}秒后重试...')
            p += 1
            time.sleep(p)
        else:
            if p > 1:
                print('重新下载成功！')
            print(filename + '下载成功！')
            break

parser = argparse.ArgumentParser(description='Autofilm script')
parser.add_argument('--webdav_url', type=str, help='WebDAV服务器地址')
parser.add_argument('--username', type=str, help='WebDAV账号')
parser.add_argument('--password', type=str, help='WebDAV密码')
parser.add_argument('--output_path', type=str, help='输出文件目录')
parser.add_argument('--subtitle', type=str, help='是否下载字幕文件', choices=['true', 'false'], default='true')
parser.add_argument('--nfo', type=str, help='是否下载NFO文件', choices=['true', 'false'], default='false')
parser.add_argument('--img', type=str, help='是否下载JPG和PNG文件', choices=['true', 'false'], default='false')
args = parser.parse_args()
# 检查参数是否为None，如果是则使用默认值
args.webdav_url = args.webdav_url or "http://example.com/webdav"
args.username = args.username or "your_username"
args.password = args.password or "your_password"
args.output_path = args.output_path or "/path/to/output"
args.subtitle = args.subtitle or 'true'
args.nfo = args.nfo or 'false'
args.img = args.img or 'false'          
print('启动参数：')
print(f'Webdav服务器地址：{args.webdav_url}')
print(f'Webdav登入用户名：{args.username}')
print(f'Webdav登入密码：{args.password}')
print(f'文件输出路径：{args.output_path}')
print(f'是否下载字幕：{args.subtitle}')
print(f'是否下载电影信息：{args.nfo}')
print(f'是否下载图片：{args.img}')

directory = list_files(args.webdav_url, args.username, args.password, depth=None, path='')[0]
files = list_files(args.webdav_url, args.username, args.password, depth=None, path='')[1]

urls = [args.webdav_url + item for item in directory + files]

for url in urls:
    if url[-1] == '/':
        continue
    filename = os.path.basename(url)
    local_path = os.path.join(args.output_path, url.replace(args.webdav_url, '').lstrip('/'))
    file_ext = filename[-3:].upper()

    if file_ext in ['MP4', 'MKV', 'FLV', 'AVI','RMVB','WMV','MOV','TS','WEBM','ISO','MPG']:
        if not os.path.exists(os.path.join(args.output_path, filename[:-3] + 'strm')):
            print('正在处理：' + filename)
            try:
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                with open(os.path.join(local_path[:-3] + 'strm'), "w", encoding='utf-8') as f:
                    f.write(url.replace('/dav', '/d'))
            except:
                print(filename + '处理失败，文件名包含特殊符号，建议重命名！')
    elif args.subtitle == 'true' and file_ext in ['ASS', 'SRT', 'SSA']:
        if not os.path.exists(local_path):
            download_file(url, local_path, filename)
    elif args.nfo == 'true' and file_ext == 'NFO':
        if not os.path.exists(local_path):
            download_file(url, local_path, filename)
    elif args.img == 'true' and file_ext in ['JPG', 'PNG']:
        if not os.path.exists(local_path):
            download_file(url, local_path, filename)

print('处理完毕！')
