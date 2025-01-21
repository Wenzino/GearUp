from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

# Product
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default = 0)
    image = models.ImageField(upload_to='products/')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True)
    specifications = models.TextField(blank=True)  # Para as especificações do produto
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']  # Ordena por padrão do mais recente para o mais antigo

# User
class User(models.Model):
    user_id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=255)
    email = models.EmailField()
    password = models.CharField(max_length=255)
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=60)
    is_staff = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username
    
# Order
class Order(models.Model):
    order_id = models.IntegerField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=45)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.oid
    
# OrderItem
class OrderItem(models.Model):
    order_item_id = models.IntegerField(primary_key=True)
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.order_item_id
    
# Payment
class Payment(models.Model): 
    payment_id = models.IntegerField(primary_key=True)
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=45)
    payment_status = models.CharField(max_length=45)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id

class Banner(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.TextField()
    image = models.ImageField(upload_to='banners/')
    button_text = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Feature(models.Model):
    icon = models.ImageField(upload_to='features/')
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Brand(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='brands/')
    url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class SectionContent(models.Model):
    SECTION_CHOICES = [
        ('latest_products', 'Latest Products Section'),
        ('coming_products', 'Coming Products Section'),
        ('deals_week', 'Deals of the Week Section'),
    ]
    
    section = models.CharField(max_length=50, choices=SECTION_CHOICES, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    products = models.ManyToManyField('Product', related_name='sections')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_section_display()} - {self.title}"

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1, 'A avaliação deve ser no mínimo 1'),
            MaxValueValidator(5, 'A avaliação deve ser no máximo 5')
        ]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        # Garante que um usuário só pode avaliar um produto uma vez
        unique_together = ('product', 'user')

    def __str__(self):
        return f'{self.user.username} - {self.product.name} - {self.rating} estrelas'

