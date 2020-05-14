import qrcode
from django.shortcuts import render, redirect
from django.urls import reverse 
from django.http import HttpResponse, HttpResponseRedirect
from django.core.files import File
from django.contrib.auth.decorators import login_required
from io import BytesIO


from .forms import LaptopForm
from .forms import OwnerForm
from .forms import UserLoginForm, UserRegistrationForm
from django.contrib.auth import authenticate, login, logout
from .models import Owner, Laptop 
from django.shortcuts import render, redirect


from django.core.paginator import Paginator

from django.shortcuts import render


def home(request):
    return render(request, 'home.html')
def faq(request):
    return render(request, 'faq.html')

def about(request):
    return render(request, 'about.html')

def aboutt(request):
    return render(request, 'aboutt.html')



def generate_qr_code_img(laptop_id, owner_type):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr.add_data(laptop_id)
    qr.make(fit=True)
    back_color='white'

    if owner_type == Owner.STUDENT:
        fill_color='black'
    elif owner_type == Owner.STAFF:
        fill_color='green'
    else:
        fill_color = 'red'

    return qr.make_image(fill_color=fill_color, back_color=back_color)

@login_required()
def registration_form(request):
    if request.method == 'POST':
        laptop_form = LaptopForm(request.POST)
        owner_form = OwnerForm(request.POST, request.FILES)
        if all([laptop_form.is_valid(), owner_form.is_valid()]):  
            owner=owner_form.save()
            laptop=laptop_form.save()
            laptop.owner=owner
            laptop.save()
            return redirect(reverse('QR:list_owners'))
    laptop_form = LaptopForm()
    owner_form = OwnerForm()
    return render(request, 'form.html', {'laptop_form':laptop_form, 'owner_form':owner_form })

def teachers_ownerlist(request):
    owners = Owner.objects.filter(owner_type=Owner.TEACHER).order_by('owner_first_name', 'owner_last_name')
    paginator = Paginator(owners, 5) 

    page_number = request.GET.get('page')
    owners = paginator.get_page(page_number)
    return render(request, 'list_owners.html', {'owners': owners})

def student_ownerlist(request):
    owners = Owner.objects.filter(owner_type=Owner.STUDENT).order_by('owner_first_name', 'owner_last_name')
    paginator = Paginator(owners, 5) 

    page_number = request.GET.get('page')
    owners = paginator.get_page(page_number)
    return render(request, 'list_owners.html', {'owners': owners})

def staff_ownerlist(request):
    owners = Owner.objects.filter(owner_type=Owner.STAFF).order_by('owner_first_name', 'owner_last_name')
    paginator = Paginator(owners, 5) 

    page_number = request.GET.get('page')
    owners = paginator.get_page(page_number)
    return render(request, 'list_owners.html', {'owners': owners})

def search(request):
    if request.method == 'POST':
        student_id = request.POST.get('owner_id')

        try:
            owner = Owner.objects.get(owner_id__icontains=student_id)
            if owner:
                return render(request, 'search_results.html', {'owner': owner})
        except Owner.DoesNotExist:
            return render(request, 'search_not_found.html')

    return render(request, 'search.html')

def generate_qr_code(request, laptop_id):
    try:
        laptop = Laptop.objects.get(id=laptop_id)
    
        if not laptop.qr_code:
            img = generate_qr_code_img(laptop.id, laptop.owner.owner_type)
            blob = BytesIO()
            img.save(blob, 'JPEG')
            laptop.qr_code.save('laptop_qr_code.jpg', File(blob), save=False)

        return render(request, 'qr.html', {'laptop': laptop})

    except Laptop.DoesNotExist:
        return render(request, 'search_not_found.html')

    
    

    return render(request, 'qr.html', {'image': laptop_id})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('QR:home'))
                else:
                    return HttpResponse('User is not active')
            else:
                return HttpResponse('User is None')
    else:
        form = UserLoginForm()
    context = {
        'form': form,
    }
    return render(request, 'login.html', context)

def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('QR:home'))

def register(request):
    if request.method == 'POST':
        form  = UserRegistrationForm(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
        return HttpResponseRedirect(reverse('QR:home'))
    else:
        form = UserRegistrationForm()
    context = {
        'form' : form,
    }
    return render(request, 'registration/register.html', context)

@login_required()
def list_owners(request):
    owners = Owner.objects.all()
    paginator = Paginator(owners, 5) 

    page_number = request.GET.get('page')
    owners = paginator.get_page(page_number)
    return render(request, 'list_owners.html', {'owners': owners})

def detail(request, owner_id):
    owner = Owner.objects.get(pk=owner_id)
    return render(request, 'detail.html', {'owner': owner})


def upload(request):
    if request.method == 'POST':
        form = OwnerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = OwnerForm()
    return render(request, 'form.html', {
        'form': form
    })

