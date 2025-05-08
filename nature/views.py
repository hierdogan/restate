from django.shortcuts import render, get_object_or_404, redirect
from .models import Property, PropertySale, PropertyRental, PropertyOwner, User
from .forms import PropertyForm, PropertySaleForm, PropertyRentalForm, PropertyFilterForm
from django.db.models import Avg, Count


# Create your views here.
def property_list(request):
    form = PropertyFilterForm(request.GET or None)
    properties = Property.objects.all()

    if form.is_valid():
        data = form.cleaned_data

        if data['city']:
            properties = properties.filter(address__city__icontains=data['city'])
        if data['min_m2']:
            properties = properties.filter(square_meters__gte=data['min_m2'])
        if data['max_m2']:
            properties = properties.filter(square_meters__lte=data['max_m2'])
        if data['room_count']:
            properties = properties.filter(room_count=data['room_count'])
        if data['heating_type']:
            properties = properties.filter(heating_type__icontains=data['heating_type'])

        # Fiyat filtresi — satış veya kiralama ayrımına göre
        if data['transaction_type'] == 'sale':
            sale_ids = PropertySale.objects.filter(
                sale_price__gte=data.get('min_price') or 0,
                sale_price__lte=data.get('max_price') or 1e12
            ).values_list('property_id', flat=True)
            properties = properties.filter(id__in=sale_ids)

        elif data['transaction_type'] == 'rent':
            rent_ids = PropertyRental.objects.filter(
                rent_price__gte=data.get('min_price') or 0,
                rent_price__lte=data.get('max_price') or 1e12
            ).values_list('property_id', flat=True)
            properties = properties.filter(id__in=rent_ids)

    return render(request, 'nature/property_list.html', {
        'properties': properties,
        'form': form,
        'filter_type': "🔍 Filtreli Sonuçlar"
    })


def property_detail(request, property_id):
    property_obj = get_object_or_404(Property, pk=property_id)

    # Sahiplik geçmişi
    ownerships = PropertyOwner.objects.filter(property=property_obj).order_by('ownership_start_date')

    # Kiralama geçmişi
    rentals = PropertyRental.objects.filter(property=property_obj).order_by('start_date')

    # Kiralamalar arası gün farkı hesaplama
    rental_history = []
    previous_end = None
    for rental in rentals:
        gap_days = (rental.start_date - previous_end).days if previous_end else None
        rental_history.append({
            'rental': rental,
            'gap_days': gap_days
        })
        previous_end = rental.end_date

    context = {
        'property': property_obj,
        'ownerships': ownerships,
        'rental_history': rental_history,
    }
    return render(request, 'nature/property_detail.html', context)


# def property_detail(request, pk):
#     property = get_object_or_404(Property, pk=pk)
#     return render(request, 'nature/property_detail.html', {'property': property})


