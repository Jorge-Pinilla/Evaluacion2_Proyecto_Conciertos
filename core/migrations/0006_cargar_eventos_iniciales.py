# core/migrations/0006_cargar_eventos_iniciales.py
from django.db import migrations
from django.utils import timezone
from django.contrib.auth.hashers import make_password
import datetime

def poblar_eventos_iniciales(apps, schema_editor):
    User = apps.get_model('core', 'User')
    Recinto = apps.get_model('core', 'Recinto')
    Evento = apps.get_model('core', 'Evento')
    Sector = apps.get_model('core', 'Sector')

    # Aseguramos un usuario organizador por defecto usando make_password
    organizador, created = User.objects.get_or_create(
        username='organizador_default',
        defaults={
            'email': 'organizador@conciertosapp.cl',
            'role': 'ORGANIZADOR',
            'first_name': 'Jorge',
            'last_name': 'Pinilla',
            'password': make_password('admin123')
        }
    )
    if created:
        organizador.password = make_password('admin123')
        organizador.save()

    recintos = list(Recinto.objects.all())
    if not recintos:
        return

    # Definición unificada de los 5 eventos iniciales (incluyendo el evento benéfico)
    eventos_data = [
        {
            "nombre": "Despedida de Aires",
            "artista_banda": "Fishmans",
            "fecha_hora": timezone.make_aware(datetime.datetime(2026, 12, 15, 21, 0)),
            "recinto": recintos[0],
            "sectores": [
                {"nombre": "Cancha VIP / Pista Premium", "precio": 95000, "stock_total": 15},
                {"nombre": "Platea Baja / Primer Piso", "precio": 65000, "stock_total": 50},
                {"nombre": "Platea Alta / Segundo Piso", "precio": 40000, "stock_total": 80},
                {"nombre": "Galería", "precio": 25000, "stock_total": 22}
            ]
        },
        {
            "nombre": "Nostalgic Tour",
            "artista_banda": "Alice in Chains",
            "fecha_hora": timezone.make_aware(datetime.datetime(2026, 10, 20, 20, 30)),
            "recinto": recintos[1] if len(recintos) > 1 else recintos[0],
            "sectores": [
                {"nombre": "Cancha General / Pista General", "precio": 55000, "stock_total": 120},
                {"nombre": "Platea Baja / Primer Piso", "precio": 75000, "stock_total": 18},
                {"nombre": "Tribuna / General", "precio": 35000, "stock_total": 90},
                {"nombre": "Zona Platinum", "precio": 120000, "stock_total": 10}
            ]
        },
        {
            "nombre": "Perdonados",
            "artista_banda": "Invisible",
            "fecha_hora": timezone.make_aware(datetime.datetime(2026, 11, 10, 19, 00)),
            "recinto": recintos[2] if len(recintos) > 2 else recintos[0],
            "sectores": [
                {"nombre": "Campo / Pista", "precio": 45000, "stock_total": 150},
                {"nombre": "Platea Baja / Primer Piso", "precio": 60000, "stock_total": 60},
                {"nombre": "Galería", "precio": 20000, "stock_total": 200},
                {"nombre": "Suite / VIP", "precio": 130000, "stock_total": 12}
            ]
        },
        {
            "nombre": "Legendary Tale",
            "artista_banda": "Rhapsody",
            "fecha_hora": timezone.make_aware(datetime.datetime(2026, 12, 1, 21, 30)),
            "recinto": recintos[3] if len(recintos) > 3 else recintos[0],
            "sectores": [
                {"nombre": "Cancha VIP / Pista Premium", "precio": 85000, "stock_total": 25},
                {"nombre": "Platea Alta / Segundo Piso", "precio": 45000, "stock_total": 70},
                {"nombre": "Tribuna / General", "precio": 30000, "stock_total": 100},
                {"nombre": "Zona Platinum", "precio": 110000, "stock_total": 14}
            ]
        },
        {
            "nombre": "Benefico Mascotas 2026",
            "artista_banda": "Leo Rey - Miguel Bosé - Pink Floyd - Pearl Jam",
            "fecha_hora": timezone.make_aware(datetime.datetime(2026, 11, 25, 18, 30)),
            "recinto": recintos[0],
            "sectores": [
                {"nombre": "Cancha VIP / Pista Premium", "precio": 50000, "stock_total": 15},
                {"nombre": "Platea Baja / Primer Piso", "precio": 35000, "stock_total": 100},
                {"nombre": "Platea Alta / Segundo Piso", "precio": 25000, "stock_total": 150},
                {"nombre": "Galería", "precio": 15000, "stock_total": 200}
            ]
        },
    ]

    for ev_data in eventos_data:
        sectores_list = ev_data.pop('sectores')
        evento, created = Evento.objects.get_or_create(
            nombre=ev_data['nombre'],
            defaults={
                'organizador': organizador,
                'artista_banda': ev_data['artista_banda'],
                'fecha_hora': ev_data['fecha_hora'],
                'recinto': ev_data['recinto']
            }
        )
        if created:
            for sec_data in sectores_list:
                Sector.objects.create(
                    evento=evento,
                    nombre=sec_data['nombre'],
                    precio=sec_data['precio'],
                    stock_total=sec_data['stock_total']
                )

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_cargar_recintos_iniciales'),
    ]

    operations = [
        migrations.RunPython(poblar_eventos_iniciales),
    ]