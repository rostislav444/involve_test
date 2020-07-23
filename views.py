from app import app
from flask import Response, url_for, send_from_directory, jsonify
from flask import request, redirect
from flask import render_template
import os, json
from models import Order
from playhouse.shortcuts import model_to_dict, dict_to_model
import requests 


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route('/', methods=['GET', 'POST'])
def home():
    msgs = {}
    def make_request(url, data, headers, order):
        response = requests.post(url, data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            response = response.json()
            order.response = response
            order.save()
            if 'error_code' in response.keys():
                if response['error_code'] == 0:
                    return response
                else: 
                    msgs['error'] = response["message"]
        else:
            msgs['error'] = "request error."
        return None
    
    if request.method == "POST":
        shop_id = 5
        secretKey = 'SecretKey01'
        data = request.form
        payways = {'643' : 'payeer_rub'}
        context = {
            'amount' : data['amount'],
            'currency' : data['currency'],
            'description' : data['description'],
            'shop_id' : shop_id,
            'secret_key' : secretKey,
            'payway' : payways[data['currency']] if data['currency'] in payways.keys() else None,
        }
        order = Order(**context)
        order.save()
        
        if order.sign:
            # EUR
            if data['currency'] == '978':
                return render_template('pages/eur.html', order=order)
            # USD
            elif data['currency'] == '840':
                url = "https://core.piastrix.com/bill/create"
                headers = {"Content-Type": "application/json",}
                data = { 
                    "payer_currency": order.currency,
                    "shop_amount": order.amount,
                    "shop_currency": order.currency,
                    "shop_id": order.shop_id,
                    "shop_order_id": order.id,
                    "sign": order.sign
                }
                response = make_request(url, data, headers, order)
                if response: 
                    return redirect(response['data']['url'], code=302) 
            # RUB
            elif data['currency'] == '643':
                url = "https://core.piastrix.com/invoice/create"
                headers = {"Content-Type": "application/json"}
                data = {
                    "amount":  order.amount,
                    "currency": order.currency,
                    "payway": order.payway,
                    "shop_id": order.shop_id,
                    "shop_order_id": order.id,
                    "sign":order.sign
                }
                response = make_request(url, data, headers, order)
                if response: 
                    return render_template('pages/rub.html', order=order, context=response['data']['data'])
        else:
            msgs['error'] = "Sing was not created"
    return render_template('home.html', msgs=msgs)


@app.route('/log')
def log():
    orders = Order.select()
    objs = []
    for order in orders:
        obj = {
            'amount' : float(order.amount),
            'currency' : order.currency,
            'id' : order.id,
            'sign' : order.sign,
            'date' : order.date,
            'response' : order.response,
            'description' : order.description
        }
        objs.append(obj)
    return jsonify(objs)


@app.route('/clear')
def clear():
    for order in Order.select():
        order.delete_instance()
    return redirect("/log", code=302)
    







