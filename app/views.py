import os
import shutil
from pathlib import Path
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import Http404, HttpResponse, JsonResponse
from django.urls import reverse
from django.db.models import Q
from django.shortcuts import redirect, render, get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required
from .forms import *
import logging
import pyperclip
import plotly.express as px
import plotly.graph_objects as go


from .utils import *


logger = logging.getLogger(__name__)

# Create your views here.


def signUpView(request):
    """
    A view function that handles user registration.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the 'sign-up.html' template with the form data.

    Description:
        This function handles user registration. It first checks if the user is already authenticated.
        If the user is authenticated, it redirects them to the 'index' page.
        If the user is not authenticated, it checks if the request method is POST.
        If the request method is POST, it creates a UserForm instance with the data from the request.
        If the form is valid, it creates a new user by saving the form data.
        It then creates a directory for the user in the 'users' directory of the media root.
        It logs in the user and displays a success message.
        If the form is not valid, it displays an error message.
        If the request method is not POST, it creates a UserForm instance without any data.
        It renders the 'sign-up.html' template with the form data.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        if request.method == 'POST':
            form = UserForm(request.POST)
            if form.is_valid():
                try:
                    user = form.save(commit=False)

                    # check username or email already exists
                    if User.objects.filter(Q(username=user.username) | Q(email=user.email)).exists():
                        raise Exception(
                            f'Username or email already exists: {user.username} or {user.email} choose another username or email')

                    # check user dir exist:
                    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'users')):
                        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'users'))
                    # create a directory inside users directory with username
                    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'users', f'{user.username}')):
                        os.makedirs(os.path.join(
                            settings.MEDIA_ROOT, 'users', f'{user.username}'))

                    user_dir = os.path.join(
                        'users', f'{user.username}')

                    user.save()
                    UserProfile.objects.create(user=user, user_dir=user_dir)

                    messages.success(request, 'User created successfully.')
                    return redirect('dashboard')
                except Exception as e:
                    messages.error(request, f'Failed to create user: {str(e)}')
        else:
            form = UserForm()

        return render(request, 'sign-up.html', {'form': form})


@login_required(login_url='sign_in')
def userProfileView(request):
    user = request.user
    user_dir = UserProfile.objects.get(user=user).user_dir
    form = UserProfileForm(initial={'user_dir': user_dir})
    user_profile = get_object_or_404(UserProfile, user=user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'User profile updated successfully.')
            return redirect('profile')

    return render(request, 'user-profile.html', {'form': form})


@login_required(login_url='sign_in')
def signOutView(request):
    logout(request)
    messages.success(request, f'You have been logged out.')
    return redirect('sign_in')


def signInView(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        if request.method == 'POST':
            form = SignInForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                user = authenticate(
                    request, username=username, password=password)
                if user is not None:
                    try:
                        login(request, user)
                        # Redirect to the home page after successful sign-in
                        return redirect('dashboard')
                    except Exception as e:
                        messages.error(request, f'Failed to sign in: {str(e)}')
                else:
                    form.add_error(None, 'Invalid username or password')
        else:
            form = SignInForm()
    return render(request, 'sign-in.html', {'form': form})


@login_required(login_url='sign_in')
def profileView(request):

    user = request.user

    projects = Project.objects.filter(Q(author=user) | Q(collaborators=user))

    context = {'projects': projects}
    return render(request, 'profile.html', context)


@login_required(login_url='sign_in')
def categoryView(request):
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.author = request.user
            category.save()
            messages.success(request, 'Category created successfully.')
            return redirect(reverse('inventory') + f'?category={category.id}')

    return render(request, 'category.html', {'form': form})


@login_required(login_url='sign_in')
def measurementUnitView(request):
    form = MeasurementUnitForm()
    if request.method == 'POST':
        form = MeasurementUnitForm(request.POST)
        if form.is_valid():
            measurement_unit = form.save(commit=False)
            measurement_unit.author = request.user
            measurement_unit.save()
            messages.success(request, 'Measurement unit created successfully.')
            return redirect(reverse('inventory') + f'?measurement_unit={measurement_unit.id}')

    return render(request, 'measurement-unit.html', {'form': form})


@login_required(login_url='sign_in')
def supplierView(request):
    suppliers = Supplier.objects.all()

    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.author = request.user
            supplier.save()
            return redirect(reverse('inventory') + f'?supplier={supplier.id}')

    else:
        form = SupplierForm()

    context = {'suppliers': suppliers, 'form': form}
    return render(request, 'supplier.html', context)


@login_required(login_url='sign_in')
def inventoryView(request):
    """
    A view function to render the inventory page with the InventoryForm.
    """

    if request.method == 'POST':

        # Use Django forms to handle form data
        form = InventoryForm(request.POST)
        if form.is_valid():

            # Create inventory object without saving to the database yet
            inventory = form.save(commit=False)
            inventory.author = request.user  # Set added_by field

            try:
                inventory.save()  # Save inventory object to the database
                messages.success(request, 'Inventory added successfully.')

            except Exception as e:
                messages.error(request, f'Failed to add inventory: {str(e)}')
        else:
            messages.error(
                request, 'Form is invalid. Please check the entered data.')

    else:

        form = InventoryForm()

    if request.method == 'GET':

        q = request.GET.get('q')
        if q:
            inventories = Inventory.objects.filter(Q(name__icontains=q) | Q(
                short_name__icontains=q) | Q(batch__icontains=q))

        else:
            inventories = Inventory.objects.all()
    else:
        inventories = Inventory.objects.all()

    context = {'form': form, 'inventories': inventories}
    return render(request, 'inventory.html', context)


@login_required(login_url='sign_in')
def updateInventory(request, inventory_id):
    """
    A view function to update inventory information in the database.
    Validates and saves the updated form data if the form is valid.
    Redirects to the inventory list page upon successful update.

    Parameters:
        request (HttpRequest): The HTTP request object.
        inventory_id (int): The ID of the inventory to be updated.

    Returns:
        HttpResponse: Renders the 'update-inventory.html' template with the form data.
    """
    inventory = get_object_or_404(
        Inventory, pk=inventory_id)  # Retrieve the inventory object to be updated

    if request.method == 'POST':
        # Populate the form with the data from the inventory object
        form = InventoryForm(request.POST, instance=inventory)

        if form.is_valid():
            form.save()  # Save the updated form data to the database
            messages.success(request, 'Inventory updated successfully.')
            return redirect('inventory')
        else:
            messages.error(
                request, 'Form is invalid. Please check the entered data.')
    else:
        form = InventoryForm(instance=inventory)
        action = 'update'

    return render(request, 'inventory.html', {'form': form, 'inventory': inventory, 'inventories': Inventory.objects.all(), 'action': action})


@login_required(login_url='sign_in')
def projectPageView(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    context = {'project': project}
    return render(request, 'project-page.html', context)


@login_required(login_url='sign_in')
def projectView(request):

    if request.method == 'POST':
        try:

            form = ProjectForm(request.POST)
            if form.is_valid():
                project = form.save(commit=False)
                project.author = request.user
                project.save()
                messages.success(request, 'Project created successfully.')
                return redirect('profile')
        except Exception as e:
            messages.error(request, f'Failed to save project: {e}')
            # You might want to log the exception for debugging purposes

    else:
        form = ProjectForm()
    context = {'form': form}
    return render(request, 'project.html', context)


def updateProjectView(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    form = ProjectForm(instance=project)
    action = 'update'
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully.')
            return redirect('profile')
    context = {'form': form, 'action': action}
    return render(request, 'project.html', context)


@ login_required(login_url='sign_in')
def experimentPageView(request, experiment_id):
    experiment = get_object_or_404(Experiment, pk=experiment_id)

    figures = jvBoxPlot(experiment_id)  # defined in utils.py
    heroJV(experiment_id)
    jv_chart = figures['fig_jv'].to_html()
    voc_chart = figures['fig_voc'].to_html()
    ff_chart = figures['fig_ff'].to_html()
    pce_chart = figures['fig_pce'].to_html()

    context = {'experiment': experiment, 'jv_chart': jv_chart,
               'voc_chart': voc_chart, 'ff_chart': ff_chart, 'pce_chart': pce_chart}
    return render(request, 'experiment-page.html', context)


@ login_required(login_url='sign_in')
def experimentView(request, project_id):
    """
    View function for adding a new experiment to a project.

    Args:
        request: HTTP request object.
        project_id: ID of the project to which the experiment will be added.

    Returns:
        Rendered HTML template displaying the form to add a new experiment or an error page.

    Raises:
        Http404: If the specified project does not exist.
    """
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        logger.error("Project with ID %s does not exist", project_id)
        # Render a custom error page if needed
        raise Http404("Project does not exist")
    total_experiment = Experiment.objects.filter(project=project).count()
    next_experiment_number = total_experiment + 1
    if request.method == 'POST':
        form = ExperimentForm(request.POST)
        if form.is_valid():
            try:
                experiment = form.save(commit=False)
                experiment.project = project
                experiment.author = request.user
                experiment.save()
                experiment_status = ExperimentStatus.objects.create(
                    experiment=experiment)
                experiment_status.save()

                messages.success(request, 'Experiment saved successfully.')
                # Redirect to profile page after successful addition
                return redirect('project-page', experiment.project.id)
            except Exception as e:
                logger.error("Error saving experiment: %s", str(e))
                messages.error(
                    request, 'An error occurred while saving the experiment.')
    else:
        form = ExperimentForm(
            initial={'project': project, 'serial_number': next_experiment_number})

    context = {'form': form}
    return render(request, 'experiment.html', context)


@ login_required(login_url='sign_in')
def updateExperimentView(request, experiment_id):
    """
    Updates an experiment with the given experiment_id using the provided form data.

    Parameters:
        request (HttpRequest): The HTTP request object.
        experiment_id (int): The ID of the experiment to be updated.

    Returns:
        HttpResponse: The HTTP response object. If the form is valid, the experiment is saved, a success message is displayed, and the user is redirected to the 'profile' page. Otherwise, the form is rendered with the existing experiment data.
    """

    experiment = get_object_or_404(Experiment, pk=experiment_id)

    if request.method == 'POST':
        form = ExperimentForm(request.POST, instance=experiment)
        if form.is_valid():
            form.save()
            project = experiment.project.id

            messages.success(request, 'Experiment saved successfully.')
            return redirect('project-page', project)
    else:
        form = ExperimentForm(instance=experiment)

    context = {'form': form, 'action': 'update'}
    return render(request, 'experiment.html', context)


def updateExperimentStatus(instance):
    """
    Updates the status of an experiment based on the given referrer and instance.

    Args:
        referrer (str): The source of the update. Something like 'stack' or 'layer'.
        instance (Experiment): The experiment instance to update.

    Returns:
        None

    Raises:
        ValueError: If the referrer is not 'stack' or 'layer'.

    This function updates the status of an experiment based on the given referrer and instance.
    If the referrer is 'stack', the 'stacks' field of the experiment's ExperimentStatus is set to True and saved.
    If the referrer is 'layer', the 'layers' field of the experiment's ExperimentStatus is set to True if all stacks in the experiment have the same number of layers as specified.
    If the referrer is neither 'stack' nor 'layer', a ValueError is raised.
    """

    # get the experment instance
    experiment = instance

    # update satck status

    if experiment.stack_set.count() == experiment.number_of_variables:

        experiment.experimentstatus.stacks = True
        experiment.experimentstatus.save()
    else:

        experiment.experimentstatus.stacks = False

    # update layer status

    if all(stack.layer_set.count() == stack.number_of_layers for stack in experiment.stack_set.all()):

        experiment.experimentstatus.layers = True
        experiment.experimentstatus.save()
    else:

        experiment.experimentstatus.layers = False
        experiment.experimentstatus.save()

    # update coating parameters status

    # Initially assuming all layers have coating parameters
    coating_parameters_status = True

    for stack in experiment.stack_set.all():
        for layer in stack.layer_set.all():
            if not layer.coating_parameters:
                # As soon as we find a layer without coating parameters, set status to False and break
                coating_parameters_status = False
                break
            else:
                continue

    if coating_parameters_status:
        experiment.experimentstatus.coating_parameters = True
        experiment.experimentstatus.save()
    else:
        experiment.experimentstatus.coating_parameters = False
        experiment.experimentstatus.save()

    # update formulation status


@ login_required(login_url='sign_in')
def stackView(request):
    """
    View function for displaying and handling the creation of Stack objects.

    Parameters:
        request (HttpRequest): The HTTP request object.
        experiment_id (int, optional): The ID of the experiment to which the stack belongs. Defaults to None.

    Returns:
        HttpResponse: The HTTP response object. If the request method is POST and the form is valid, the stack is saved, a success message is displayed, and the user is redirected to the 'stack' page. Otherwise, the form is rendered with the existing stacks.
    """
    if request.GET.get('experiment'):
        experiment_id = request.GET.get('experiment')
        experiment = get_object_or_404(Experiment, pk=experiment_id)
        form = StackForm(initial={'experiment': experiment})
    else:
        form = StackForm()

    if request.method == 'POST':
        form = StackForm(request.POST)
        if form.is_valid():
            stack = form.save(commit=False)
            stack.author = request.user
            experiment_dir = stack.experiment.data_dir

            try:
                # Create stack directory inside JV directory
                stack_jv_dir = os.path.join(
                    settings.MEDIA_ROOT, experiment_dir, 'JV', stack.name)

                if not os.path.exists(stack_jv_dir):
                    os.makedirs(stack_jv_dir)
                else:
                    raise Exception(
                        'Stack directory already exists, chose another name for stack')

                stack.jv_dir = os.path.join(experiment_dir, 'JV', stack.name)
                stack.save()

            except Exception as e:
                messages.error(request, str(e))
                return redirect('stack')

            # Update experiment status
            experiment = Experiment.objects.get(pk=stack.experiment.pk)
            updateExperimentStatus(experiment)

            messages.success(request, 'Stack saved successfully.')
            if request.GET.get('experiment'):
                return redirect('project-page', stack.experiment.project.pk)
            else:
                return redirect('stack')

    stacks = Stack.objects.all()
    context = {'form': form, 'stacks': stacks}

    return render(request, 'stack.html', context)


@ login_required(login_url='sign_in')
def updateStackView(request, stack_id):
    stack = get_object_or_404(Stack, pk=stack_id)

    if request.method == 'POST':
        form = StackForm(request.POST, instance=stack)
        if form.is_valid():
            if request.POST.get('save_as_new'):
                # Create a new instance with the updated data
                new_stack = form.save(commit=False)
                new_stack.pk = None  # Clear the primary key to create a new instance

                experiment_dir = new_stack.experiment.data_dir
                try:
                    # Create stack directory inside JV directory
                    stack_jv_dir = os.path.join(settings.MEDIA_ROOT,
                                                experiment_dir, 'JV', new_stack.name)

                    if not os.path.exists(stack_jv_dir):
                        os.makedirs(stack_jv_dir)
                    else:
                        raise Exception(
                            'Stack directory already exists, chose another name for stack')

                    new_stack.jv_dir = os.path.join(
                        experiment_dir, 'JV', new_stack.name)
                    new_stack.save()

                except Exception as e:
                    messages.error(request, str(e))
                    return redirect('stack')
                # Update experiment status
                experiment = Experiment.objects.get(pk=new_stack.experiment.pk)
                updateExperimentStatus(experiment)

                messages.success(
                    request, 'Stack saved as a new instance successfully.')
                project_id = new_stack.experiment.project.pk
                return redirect('project-page', project_id)
            else:
                stack = form.save(commit=False)

                experiment_dir = stack.experiment.data_dir
                # what if jv_dir field was added later
                try:
                    # Create stack directory inside JV directory
                    stack_jv_dir = os.path.join(settings.MEDIA_ROOT,
                                                experiment_dir, 'JV', stack.name)

                    if not os.path.exists(stack_jv_dir):
                        os.makedirs(stack_jv_dir)
                    else:
                        raise Exception(
                            'Stack directory already exists, chose another name for stack')

                    stack.jv_dir = os.path.join(
                        experiment_dir, 'JV', stack.name)
                    stack.save()

                except Exception as e:
                    messages.error(request, str(e))
                    return redirect('stack')
                    # Update experiment status
                experiment = Experiment.objects.get(pk=stack.experiment.pk)
                updateExperimentStatus(experiment)

                messages.success(request, 'Stack updated successfully.')
                project_id = stack.experiment.project.pk
                return redirect('project-page', project_id)
    else:
        form = StackForm(instance=stack)

    context = {'form': form,  'action': 'update'}
    return render(request, 'stack.html', context)


@ login_required(login_url='sign_in')
def layerTypeView(request):
    layer_type = request.POST.get('layer_type')
    if layer_type == 'Surface Treatment':
        return render(request, 'partials/surface-treatment.html', {'form': LayerForm(author=request.user)})
    elif layer_type == 'Coating Layer':
        return render(request, 'partials/coating-layer.html',
                      {'form': LayerForm(author=request.user), 'coating_parameters_form': CoatingParametersForm()})


@ login_required(login_url='sign_in')
def layerView(request):
    stack_id = request.GET.get('stack') or None

    if stack_id:
        stack = get_object_or_404(Stack, pk=stack_id)
        form = LayerForm(initial={'stack': stack}, author=request.user)

    else:
        form = LayerForm(author=request.user)
    coating_parameters_form = CoatingParametersForm()

    if request.method == 'POST':
        form = LayerForm(request.POST)

        if form.is_valid():
            layer = form.save(commit=False)
            layer.author = request.user
            # Get the selected coating method
            if layer.layer_type == 'Surface Treatment':
                layer.coating_parameters = None
                layer.save()
                experiment = Experiment.objects.get(
                    pk=layer.stack.experiment.pk)
                project_id = experiment.project.pk
                messages.success(request, ' Treatment added successfully.')
                return redirect('project-page', project_id)

            elif layer.coating_method == 'Spin Coating':

                # Get the selected spin coating instance
                spin_coating_instance = request.POST.get('spin_coating')

                spin_coating = SpinCoating.objects.get(
                    pk=spin_coating_instance)

                # Create a new CoatingParameters instance with the selected spin coating and add it to the layer
                coating_parameters, created = CoatingParameters.objects.get_or_create(
                    author=request.user, spin_coating=spin_coating)
                layer.coating_parameters = coating_parameters

            elif layer.coating_method == 'Thermal Evaporation':
                # Get the selected thermal evaporation instance
                thermal_evaporation_instance = request.POST.get(
                    'thermal_evaporation')
                # if user selects a non thermal evaporation settings then show error
                thermal_evaporation = ThermalEvaporation.objects.get(
                    pk=thermal_evaporation_instance)

                # Create a new CoatingParameters instance with the selected thermal evaporation and add it to the layer
                coating_parameters, created = CoatingParameters.objects.get_or_create(
                    author=request.user, thermal_evaporation=thermal_evaporation)
                layer.coating_parameters = coating_parameters

            elif layer.coating_method == 'Screen Printing':

                # Get the selected screen printing instance
                screen_printing_instance = request.POST.get('screen_printing')

                screen_printing = ScreenPrinting.objects.get(
                    pk=screen_printing_instance)

                # Create a new CoatingParameters instance with the selected screen printing and add it to the layer
                coating_parameters, created = CoatingParameters.objects.get_or_create(
                    author=request.user, screen_printing=screen_printing)
                layer.coating_parameters = coating_parameters

            elif layer.coating_method == 'Infiltration':
                # Get the selected Infiltration instance
                infilteration_instance = request.POST.get('infilteration')

                infilteration = Infiltration.objects.get(
                    pk=infilteration_instance)

                # Create a new CoatingParameters instance with the selected Infiltration and add it to the layer
                coating_parameters, created = CoatingParameters.objects.get_or_create(
                    author=request.user, infilteration=infilteration)

            else:
                messages.error(
                    request, 'Selected coating method is not supported.')
                return redirect('layer')

            layer.save()
            experiment = Experiment.objects.get(pk=layer.stack.experiment.pk)
            updateExperimentStatus(experiment)
            messages.success(request, 'Layer saved successfully.')
            project_id = experiment.project.pk
            return redirect('project-page', project_id)

    # Set the querysets for the form fields based on the user
    form.fields['stack'].queryset = Stack.objects.filter(
        author=request.user
    )
    form.fields['formulation'].queryset = Formulation.objects.filter(
        author=request.user
    )

    # Set the querysets for the all the form fields based on the user

    coating_parameters_form['thermal_evaporation'].queryset = ThermalEvaporation.objects.filter(
        author=request.user
    )
    coating_parameters_form['spin_coating'].queryset = SpinCoating.objects.filter(
        author=request.user
    )

    context = {

        'form': form,
        'coating_parameters_form': coating_parameters_form,

    }

    return render(request, 'layer.html', context)


@ login_required(login_url='sign_in')
def updateLayerTypeView(request, layer_id):
    layer = get_object_or_404(Layer, pk=layer_id)
    layer_type = request.POST.get('layer_type')
    if layer_type == 'Surface Treatment':
        return render(request, 'partials/surface-treatment.html', {'form': LayerForm(author=request.user, instance=layer)})
    elif layer_type == 'Coating Layer':
        coating_parameters = layer.coating_parameters.id
        coating_parameters = CoatingParameters.objects.get(pk=coating_parameters)
        
        return render(request, 'partials/coating-layer.html',
                      {'form': LayerForm(author=request.user, instance=layer), 'coating_parameters_form': CoatingParametersForm(instance = coating_parameters)})


@ login_required(login_url='sign_in')
def updateLayerView(request, layer_id):
    layer = get_object_or_404(Layer, pk=layer_id)

    if request.method == 'POST':
        form = LayerForm(request.POST, instance=layer)
        if form.is_valid():
            if request.POST.get('save_as_new'):
                # Create a new instance with the updated data
                new_layer = form.save(commit=False)
                new_layer.pk = None  # Clear the primary key to create a new instance

                if new_layer.layer_type == 'Surface Treatment':
                    new_layer.coating_parameters = None
                    new_layer.save()
                    experiment = Experiment.objects.get(
                        pk=new_layer.stack.experiment.pk)
                    project_id = experiment.project.pk
                    messages.success(request, ' Treatment added successfully.')
                    return redirect('project-page', project_id)

                elif new_layer.coating_method == 'Spin Coating':

                    # Get the selected spin coating instance
                    spin_coating_instance = request.POST.get('spin_coating')
                    spin_coating = SpinCoating.objects.get(
                        pk=spin_coating_instance)

                    # Create a new CoatingParameters instance with the selected spin coating and add it to the layer
                    coating_parameters, created = CoatingParameters.objects.get_or_create(
                        author=request.user, spin_coating=spin_coating)
                    layer.coating_parameters = coating_parameters

                elif new_layer.coating_method == 'Thermal Evaporation':
                    # Get the selected thermal evaporation instance
                    thermal_evaporation_instance = request.POST.get(
                        'thermal_evaporation')
                    thermal_evaporation = ThermalEvaporation.objects.get(
                        pk=thermal_evaporation_instance)

                    # Create a new CoatingParameters instance with the selected thermal evaporation and add it to the layer
                    coating_parameters, created = CoatingParameters.objects.get_or_create(
                        author=request.user, thermal_evaporation=thermal_evaporation)
                    layer.coating_parameters = coating_parameters

                elif new_layer.coating_method == 'Infiltration':
                    # Get the selected Infiltration instance
                    infilteration_instance = request.POST.get('infilteration')
                    infilteration = Infiltration.objects.get(
                        pk=infilteration_instance)

                    # Create a new CoatingParameters instance with the selected Infiltration and add it to the layer
                    coating_parameters, created = CoatingParameters.objects.get_or_create(
                        author=request.user, infilteration=infilteration)
                    layer.coating_parameters = coating_parameters

                elif new_layer.coating_method == 'Screen Printing':
                    # Get the selected Screen Printing instance
                    screen_printing_instance = request.POST.get(
                        'screen_printing')
                    screen_printing = ScreenPrinting.objects.get(
                        pk=screen_printing_instance)

                    # Create a new CoatingParameters instance with the selected Screen Printing and add it to the layer
                    coating_parameters, created = CoatingParameters.objects.get_or_create(
                        author=request.user, screen_printing=screen_printing)

                else:
                    messages.error(
                        request, 'Selected coating method is not supported.')
                    return redirect('layer')
                new_layer.save()

                # Update experiment status
                experiment = Experiment.objects.get(
                    pk=new_layer.stack.experiment.pk)
                updateExperimentStatus(experiment)
                messages.success(
                    request, 'Layer saved as a new instance successfully.')
                project_id = new_layer.stack.experiment.project.pk
                return redirect('project-page', project_id)
            else:
                layer = form.save(commit=False)

                if layer.layer_type == 'Surface Treatment':
                    layer.coating_parameters = None

                if layer.coating_method == 'Spin Coating':

                    # Get the selected spin coating instance
                    spin_coating_instance = request.POST.get('spin_coating')
                    spin_coating = SpinCoating.objects.get(
                        pk=spin_coating_instance)

                    # Create a new CoatingParameters instance with the selected spin coating and add it to the layer
                    coating_parameters, created = CoatingParameters.objects.get_or_create(
                        author=request.user, spin_coating=spin_coating)
                    layer.coating_parameters = coating_parameters

                elif layer.coating_method == 'Thermal Evaporation':
                    # Get the selected thermal evaporation instance
                    thermal_evaporation_instance = request.POST.get(
                        'thermal_evaporation')
                    # if user selects a non thermal evaporation settings then show error
                    thermal_evaporation = ThermalEvaporation.objects.get(
                        pk=thermal_evaporation_instance)

                    # Create a new CoatingParameters instance with the selected thermal evaporation and add it to the layer
                    coating_parameters, created = CoatingParameters.objects.get_or_create(
                        author=request.user, thermal_evaporation=thermal_evaporation)
                    layer.coating_parameters = coating_parameters

                elif layer.coating_method == 'Infiltration':
                    # Get the selected Infiltration instance
                    infilteration_instance = request.POST.get('infilteration')
                    infilteration = Infiltration.objects.get(
                        pk=infilteration_instance)

                    # Create a new CoatingParameters instance with the selected Infiltration and add it to the layer
                    coating_parameters, created = CoatingParameters.objects.get_or_create(

                        author=request.user, infilteration=infilteration)
                    layer.coating_parameters = coating_parameters

                elif layer.coating_method == 'Screen Printing':
                    # Get the selected Screen Printing instance
                    screen_printing_instance = request.POST.get(
                        'screen_printing')
                    screen_printing = ScreenPrinting.objects.get(
                        pk=screen_printing_instance)

                    # Create a new CoatingParameters instance with the selected Screen Printing and add it to the layer
                    coating_parameters, created = CoatingParameters.objects.get_or_create(
                        author=request.user, screen_printing=screen_printing)

                else:
                    messages.error(
                        request, 'Selected coating method is not supported.')
                    return redirect('layer')
                layer.save()
                experiment = Experiment.objects.get(
                    pk=layer.stack.experiment.pk)
                updateExperimentStatus(experiment)
                messages.success(request, 'Layer updated successfully.')
                project_id = layer.stack.experiment.project.pk
                return redirect('project-page', project_id)
    else:
        form = LayerForm(instance=layer, author=request.user)

    context = {'form': form, 'coating_parameters_form': CoatingParametersForm(
        instance=layer.coating_parameters), 'layer_id': layer_id, 'action': 'update'}
    return render(request, 'update-layer.html', context)


@ login_required(login_url='sign_in')
def dryingProgramView(request):
    if request.method == 'POST':
        form = DryingProgramForm(request.POST)
        if form.is_valid():
            drying_program = form.save(commit=False)
            drying_program.author = request.user

            # Check if a similar entry already exists by name
            if not DryingProgram.objects.filter(name=form.cleaned_data['name'], author=request.user).exists():
                form.save()
                messages.success(request, 'Drying program saved successfully.')

            else:
                messages.error(
                    request, 'A Drying program with this name already exists.')

    context = {'form': DryingProgramForm(),
               'step_form': DryingProgramStepForm()}
    return render(request, 'drying-program.html', context)


@ login_required(login_url='sign_in')
def layerCompositionView(request):

    if request.method == 'POST':
        form = LayerCompositionForm(request.POST)
        if form.is_valid():
            composition = form.save(commit=False)

            # Check if a similar entry already exists
            if not LayerComposition.objects.filter(name__iexact=form.cleaned_data['name'], author=request.user).exists():
                composition.author = request.user
                composition.save()
                messages.success(
                    request, 'Layer composition saved successfully.')
                return redirect('layer')

            else:
                messages.error(
                    request, 'A Layer composition with this name already exists.')

    context = {'form': LayerCompositionForm()}

    return render(request, 'layer-composition.html', context)


@ login_required(login_url='sign_in')
def dryingProgramStepView(request):

    form = DryingProgramStepForm(request.POST)
    message = ''
    if form.is_valid():
        form.author = request.user
        # Check if a similar entry already exists
        if not DryingProgramStep.objects.filter(**form.cleaned_data).exists():
            step = form.save(commit=False)
            step.author = request.user
            step.save()
            message = 'Drying step saved successfully.'

        else:
            message = 'An identical drying step already exists.'

    # to show the steps field in drying program form
    return render(request, 'partials/drying-step-selection-field copy.html', {'form': DryingProgramForm(), 'message': message})


@ login_required(login_url='sign_in')
def spinStep(request):
    form = SpinStepForm(request.POST)
    if form.is_valid():
        form.author = request.user
        # Check if a similar entry already exists
        if not SpinStep.objects.filter(**form.cleaned_data).exists():
            spin_step = form.save(commit=False)
            spin_step.author = request.user
            spin_step.save()
            message = 'Spin step saved successfully.'

        else:
            message = 'An identical spin step already exists.'

    # to show the steps field in spin coating form
    form = SpinCoatingForm()
    return render(request, 'partials/spin-step-selection-field.html', {'form': form, 'message': message})


@ login_required(login_url='sign_in')
def spinCoatingView(request):

    if request.method == 'POST':
        form = SpinCoatingForm(request.POST)
        if form.is_valid():
            spin_coating = form.save(commit=False)
            spin_coating.author = request.user
            form.save()

            messages.success(request, 'Spin coating saved successfully.')
            return redirect('spin_coating')

    form = SpinCoatingForm(author=request.user)
    spin_step_form = SpinStepForm()

    context = {'form': form, 'spin_step_form': spin_step_form}

    return render(request, 'spin-coating.html', context)


@ login_required(login_url='sign_in')
def updateSpinCoatingView(request, layer_id):

    layer = get_object_or_404(Layer, pk=layer_id)
    spin_coating = layer.coating_parameters.spin_coating.pk
    spin_coating = SpinCoating.objects.get(pk=spin_coating)
    spin_step_form = SpinStepForm()

    if request.method == 'POST':
        form = SpinCoatingForm(request.POST, instance=spin_coating)
        if form.is_valid():
            form.save(commit=False)

            form.save()

            messages.success(request, 'Spin coating updated successfully.')

    else:
        form = SpinCoatingForm(instance=spin_coating)

    context = {'form': form,
               'spin_step_form': spin_step_form, 'action': 'update'}
    return render(request, 'spin-coating.html', context)


def thermalEvaporationStepView(request):

    form = ThermalEvaporationStepForm(request.POST)

    if form.is_valid():
        step = form.save(commit=False)
        step.author = request.user
        # check if already exists
        if ThermalEvaporationStep.objects.filter(author=request.user, order=step.order, time=step.time, rate=step.rate).exists():
            message = 'Step already exists.'
        else:
            step.save()
            message = 'Step saved successfully.'

    context = {'form': ThermalEvaporationForm(
        author=request.user), 'message': message}

    return render(request, 'partials/thermal-evaporation-step-selection-field.html', context)


def thermalEvaporationView(request):

    if request.method == 'POST':
        form = ThermalEvaporationForm(request.POST)
        if form.is_valid():
            thermal_evaporation = form.save(commit=False)
            thermal_evaporation.author = request.user
            form.save()
            messages.success(
                request, 'Thermal evaporation saved successfully.')
            return redirect('thermal_evaporation')
    else:
        form = ThermalEvaporationForm(author=request.user)

    context = {'form': form,
               'thermal_evaporation_step_form': ThermalEvaporationStepForm()}
    return render(request, 'thermal-evaporation.html', context)


@ login_required(login_url='sign_in')
def updateThermalEvaporationView(request, layer_id):
    layer = get_object_or_404(Layer, pk=layer_id)
    thermal_evaporation = layer.coatingparameters.thermal_evaporation.id
    form = ThermalEvaporationForm(request.POST, instance=thermal_evaporation)
    if request.method == 'POST':
        if form.is_valid():
            form.save(commit=False)
            form.save()
            messages.success(
                request, 'Thermal evaporation updated successfully.')
            return redirect('thermal_evaporation')

    return render(request, 'thermal-evaporation.html', {'form': form, 'action': 'update'})


@ login_required(login_url='sign_in')
def screenPrintingView(request):

    if request.method == 'POST':
        form = ScreenPrintingForm(request.POST)
        if form.is_valid():
            screen_printing = form.save(commit=False)
            screen_printing.author = request.user
            screen_printing.save()
            messages.success(request, 'Screen printing saved successfully.')
            return redirect('screen_printing')
    else:
        form = ScreenPrintingForm()

    context = {'form': form}
    return render(request, 'screen-printing.html', context)


@ login_required(login_url='sign_in')
def infiltrationView(request):

    if request.method == 'POST':
        form = InfiltrationForm(request.POST)
        if form.is_valid():
            infiltrate = form.save(commit=False)
            infiltrate.author = request.user
            infiltrate.save()
            messages.success(request, 'Infiltration saved successfully.')
            return redirect('infiltration')

    context = {'form': InfiltrationForm()}
    return render(request, 'infiltration.html', context)


@ login_required(login_url='sign_in')
def formulationView(request):

    if request.method == 'POST':
        author = request.user
        name = request.POST.get('formulation-name')
        atmosphere = request.POST.get('atmosphere')

        created = request.POST.get('formulation-created')
        notes = request.POST.get('notes')

        formulation = Formulation.objects.create(author=author,
                                                 name=name, atmosphere=atmosphere, notes=notes, created=created)

        inventory_ids = request.POST.getlist('inventory-name[]')
        quantities = request.POST.getlist('quantity[]')
        measurement_units_ids = request.POST.getlist('measurement-unit[]')

        for i in range(len(inventory_ids)):
            FormulationComponent.objects.create(author=author, formulation=formulation, ingredient=Inventory.objects.get(
                id=inventory_ids[i]), quantity=quantities[i], measurement_unit=MeasurementUnit.objects.get(id=measurement_units_ids[i]))

        messages.success(request, 'Formulation added successfully')
        return redirect('formulation')
    else:
        inventory_list = Inventory.objects.filter(
            completed=False, category__name='Chemical')
        measurement_units = MeasurementUnit.objects.all()
        form = FormulationForm()
    context = {'form': form, 'inventory_list': inventory_list,
               'measurement_units': measurement_units}
    return render(request, 'formulation.html', context)


@ login_required(login_url='sign-in')
def updateFormulationView(request, formulation_id):
    formulation = Formulation.objects.get(id=formulation_id)
    formulation_components = FormulationComponent.objects.filter(
        formulation=formulation)
    inventory_list = Inventory.objects.filter(
        completed=False, category__name='Chemical')
    measurement_units = MeasurementUnit.objects.all()

    author = request.user
    name = request.POST.get('formulation-name')
    atmosphere = request.POST.get('atmosphere')
    created = request.POST.get('formulation-created')
    notes = request.POST.get('notes')

    inventory_ids = request.POST.getlist('inventory-name[]')
    quantities = request.POST.getlist('quantity[]')
    measurement_units_ids = request.POST.getlist('measurement-unit[]')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'save-as-new':
            new_formulation = Formulation.objects.create(author=author,
                                                         name=name, atmosphere=atmosphere, notes=notes, created=created)

            for i in range(len(inventory_ids)):
                FormulationComponent.objects.create(author=author, formulation=new_formulation, ingredient=Inventory.objects.get(
                    id=inventory_ids[i]), quantity=quantities[i], measurement_unit=MeasurementUnit.objects.get(id=measurement_units_ids[i]))
            messages.success(request, 'New Formulation has been added')
            return redirect('formulation')
        elif action == 'update':
            formulation.name = name
            formulation.atmosphere = atmosphere
            formulation.notes = notes
            formulation.save()
            if len(formulation_components) == len(inventory_ids):
                for count, ingredient in enumerate(formulation_components):
                    ingredient.inventory = Inventory.objects.get(
                        id=inventory_ids[count])
                    ingredient.quantity = quantities[count]
                    ingredient.measurement_unit = MeasurementUnit.objects.get(
                        id=measurement_units_ids[count])
                    ingredient.save()
            # what if user adds more ingredients to the forumulation
            elif len(formulation_components) < len(inventory_ids):
                # save the existing ingredients
                for count, ingredient in enumerate(formulation_components):
                    ingredient.inventory = Inventory.objects.get(
                        id=inventory_ids[count])
                    ingredient.quantity = quantities[count]
                    ingredient.measurement_unit = MeasurementUnit.objects.get(
                        id=measurement_units_ids[count])
                    ingredient.save()
                # add the new ingredients
                for i in range(len(formulation_components), len(inventory_ids)):
                    FormulationComponent.objects.create(author=author, formulation=formulation, ingredient=Inventory.objects.get(
                        id=inventory_ids[i]), quantity=quantities[i], measurement_unit=MeasurementUnit.objects.get(id=measurement_units_ids[i]))

            # what if user removes ingredients from the formulation

            elif len(formulation_components) > len(inventory_ids):
                for i, ingredient in enumerate(formulation_components):
                    if i < len(inventory_ids):
                        ingredient.inventory = Inventory.objects.get(
                            id=inventory_ids[i])
                        ingredient.quantity = quantities[i]
                        ingredient.measurement_unit = MeasurementUnit.objects.get(
                            id=measurement_units_ids[i])
                        ingredient.save()
                    elif i >= len(inventory_ids):
                        ingredient.delete()

            else:
                messages.error(
                    request, 'Formulation ingredients could not be updated')
        messages.success(request, 'Formulation updated successfully')

        return redirect('formulation')

    context = {'formulation': formulation,
               'formulation_components': formulation_components, 'inventory_list': inventory_list, 'measurement_units': measurement_units,
               'action': 'update'}
    return render(request, 'update-formulation.html', context)


########################### Dashboard Start############################

@ login_required(login_url='sign_in')
def dashboardView(request):

    if request.method == 'POST':
        pass

    users = User.objects.all()
    experiments = Experiment.objects.all()
    my_experiments = Experiment.objects.filter(author=request.user)

    stacks = Stack.objects.all()
    if not stacks:
        # Handle case where there are no stacks
        # For example, you can set default values for X, Y, and user lists
        X = []
        Y = []
        user = []
    else:
        # Initialize lists to store data for plotting
        X = []
        Y = []
        user = []

        # Iterate through Stack objects to collect data
        for stack in stacks:
            Y.append(stack.hero_device_pce)
            created = stack.created.strftime("%Y-%m-%d")
            X.append(created)
            user.append(f"{stack.author.first_name} {stack.author.last_name}")

    if not stacks:
        # Provide default data or message to display
        X = []
        Y = []
        user = []
        pce_chart = "<p>No data available</p>"
    else:
        # Proceed with plotting logic as before
        fig = px.scatter(
            x=X,
            y=Y,
            title="Stacks Hero Device vs Date Created",
            labels=dict(x="Date Created", y="Power Conversion Efficiency (%)"),
            template="simple_white",
        )
        fig.update_traces(
            hovertemplate="<b>Date:</b> %{x}<br><b>PCE:</b> %{y}%<br><b>Author:</b> %{text}",
            text=user,
            marker=dict(
                size=10,
                color='navy',
                symbol='circle',
                line=dict(width=2, color='navy'),
            )
        )
        pce_chart = fig.to_html()

    context = {'users': users, 'experiments': experiments, 'my_experiments': my_experiments,
               'pce_chart': pce_chart, 'stacks': Stack.objects.all()}
    return render(request, 'dashboard.html', context)


def dashboard_data_view(request):
    author = request.GET.get('author')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    stacks = Stack.objects.all()  # Adjust according to your query

    if author and author != 'all':
        stacks = stacks.filter(author__username=author) 
    if date_from:
        stacks = stacks.filter(created__gte=date_from)
    if date_to:
        stacks = stacks.filter(created__lte=date_to)

    stacks_data = [
        {
            'created': stack.created.strftime('%Y-%m-%d'),
            'hero_device_pce': stack.hero_device_pce,
            'author': f"{stack.author.first_name} {stack.author.last_name}",
            'url': reverse('experiment_page', args=[stack.experiment.id])
        }
        for stack in stacks
    ]
    return JsonResponse(stacks_data, safe=False)
def get_stacks(request):

    stacks = Stack.objects.all()
    data = []
    for stack in stacks:
        data.append({'name': stack.name, 'pce': stack.hero_device_pce})
    return JsonResponse(data, safe=False)

########################### Dashboard End############################

########################### Home Start############################


def homeView(request):
    return render(request, 'home.html')


########################### Home End############################
@ login_required(login_url='sign_in')
def fileManager(request, path=''):
    if path == '':
        media_path = settings.MEDIA_ROOT
        # Default breadcrumb for the user root
        navigation_path = [('Media', '')]

    else:
        media_path = os.path.join(settings.MEDIA_ROOT, path)
        parts = path.split('/')

        navigation_path = [('Media', '')]  # Start with the media root
        cumulative_path = ''
        for part in parts:
            cumulative_path = os.path.join(cumulative_path, part)
            navigation_path.append((part, cumulative_path))

    if os.path.exists(media_path):
        directories = os.listdir(media_path)

        # Get a list of dictionaries representing directories and files in the specified media path
        directory_list = [{'name': directory, 'path': os.path.join(media_path, directory)[len(str(
            settings.MEDIA_ROOT)) + 1:]} for directory in directories if os.path.isdir(os.path.join(media_path, directory))]
        files_list = [{'name': file, 'path': os.path.join(media_path, file)} for file in os.listdir(
            media_path) if os.path.isfile(os.path.join(media_path, file))]
    else:
        directory_list = []
        files_list = []
    current_directory = os.path.join(path)

    context = {
        'directory_list': directory_list,
        'files_list': files_list,
        'breadcrumb_data': navigation_path,
        'current_directory': current_directory

    }
    return render(request, 'file-manager.html', context)


@ login_required(login_url='sign_in')
def rename(request):
    if request.method == 'POST':
        selected_items = request.POST.getlist('selected_items_rename')
        selected_item = selected_items[0]

        directory = request.POST.get('current_directory')
        old_name = os.path.join(directory, selected_item)

        new_name = request.POST.get('new_name')
        new_name = os.path.join(directory, new_name)

        if os.path.exists(new_name):
            messages.error(request, 'Folder already exists')
        else:
            os.rename(old_name, new_name)

        messages.success(request, ' Renamed successfully')

    return redirect(request.META.get('HTTP_REFERER'))


@ login_required(login_url='sign_in')
def uploadFiles(request):
    if request.method == 'POST':

        current_directory = request.POST.get('current_directory')

        current_directory = os.path.join(
            settings.MEDIA_ROOT, current_directory)

        # Ensure the directory exists
        os.makedirs(current_directory, exist_ok=True)

        files = request.FILES.getlist('files')  # Get multiple files
        for file in files:
            file_path = os.path.join(current_directory, file.name)
            with open(file_path, 'wb') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

        return redirect(request.META.get('HTTP_REFERER'))

    # If not POST method, or if nothing was uploaded, redirect back
    return redirect(request.META.get('HTTP_REFERER'))


@ login_required(login_url='sign_in')
def newFolder(request):
    if request.method == 'POST':
        current_directory = request.POST.get('current_directory')
        current_directory = os.path.join(
            settings.MEDIA_ROOT, current_directory)
        new_folder_name = request.POST.get('new_folder_name')

        new_folder_path = os.path.join(current_directory, new_folder_name)
        os.makedirs(new_folder_path)

        messages.success(request, 'Folder created successfully')

    return redirect(request.META.get('HTTP_REFERER'))


@ login_required(login_url='sign_in')
def deleteFiles(request):
    if request.method == 'POST':
        selected_items = request.POST.get('selected_items')
        current_directory = request.POST.get('current_directory')

        current_directory = os.path.join(
            settings.MEDIA_ROOT, current_directory)

        if not selected_items:
            messages.error(request, 'No files selected')
            return redirect(request.META.get('HTTP_REFERER'))
        else:

            for item in selected_items.split(','):
                item_path = os.path.join(current_directory, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)

            messages.success(request, 'Files deleted successfully')

    return redirect(request.META.get('HTTP_REFERER'))


def formulationIngredient(request):

    return render(request, 'partials/formulation-ingredient.html')
