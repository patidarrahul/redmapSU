from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.urls import reverse
from django.http import request


class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email',
                  'password1', 'password2']  # Use all fields from the User model


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role', 'user_dir']


class SignInForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name']


class MeasurementUnitForm(forms.ModelForm):

    class Meta:
        model = MeasurementUnit
        fields = ['name', 'short_name']


class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['name', 'short_name', 'category', 'supplier', 'type', 'batch', 'arrival_date', 'expiry_date',
                  'total_units', 'unit_size', 'measurement_unit', 'notes']  # Use all fields from the Inventory model

        # You can customize the form field widgets, labels, and more here if needed
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Name'}),
            'short_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Short Name'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'batch': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Batch'}),
            'arrival_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'total_units': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Total Units'}),
            'unit_size': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Enter Unit Size'}),
            'measurement_unit': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control ', 'placeholder': 'Enter Notes', 'rows': '3'}),
        }


class ProjectForm(forms.ModelForm):

    collaborators = forms.ModelMultipleChoiceField(
        queryset=User.objects.all())

    class Meta:
        model = Project
        fields = ['title',  'collaborators', 'created', 'description']

        widgets = {
            'description': forms.Textarea(attrs={'placeholder': 'Describe the project here', 'style': 'height: 100px;'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Title'}),
            'collaborators': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'created': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

        # You can customize the form field widgets, labels, and more here if needed


class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = ['project', 'objective', 'number_of_variables',
                  'notes', 'created', 'serial_number', 'data_dir']

        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'objective': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter objective', 'style': 'height: 50px;'}),
            'number_of_variables': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Number of Variables'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter notes', 'style': 'height: 100px;'}),
            'created': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'serial_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Serial Number'}),
            'data_dir': forms.TextInput(attrs={'class': 'form-control ', 'placeholder': 'Enter Data Directory', 'required': 'required'}),
        }


class StackForm(forms.ModelForm):

    substrate = forms.ModelChoiceField(
        queryset=Inventory.objects.filter(category__name='Substrate'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Stack
        fields = ['experiment', 'name', 'substrate', 'geometry',
                  'number_of_layers', 'number_of_devices', 'created', 'jv_dir']

        widgets = {
            'experiment': forms.Select(attrs={'class': 'form-select'}),
            'author': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'geometry': forms.Select(attrs={'class': 'form-select'}),
            'number_of_layers': forms.NumberInput(attrs={'class': 'form-control', }),
            'number_of_devices': forms.NumberInput(attrs={'class': 'form-control', }),
            'created': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'jv_dir': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Experiment Directory'}),

        }


class LayerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        author = kwargs.pop('author', None)  # Retrieve the user from kwargs
        super().__init__(*args, **kwargs)
        if author:
            # Filter the queryset based on the current user
            self.fields['formulation'].queryset = Formulation.objects.filter(
                author=author)
            self.fields['stacks'].queryset = Stack.objects.filter(
                author=author)
            self.fields['drying_program'].queryset = DryingProgram.objects.filter(
                author=author)

    class Meta:
        model = Layer

        fields = ['stacks', 'name', 'sequence', 'coating_method', 'formulation_volume',
                  'layer_role', 'dry_film_thickness', 'room_temperature', 'room_humidity', 'layer_composition', 'layer_type',
                  'atmosphere', 'drying_type', 'drying_program', 'completed', 'created', 'formulation',
                  'treatment', 'treatment_time', 'treatment_power',]

        widgets = {
            'stacks': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', }),
            'sequence': forms.NumberInput(attrs={'class': 'form-control', }),
            'coating_method': forms.Select(attrs={'class': 'form-select', }),
            'formulation_volume': forms.NumberInput(attrs={'class': 'form-control', }),
            'layer_type': forms.Select(attrs={'class': 'form-select', }),
            'layer_role': forms.Select(attrs={'class': 'form-select'}),
            'dry_film_thickness': forms.NumberInput(attrs={'class': 'form-control', }),
            'room_temperature': forms.NumberInput(attrs={'class': 'form-control', }),
            'room_humidity': forms.NumberInput(attrs={'class': 'form-control', }),
            'layer_composition': forms.Select(attrs={'class': 'form-select', }),
            'atmosphere': forms.Select(attrs={'class': 'form-select'}),
            'drying_program': forms.Select(attrs={'class': 'form-select'}),
            'drying_type': forms.Select(attrs={'class': 'form-select'}),
            'completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'created': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'formulation': forms.Select(attrs={'class': 'form-select'}),
            'treatment': forms.Select(attrs={'class': 'form-select'}),
            'treatment_time': forms.NumberInput(attrs={'class': 'form-control', }),
            'treatment_power': forms.NumberInput(attrs={'class': 'form-control', }),
        }


class LayerCompositionForm(forms.ModelForm):
    class Meta:
        model = LayerComposition
        fields = ['name']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class DryingProgramStepForm(forms.ModelForm):
    class Meta:
        model = DryingProgramStep
        fields = ['temperature', 'time', 'order']

        widgets = {
            'temperature': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Temperature'}),
            'time': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Time'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Order'}),
        }


class DryingProgramForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        author = kwargs.pop('author', None)  # Retrieve the user from kwargs
        super().__init__(*args, **kwargs)
        if author:
            # Filter the queryset based on the current user
            self.fields['steps'].queryset = SpinStep.objects.filter(
                author=author)

    class Meta:
        model = DryingProgram
        fields = ['name', 'steps']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'steps': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }


class SpinStepForm(forms.ModelForm):
    class Meta:
        model = SpinStep
        fields = ['spin_speed', 'spin_acceleration', 'spin_time', 'order']

        widgets = {
            'spin_speed': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Spin Speed'}),
            'spin_acceleration': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Spin Acceleration'}),
            'spin_time': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Spin Time'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Order'}),
        }


class SpinCoatingForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        author = kwargs.pop('author', None)  # Retrieve the user from kwargs
        super().__init__(*args, **kwargs)
        if author:
            # Filter the queryset based on the current user
            self.fields['steps'].queryset = SpinStep.objects.filter(
                author=author)

    class Meta:
        model = SpinCoating
        fields = ['name', 'steps', 'antisolvent_used', 'antisolvent',
                  'antisolvent_volume', 'antisolvent_drop_time']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'steps': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'antisolvent_used': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'antisolvent': forms.Select(attrs={'class': 'form-select'}),
            'antisolvent_volume': forms.NumberInput(attrs={'class': 'form-control', }),
            'antisolvent_drop_time': forms.NumberInput(attrs={'class': 'form-control', }),
        }


class ThermalEvaporationStepForm(forms.ModelForm):

    class Meta:
        model = ThermalEvaporationStep
        fields = ['rate', 'time', 'order']

        widgets = {
            'rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Evaporation Rate'}),
            'time': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Evaporation Time'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Order'}),
        }


class ThermalEvaporationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        author = kwargs.pop('author', None)  # Retrieve the user from kwargs
        super().__init__(*args, **kwargs)
        if author:
            # Filter the queryset based on the current user
            self.fields['steps'].queryset = ThermalEvaporationStep.objects.filter(
                author=author)

    class Meta:
        model = ThermalEvaporation
        fields = ['name', 'steps']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'steps': forms.SelectMultiple(attrs={'class': 'form-select'}), }


class InfiltrationForm(forms.ModelForm):
    class Meta:
        model = Infiltration
        fields = ['name', 'volume', 'time', 'precursor_temperature', 'cover']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', }),
            'volume': forms.NumberInput(attrs={'class': 'form-control', }),
            'time': forms.NumberInput(attrs={'class': 'form-control', }),
            'precursor_temperature': forms.NumberInput(attrs={'class': 'form-control', }),
            'cover': forms.CheckboxInput(attrs={'class': 'form-check-input', }),
        }


class ScreenPrintingForm(forms.ModelForm):
    class Meta:
        model = ScreenPrinting
        fields = ['name']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class SlotDieCoatingForm(forms.ModelForm):
    class Meta:
        model = SlotDieCoating
        fields = ['name', 'coating_speed', 'pump_rate', 'wet_film_thickness',
                  'coating_width', 'slot_die_and_substrate_gap',
                  'shim_thickness', 'meniscus_guide_thickness',
                  'meniscus_guide_tab_depth']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'coating_speed': forms.NumberInput(attrs={'class': 'form-control', }),
            'pump_rate': forms.NumberInput(attrs={'class': 'form-control', }),
            'wet_film_thickness': forms.NumberInput(attrs={'class': 'form-control', }),
            'coating_width': forms.NumberInput(attrs={'class': 'form-control', }),
            'slot_die_and_substrate_gap': forms.NumberInput(attrs={'class': 'form-control', }),
            'shim_thickness': forms.NumberInput(attrs={'class': 'form-control', }),
            'meniscus_guide_thickness': forms.NumberInput(attrs={'class': 'form-control', }),
            'meniscus_guide_tab_depth': forms.NumberInput(attrs={'class': 'form-control', }),
        }


class DoctorBladeCoatingForm(forms.ModelForm):
    class Meta:
        model = DoctorBladeCoating
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CoatingParametersForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Retrieve the user from kwargs
        super().__init__(*args, **kwargs)
        if user:
            # Filter the queryset based on the current user
            self.fields['spin_coating'].queryset = SpinCoating.objects.filter(
                author=user)
            self.fields['thermal_evaporation'].queryset = ThermalEvaporation.objects.filter(
                author=user)
            self.fields['infilteration'].queryset = Infiltration.objects.filter(
                author=user)
            self.fields['screen_printing'].queryset = ScreenPrinting.objects.filter(
                author=user)
            self.fields['slot_die_coating'].queryset = SlotDieCoating.objects.filter(
                author=user)
            self.fields['doctor_blade_coating'].queryset = DoctorBladeCoating.objects.filter(
                author=user)

    class Meta:
        model = CoatingParameters
        fields = '__all__'

        widgets = {
            'spin_coating': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'thermal_evaporation': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'infilteration': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'screen_printing': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'slot_die_coating': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'doctor_blade_coating': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
        }


class FormulationForm(forms.ModelForm):
    class Meta:
        model = Formulation
        fields = ['name', 'atmosphere', 'notes', 'created']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Name'}),
            'atmosphere': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Notes'}),
            'created': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
