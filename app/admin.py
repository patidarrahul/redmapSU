from django.contrib import admin
from . models import *
# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(Supplier)
admin.site.register(MeasurementUnit)
admin.site.register(Inventory)
admin.site.register(Project)
admin.site.register(Experiment)
admin.site.register(Stack)
admin.site.register(ExperimentStatus)
admin.site.register(Layer)
admin.site.register(SpinCoating)


admin.site.register(SpinStep)
admin.site.register(CoatingParameters)

admin.site.register(Formulation)

admin.site.register(FormulationComponent)

admin.site.register(ThermalEvaporationStep)
admin.site.register(ThermalEvaporation)
admin.site.register(DryingProgram)
admin.site.register(DryingProgramStep)
admin.site.register(ScreenPrinting)
admin.site.register(Infiltration)
admin.site.register(SlotDieCoating)
