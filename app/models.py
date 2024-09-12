import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User


def user_directory_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/users/<username>/<filename>
    return os.path.join('users', instance.user.username, filename)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=100, blank=True, null=True)
    user_dir = models.CharField(
        max_length=1000, unique=True, null=True, blank=True)
    photo = models.ImageField(
        upload_to=user_directory_path, blank=True, null=True)
    color = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user.username


class Category(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = '1.Categories'

    def __str__(self):
        return self.name


class Supplier(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = '2.Suppliers'

    def __str__(self):
        return self.name


class MeasurementUnit(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, unique=True)
    short_name = models.CharField(max_length=10, unique=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = '3.Measurmemt Units'

    def __str__(self):
        return self.short_name


class Inventory(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)

    type_choice = [
        ('Solid', 'Solid'),
        ('Liquid', 'Liquid'),
        ('Gas', 'Gas'),
    ]
    type = models.CharField(max_length=20, choices=type_choice)
    batch = models.CharField(max_length=100)

    arrival_date = models.DateField()
    expiry_date = models.DateField()

    total_units = models.IntegerField()
    unit_size = models.FloatField()

    measurement_unit = models.ForeignKey(
        MeasurementUnit, on_delete=models.SET_NULL, null=True, blank=True)

    notes = models.TextField(null=True, blank=True)
    completed = models.BooleanField(default=False)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = '4.Inventory'
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name


class Project(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE)

    title = models.CharField(max_length=100)
    description = models.TextField()

    collaborators = models.ManyToManyField(
        User, related_name='collaborators')

    created = models.DateTimeField()
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Projects'
        ordering = ['-created']

    def __str__(self):
        return self.title


class Experiment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    objective = models.CharField(max_length=200)
    number_of_variables = models.IntegerField(null=True, blank=True)
    notes = models.TextField()
    created = models.DateTimeField()
    serial_number = models.IntegerField(null=True, blank=True)
    data_dir = models.CharField(max_length=1000, null=True, blank=True)
    notified = models.BooleanField(default=False)

    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Experiments'
        ordering = ['-serial_number']

    def __str__(self):
        return "Expreiment ID:{} {}".format(self.id, self.objective[:20])


class ExperimentStatus(models.Model):
    experiment = models.OneToOneField(Experiment, on_delete=models.CASCADE)
    stacks = models.BooleanField(default=False)
    layers = models.BooleanField(default=False)
    coating_parameters = models.BooleanField(default=False)
    formulations = models.BooleanField(default=False)
    has_jv_files = models.BooleanField(default=False)

class Comment(models.Model):
    Experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True, blank = True, null = True)
    updated = models.DateTimeField(auto_now=True, blank = True, null = True)
class Stack(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    substrate = models.ForeignKey(
        Inventory, on_delete=models.SET_NULL, null=True, blank=True)
    geometry_choices = (
        ('N-I-P', 'N-I-P'),
        ('P-I-N', 'P-I-N'),
        ('Power-Roll', 'Power-Roll'),
        ('Other', 'Other')
    )
    geometry = models.CharField(
        max_length=100, choices=geometry_choices)

    number_of_layers = models.IntegerField(default=0)
    number_of_devices = models.IntegerField(default=0)

    # this os done to check which software is being used for the measurement, default is old software, this will help deal with the output file
    jv_software_choices = (
        ('default', 'default'),
        ('new', 'new')
    )
    jv_software = models.CharField(
        max_length=100, choices=jv_software_choices, default='default')

    jv_dir = models.CharField(max_length=1000, null=True, blank=True)
    hero_device_jv_dir = models.CharField(
        max_length=1000, null=True, blank=True)
    hero_device_pce = models.FloatField(null=True, blank=True)

    completed = models.BooleanField(default=False)
    created = models.DateTimeField()
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = '5.Stacks'
        ordering = ['-created']

    def __str__(self):
        return f'{self.name} (Experiment: {self.experiment.serial_number})'


class SpinStep(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, default='')

    spin_speed = models.IntegerField()
    spin_acceleration = models.IntegerField()
    spin_time = models.IntegerField()
    order = models.IntegerField(default=1)

    class Meta:
        verbose_name_plural = '9.Spin Steps'

    def __str__(self):
        return f'{self.order}. Speed-{self.spin_speed} rpm, Acc-{self.spin_acceleration} rpm, {self.spin_time} s'


class SpinCoating(models.Model):

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, default='')
    name = models.CharField(max_length=100, default='')

    steps = models.ManyToManyField(SpinStep)

    antisolvent_used = models.BooleanField(default=False)
    antisolvent = models.ForeignKey(
        Inventory, on_delete=models.SET_NULL, null=True, blank=True)
    antisolvent_volume = models.FloatField(null=True, blank=True)
    antisolvent_drop_time = models.IntegerField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)

    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Spin Coating'

    def __str__(self):
        return f'{self.name}'


class ThermalEvaporationStep(models.Model):

    author = models.ForeignKey(User, on_delete=models.CASCADE, default='')
    rate = models.FloatField()
    time = models.IntegerField()
    order = models.IntegerField(default=1)

    class Meta:
        verbose_name_plural = '10.Thermal Evaporation Steps'

    def __str__(self):
        return f'Order-{self.order} {self.rate} A/sec, {self.time} sec'


class ThermalEvaporation(models.Model):

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)

    name = models.CharField(max_length=100)
    steps = models.ManyToManyField(ThermalEvaporationStep)

    class Meta:
        verbose_name_plural = 'Thermal Evaporation'

    def __str__(self):
        return f'{self.name}'


