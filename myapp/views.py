from django.shortcuts import render, redirect
from .models import User, Product, News, Contact, Wishlist, Cart
from django.core.mail import send_mail
from django.conf import settings
import random
from django.shortcuts import render, redirect, get_object_or_404
import requests
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import stripe


stripe.api_key = settings.STRIPE_PRIVATE_KEY
YOUR_DOMAIN = 'http://localhost:8000'


# Create your views here.
def index(request):
    products = Product.objects.order_by('?')[:3]

    try:
        user = User.objects.get(email=request.session['email'])

        if user.usertype == "buyer":
            return render(request, 'index.html', {
                'products': products
            })
        else:
            return render(request, 'seller-index.html')

    except:
        return render(request, 'index.html', {
            'products': products
        })

def about(request):
    return render(request,'about.html')

def contact(request):
    if 'email' not in request.session:
        return redirect('login')

    user = User.objects.get(email=request.session['email'])
    msg = None

    if request.method == "POST":
        Contact.objects.create(
            name=f"{user.fname} {user.lname}",
            email=user.email,
            phone=request.POST.get("phone"),
            subject=request.POST.get("subject"),
            message=request.POST.get("message"),
        )
        msg = "Thank you! Your message has been sent successfully."

    return render(request, "contact.html", {"user": user, "msg": msg})


def not_found(request):
    return render(request,'404.html')


def login(request):
    if request.method=="POST":
       try:
           user=User.objects.get(email=request.POST['email'])
           if user.password==request.POST['password']:
               request.session['email']=user.email
               request.session['fname']=user.fname
               request.session['profile_picture']=user.profile_picture.url
               wishlists=Wishlist.objects.filter(user=user)
               request.session['wishlist_count']=len(wishlists)
               carts=Cart.objects.filter(user=user,payment_status=False)
               request.session['cart_count']=len(carts)
               if user.usertype=="buyer":
                    return render(request,'index.html')
               else:
                    return render(request,'seller-index.html')
           else:
               msg="Incorrect Password"
               return render(request,'login.html',{'msg':msg})
       except:
            msg="Email Not Registered"
            return render(request,'login.html',{'msg':msg})
    else:
        return render(request,'login.html')

def signup(request):
    if request.method=="POST":
        try:
            user=User.objects.get(email=request.POST['email'])
            msg="Email Already Registered"
            return render(request,'login.html',{'msg':msg})
        except:
            if request.POST['password']==request.POST['cpassword']:
                User.objects.create(
                    fname=request.POST['fname'],
                    lname=request.POST['lname'],
                    email=request.POST['email'],
                    mobile=request.POST['mobile'],
                    address=request.POST['address'],
                    password=request.POST['password'],
                    profile_picture=request.FILES['profile_picture'],
                    usertype=request.POST['usertype'],
                )
                msg="User SignUp Successfully"
                return render(request,'login.html',{'msg':msg})
            else:
                msg="Password & Confirm Password Does Not Matched"  
                return render(request,'signup.html',{'msg':msg})        
    else:
        return render(request,'signup.html')
    
def logout(request):
    try:
        del request.session['email']
        del request.session['fname']
        del request.session['profile_picture']
        msg="Logged Out Successfully"
        return render(request,'login.html',{'msg':msg})
    except:
        msg="Logged Out Successfully"
        return render(request,'login.html',{'msg':msg})
    
def profile(request):
    if 'email' not in request.session:
        return redirect('login')
    
    user=User.objects.get(email=request.session['email'])
    if request.method=="POST":
        user.fname=request.POST['fname']
        user.lname=request.POST['lname']
        user.mobile=request.POST['mobile']
        user.address=request.POST['address']
        try:
            user.profile_picture=request.FILES['profile_picture']
        except:
            pass
        user.save()
        request.session['profile_picture']=user.profile_picture.url
        msg="Profile Updated Successfully"
        if user.usertype=="buyer":
            return render(request,'profile.html',{'user':user, 'msg':msg})
        else:
            return render(request,'seller-profile.html',{'user':user, 'msg':msg})
    else:
        if user.usertype=="buyer":
            return render(request,'profile.html',{'user':user})
        else:
            return render(request,'seller-profile.html',{'user':user})
    
