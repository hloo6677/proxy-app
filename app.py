import os
from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return "NekoBox Universal Proxy Bridge is Active!"

@app.route('/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy_catchall(subpath):
    # التقاط الرابط الكامل المطلوب تمريره عبر البروكسي
    target_url = request.url.replace(request.host_url, '', 1)
    
    # إصلاح تنسيق الروابط في حال تم إرسالها بشكل مباشر
    if target_url.startswith('http:/') and not target_url.startswith('http://'):
        target_url = target_url.replace('http:/', 'http://', 1)
    elif target_url.startswith('https:/') and not target_url.startswith('https://'):
        target_url = target_url.replace('https:/', 'https://', 1)
        
    if not target_url or target_url == '':
        return "Proxy Ready: Send target request.", 200

    try:
        # إزالة هيدر الهوست الأساسي لتجنب التعارض وتمرير الطلب بسلاسة
        headers = {key: value for key, value in request.headers if key.lower() != 'host'}
        
        if request.method == 'POST':
            resp = requests.post(target_url, headers=headers, data=request.get_data(), stream=True, timeout=20)
        else:
            resp = requests.get(target_url, headers=headers, stream=True, timeout=20)
            
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        response_headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]

        return Response(resp.content, resp.status_code, response_headers)
        
    except Exception as e:
        return f"Proxy Routing Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
