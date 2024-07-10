from flask import Flask, render_template, request

app = Flask(__name__)

# 首页路由
@app.route('/')
def index():
    return "hellow"


# 处理表单提交的路由
@app.route('/info')
def submit():
    # 在这里执行表单数据处理的逻辑
    return 'Form submitted successfully!'



if __name__ == '__main__':
    app.run(debug=True)