def change_password(request):
    user=User.objects.get(email=request.session['email'])
    if request.method=="POST":
        if user.password==request.POST['old_password']:
            if request.POST['new_password']==request.POST['cnew_password']:
                if user.password!=request.POST['new_password']:
                    user.password=request.POST['new_password']
                    user.save()
                    del request.session['email']
                    del request.session['fname']
                    del request.session['profile_picture']
                    msg="Password Changed Successfully"
                    return render(request,'login.html',{'msg':msg})
                else:
                    msg="Your New Password Can't be Your Old Password"
                    if user.usertype=="buyer":
                        return render(request,'change-password.html',{'msg':msg})
                    else:
                        return render(request,'seller-change-password.html',{'msg':msg})                   
            else:
                msg="New Password and Confirm New Passsword Does Not Matched"
                if user.usertype=="buyer":
                    return render(request,'change-password.html',{'msg':msg})
                else:
                    return render(request,'seller-change-password.html',{'msg':msg})                   
        else:
            msg="Old Password Does Not Matched"
            if user.usertype=="buyer":
                return render(request,'change-password.html',{'msg':msg})
            else:
                return render(request,'seller-change-password.html',{'msg':msg})                   
    else:
        if user.usertype=="buyer":
            return render(request,'change-password.html')
        else:
            return render(request,'seller-change-password.html')

def forgot_password(request):
    if request.method=="POST":
        try:
            user=User.objects.get(email=request.POST['email'])
            otp=random.randint(1000,9999)
            context = {}
            address = request.POST['email']
            subject = 'OTP for Forgot Password'
            message = 'Hello, Your OTP for Forgot password is '+str(otp)
            
            if address and subject and message:
                try:
                    send_mail(subject, message, settings.EMAIL_HOST_USER, [address])
                    context['result'] = 'Email sent successfully'
                    request.session['email1']=request.POST['email']
                    request.session['otp']=otp                
                except Exception as e:
                    context['result'] = f'Error sending email: {e}'
            else:
                context['result'] = 'All fields are required'
    
            return render(request, "otp.html", context)
        except Exception as e:
            print(e)
            msg="Email Not Registered" 
            return render(request,'forgot-password.html',{'msg':msg})
    else:
        return render(request,'forgot-password.html')
    
def verify_otp(request):
    if 'otp' in request.session and str(request.session['otp']) == request.POST['otp']:
        del request.session['otp']
        return render(request, 'new-password.html')
    else:
        msg = "Invalid OTP"
        return render(request, "otp.html", {'msg': msg})
    
def new_password(request):
    if request.POST['new_password']==request.POST['cnew_password']:
        user=User.objects.get(email=request.session['email1'])
        user.password=request.POST['new_password']
        user.save()
        msg="password updated sucessfully"
        del request.session['email1']
        return render(request,'login.html',{'msg':msg})
    else:
        msg="New Password & confirm new password does not matched"
        return render(request,'new-password.html',{'msg':msg})
    
def add_product(request):
    seller = User.objects.get(email=request.session['email'])

    if request.method == "POST":
        product_category = request.POST.get('product_category')
        product_name = request.POST.get('product_name')
        product_price = request.POST.get('product_price')
        product_desc = request.POST.get('product_desc')
        product_image = request.FILES.get('product_image')

        if not product_category:
            return render(request, 'add-product.html', {
                'msg': 'Please select a product category'
            })

        Product.objects.create(
            seller=seller,
            product_category=product_category,
            product_name=product_name,
            product_price=product_price,
            product_desc=product_desc,
            product_image=product_image,
        )

        return render(request, 'add-product.html', {
            'msg': 'Product Added Successfully'
        })

    return render(request, 'add-product.html')
    
