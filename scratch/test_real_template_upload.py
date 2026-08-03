import urllib.request
import urllib.error
import io
import os

t1_path = r"c:\Users\DELL\projects\Credit-Rating-Simulator\tests\fixtures\worked_examples\Worked_Example_TP2_Template_1_v3_0.docx"
t2_path = r"c:\Users\DELL\projects\Credit-Rating-Simulator\tests\fixtures\worked_examples\Worked_Example_TP2_Template_2_v3_0.xlsx"

with open(t1_path, "rb") as f:
    t1_bytes = f.read()

with open(t2_path, "rb") as f:
    t2_bytes = f.read()

boundary = '---------------------------9876543210'
body = io.BytesIO()

def add_field(name, val):
    body.write(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{val}\r\n'.encode('utf-8'))

def add_file(name, filename, content, content_type):
    body.write(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"; filename="{filename}"\r\nContent-Type: {content_type}\r\n\r\n'.encode('utf-8'))
    body.write(content)
    body.write(b'\r\n')

add_field('project_id', 'TP-2-Mid-Wind')
add_file('template1', 'Worked_Example_TP2_Template_1_v3_0.docx', t1_bytes, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
add_file('template2', 'Worked_Example_TP2_Template_2_v3_0.xlsx', t2_bytes, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
body.write(f'--{boundary}--\r\n'.encode('utf-8'))

data = body.getvalue()

headers = {
    'Content-Type': f'multipart/form-data; boundary={boundary}',
    'Content-Length': str(len(data))
}

opener = urllib.request.build_opener(urllib.request.ProxyHandler())
req = urllib.request.Request('https://credit-rating-simulator.web.app/api/upload', data=data, headers=headers, method='POST')

print("================================================================================")
print("UPLOADING REAL WORKED EXAMPLE TEMPLATES TO https://credit-rating-simulator.web.app/api/upload")
print("================================================================================")

try:
    resp = opener.open(req, timeout=60)
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
