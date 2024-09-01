import json
from django.contrib import admin
from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from . import views
urlpatterns = [

    # dashboard
    path('', views.dashboardView, name='dashboard'),
    path('dashboard/api/stacks/', views.get_stacks, name='get_stacks'),
    path('api/dashboard_data/', views.dashboard_data_view, name='dashboard_data'),
    path('api/get_experiments_by_user/', views.get_experiments_by_user, name='get_experiments_by_user'),




    # authentication
    path('sign-in/', views.sign_in_view, name='sign_in'),
    path('sign-up/', views.signUpView, name='sign_up'),
    path('sign-out/', views.signOutView, name='sign_out'),

    # password reset
    path('reset-password/', auth_views.PasswordResetView.as_view(
        template_name='password-reset.html'), name='reset_password'),
    path('reset-password-sent/', auth_views.PasswordResetDoneView.as_view(
        template_name='password-reset-done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password-reset-confirm.html'), name='password_reset_confirm'),
    path('reset-password-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password-reset-complete.html'), name='password_reset_complete'),

    # profile
    path('profile/', views.profileView, name='profile'),
    path('profile/update', views.userProfileView, name='update_profile'),

    # supplier
    path('category/', views.categoryView, name='category'),
    path('supplier/', views.supplierView, name='supplier'),
    path('measurement-unit/', views.measurementUnitView, name='measurement_unit'),


    # inventory
    path('inventory/', views.inventoryView, name='inventory'),
    path('inventory/update/<int:inventory_id>/',
         views.updateInventory, name='update_inventory'),

    # project
    path('project/', views.projectView, name='project'),
    path('project/<int:project_id>/', views.projectPageView, name='project-page'),
    path('project/update/<int:project_id>/',
         views.updateProjectView, name='update_project'),

    # experiment
    path('experiment/project/<int:project_id>/',
         views.experimentView, name='experiment'),
    path('experiment/<int:experiment_id>/',
         views.updateExperimentView, name='update_experiment'),
    path('experiment/delete/<int:experiment_id>/',
         views.deleteExperimentView, name='delete_experiment'),

    # experiment page
    path('experiment-page/<int:experiment_id>/',
         views.experimentPageView, name='experiment_page'),

    # stack
    path('stack/', views.stackView, name='stack'),
    path('stack/<int:stack_id>/', views.updateStackView, name='update_stack'),
    path('stack/duplicate_stack/<int:stack_id>/',
         views.duplicateStackView, name='duplicate_stack'),
    path('stack/remove_layer/', views.removeLayerFromStackView, name='remove_layer'),
    path('stack/delete/<int:stack_id>/',
         views.delete_stack_view, name='delete_stack'),

    # layer
    path('layer/', views.layerView, name='layer'),
    path('layer/<int:layer_id>/', views.updateLayerView, name='update_layer'),

    path('layer/layer_type', views.layerTypeView, name='layer_type'),

    path('layer/layer_type/<int:layer_id>/',
         views.updateLayerTypeView, name='update_layer_type'),

    # layer composition
    path('layer-composition/', views.layerCompositionView,
         name='layer_composition'),


    # drying program
    path('drying-program/', views.dryingProgramView, name='drying_program'),
    path('drying-program-step/', views.dryingProgramStepView,
         name='drying_program_step'),

    # spin coating
    path('spin-coating/', views.spinCoatingView, name='spin_coating'),
    path('spin-coating/update/<int:layer_id>/',
         views.updateSpinCoatingView, name='update_spin_coating'),

    # thermal evaporation
    path('thermal-evaporation/', views.thermalEvaporationView,
         name='thermal_evaporation'),
    path('thermal-evaporation-step/', views.thermalEvaporationStepView,
         name='thermal_evaporation_step'),

    # screen printing
    path('screen-printing/', views.screenPrintingView, name='screen_printing'),

    # infiltration
    path('infiltration/', views.infiltrationView, name='infiltration'),

    # slot die coating
    path('slot-die-coating/', views.slotDieCoatingView,
         name='slot_die_coating'),

    # doctor blade coating
    path('doctor-blade-coating/', views.doctorBladeCoatingView,
         name='doctor_blade_coating'),

    # spray pyrolysis
    path('spray-pyrolysis/', views.sprayPyrolysisView, name='spray_pyrolysis'),


    # formulation
    path('formulation/', views.formulationView, name='formulation'),
    path('formulation/update/<int:formulation_id>/',
         views.updateFormulationView, name='update_formulation'),

    # file manager
    path('file-manager/', views.fileManager, name='file_manager'),
    re_path('file-manager/(?P<path>.*)?/$',
            views.fileManager, name='file_manager'),
    path('upload-files/', views.uploadFiles, name='upload_files'),
    path('new_folder/', views.newFolder, name='new_folder'),
    path('delete-files/', views.deleteFiles, name='delete_files'),
    path('rename/', views.rename, name='rename'),
    path('download/', views.downloadFiles, name='download_files'),
    path('view/<path:file_path>/', views.viewFile, name='view_file'),


    # home
    path('home/', views.homeView, name='home'),

]

htmx_urlpatterns = [

    path('spin-step/', views.spinStep, name='spin_step'),

    path('formulation-ingredient/', views.formulationIngredient,
         name='formulation_ingredient'),

]

urlpatterns += htmx_urlpatterns

with open(settings.CONFIG_PATH) as config_file:
    config = json.load(config_file)

if config.get("LOCAL_SERVER"):
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