def view_product(request):
    seller = User.objects.get(email=request.session['email'])
    selected_category = request.GET.get('category')

    products = Product.objects.filter(seller=seller)

    if selected_category:
        products = products.filter(
            product_category__iexact=selected_category
        )

    return render(request, 'view-product.html', {
        'products': products,
        'selected_category': selected_category
    })


def seller_profile(request):
    user=User.objects.get(email=request.session['email'])
    if request.method=="POST":
        user.fname=request.POST['fname']
        user.lname=request.POST['lname']
        user.mobile=request.POST['mobile']
        user.address=request.POST['address']
        try:
            user.profile_picture=request.FILES['profile_picture']
        except:
            pass
        user.save()
        request.session['profile_picture']=user.profile_picture.url
        msg="Profile Updated Successfully"
        if user.usertype=="buyer":
            return render(request,'profile.html',{'user':user, 'msg':msg})
        else:
            return render(request,'seller-profile.html',{'user':user, 'msg':msg})
    else:
        if user.usertype=="buyer":
            return render(request,'profile.html',{'user':user})
        else:
            return render(request,'seller-profile.html',{'user':user})

def seller_product_details(request,pk):
    product=Product.objects.get(pk=pk)
    return render(request,'seller-product-details.html',{'product':product})

def seller_product_edit(request,pk):
    product=Product.objects.get(pk=pk)
    if request.method=="POST":
        product.product_category=request.POST['product_category']
        product.product_name=request.POST['product_name']
        product.product_price=request.POST['product_price']
        product.product_desc=request.POST['product_desc']
        try:
            product.product_image=request.FILES['product_image']
        except:
            pass
        product.save()
        return redirect('view-product')
    else:
        return render(request,'seller-product-edit.html',{'product':product})
    
def seller_product_delete(request,pk):
    product=Product.objects.get(pk=pk)
    product.delete()
    return redirect('view-product')

def category(request):
    selected_category = request.GET.get('category')

    products = Product.objects.all()

    if selected_category:
        products = products.filter(
            product_category__iexact=selected_category
        )

    return render(request, 'category.html', {
        'products': products,
        'selected_category': selected_category
    })


def news(request):
    all_news = News.objects.all().order_by('-news_date')
    return render(request, 'news.html', {
        'news': all_news
    })

def view_news(request):
    news = News.objects.all().order_by('-news_date')
    return render(request, 'view-news.html', {'news': news})


def add_news(request):
    seller = User.objects.get(email=request.session['email'])

    if request.method == "POST":
        news_title = request.POST.get('news_title')
        news_date = request.POST.get('news_date')
        news_desc = request.POST.get('news_desc')
        news_image = request.FILES.get('news_image')

        News.objects.create(
            seller=seller,
            news_title=news_title,
            news_date=news_date,
            news_desc=news_desc,
            news_image=news_image
        )

        return render(request, 'add-news.html', {
            'msg': 'News Added Successfully'
        })

    return render(request, 'add-news.html')

def seller_news_details(request,pk):
    news=News.objects.get(pk=pk)
    return render(request,'seller-news-details.html',{'news':news})

def seller_news_edit(request, pk):
    news = get_object_or_404(News, pk=pk)

    if request.method == "POST":
        news.news_title = request.POST.get('news_title')
        news.news_date = request.POST.get('news_date')
        news.news_desc = request.POST.get('news_desc')

        if 'news_image' in request.FILES:
            news.news_image = request.FILES['news_image']

        news.save()
        return redirect('seller-news-details', pk=news.pk)

    return render(request, 'seller-news-edit.html', {'news': news})

def seller_news_delete(request,pk):
    news=News.objects.get(pk=pk)
    news.delete()
    return redirect('seller-news-details, pk=news.pk')

def product_details(request,pk):
    wishlist_flag=False
    cart_flag=False
    user=User()
    try:
        user=User.objects.get(email=request.session['email'])
    except:
        pass
    product=Product.objects.get(pk=pk)
    try:
        Wishlist.objects.get(user=user,product=product)
        wishlist_flag=True
    except:
        pass
    try:
        Cart.objects.get(user=user,product=product,payment_status=False)
        cart_flag=True
    except:
        pass
    return render(request, 'product-details.html',{'product':product,'wishlist_flag':wishlist_flag,'cart_flag':cart_flag})

