# api/views.py
from django.shortcuts import get_object_or_404, render
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from core.models import Evento, Sector, CarroTickets, ItemCarro, Compra, ItemCompra, EntradaComprada
from .serializers import (
    CustomTokenObtainPairSerializer, EventoSerializer, SectorSerializer,
    CarroTicketsSerializer, ItemCarroSerializer, CompraSerializer
)
from .permissions import EspectadorOnly, OrganizadorOnly

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# Endpoints Públicos
class EventoListView(generics.ListCreateAPIView):
    queryset = Evento.objects.all().order_by('fecha_hora')
    serializer_class = EventoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['artista_banda', 'recinto__ciudad']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [OrganizadorOnly()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(organizador=self.request.user)

class SectorByEventoView(generics.ListAPIView):
    serializer_class = SectorSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        evento_id = self.kwargs['evento_id']
        return Sector.objects.filter(evento_id=evento_id)

# Carro de Compras Persistente (Espectador)
class CarroTicketsDetailView(APIView):
    permission_classes = [EspectadorOnly]

    def get(self, request):
        carro, _ = CarroTickets.objects.get_or_create(usuario=request.user)
        serializer = CarroTicketsSerializer(carro)
        return Response(serializer.data)

    def post(self, request):
        carro, _ = CarroTickets.objects.get_or_create(usuario=request.user)
        sector_id = request.data.get('sector_id')
        cantidad = int(request.data.get('cantidad', 1))
        sector = get_object_or_404(Sector, id=sector_id)

        item, created = ItemCarro.objects.get_or_create(carro=carro, sector=sector)
        if not created:
            item.cantidad += cantidad
        else:
            item.cantidad = cantidad
        item.save()
        return Response(CarroTicketsSerializer(carro).data, status=status.HTTP_200_OK)

    def delete(self, request):
        carro = get_object_or_404(CarroTickets, usuario=request.user)
        sector_id = request.data.get('sector_id')
        if sector_id:
            ItemCarro.objects.filter(carro=carro, sector_id=sector_id).delete()
        else:
            carro.items.all().delete()
        return Response({"message": "Carro actualizado."}, status=status.HTTP_200_OK)

# Checkout Transaccional y Control de Stock
class ComprasPagarView(APIView):
    permission_classes = [EspectadorOnly]

    @transaction.atomic
    def post(self, request):
        carro = get_object_or_404(CarroTickets, usuario=request.user)
        items = carro.items.all()
        if not items.exists():
            return Response({"error": "El carro está vacío."}, status=status.HTTP_400_BAD_REQUEST)

        total = 0
        for item in items:
            # Validación previa de stock disponible (NO se descuenta al agregar al carro)
            if item.sector.stock_total < item.cantidad:
                return Response({"error": f"Stock insuficiente para el sector {item.sector.nombre}."}, status=status.HTTP_400_BAD_REQUEST)
            total += item.sector.precio * item.cantidad

        # Crear orden con estado inicial PAGADO tras confirmar pago exitoso
        compra = Compra.objects.create(usuario=request.user, total=total, estado='PAGADO')

        for item in items:
            ItemCompra.objects.create(
                compra=compra,
                sector=item.sector,
                cantidad=item.cantidad,
                precio_unitario=item.sector.precio
            )
            # Descuento atómico de stock del catálogo físico
            item.sector.stock_total -= item.cantidad
            item.sector.save()

            # Emisión automática de entradas con UUID único por cada ticket
            for _ in range(item.cantidad):
                EntradaComprada.objects.create(compra=compra, sector=item.sector, titular=request.user.get_full_name() or request.user.username)

        # Vaciar carro persistente tras liquidación exitosa
        carro.items.all().delete()
        return Response(CompraSerializer(compra).data, status=status.HTTP_201_CREATED)

class MisEntradasListView(generics.ListAPIView):
    permission_classes = [EspectadorOnly]
    serializer_class = CompraSerializer

    def get_queryset(self):
        return Compra.objects.filter(usuario=self.request.user).order_by('-creado_en')

# Gestión de Estados de Órdenes por el Organizador
class OrganizadorEstadoOrdenView(APIView):
    permission_classes = [OrganizadorOnly]

    @transaction.atomic
    def patch(self, request, pk):
        compra = get_object_or_404(Compra, id=pk)
        nuevo_estado = request.data.get('estado')

        if nuevo_estado not in dict(Compra.ESTADO_CHOICES).keys():
            return Response({"error": "Estado inválido."}, status=status.HTTP_400_BAD_REQUEST)

        # Lógica de reposición automática de stock si la orden pasa a CANCELADO
        if compra.estado != 'CANCELADO' and nuevo_estado == 'CANCELADO':
            for item in compra.items.all():
                if item.sector:
                    item.sector.stock_total += item.cantidad
                    item.sector.save()

        compra.estado = nuevo_estado
        compra.save()
        return Response(CompraSerializer(compra).data, status=status.HTTP_200_OK)