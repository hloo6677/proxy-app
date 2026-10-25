import os
from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return "Dark Proxy Bridge is Active and Running!"

@app.route('/proxy', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy_handler():
    # استقبال الرابط أو الهدف المطلوب تمريره عبر الترافيك
    target_url = request.args.get('url')
    
    if not target_url:
        return "Proxy Active: Send target URL via ?url=...", 200

    try:
        # تجهيز الهيدرات وتجاوز هيدر الهوست الأساسي لضمان عدم الحظر
        headers = {key: value for key, value in request.headers if key.lower() != 'host'}
        
        # تمرير الطلب بناءً على نوع الطلب (GET أو POST)
        if request.method == 'POST':
            resp = requests.post(target_url, headers=headers, data=request.get_data(), stream=True, timeout=20)
        else:
            resp = requests.get(target_url, headers=headers, stream=True, timeout=20)
        
        # استثناء الهيدرات المعارضة لضمان سلاسة تدفق البيانات
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        response_headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]

        # إرجاع الاستجابة الكاملة والسريعة للمستخدم
        return Response(resp.content, resp.status_code, response_headers)
        
    except Exception as e:
        return f"Proxy Tunnel Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
