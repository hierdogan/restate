from django import forms
from .models import Property, PropertySale, PropertyRental, Address


class PropertyForm(forms.ModelForm):
    city = forms.CharField(label="Şehir")
    district = forms.CharField(label="İlçe")
    neighborhood = forms.CharField(label="Mahalle")
    street = forms.CharField(label="Cadde/Sokak")
    site_name = forms.CharField(label="Site Adı", required=False)
    building_number = forms.CharField(label="Bina No")
    apartment_number = forms.CharField(label="Kapı No")

    class Meta:
        model = Property
        fields = ['description', 'square_meters', 'room_count', 'heating_type', 'current_owner']

    def save(self, commit=True):
        # önce adres objesini oluştur
        address = Address.objects.create(
            city=self.cleaned_data['city'],
            district=self.cleaned_data['district'],
            neighborhood=self.cleaned_data['neighborhood'],
            street=self.cleaned_data['street'],
            building_number=self.cleaned_data['building_number'],
            apartment_number=self.cleaned_data['apartment_number']
        )

        property_instance = super().save(commit=False)
        property_instance.address = address

        if commit:
            property_instance.save()
        return property_instance




# class PropertyForm(forms.ModelForm):
#     class Meta:
#         model = Property
#         fields = ['address', 'description', 'square_meters', 'room_count', 'heating_type', 'current_owner']


class PropertySaleForm(forms.ModelForm):
    class Meta:
        model = PropertySale
        fields = ['property', 'buyer', 'sale_price']


class PropertyRentalForm(forms.ModelForm):
    class Meta:
        model = PropertyRental
        fields = ['property', 'tenant', 'rent_price', 'start_date', 'end_date']


class PropertyFilterForm(forms.Form):
    city = forms.CharField(max_length=50, required=False, label="Şehir")
    min_m2 = forms.IntegerField(required=False, label="Min m²")
    max_m2 = forms.IntegerField(required=False, label="Max m²")
    min_price = forms.IntegerField(required=False, label="Min Fiyat")
    max_price = forms.IntegerField(required=False, label="Max Fiyat")
    room_count = forms.IntegerField(required=False, label="Oda Sayısı")
    heating_type = forms.CharField(max_length=50, required=False, label="Isınma Tipi")
    transaction_type = forms.ChoiceField(
        choices=[('', 'Hepsi'), ('sale', 'Satılık'), ('rent', 'Kiralık')],
        required=False,
        label="Tür"
    )
