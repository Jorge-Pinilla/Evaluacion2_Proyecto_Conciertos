# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from core.models import Evento, Sector, CarroTickets, ItemCarro, Compra, ItemCompra, EntradaComprada, Recinto
from .forms import RegistroForm, EventoForm, SectorForm

def home_view(request):
    """Catálogo público de eventos con buscador opcional."""
    eventos = Evento.objects.all().order_by('fecha_hora')
    query = request.GET.get('q')
    if query:
        eventos = eventos.filter(nombre__icontains=query) | eventos.filter(artista_banda__icontains=query)
    return render(request, 'home.html', {'eventos': eventos})

def evento_detail_view(request, evento_id):
    """Detalle del evento y sus sectores/localidades disponibles."""
    evento = get_object_or_404(Evento, id=evento_id)
    sectores = evento.sectores.all()
    return render(request, 'evento_detail.html', {'evento': evento, 'sectores': sectores})

def registro_view(request):
    """Registro de nuevos usuarios (Espectadores u Organizadores)."""
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            if user.role == 'ORGANIZADOR':
                return redirect('organizador_dashboard')
            return redirect('home')
    else:
        form = RegistroForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    """Inicio de sesión general en la plataforma web."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.role == 'ORGANIZADOR':
                return redirect('organizador_dashboard')
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    """Cierre de sesión seguro."""
    logout(request)
    return redirect('home')

@login_required
def carro_view(request):
    """Gestión del carro de compras persistente del espectador."""
    if request.user.role != 'ESPECTADOR':
        return redirect('home')
    carro, _ = CarroTickets.objects.get_or_create(usuario=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            sector_id = request.POST.get('sector_id')
            cantidad = int(request.POST.get('cantidad', 1))
            sector = get_object_or_404(Sector, id=sector_id)
            item, created = ItemCarro.objects.get_or_create(carro=carro, sector=sector)
            if not created:
                item.cantidad += cantidad
            else:
                item.cantidad = cantidad
            item.save()
        elif action == 'remove':
            item_id = request.POST.get('item_id')
            ItemCarro.objects.filter(id=item_id, carro=carro).delete()
        return redirect('carro')
    
    total = sum(item.sector.precio * item.cantidad for item in carro.items.all())
    return render(request, 'carro.html', {'carro': carro, 'total': total})

@login_required
@transaction.atomic
def checkout_view(request):
    """Checkout: valida stock atómicamente, descuenta inventario y emite entradas UUID."""
    if request.user.role != 'ESPECTADOR':
        return redirect('home')
    carro = get_object_or_404(CarroTickets, usuario=request.user)
    items = carro.items.all()
    if not items.exists():
        return redirect('carro')

    total = 0
    for item in items:
        if item.sector.stock_total < item.cantidad:
            total = sum(i.sector.precio * i.cantidad for i in items)
            return render(request, 'carro.html', {'carro': carro, 'total': total, 'error': f'Stock insuficiente para el sector: {item.sector.nombre}'})
        total += item.sector.precio * item.cantidad

    # Crear compra transaccional en estado PAGADO
    compra = Compra.objects.create(usuario=request.user, total=total, estado='PAGADO')
    for item in items:
        ItemCompra.objects.create(compra=compra, sector=item.sector, cantidad=item.cantidad, precio_unitario=item.sector.precio)
        # Descuento estricto de stock del catálogo físico
        item.sector.stock_total -= item.cantidad
        item.sector.save()
        # Generación de entradas con código Hash/UUID único por ticket
        for _ in range(item.cantidad):
            EntradaComprada.objects.create(compra=compra, sector=item.sector, titular=request.user.get_full_name() or request.user.username)

    # Vaciar carro persistente tras compra exitosa
    carro.items.all().delete()
    return redirect('mis_entradas')

@login_required
def mis_entradas_view(request):
    """Historial de compras y tickets emitidos del espectador."""
    if request.user.role != 'ESPECTADOR':
        return redirect('home')
    compras = Compra.objects.filter(usuario=request.user).order_by('-creado_en')
    return render(request, 'mis_entradas.html', {'compras': compras})

@login_required
def organizador_dashboard_view(request):
    """Panel de gestión para el Organizador (Crear eventos/sectores y actualizar estados)."""
    if request.user.role != 'ORGANIZADOR':
        return redirect('home')
    
    mis_eventos = Evento.objects.filter(organizador=request.user)
    recintos = Recinto.objects.all()
    compras_clientes = Compra.objects.filter(items__sector__evento__organizador=request.user).distinct().order_by('-creado_en')

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'evento':
            form = EventoForm(request.POST)
            if form.is_valid():
                ev = form.save(commit=False)
                ev.organizador = request.user
                ev.save()
                return redirect('organizador_dashboard')
        elif form_type == 'sector':
            evento_id = request.POST.get('evento_id')
            evento_obj = get_object_or_404(Evento, id=evento_id, organizador=request.user)
            s_form = SectorForm(request.POST)
            if s_form.is_valid():
                sec = s_form.save(commit=False)
                sec.evento = evento_obj
                sec.save()
                return redirect('organizador_dashboard')
        elif form_type == 'estado_compra':
            compra_id = request.POST.get('compra_id')
            nuevo_estado = request.POST.get('estado')
            c_obj = get_object_or_404(Compra, id=compra_id)
            # Si se cambia a CANCELADO, reposición automática de stock
            if c_obj.estado != 'CANCELADO' and nuevo_estado == 'CANCELADO':
                with transaction.atomic():
                    for it in c_obj.items.all():
                        if it.sector:
                            it.sector.stock_total += it.cantidad
                            it.sector.save()
            c_obj.estado = nuevo_estado
            c_obj.save()
            return redirect('organizador_dashboard')

    evento_form = EventoForm()
    sector_form = SectorForm()
    return render(request, 'organizador_dashboard.html', {
        'mis_eventos': mis_eventos,
        'recintos': recintos,
        'compras_clientes': compras_clientes,
        'evento_form': evento_form,
        'sector_form': sector_form
    })