
from django import forms
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError

class UsuarioCreationForm(forms.ModelForm):
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirmar Senha', widget=forms.PasswordInput)
    group = forms.ChoiceField(label='Perfil', choices=[
        ('Gestão', 'Gestão'),
        ('Núcleo', 'Núcleo'),
        ('Operacional', 'Operacional'),
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
                if group_name == 'Gestão':
                    user.is_staff = True
                    user.save()
        return user

class UsuarioUpdateForm(forms.ModelForm):
    password = forms.CharField(label='Nova Senha', widget=forms.PasswordInput, required=False, help_text="Deixe em branco para manter a senha atual.")
    confirm_password = forms.CharField(label='Confirmar Nova Senha', widget=forms.PasswordInput, required=False)
    group = forms.ChoiceField(label='Perfil', choices=[
        ('Gestão', 'Gestão'),
        ('Núcleo', 'Núcleo'),
        ('Operacional', 'Operacional'),
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
        
        if self.instance.pk:
            current_group = self.instance.groups.first()
            if current_group:
                self.fields['group'].initial = current_group.name

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password or confirm_password:
            if password != confirm_password:
                raise ValidationError("As senhas não conferem.")
                
        email = cleaned_data.get("email")
        if email and User.objects.exclude(pk=self.instance.pk).filter(username=email).exists():
            self.add_error('email', "Já existe um usuário com este email.")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]
        
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        
        if commit:
            user.save()
            group_name = self.cleaned_data.get('group')
            if group_name:
                user.groups.clear()
                group, _ = Group.objects.get_or_create(name=group_name)
                user.groups.add(group)
                if group_name == 'Gestão':
                    user.is_staff = True
                else:
                    user.is_staff = False
                user.save()
        return user
