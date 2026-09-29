# api/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from core.models import Evento, Sector, CarroTickets, ItemCarro, Compra, EntradaComprada

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Inyecta el rol personalizado en los claims del token JWT."""
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['username'] = user.username
        return token

class EventoSerializer(serializers.ModelSerializer):
    organizador_nombre = serializers.CharField(source='organizador.username', read_only=True)
    recinto_nombre = serializers.CharField(source='recinto.nombre', read_only=True)
    class Meta:
        model = Evento
        fields = ['id', 'nombre', 'artista_banda', 'fecha_hora', 'recinto', 'recinto_nombre', 'organizador', 'organizador_nombre']
        read_only_fields = ['organizador']

class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = ['id', 'evento', 'nombre', 'precio', 'stock_total']

class ItemCarroSerializer(serializers.ModelSerializer):
    sector_nombre = serializers.CharField(source='sector.nombre', read_only=True)
    precio_unitario = serializers.DecimalField(source='sector.precio', max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = ItemCarro
        fields = ['id', 'sector', 'sector_nombre', 'cantidad', 'precio_unitario']

class CarroTicketsSerializer(serializers.ModelSerializer):
    items = ItemCarroSerializer(many=True, read_only=True)
    total_carro = serializers.SerializerMethodField()

    class Meta:
        model = CarroTickets
        fields = ['id', 'usuario', 'items', 'total_carro', 'actualizado_en']
        read_only_fields = ['usuario']

    def get_total_carro(self, obj):
        return sum(item.sector.precio * item.cantidad for item in obj.items.all())

class EntradaCompradaSerializer(serializers.ModelSerializer):
    sector_nombre = serializers.CharField(source='sector.nombre', read_only=True)
    class Meta:
        model = EntradaComprada
        fields = ['id', 'codigo_hash', 'sector_nombre', 'titular']

class CompraSerializer(serializers.ModelSerializer):
    entradas = EntradaCompradaSerializer(many=True, read_only=True)
    class Meta:
        model = Compra
        fields = ['id', 'estado', 'total', 'creado_en', 'entradas']
        read_only_fields = ['usuario', 'total', 'estado']