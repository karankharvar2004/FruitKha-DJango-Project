from django.db import models
from django.utils import timezone


# Create your models here.
class User(models.Model):
    fname=models.CharField(max_length=100)
    lname=models.CharField(max_length=100)
    email=models.EmailField()
    mobile=models.PositiveIntegerField()
    address=models.TextField()
    password=models.CharField(max_length=100)
    profile_picture=models.ImageField(upload_to="profile_picture/")
    usertype=models.CharField(max_length=100,default="buyer")
    
    def __str__(self):
        return self.fname+" "+self.lname
    
class Product(models.Model):
    category = (
        ("berry","berry"),
        ("tropical","tropical"),
        ("citrus","citrus"),
        ("seeded","seeded"),
        ("coastal","coastal"),
        ("special","special"),
        ("superfood","superfood"),
    )

    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    product_category = models.CharField(max_length=100, choices=category)
    product_name = models.CharField(max_length=100)
    product_price = models.PositiveBigIntegerField()
    product_desc = models.TextField()
    product_image = models.ImageField(upload_to="product_image/", null=True, blank=True)

    def __str__(self):
        return self.seller.fname + " - " + self.product_name
    
class News(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    news_title = models.CharField(max_length=200)
    news_image = models.ImageField(upload_to='news_image/', blank=True, null=True)
    news_desc = models.TextField()
    news_date = models.DateField(default=timezone.now)

    def __str__(self):
        return self.news_title
    
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=150)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"
    
class Wishlist(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    time=models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.user.fname+" - "+self.product.product_name
    
class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    time=models.DateTimeField(default=timezone.now)
    product_price=models.PositiveBigIntegerField()
    product_qty=models.PositiveIntegerField()
    total_price=models.PositiveIntegerField()
    payment_status=models.BooleanField(default=False)
    
def __str__(self):
    return self.user.fname+" - "+self.product.product_name