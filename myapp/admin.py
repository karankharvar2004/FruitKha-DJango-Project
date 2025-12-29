from django.contrib import admin
from .models import User, Product, News, Contact, Wishlist, Cart


# Register your models here.
admin.site.register(User)
admin.site.register(Product)
admin.site.register(News)
admin.site.register(Contact)
admin.site.register(Wishlist)
admin.site.register(Cart)

