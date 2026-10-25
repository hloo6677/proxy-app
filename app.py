import os
from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return "Proxy and Routing Server is Active!"

@app.route('/proxy')
def proxy_handler():
    # استقبال الرابط المطلوب تمريره عبر البارامتر
    target_url = request.args.get('url')
    if not target_url:
        return "Error: Please provide a 'url' parameter.", 400

    try:
        # نسخ الهيدر (Headers) القادمة وتجاوز هيدر الهوست الأساسي
        headers = {key: value for key, value in request.headers if key.lower() != 'host'}
        
        # جلب البيانات من المصدر عبر سيرفر البروكسي
        resp = requests.get(target_url, headers=headers, stream=True, timeout=15)
        
        # استثناء بعض الهيدرات لمنع تعارض الحجم أو التشفير
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        response_headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]

        # إعادة إرسال الستريم أو البيانات للمستخدم مباشرة
        return Response(resp.content, resp.status_code, response_headers)
        
    except Exception as e:
        return f"Proxy Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