def add_to_wishlist(request,pk):
    product=Product.objects.get(pk=pk)
    user=User.objects.get(email=request.session['email'])
    Wishlist.objects.create(user=user,product=product)
    return redirect('wishlist')

def wishlist(request):
    if 'email' not in request.session:
        return redirect('login')
    
    user=User.objects.get(email=request.session['email'])
    wishlists=Wishlist.objects.filter(user=user)
    request.session['wishlist_count']=len(wishlists)
    return render(request,'wishlist.html',{'wishlists':wishlists})

def remove_from_wishlist(request,pk):
    product=Product.objects.get(pk=pk)
    user=User.objects.get(email=request.session['email'])
    wishlist=Wishlist.objects.get(user=user,product=product)
    wishlist.delete()
    return redirect('wishlist')

def add_to_cart(request,pk):
    product=Product.objects.get(pk=pk)
    user=User.objects.get(email=request.session['email'])
    Cart.objects.create(
        user=user,
        product=product,
        product_price=product.product_price,
        product_qty=1,
        total_price=product.product_price,
        payment_status=False,
        )
    return redirect('cart')

def cart(request):
    if 'email' not in request.session:
        return redirect('login')
    
    net_price=0
    user=User.objects.get(email=request.session['email'])
    carts=Cart.objects.filter(user=user,payment_status=False)
    for i in carts:
        net_price=net_price+i.total_price
    request.session['cart_count']=len(carts)
    return render(request,'cart.html',{'carts':carts,'net_price':net_price})

def remove_from_cart(request,pk):
    product=Product.objects.get(pk=pk)
    user=User.objects.get(email=request.session['email'])
    cart=Cart.objects.get(user=user,product=product,payment_status=False)
    cart.delete()
    return redirect('cart')

def change_qty(request):
    cart=Cart.objects.get(pk=int(request.POST['cid']))
    product_qty=int(request.POST['product_qty'])
    cart.total_price=cart.product_price*product_qty
    cart.product_qty=product_qty
    cart.save()
    return redirect('cart')

@csrf_exempt
def create_checkout_session(request):
	amount = int(json.load(request)['post_data'])
	final_amount=amount*100
	user=User.objects.get(email=request.session['email'])
	user_name=f"{user.fname} {user.lname}"
	user_address=f"{user.address}"
	user_mobile=f"{user.mobile}"
	session = stripe.checkout.Session.create(
		payment_method_types=['card'],
		line_items=[{
			'price_data': {
				'currency': 'inr',
				'unit_amount': final_amount,
				'product_data': {
					'name': 'Checkout Session Data',
					'description':f'''Customer:{user_name},\n\n
					Address:{user_address},\n
					Mobile:{user_mobile}''',
				},
			},
			'quantity': 1,
			}],
		mode='payment',
		success_url=YOUR_DOMAIN + '/success.html',
		cancel_url=YOUR_DOMAIN + '/cancel.html',
		customer_email=user.email,
		shipping_address_collection={
			'allowed_countries':['IN'],
		}
		)
	return JsonResponse({'id': session.id})

def success(request):
    email = request.session.get('email')
    if not email:
        return redirect('login')

    user = User.objects.get(email=email)

    # Mark all cart items as paid
    Cart.objects.filter(
        user=user,
        payment_status=False
    ).update(payment_status=True)

    # Reset cart count
    request.session['cart_count'] = 0

    return redirect('myorder')


def cancel(request):
	return render(request,'cancel.html')

def myorder(request):
    email = request.session.get('email')
    if not email:
        return redirect('login')

    user = User.objects.get(email=email)
    carts = Cart.objects.filter(user=user, payment_status=True)

    return render(request, 'myorder.html', {'carts': carts})