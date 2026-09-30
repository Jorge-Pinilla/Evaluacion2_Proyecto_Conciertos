# core/migrations/0007_cargar_evento_benefico.py
from django.db import migrations
from django.utils import timezone
import datetime

def poblar_evento_benefico(apps, schema_editor):
    User = apps.get_model('core', 'User')
    Recinto = apps.get_model('core', 'Recinto')
    Evento = apps.get_model('core', 'Evento')
    Sector = apps.get_model('core', 'Sector')

    # Buscamos un usuario organizador disponible
    organizador = User.objects.filter(role='ORGANIZADOR').first()
    if not organizador:
        organizador = User.objects.first()

    recintos = list(Recinto.objects.all())
    if not recintos:
        return

    # Creación del evento benéfico
    evento, created = Evento.objects.get_or_create(
        nombre="Benefico Mascotas 2026",
        defaults={
            'organizador': organizador,
            'artista_banda': "Leo Rey - Miguel Bosé - Pink Floyd - Pearl Jam",
            'fecha_hora': timezone.make_aware(datetime.datetime(2026, 11, 25, 18, 30)),
            'recinto': recintos[0]
        }
    )
    
    if created:
        sectores_data = [
            {"nombre": "Cancha VIP / Pista Premium", "precio": 50000, "stock_total": 15},
            {"nombre": "Platea Baja / Primer Piso", "precio": 35000, "stock_total": 100},
            {"nombre": "Platea Alta / Segundo Piso", "precio": 25000, "stock_total": 150},
            {"nombre": "Galería", "precio": 15000, "stock_total": 200}
        ]
        for sec_data in sectores_data:
            Sector.objects.create(
                evento=evento,
                nombre=sec_data['nombre'],
                precio=sec_data['precio'],
                stock_total=sec_data['stock_total']
            )

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_cargar_eventos_iniciales'),
    ]

    operations = [
        migrations.RunPython(poblar_evento_benefico),
    ]