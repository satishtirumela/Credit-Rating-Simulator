import urllib.request
import urllib.error
import io

boundary = '---------------------------1234567890'
body = io.BytesIO()

def add_field(name, val):
    body.write(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{val}\r\n'.encode('utf-8'))

def add_file(name, filename, content, content_type):
    body.write(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"; filename="{filename}"\r\nContent-Type: {content_type}\r\n\r\n'.encode('utf-8'))
    body.write(content)
    body.write(b'\r\n')

add_field('project_id', 'TP-2-Mid-Wind')
add_file('template1', 'test.docx', b'fake docx content', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
add_file('template2', 'test.xlsx', b'fake xlsx content', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
body.write(f'--{boundary}--\r\n'.encode('utf-8'))

data = body.getvalue()

headers = {
    'Content-Type': f'multipart/form-data; boundary={boundary}',
    'Content-Length': str(len(data))
}

opener = urllib.request.build_opener(urllib.request.ProxyHandler())
req = urllib.request.Request('https://credit-rating-simulator.web.app/api/upload', data=data, headers=headers, method='POST')

print("================================================================================")
print("SENDING POST /api/upload TO https://credit-rating-simulator.web.app/api/upload")
print("================================================================================")

try:
    resp = opener.open(req, timeout=15)
    print('HTTP Status:', resp.getcode())
    print('FULL RESPONSE BODY:')
    print(resp.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print('HTTP Error Code:', e.code)
    print('FULL HTTP ERROR RESPONSE BODY:')
    print(e.read().decode('utf-8'))
except Exception as e:
    print('Error:', e)

print("================================================================================")
