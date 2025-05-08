from django.db import models

# Create your models here.
from django.db import models


class User(models.Model):
    USER_TYPES = [
        ('kiracı', 'Kiracı'),
        ('ev sahibi', 'Ev Sahibi'),
        ('alıcı', 'Alıcı'),
        ('satıcı', 'Satıcı'),
    ]

    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES)

    def __str__(self):
        return self.full_name


class Address(models.Model):
    city = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    neighborhood = models.CharField(max_length=50)
    street = models.CharField(max_length=50)
    building_number = models.CharField(max_length=10)
    apartment_number = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.street} {self.building_number}, {self.neighborhood}, {self.district}, {self.city}"


class Property(models.Model):
    # address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    square_meters = models.DecimalField(max_digits=10, decimal_places=2)
    room_count = models.IntegerField()
    heating_type = models.CharField(max_length=50, null=True, blank=True)
    # current_owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='owned_properties')
    current_owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    adres_kodu = models.CharField(max_length=20, unique=True, null=False, blank=False)

    def __str__(self):
        return f"{self.address} - {self.square_meters} m²"


class PropertyOwner(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    ownership_start_date = models.DateField()
    ownership_end_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('property', 'owner', 'ownership_start_date')

    def __str__(self):
        return f"{self.owner} -> {self.property} ({self.ownership_start_date} - {self.ownership_end_date or 'devam'})"


class PropertyTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('satış', 'Satış'),
        ('kiralama', 'Kiralama'),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.transaction_type.title()} - {self.user} - {self.property}"


class PropertySale(models.Model):
    property = models.OneToOneField(Property, on_delete=models.CASCADE, primary_key=True)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    sale_price = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"{self.property} satıldı -> {self.buyer}"


class PropertyRental(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    tenant = models.ForeignKey(User, on_delete=models.CASCADE)
    rent_price = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('property', 'tenant', 'start_date')

    def __str__(self):
        return f"{self.property} kirada -> {self.tenant}"
