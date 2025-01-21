from flask import Flask, render_template
from data import Articles

app = Flask (__name__)

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/articles')
def articles():
    return render_templates('articles.html', articles = Articles)

@app.route('/article/<string:id>/')
def article(id)
    return render_templates('article.html', id=id)
    
if __name__ == '__main__':
    app.run(debug=True)
  