class Infiltration(models.Model):

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True, blank=True)
    volume = models.FloatField(null=True, blank=True)
    time = models.IntegerField(null=True, blank=True)
    precursor_temperature = models.FloatField(null=True, blank=True)
    cover = models.BooleanField()

    class Meta:
        verbose_name_plural = 'Infiltration'

    def __str__(self):
        return f'{self.name}'


class ScreenPrinting(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Screen Printing'

    def __str__(self):
        return f'{self.name}'

#### A bridge between layer and all coating techniques to add respective parameters ####


class SlotDieCoating(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    coating_speed = models.FloatField(null=True, blank=True)
    wet_film_thickness = models.FloatField(null=True, blank=True)
    slot_die_and_substrate_gap = models.FloatField(null=True, blank=True)
    coating_width = models.FloatField(null=True, blank=True)
    shim_thickness = models.FloatField(null=True, blank=True)
    meniscus_guide_thickness = models.FloatField(null=True, blank=True)
    meniscus_guide_tab_depth = models.FloatField(null=True, blank=True)
    pump_rate = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Slot Die Coating'

    def __str__(self):
        return f'{self.name}'


class DoctorBladeCoating(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Doctor Blade Coating'

    def __str__(self):
        return f'{self.name}'


class SprayPyrolysis(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Spray Pyrolysis'

    def __str__(self):
        return f'{self.name}'


class CoatingParameters(models.Model):

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, default='')
    spin_coating = models.ForeignKey(
        SpinCoating, on_delete=models.CASCADE, null=True, blank=True)
    thermal_evaporation = models.ForeignKey(
        ThermalEvaporation, on_delete=models.CASCADE, null=True, blank=True)
    infiltration = models.ForeignKey(
        Infiltration, on_delete=models.CASCADE, null=True, blank=True)

    screen_printing = models.ForeignKey(
        ScreenPrinting, on_delete=models.CASCADE, null=True, blank=True)

    slot_die_coating = models.ForeignKey(
        SlotDieCoating, on_delete=models.CASCADE, null=True, blank=True)

    doctor_blade_coating = models.ForeignKey(
        DoctorBladeCoating, on_delete=models.CASCADE, null=True, blank=True)
    spray_pyrolysis = models.ForeignKey(
        SprayPyrolysis, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        if self.thermal_evaporation:
            return f'Thermal Evaporation: {self.thermal_evaporation}'
        elif self.spin_coating:
            return f'Spin Coating: {self.spin_coating}'
        elif self.infiltration:
            return f'Infiltration: {self.infiltration}'
        elif self.screen_printing:
            return f'Screen Printing: {self.screen_printing}'
        elif self.slot_die_coating:
            return f'Slot Die Coating: {self.slot_die_coating}'
        elif self.doctor_blade_coating:
            return f'Doctor Blade Coating: {self.doctor_blade_coating}'
        else:
            return f'No Coating Parameters'

    class Meta:
        verbose_name_plural = 'Coating Parameters'


class DryingProgramStep(models.Model):

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.IntegerField()
    temperature = models.FloatField()
    order = models.IntegerField(default=1)

    class Meta:
        verbose_name_plural = 'Drying Steps'

    def __str__(self):
        return f'Order-{self.order} {self.temperature} C, {self.time} minutes'


class DryingProgram(models.Model):

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    steps = models.ManyToManyField(DryingProgramStep)

    class Meta:
        verbose_name_plural = 'Drying Programs'

    def __str__(self):
        return f'{self.name}'


class LayerComposition(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Layer Composition'

    def __str__(self):
        return f'{self.name}'


class Layer(models.Model):
    # general info
    stacks = models.ManyToManyField(Stack, related_name='layers')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    sequence = models.IntegerField()
    layer_type_choices = (
        ('Coating Layer', 'Coating Layer'),
        ('Surface Treatment', 'Surface Treatment'),
    )

    layer_type = models.CharField(
        max_length=100, choices=layer_type_choices, default='Coating Layer')
    layer_role_choices = (
        ('ETL', 'ETL'),
        ('Active Layer', 'Active Layer'),
        ('HTL', 'HTL'),
        ('Top Contact', 'Top Contact'),
        ('Other', 'Other'),
    )
    layer_composition = models.ForeignKey(
        LayerComposition, on_delete=models.SET_NULL, null=True, blank=True)

    layer_role = models.CharField(
        max_length=100, choices=layer_role_choices, null=True, blank=True)
    formulation_volume = models.FloatField(null=True, blank=True)

    # room info
    atmosphere_choices = (
        ('N2', 'N2'),
        ('Air', 'Air'),
        ('Other', 'Other'),
    )
    atmosphere = models.CharField(
        max_length=50, choices=atmosphere_choices, null=True, blank=True)
    room_temperature = models.IntegerField(blank=True, null=True)
    room_humidity = models.IntegerField(blank=True, null=True)

    # drying info
    drying_type_choices = (
        ('Hot Plate', 'Hot Plate'),
        ('Covection Oven', 'Covection Oven'),
        ('Other', 'Other'),
    )
    drying_type = models.CharField(
        max_length=50, choices=drying_type_choices, null=True, blank=True)
    drying_program = models.ForeignKey(
        DryingProgram, on_delete=models.SET_NULL, null=True, blank=True
    )
    # coating info
    dry_film_thickness = models.FloatField(blank=True, null=True)
    coating_method_choices = (
        ('Spin Coating', 'Spin Coating'),
        ('Thermal Evaporation', 'Thermal Evaporation'),
        ('Screen Printing', 'Screen Printing'),
        ('Infiltration', 'Infiltration'),
        ('Slot Die Coating', 'Slot Die Coating'),
        ('Doctor Blade Coating', 'Doctor Blade Coating'),
        ('Spray Pyrolysis', 'Spray Pyrolysis'),
    )
    coating_method = models.CharField(
        max_length=100, choices=coating_method_choices, null=True, blank=True)

    # coating method parameters
    coating_parameters = models.ForeignKey(
        CoatingParameters, on_delete=models.SET_NULL, null=True, blank=True
    )

    # formulation info
    formulation = models.ForeignKey(
        'Formulation', on_delete=models.SET_NULL, null=True, blank=True)

    # date
    created = models.DateTimeField()

    # surface treatment
    treatment_choices = (
        ("UV-Ozone", "UV-Ozone"),
        ("Plasma", "Plasma"),
        ("Corona", "Corona"),
        ("Other", "Other"),
    )
    treatment = models.CharField(
        max_length=100, choices=treatment_choices, null=True, blank=True
    )
    treatment_time = models.IntegerField(null=True, blank=True)
    treatment_power = models.IntegerField(null=True, blank=True)

    # not required user input
    completed = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = '6.Layers'
        ordering = ['sequence']

    def __str__(self):
        return f'{self.name}'


class Formulation(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    atmosphere = models.CharField(max_length=10, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)

    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = '8.Formulations'
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name


class FormulationComponent(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    formulation = models.ForeignKey(Formulation, on_delete=models.CASCADE)
    quantity = models.FloatField()
    measurement_unit = models.ForeignKey(
        MeasurementUnit, on_delete=models.SET_NULL, null=True, blank=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