def property_create(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('property_list')
    else:
        form = PropertyForm()

    return render(request, 'nature/property_form.html', {'form': form})


def property_sale_create(request):
    if request.method == 'POST':
        form = PropertySaleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('property_list')
    else:
        form = PropertySaleForm()
    return render(request, 'nature/property_sale_form.html', {'form': form})


def property_rental_create(request):
    if request.method == 'POST':
        form = PropertyRentalForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('property_list')
    else:
        form = PropertyRentalForm()
    return render(request, 'nature/property_rental_form.html', {'form': form})


def stats(request):
    total_properties = Property.objects.count()
    total_sales = PropertySale.objects.count()
    total_rentals = PropertyRental.objects.count()

    avg_sale_price = PropertySale.objects.aggregate(Avg('sale_price'))['sale_price__avg']
    avg_rent_price = PropertyRental.objects.aggregate(Avg('rent_price'))['rent_price__avg']

    context = {
        'total_properties': total_properties,
        'total_sales': total_sales,
        'total_rentals': total_rentals,
        'avg_sale_price': avg_sale_price,
        'avg_rent_price': avg_rent_price,
    }

    return render(request, 'nature/stats.html', context)


def properties_by_owner(request, user_id):
    properties = Property.objects.filter(current_owner_id=user_id)
    user = User.objects.get(pk=user_id)
    return render(request, 'nature/property_list.html', {
        'properties': properties,
        'filter_type': f"{user.full_name} → sahip olduğu evler"
    })


def properties_by_tenant(request, user_id):
    property_ids = PropertyRental.objects.filter(tenant_id=user_id).values_list('property_id', flat=True)
    properties = Property.objects.filter(id__in=property_ids)
    user = User.objects.get(pk=user_id)
    return render(request, 'nature/property_list.html', {
        'properties': properties,
        'filter_type': f"{user.full_name} → kiraladığı evler"
    })


def properties_by_buyer(request, user_id):
    property_ids = PropertySale.objects.filter(buyer_id=user_id).values_list('property_id', flat=True)
    properties = Property.objects.filter(id__in=property_ids)
    user = User.objects.get(pk=user_id)
    return render(request, 'nature/property_list.html', {
        'properties': properties,
        'filter_type': f"{user.full_name} → satın aldığı evler"
    })


def user_list(request):
    users = User.objects.all()
    return render(request, 'nature/user_list.html', {'users': users})


def user_detail(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    # 1. PropertyOwner kayıtlı olanlar
    current_ownerships = list(PropertyOwner.objects.filter(owner=user, ownership_end_date__isnull=True))

    # 2. current_owner olup da PropertyOwner kaydı olmayan evler
    owned_properties = Property.objects.filter(current_owner=user)
    already_tracked = [o.property.id for o in current_ownerships]
    missing_owner_records = owned_properties.exclude(id__in=already_tracked)

    # Sahiplik listesine ekle
    for prop in missing_owner_records:
        dummy_owner = PropertyOwner(
            property=prop,
            owner=user,
            ownership_start_date=None,  # bilinmiyor
            ownership_end_date=None
        )
        current_ownerships.append(dummy_owner)

    # Satın alma işlemleri
    purchases = []
    for po in PropertyOwner.objects.filter(owner=user):
        sale = PropertySale.objects.filter(property=po.property, buyer=user).first()
        if sale:
            previous_owner = PropertyOwner.objects.filter(
                property=po.property,
                ownership_end_date=po.ownership_start_date
            ).first()
            purchases.append({
                'property': po.property,
                'sale_price': sale.sale_price,
                'sale_date': po.ownership_start_date,
                'seller': previous_owner.owner if previous_owner else None
            })

    # Satış işlemleri
    past_ownerships = PropertyOwner.objects.filter(owner=user, ownership_end_date__isnull=False)
    sales = []
    for po in past_ownerships:
        sale = PropertySale.objects.filter(property=po.property).first()
        if sale and sale.buyer != user:
            sales.append({
                'property': po.property,
                'sale_price': sale.sale_price,
                'sale_date': po.ownership_end_date,
                'buyer': sale.buyer
            })

    rentals = PropertyRental.objects.filter(tenant=user)

    context = {
        'user': user,
        'current_ownerships': current_ownerships,
        'past_sales': sales,
        'purchases': purchases,
        'rentals': rentals,
    }
    return render(request, 'nature/user_detail.html', context)


def transaction_history(request):
    sales = PropertySale.objects.select_related('property', 'buyer').all()
    rentals = PropertyRental.objects.select_related('property', 'tenant').all()

    context = {
        'sales': sales,
        'rentals': rentals,
    }

    return render(request, 'nature/transaction_history.html', context)




# def user_detail(request, user_id):
#     user = get_object_or_404(User, pk=user_id)
#
#     current_ownerships = PropertyOwner.objects.filter(owner=user, ownership_end_date__isnull=True)
#     past_ownerships = PropertyOwner.objects.filter(owner=user, ownership_end_date__isnull=False)
#
#     # Satın alınan evler
#     purchases = []
#     for po in PropertyOwner.objects.filter(owner=user):
#         sale = PropertySale.objects.filter(property=po.property, buyer=user).first()
#         if sale:
#             previous_owner = PropertyOwner.objects.filter(
#                 property=po.property,
#                 ownership_end_date=po.ownership_start_date
#             ).first()
#             purchases.append({
#                 'property': po.property,
#                 'sale_price': sale.sale_price,
#                 'sale_date': po.ownership_start_date,
#                 'seller': previous_owner.owner if previous_owner else None
#             })
#
#     # Sattığı evler
#     sales = []
#     for po in past_ownerships:
#         sale = PropertySale.objects.filter(property=po.property).first()
#         if sale and sale.buyer != user:
#             sales.append({
#                 'property': po.property,
#                 'sale_price': sale.sale_price,
#                 'sale_date': po.ownership_end_date,
#                 'buyer': sale.buyer
#             })
#
#     rentals = PropertyRental.objects.filter(tenant=user)
#
#     context = {
#         'user': user,
#         'current_ownerships': current_ownerships,
#         'past_sales': sales,
#         'purchases': purchases,
#         'rentals': rentals,
#     }
#     return render(request, 'nature/user_detail.html', context)

