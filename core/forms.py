
from django import forms
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError

class UsuarioCreationForm(forms.ModelForm):
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirmar Senha', widget=forms.PasswordInput)
    group = forms.ChoiceField(label='Perfil', choices=[
        ('Admin', 'Administrador'),
        ('Professor', 'Professor'),
    ])

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget.attrs.update({'class': 'form-control'})
        self.fields['confirm_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['group'].widget.attrs.update({'class': 'form-select'})

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise ValidationError("As senhas não conferem.")
            
        email = cleaned_data.get("email")
        if email and User.objects.filter(username=email).exists():
            self.add_error('email', "J existe um usurio com este email.")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]  # Use email as username
        user.set_password(self.cleaned_data["password"])
        
        if commit:
            user.save()
            group_name = self.cleaned_data.get('group')
            if group_name:
                group, _ = Group.objects.get_or_create(name=group_name)
                user.groups.add(group)
                if group_name == 'Admin':
                    user.is_staff = True
                    user.save()
        return user
