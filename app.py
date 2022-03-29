import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from flask import Flask, redirect, url_for, render_template, request, jsonify
import json
import numpy as np
import tensorflow as tf

interpreter = tf.lite.Interpreter(model_path="tflite_qaware_model.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()


storebranches = None
products = None
data_columns = None
model = None



with open("columns.json", "r") as f:
    data_columns = json.load(f)['data_columns']
    storebranches = data_columns[1:5122]
    products = data_columns[5122:7487]

app = Flask(__name__)
@app.route('/')
def home():
    return  render_template('app.html')




def get_store_branch():
    return storebranches


def get_product_names():
    return products


@app.route('/get_store_branches', methods=['GET'])
def get_store_names():
    response = jsonify({
        'storebranches': get_store_branch()
    })
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@app.route('/product', methods=['GET'])
def get_products():
    response = jsonify({
        'products': get_product_names()
    })
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response





@app.route('/success/<int:score>')
def success(score):
    exp = {'Total Quantity': score}
    return render_template('result.html', result=exp)


@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if request.method == 'POST':
        storebranch = request.form['StoreBranch']
        product = request.form['Product']
        month = int(request.form['month'])
    try:
        storebranch_index = data_columns.index(storebranch.lower())

    except:
        storebranch_index = -1
    try:
        product_index = data_columns.index(product.lower())
    except:
        product_index = -1

    x = [0] * (len(data_columns))
    if month >= 1 and month <= 12:
        x[0] = month
    else:
        return render_template('validation.html')

    if storebranch_index >= 0:
        x[storebranch_index] = 1
    if product_index >= 0:
        x[product_index] = 1

    input_data = np.array([x], dtype=np.float32)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    total_score = interpreter.get_tensor(output_details[0]['index'])

    return redirect(url_for('success', score=abs(int(total_score))))






if __name__ == '__main__':

    app.run(debug=True)
