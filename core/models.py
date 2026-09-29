# core/models.py
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    MODELO: User (3NF)
    Representa a los usuarios del sistema con separación estricta de roles mediante CHOICES.
    Evita redundancias al centralizar la autenticación.
    """
    ROLE_CHOICES = (
        ('ESPECTADOR', 'Espectador'),
        ('ORGANIZADOR', 'Organizador de Eventos'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='ESPECTADOR')

    def __str__(self):
        return f"{self.username} ({self.role})"


class Recinto(models.Model):
    """
    MODELO: Recinto (3NF)
    Entidad independiente que almacena la ubicación física de los eventos.
    Previene la duplicación de datos de direcciones y ciudades por cada evento.
    """
    nombre = models.CharField(max_length=150)
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre} - {self.ciudad}"


class Evento(models.Model):
    """
    MODELO: Evento (3NF)
    Relacionado con Organizador (1:N) y Recinto (1:N). 
    Depende funcionalmente de sus propias claves foráneas primarias.
    """
    organizador = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'ORGANIZADOR'}, related_name='eventos_organizados')
    recinto = models.ForeignKey(Recinto, on_delete=models.CASCADE, related_name='eventos')
    nombre = models.CharField(max_length=200)
    artista_banda = models.CharField(max_length=200)
    fecha_hora = models.DateTimeField()

    def __str__(self):
        return f"{self.nombre} ({self.artista_banda})"


class Sector(models.Model):
    """
    MODELO: Sector (3NF)
    Zonas de un evento con opciones predefinidas mediante CHOICES estrictos.
    """
    SECTOR_CHOICES = (
        ('Cancha VIP / Pista Premium', 'Cancha VIP / Pista Premium'),
        ('Cancha General / Pista General', 'Cancha General / Pista General'),
        ('Campo / Pista', 'Campo / Pista'),
        ('Platea Baja / Primer Piso', 'Platea Baja / Primer Piso'),
        ('Platea Alta / Segundo Piso', 'Platea Alta / Segundo Piso'),
        ('Tribuna / General', 'Tribuna / General'),
        ('Galería', 'Galería'),
        ('Suite / VIP', 'Suite / VIP'),
        ('Zona Platinum', 'Zona Platinum'),
    )

    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='sectores')
    nombre = models.CharField(max_length=150, choices=SECTOR_CHOICES)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock_total = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} - {self.evento.nombre} (${self.precio})"


class CarroTickets(models.Model):
    """
    MODELO: CarroTickets (3NF)
    Relación 1 a 1 estricta con el Usuario. 
    Garantiza la persistencia post-logout y entre diferentes dispositivos en PostgreSQL[cite: 15].
    """
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='carro')
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Carro de {self.usuario.username}"


class ItemCarro(models.Model):
    """
    MODELO: ItemCarro (3NF)
    Tabla intermedia normalizada que resuelve la relación N:M entre Carro y Sector.
    Incluye restricción 'unique_together' para evitar duplicar el mismo sector en el carro activo.
    """
    carro = models.ForeignKey(CarroTickets, on_delete=models.CASCADE, related_name='items')
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('carro', 'sector')


class Compra(models.Model):
    """
    MODELO: Compra / Orden (3NF)
    Registro histórico transaccional. Sus estados utilizan CHOICES obligatorios 
    (PENDIENTE, PAGADO, ENTREGADO, CANCELADO)[cite: 15].
    """
    ESTADO_CHOICES = (
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
        ('ENTREGADO', 'Entregado / Ingresado'),
        ('CANCELADO', 'Cancelado'),
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='compras')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    total = models.DecimalField(max_digits=12, decimal_places=2)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Orden #{self.id} - {self.usuario.username} [{self.estado}]"


class ItemCompra(models.Model):
    """
    MODELO: ItemCompra (3NF - Normalización Histórica)
    Congela el precio unitario exacto al momento de la compra. 
    Evita la dependencia transitiva si el precio del sector cambia en el futuro en la tabla Sector.
    """
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='items')
    sector = models.ForeignKey(Sector, on_delete=models.SET_NULL, null=True)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)


class EntradaComprada(models.Model):
    """
    MODELO: EntradaComprada (3NF)
    Tickets digitales individuales emitidos al validar el pago. 
    Contiene un código Hash UUID único e irrepetible para control de acceso al evento[cite: 15].
    """
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='entradas')
    sector = models.ForeignKey(Sector, on_delete=models.SET_NULL, null=True)
    codigo_hash = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    titular = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f"Ticket UUID: {self.codigo_hash} ({self.sector})"