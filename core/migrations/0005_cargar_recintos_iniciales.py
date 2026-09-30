# core/migrations/000X_cargar_recintos_iniciales.py
from django.db import migrations

def poblar_recintos(apps, schema_editor):
    Recinto = apps.get_model('core', 'Recinto')
    recintos_chile = [
        {"nombre": "Estadio Nacional Julio Martínez Prádanos", "direccion": "Av. Grecia 2001", "ciudad": "Santiago"},
        {"nombre": "Movistar Arena", "direccion": "Parque O'Higgins", "ciudad": "Santiago"},
        {"nombre": "Teatro Caupolicán", "direccion": "San Diego 850", "ciudad": "Santiago"},
        {"nombre": "Anfiteatro de la Quinta Vergara", "direccion": "Errazuriz s/n", "ciudad": "Viña del Mar"},
        {"nombre": "Claro Arena", "direccion": "Av. Las Flores 13000 (San Carlos de Apoquindo)", "ciudad": "Santiago"},
        {"nombre": "Teatro Municipal de Santiago", "direccion": "Calle Agustinas 794", "ciudad": "Santiago"},
        {"nombre": "Espacio Riesco", "direccion": "Av. El Salto 5000", "ciudad": "Huechuraba, Santiago"},
        {"nombre": "Teatro Teletón", "direccion": "Mario Kreutzberger 1531", "ciudad": "Santiago"},
    ]
    for r in recintos_chile:
        Recinto.objects.get_or_create(
            nombre=r["nombre"],
            defaults={"direccion": r["direccion"], "ciudad": r["ciudad"]}
        )

class Migration(migrations.Migration):

    dependencies = [
    ('core', '0004_notificacionleida'),
]

    operations = [
        migrations.RunPython(poblar_recintos),
    ]