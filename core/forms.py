# core/forms.py
from django import forms
from core.models import User, Evento, Sector, Recinto

class RegistroForm(forms.ModelForm):
    username = forms.CharField(
        label="Nombre de usuario",
        max_length=150,
        help_text="Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    role = forms.ChoiceField(
        label="Rol en el sistema",
        choices=User.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    first_name = forms.CharField(
        label="Nombre",
        required=True,  # Obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label="Apellido",
        required=True,  # Obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'first_name', 'last_name']


class EventoForm(forms.ModelForm):
    recinto = forms.ModelChoiceField(
        queryset=Recinto.objects.all(),
        empty_label="-- Seleccione un recinto --",
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Recinto / Lugar"
    )

    class Meta:
        model = Evento
        fields = ['recinto', 'nombre', 'artista_banda', 'fecha_hora']
        labels = {
            'recinto': 'Recinto / Lugar',
            'nombre': 'Nombre del Evento',
            'artista_banda': 'Artista o Banda',
            'fecha_hora': 'Fecha y Hora'
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'artista_banda': forms.TextInput(attrs={'class': 'form-control'}), # Corregido con el signo '='
            'fecha_hora': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class SectorForm(forms.ModelForm):
    class Meta:
        model = Sector
        fields = ['nombre', 'precio', 'stock_total']
        labels = {
            'nombre': 'Tipo de Sector',
            'precio': 'Precio Unitario ($)',
            'stock_total': 'Cantidad de Entradas (Stock)'
        }
        widgets = {
            'nombre': forms.Select(attrs={'class': 'form-select'}),  # Menú desplegable Bootstrap
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_total': forms.NumberInput(attrs={'class': 'form-control'}),
        }