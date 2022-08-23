from django.shortcuts import render
from .models import *
import json
import datetime
from django.http import JsonResponse
from . utils import cookieCart, cartData , guestOrder



def store(request):
	data = cookieCart(request)
	cartItems = data['cartItems']
	products = Product.objects.all()
	context= {'products':products, 'cartItems':cartItems}
	return render(request, 'store/store.html', context)

def cart(request):
	data = cookieCart(request)
	items = data['items']
	order = data['order']
	cartItems = data['cartItems']
	context= {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)

def checkout(request):
	data = cookieCart(request)
	items = data['items']
	order = data['order']
	cartItems = data['cartItems']
	context= {'items':items, 'order':order, 'cartItems':cartItems }
	return render(request, 'store/checkout.html', context)

def updateItem(request):
	# we get the data form frontenn by helping from js and token that created in the main.html
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)
	#Here we use the data from frontend to get the real objects on the backend, like we generate product based on customerId and create or get into order and create or get into orderItem that based on product.
	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)
	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product) 

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)
	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse("Item was added", safe=False)


def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		
	else:
		print("user not logged in...")

		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id
	
	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
			customer= customer,
			order = order,
			address = data['shipping']['address'],
			city = data['shipping']['city'],
			state = data['shipping']['state'],
			zipcode = data['shipping']['zipcode'],
			)


	return JsonResponse('Payment subbmitted..',safe=False)



