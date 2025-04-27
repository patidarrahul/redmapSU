from datetime import timedelta, datetime
import json
from django.apps import apps
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
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncDate
import numpy as np

from redmap.settings import BASE_DIR
from .models import (
    UserProfile,
    Supplier,
    MeasurementUnit,
    Inventory,
    Project,
    Experiment,
    ExperimentStatus,
    Stack,
    SpinStep,
    SpinCoating,
    ThermalEvaporationStep,
    ThermalEvaporation,
    Infiltration,
    ScreenPrinting,
    SlotDieCoating,
    DoctorBladeCoating,
    SprayPyrolysis,
    CoatingParameters,
    DryingProgramStep,
    DryingProgram,
    LayerComposition,
    Layer,
    Formulation,
    FormulationComponent
)

from .forms import (
    UserForm,
    UserProfileForm,
    SignInForm,
    CategoryForm,
    SupplierForm,
    MeasurementUnitForm,
    InventoryForm,
    ProjectForm,
    ExperimentForm,
    StackForm,
    LayerForm,
    LayerCompositionForm,
    DryingProgramStepForm,
    DryingProgramForm,
    SpinStepForm,
    SpinCoatingForm,
    ThermalEvaporationStepForm,
    ThermalEvaporationForm,
    InfiltrationForm,
    ScreenPrintingForm,
    SlotDieCoatingForm,
    DoctorBladeCoatingForm,
    SprayPyrolysisForm,
    CoatingParametersForm,
    FormulationForm
)
import logging
import zipfile
from io import BytesIO
import mimetypes
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


from .utils import *


logger = logging.getLogger(__name__)

# Create your views here.


def signUpView(request):
    """
    Handles user sign-up process.

    Parameters:
    request (HttpRequest): The current HTTP request.

    Returns:
    HttpResponse: A redirect to the dashboard if the user is already authenticated or if the sign-up is successful.
    HttpResponse: A render of the sign-up page with error messages if the sign-up form is invalid or if the username or email already exists.
    """
    # if request.user.is_authenticated:
    #     return redirect('dashboard')

    # if request.method == 'POST':
    #     form = UserForm(request.POST)
    #     if form.is_valid():
    #         user = form.save(commit=False)
    #         if User.objects.filter(Q(username=user.username) | Q(email=user.email)).exists():
    #             messages.error(
    #                 request, 'Username or email already exists. Please choose another.')
    #             return render(request, 'sign-up.html', {'form': form})

    #         user_dir_path = Path(settings.MEDIA_ROOT) / 'users' / user.username
    #         user_dir_path.mkdir(parents=True, exist_ok=True)

    #         user.save()
    #         UserProfile.objects.create(user=user, user_dir=str(user_dir_path))
    #         login(request, user)
    #         messages.success(request, 'User created successfully.')
    #         return redirect('dashboard')

    #     messages.error(request, 'Please correct the errors below.')

    # else:
    #     form = UserForm()

    # return render(request, 'sign-up.html', {'form': form})
    return render(request, 'sign-up.html')


@login_required(login_url='sign_in')
def userProfileView(request):
    """
    Handles user profile view and update process.

    Parameters:
    request (HttpRequest): The current HTTP request.

    Returns:
    HttpResponse: A render of the user profile page with the form.
    """
    user = request.user

    # Retrieve the user's profile; return 404 if not found
    user_profile = get_object_or_404(UserProfile, user=user)

    if request.method == 'POST':
        # Initialize form with POST data and bind it to the user profile
        form = UserProfileForm(
            request.POST, request.FILES, instance=user_profile)

        if form.is_valid():
            form.save()  # Save the updated profile
            messages.success(request, 'User profile updated successfully.')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Initialize the form with the current user profile data
        form = UserProfileForm(instance=user_profile)

    # Render the profile page with the form
    return render(request, 'user-profile.html', {'form': form})


@login_required(login_url='sign_in')
def signOutView(request):
    logout(request)
    messages.success(request, f'You have been logged out.')
    return redirect('sign_in')


def sign_in_view(request):
    """
    Handles user sign-in process.

    Parameters:
    request (HttpRequest): The current HTTP request.

    Returns:
    HttpResponse: A redirect to the dashboard if the user is already authenticated or if the sign-in is successful.
    HttpResponse: A render of the sign-in page with the form.
    """
    # Redirect authenticated users directly to the dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        sign_in_form = SignInForm(request.POST)

        if sign_in_form.is_valid():
            username = sign_in_form.cleaned_data['username']
            password = sign_in_form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('feed')

            sign_in_form.add_error(None, 'Invalid username or password')
    else:
        sign_in_form = SignInForm()

    return render(request, 'sign-in.html', {'form': sign_in_form})


@login_required(login_url='sign_in')
def profile_view(request):
    """
    Handles user profile page rendering.

    Parameters:
    request (HttpRequest): The current HTTP request.

    Returns:
    HttpResponse: A render of the profile page with the user's projects.
    """
    user = request.user
    projects = Project.objects.filter(
        Q(author=user) |
        Q(collaborators=user)
    )

    context = {'projects': projects}
    return render(request, 'profile.html', context)


@login_required(login_url='sign_in')
def profile_page_view(request, user_id):
    """
    Handles user profile page rendering.

    Parameters:
    request (HttpRequest): The current HTTP request.

    Returns:
    HttpResponse: A render of the profile page with the user's projects.
    """
    user = get_object_or_404(User, id=user_id)
    projects = Project.objects.filter(
        Q(author=user) |
        Q(collaborators=user)
    )
    experiments = Experiment.objects.filter(author=user)

    context = {'projects': projects, 'user': user, 'experiments': experiments}
    return render(request, 'profile-page.html', context)


@login_required(login_url='sign_in')
def create_category_view(request):
    """
    Handles GET and POST requests for the category creation page.

    Parameters:
    request (HttpRequest): The current HTTP request.

    Returns:
    HttpResponse: A render of the category creation page or a redirect to the
        inventory page if the category is created successfully.
    """
    category_form = CategoryForm()
    if request.method == 'POST':
        category_form = CategoryForm(request.POST)
        if category_form.is_valid():
            category = category_form.save(commit=False)
            category.author = request.user
            category.save()
            messages.success(request, 'Category created successfully.')
            return redirect(reverse('inventory') + f'?category={category.id}')

    return render(request, 'category.html', {'form': category_form})


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
def inventory_view(request):
    """View function to render the inventory page with the InventoryForm."""

    form = InventoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        inventory = form.save(commit=False)
        inventory.author = request.user
        try:
            inventory.save()
            messages.success(request, 'Inventory added successfully.')
        except Exception as e:
            messages.error(request, f'Failed to add inventory: {str(e)}')
    else:
        form = InventoryForm()

    inventories = Inventory.objects.all()
    if request.GET.get('q'):
        inventories = inventories.filter(
            Q(name__icontains=request.GET['q']) |
            Q(short_name__icontains=request.GET['q']) |
            Q(batch__icontains=request.GET['q'])
        )

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
def deleteExperimentView(request, experiment_id):

    experiment = get_object_or_404(Experiment, pk=experiment_id)

    if request.method == 'POST':
        try:
            # delete the experiment director
            experiment_dir = os.path.join(
                settings.MEDIA_ROOT, experiment.data_dir)
            if os.path.exists(experiment_dir):
                shutil.rmtree(experiment_dir)
            experiment.delete()
            messages.success(request, 'Experiment deleted successfully.')

        except Exception as e:
            messages.error(request, f'Failed to delete experiment: {e}')
        return redirect('project-page', project_id=experiment.project.id)

    return redirect('project-page', project_id=experiment.project.id)


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
        form = ProjectForm(initial={'created': datetime.now()})
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


@login_required(login_url='sign_in')
def experimentPageView(request, experiment_id):
    experiment = get_object_or_404(Experiment, pk=experiment_id)

    update_jv_summary = request.GET.get('update_jv_summary')
    # update the experiment status if missed somewhere
    updateExperimentStatus(experiment)
    try:
        # defined in utils.py
        figures = jvBoxPlot(experiment_id, update_jv_summary)

    except Exception as e:
        messages.error(request, f'Failed to generate charts: {str(e)}')
        return redirect(request.META.get('HTTP_REFERER'))

    jsc_chart = figures['fig_jsc']
    voc_chart = figures['fig_voc']
    ff_chart = figures['fig_ff']
    pce_chart = figures['fig_pce']

    context = {'experiment': experiment, 'jsc_chart': jsc_chart,
               'voc_chart': voc_chart, 'ff_chart': ff_chart, 'pce_chart': pce_chart}
    return render(request, 'experiment-page.html', context)


@login_required(login_url='sign_in')
def jv_curve_view(request):

    # Option B: Using encoded file_path
    encoded_file_path = request.GET.get('file_path')
    if encoded_file_path:
        rel_file_path = urllib.parse.unquote(encoded_file_path)
    else:
        return HttpResponse("No file specified", status=400)
    file_path = os.path.join(settings.MEDIA_ROOT, rel_file_path)

    # Validate and sanitize the file_path
    if not os.path.exists(file_path):
        return HttpResponse("Invalid file path", status=400)

    # Read the data from the file
    try:
        # Open the file with 'latin-1' encoding and load it with np.genfromtxt
        with open(file_path, 'r', encoding='latin-1') as f:
            data = np.genfromtxt(f, skip_header=35, dtype=float,
                                 delimiter='\t')  # loading txt file
            split_file = []

        # Extract the voltage and current points
        forward_voltage_points = data[:, 5] if np.isnan(
            data[0][4]) else data[:, 4]
        forward_current_points = data[:, 6] if np.isnan(
            data[0][4]) else data[:, 5]
        reverse_voltage_points = data[:, 0]
        reverse_current_points = data[:, 1] if np.isnan(
            data[0][2]) else data[:, 2]

    except Exception as e:
        return HttpResponse(f"Error reading file: {e}", status=500)

    try:
        if file_path.endswith('.SEQ'):
            df = dataframe(file_path)
        elif file_path.endswith('.txt'):
            df = dataframe_new(file_path)
        else:
            return HttpResponse("Invalid file type", status=400)
        print(df)
        jsc_rev = df['Jsc Rev'][0]
        jsc_fwd = df['Jsc Fwd'][0]
        voc_rev = df['Voc Rev'][0]
        voc_fwd = df['Voc Fwd'][0]
        ff_rev = df['FF Rev'][0]
        ff_fwd = df['FF Fwd'][0]
        pce_rev = df['PCE Rev'][0]
        pce_fwd = df['PCE Fwd'][0]
        shunt_rev = df['Shunt Resistance Rev'][0]
        shunt_fwd = df['Shunt Resistance Fwd'][0]
        series_rev = df['Series Resistance Rev'][0]
        series_fwd = df['Series Resistance Fwd'][0]

    except Exception as e:
        return HttpResponse(f"Error parsing file: {e}", status=500)

        # Generate the JV curve plot using Plotly
    fig = go.Figure()

    # Plot the forward scan
    fig.add_trace(go.Scatter(x=forward_voltage_points,
                  y=forward_current_points, mode='lines+markers', name='Forward Scan'))

    # Plot the reverse scan
    fig.add_trace(go.Scatter(x=reverse_voltage_points,
                  y=reverse_current_points, mode='lines+markers', name='Reverse Scan'))

    # Update plot layout
    fig.update_layout(
        title={
            'text': 'JV Curve',
            'x': 0.5,  # Center the title
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title='Voltage (V)',
        yaxis_title='Current Density (mA/cm²)',
        template='plotly_white',
        xaxis=dict(
            range=[0, None],  # Set x-axis minimum to 0
            showline=True,  # Show the bottom and top x-axis lines
            linewidth=1,  # Increase line thickness
            linecolor='black',  # Set line color
            mirror=True  # Show axis lines on both bottom and top
        ),
        yaxis=dict(
            range=[0, None],  # Set y-axis minimum to 0
            showline=True,  # Show the left and right y-axis lines
            linewidth=1,  # Increase line thickness
            linecolor='black',  # Set line color
            mirror=True  # Show axis lines on both left and right
        ),
        legend=dict(
            x=0.99,  # Position the legend at the top-right inside the plot
            y=0.98,
            xanchor='right',
            yanchor='top',
            # Slightly transparent background for better readability
            bgcolor='rgba(255, 255, 255, 0.5)',
            bordercolor='Black',
            borderwidth=0.5
        ),
        width=800,  # Set the width of the chart
        height=600  # Set the height of the chart
    )

    # Convert the plot to HTML
    plot_html = fig.to_html(full_html=False)

    # Pass the plot HTML to the template
    return render(request, 'jv-curve.html', {
        'plot_html': plot_html,
        'jsc_rev': jsc_rev, 'voc_rev': voc_rev, 'ff_rev': ff_rev, 'pce_rev': pce_rev, 'series_rev': series_rev, 'shunt_rev': shunt_rev,
        'jsc_fwd': jsc_fwd, 'voc_fwd': voc_fwd, 'ff_fwd': ff_fwd, 'pce_fwd': pce_fwd, 'series_fwd': series_fwd, 'shunt_fwd': shunt_fwd
    })


@login_required(login_url='sign_in')
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
                data_dir_name = experiment.data_dir
                data_dir = os.path.join(
                    settings.MEDIA_ROOT, 'users', request.user.username, data_dir_name)
                if not os.path.exists(data_dir):
                    os.makedirs(data_dir)
                    experiment.data_dir = os.path.join(
                        'users', request.user.username, data_dir_name)
                    experiment.save()
                    experiment_status = ExperimentStatus.objects.create(
                        experiment=experiment)
                    experiment_status.save()
                else:
                    raise Exception(
                        'Experiment directory already exists, chose another name for experiment')

                messages.success(request, 'Experiment saved successfully.')
                # Redirect to profile page after successful addition
                return redirect('project-page', experiment.project.id)
            except Exception as e:
                messages.error(request, str(e))
    else:
        form = ExperimentForm(
            initial={'project': project, 'serial_number': next_experiment_number, 'created': datetime.now()})

    context = {'form': form}
    return render(request, 'experiment.html', context)


@login_required(login_url='sign_in')
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
    old_data_dir = experiment.data_dir

    if request.method == 'POST':
        form = ExperimentForm(request.POST, instance=experiment)
        if form.is_valid():
            updated_experiment = form.save(commit=False)
            project = updated_experiment.project.id
            # checking the change in the data_dir
            updated_data_dir = os.path.join(
                settings.MEDIA_ROOT, 'users', request.user.username, updated_experiment.data_dir)
            if not updated_data_dir == os.path.join(settings.MEDIA_ROOT, old_data_dir):
                if not os.path.exists(updated_data_dir):
                    os.makedirs(updated_data_dir)
                    updated_experiment.data_dir = os.path.join(
                        'users', request.user.username, updated_experiment.data_dir
                    )
                    updated_experiment.save()
                else:
                    messages.error(
                        request, 'Experiment directory already exists, chose another name for experiment'
                    )
                    return render(request, 'experiment.html', {'form': form, 'action': 'update'})
            else:
                updated_experiment.data_dir = old_data_dir
                updated_experiment.save()

            messages.success(request, 'Experiment updated successfully.')
            return redirect('project-page', project)
    else:
        form = ExperimentForm(instance=experiment)

    context = {'form': form, 'action': 'update'}
    return render(request, 'experiment.html', context)


def updateExperimentStatus(instance):
    """
    Updates the status of an experiment based on the given instance.

    Args:
        instance (Experiment): The experiment instance to update.

    Returns:
        None

    This function updates the status of an experiment based on the given instance.
    If the experiment has the same number of stacks as the number of variables, the 'stacks' field of the experiment's ExperimentStatus is set to True and saved.
    If the experiment has the same number of layers in all stacks, the 'layers' field of the experiment's ExperimentStatus is set to True and saved.
    If the experiment has formulation and coating parameters for all layers, the 'formulations' and 'coating_parameters' fields of the experiment's ExperimentStatus are set to True and saved.
    """

    experiment = instance

    # update stack status
    experiment.experimentstatus.stacks = experiment.stack_set.count(
    ) == experiment.number_of_variables
    experiment.experimentstatus.save()

    # update layer status
    experiment.experimentstatus.layers = all(stack.layers.count(
    ) == stack.number_of_layers for stack in experiment.stack_set.all())
    experiment.experimentstatus.save()

    # update coating parameters status
    coating_parameters_status = all(layer.coating_parameters for stack in experiment.stack_set.all(
    ) for layer in stack.layers.all()) if experiment.experimentstatus.layers else False
    experiment.experimentstatus.coating_parameters = coating_parameters_status
    experiment.experimentstatus.save()

    # update formulation status
    formulation_status = all(layer.formulation for stack in experiment.stack_set.all(
    ) for layer in stack.layers.all()) if experiment.experimentstatus.layers else False
    experiment.experimentstatus.formulations = formulation_status
    experiment.experimentstatus.save()

    # update has_jv_files status

    if all(stack.jv_dir for stack in experiment.stack_set.all()):
        all_jv_summary_files = [os.path.join(
            settings.MEDIA_ROOT, stack.jv_dir, 'summary_jv.csv') for stack in experiment.stack_set.all()]
    else:
        raise Exception(
            'address to stack JV Dir not found for experiment {} please check update experiment and update stack'.format(experiment.id))

    for file in all_jv_summary_files:
        if os.path.exists(file):
            df = pd.read_csv(file)
            if df.shape[0] > 0:
                experiment.experimentstatus.has_jv_files = True

            else:
                experiment.experimentstatus.has_jv_files = False
                break

    experiment.experimentstatus.save()


def sendNotificationView(request, experiment_id):
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    if experiment.notified:
        messages.error(
            request, 'You have already shared this experiment with userss.')
        return
    else:
        CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')
        with open(CONFIG_PATH) as config_file:
            config = json.load(config_file)

        sender_email = config["EMAIL_HOST_USER"]
        password = config["EMAIL_HOST_PASSWORD"]
        smtp_server = "smtp.gmail.com"
        port = config["EMAIL_PORT"]

        # get emails of all users
        receiver_emails = list(
            User.objects.all().values_list('email', flat=True))

        # Create server object
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()  # Secure the connection
        server.login(sender_email, password)

        # Send email to each recipient
        for receiver_email in receiver_emails:
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = receiver_email
            message["Subject"] = f"{experiment.author.first_name} {experiment.author.last_name} - A new Experiment has been added on Redmap"

            # Text message with URL
            body = f"Hello,\n\nA new experiment has been added on Redmap. Follow the link to see what amazing work {experiment.author.first_name} {experiment.author.last_name} has done with the experiment details here: https://redmap.xyz/experiment-page/{experiment.id}/  \n\nBest regards,\nReadmap Team\n All HAIL REDMAP!!!!!"
            message.attach(MIMEText(body, "plain"))

            try:
                text = message.as_string()
                server.sendmail(sender_email, receiver_email, text)
                experiment.notified = True
                experiment.save()
            except Exception as e:
                messages.error(
                    request, f'Failed to send email to {receiver_email}. Error: {str(e)}')
        server.quit()
    return redirect('experiment_page', experiment_id)


@login_required(login_url='sign_in')
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
        form = StackForm(
            initial={'experiment': experiment, 'created': datetime.now()})
    else:
        form = StackForm(initial={'created': datetime.now()})

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


@login_required(login_url='sign_in')
def updateStackView(request, stack_id):
    old_stack = get_object_or_404(Stack, pk=stack_id)
    old_stack_name = old_stack.name

    if request.method == 'POST':
        form = StackForm(request.POST, instance=old_stack)
        if form.is_valid():
            if request.POST.get('save_as_new'):
                # Create a new instance with the updated data
                new_stack = form.save(commit=False)
                new_stack.pk = None  # Clear the primary key to create a new instance
                # Ensure the name is taken from the form
                new_stack.name = form.cleaned_data['name']

                experiment_dir = new_stack.experiment.data_dir
                stack_jv_dir = os.path.join(
                    settings.MEDIA_ROOT, experiment_dir, 'JV', new_stack.name)

                try:
                    if not os.path.exists(stack_jv_dir):
                        os.makedirs(stack_jv_dir)
                    else:
                        raise Exception(
                            'Stack directory already exists, choose another name for the stack')

                    new_stack.jv_dir = os.path.join(
                        experiment_dir, 'JV', new_stack.name)
                    new_stack.save()

                except Exception as e:
                    messages.error(request, str(e))
                    return redirect('stack')

                # Update experiment status
                updateExperimentStatus(new_stack.experiment)

                messages.success(
                    request, 'Stack saved as a new instance successfully.')
                project_id = new_stack.experiment.project.pk
                return redirect('project-page', project_id=project_id)
            else:
                # Update the old stack instance with the updated data
                new_stack = form.save(commit=False)

                try:
                    if old_stack_name != new_stack.name:
                        # Rename the old stack directory
                        old_stack_jv_dir = os.path.join(
                            settings.MEDIA_ROOT, old_stack.experiment.data_dir, 'JV',
                            old_stack_name)
                        new_stack_jv_dir = os.path.join(
                            settings.MEDIA_ROOT, new_stack.experiment.data_dir, 'JV', new_stack.name)

                        if os.path.exists(old_stack_jv_dir):
                            os.rename(old_stack_jv_dir, new_stack_jv_dir)
                            new_stack.jv_dir = os.path.join(
                                new_stack.experiment.data_dir, 'JV', new_stack.name
                            )
                        elif not os.path.exists(old_stack_jv_dir):
                            os.makedirs(new_stack_jv_dir)
                            new_stack.jv_dir = os.path.join(
                                new_stack.experiment.data_dir, 'JV', new_stack.name
                            )
                        else:
                            raise Exception(
                                'Stack directory already exists, choose another name for the stack')

                    new_stack.author = request.user
                    new_stack.save()

                except Exception as e:
                    messages.error(request, str(e))
                    return redirect('stack')

                # Update experiment status
                updateExperimentStatus(new_stack.experiment)

                messages.success(request, 'Stack updated successfully.')
                project_id = new_stack.experiment.project.pk
                return redirect('project-page', project_id=project_id)
    else:
        form = StackForm(instance=old_stack)

    context = {'form': form, 'action': 'update'}
    return render(request, 'stack.html', context)


@login_required(login_url='sign_in')
def delete_stack_view(request, stack_id):
    """
    View function to handle the deletion of a Stack object.

    Parameters:
        request (HttpRequest): The HTTP request object.
        stack_id (int): The ID of the Stack object to be deleted.

    Returns:
        HttpResponse: The HTTP response object. Redirects the user to the project page after deleting the Stack object.
    """

    # Get the Stack object with the given ID
    stack = get_object_or_404(Stack, pk=stack_id)

    # Get the ID of the project associated with the Stack object
    project_id = stack.experiment.project.pk

    try:
        # Delete the folder of the stack
        stack_jv_dir = os.path.join(
            settings.MEDIA_ROOT, stack.experiment.data_dir, 'JV', stack.name)
        if os.path.exists(stack_jv_dir):
            shutil.rmtree(stack_jv_dir)

        # Delete the Stack object
        stack.delete()

        # Display a success message to the user
        messages.success(request, 'Stack deleted successfully.')

    except Exception as e:
        messages.error(request, str(e))

    # Redirect the user to the project page
    return redirect('project-page', project_id=project_id)


@login_required(login_url='sign_in')
def duplicateStackView(request, stack_id):
    stack = get_object_or_404(Stack, pk=stack_id)
    # duplicate stack with new name and add all the layers associated with the stack to the new stack
    experiment = stack.experiment
    all_stacks_count = Stack.objects.filter(experiment=experiment).count()

    new_stack_name = stack.name + ' ' + str(all_stacks_count + 1)

    new_stack_jv_dir = os.path.join(
        settings.MEDIA_ROOT, stack.experiment.data_dir, 'JV', new_stack_name)

    new_stack = Stack.objects.create(
        name=new_stack_name, experiment=experiment, substrate=stack.substrate, geometry=stack.geometry,
        number_of_layers=stack.number_of_layers, number_of_devices=stack.number_of_devices, created=stack.created,
        author=request.user


    )

    if not os.path.exists(new_stack_jv_dir):
        os.makedirs(new_stack_jv_dir)

        new_stack.jv_dir = os.path.join(
            stack.experiment.data_dir, 'JV', new_stack_name)  # save relative path

    else:
        raise Exception(
            'Stack directory already exists, choose another name for the stack')

    for layer in stack.layers.all():
        new_stack.layers.add(layer)
    new_stack.save()
    return redirect('project-page', project_id=experiment.project.pk)


@login_required(login_url='sign_in')
def removeLayerFromStackView(request):
    stack_id = request.GET.get('stack')
    layer_id = request.GET.get('layer')
    layer = get_object_or_404(Layer, pk=layer_id)
    stack = get_object_or_404(Stack, pk=stack_id)
    stack.layers.remove(layer)
    experiment = stack.experiment
    messages.success(request, 'Layer removed successfully.')
    return redirect('project-page', project_id=experiment.project.pk)


@login_required(login_url='sign_in')
def layerTypeView(request):
    layer_type = request.POST.get('layer_type')
    stack_id = request.POST.get('stack_id')
    if stack_id != 'None':
        form_initial = {'stacks': [get_object_or_404(
            Stack, pk=stack_id)]} if stack_id else {}
        form_initial['created'] = datetime.now()
    else:
        form_initial = {'created': datetime.now()}

    if layer_type == 'Surface Treatment':
        return render(request, 'partials/surface-treatment.html', {'form': LayerForm(initial=form_initial, author=request.user)})
    elif layer_type == 'Coating Layer':
        return render(request, 'partials/coating-layer.html',
                      {'form': LayerForm(initial=form_initial, author=request.user), 'coating_parameters_form': CoatingParametersForm()})


# defining global coating methods

coating_method_choices = Layer.coating_method_choices
coating_methods = {
    key: (key.lower().replace(' ', '_'),
          apps.get_model('app', key.replace(' ', '')))
    for key, _ in coating_method_choices
}


@login_required(login_url='sign_in')
def layerView(request):
    stack_id = request.GET.get('stack')
    if stack_id:
        form_initial = {'stacks': [get_object_or_404(
            Stack, pk=stack_id)]} if stack_id else {}
        form_initial['created'] = datetime.now()
    else:
        form_initial = {'created': datetime.now()}

    form = LayerForm(request.POST or None,
                     initial=form_initial, author=request.user)

    coating_parameters_form = CoatingParametersForm()

    if request.method == 'POST' and form.is_valid():
        layer = form.save(commit=False)
        layer.author = request.user

        if layer.layer_type == 'Surface Treatment':
            layer.coating_parameters = None
            layer.save()
            layer.stacks.set(form.cleaned_data['stacks'])
            return redirect_to_project_page(layer.stacks.first(), request)

        elif layer.coating_method in coating_methods:
            param_name, model = coating_methods[layer.coating_method]
            instance = request.POST.get(param_name)
            obj = model.objects.get(pk=instance)
            coating_parameters, created = CoatingParameters.objects.get_or_create(
                author=request.user, **{param_name: obj}
            )
            layer.coating_parameters = coating_parameters
            layer.save()
            layer.stacks.set(form.cleaned_data['stacks'])
            updateExperimentStatus(layer.stacks.first().experiment)
            return redirect_to_project_page(layer.stacks.first(), request)

        else:
            messages.error(
                request, 'Selected coating method is not supported.')
            return redirect('layer')

    return render(request, 'layer.html', {
        'form': form,
        'coating_parameters_form': coating_parameters_form,
        'stack_id': stack_id
    })


def redirect_to_project_page(stack, request):
    experiment = Experiment.objects.get(pk=stack.experiment.pk)
    project_id = experiment.project.pk
    return redirect('project-page', project_id)


@login_required(login_url='sign_in')
def updateLayerTypeView(request, layer_id):
    layer = get_object_or_404(Layer, pk=layer_id)
    layer_type = request.POST.get('layer_type')
    if layer_type == 'Surface Treatment':
        return render(request, 'partials/surface-treatment.html', {'form': LayerForm(author=request.user, instance=layer)})
    elif layer_type == 'Coating Layer':
        coating_parameters = layer.coating_parameters.id
        coating_parameters = CoatingParameters.objects.get(
            pk=coating_parameters)

        return render(request, 'partials/coating-layer.html',
                      {'form': LayerForm(author=request.user, instance=layer), 'coating_parameters_form': CoatingParametersForm(instance=coating_parameters)})


@login_required(login_url='sign_in')
def updateLayerView(request, layer_id):
    layer = get_object_or_404(Layer, pk=layer_id)

    if request.method == 'POST':
        form = LayerForm(request.POST, instance=layer)

        if form.is_valid():
            new_layer = form.save(commit=False)

            if request.POST.get('save_as_new'):
                new_layer.pk = None  # Clear the primary key to create a new instance

            if new_layer.layer_type == 'Surface Treatment':
                new_layer.coating_parameters = None

            elif new_layer.coating_method:

                if new_layer.coating_method in coating_methods:
                    param_name, model = coating_methods[new_layer.coating_method]
                    instance = request.POST.get(param_name)
                    obj = model.objects.get(pk=instance)
                    coating_parameters, created = CoatingParameters.objects.get_or_create(
                        author=request.user, **{param_name: obj}
                    )
                    new_layer.coating_parameters = coating_parameters
                else:
                    messages.error(
                        request, 'Selected coating method is not supported.')
                    return redirect('layer')

            new_layer.save()
            new_layer.stacks.set(form.cleaned_data['stacks'])
            updateExperimentStatus(new_layer.stacks.first().experiment)
            messages.success(
                request,
                'Layer saved as a new instance successfully.' if request.POST.get(
                    'save_as_new') else 'Layer updated successfully.'
            )
            return redirect_to_project_page(new_layer.stacks.first(), request)

    else:
        form = LayerForm(instance=layer, author=request.user)

    context = {
        'form': form,
        'coating_parameters_form': CoatingParametersForm(instance=layer.coating_parameters),
        'layer_id': layer_id,
        'action': 'update',
    }
    return render(request, 'update-layer.html', context)


@login_required(login_url='sign_in')
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


@login_required(login_url='sign_in')
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


@login_required(login_url='sign_in')
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


@login_required(login_url='sign_in')
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


@login_required(login_url='sign_in')
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


@login_required(login_url='sign_in')
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


@login_required(login_url='sign_in')
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


@login_required(login_url='sign_in')
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


@login_required(login_url='sign_in')
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


@login_required(login_url='sign_in')
def slotDieCoatingView(request):

    if request.method == 'POST':
        form = SlotDieCoatingForm(request.POST)
        if form.is_valid():
            settings = form.save(commit=False)
            settings.author = request.user
            form.save()
            messages.success(request, 'Slot die coating saved successfully.')
            return redirect('slot_die_coating')

    context = {'form': SlotDieCoatingForm()}
    return render(request, 'slot-die-coating.html', context)


@login_required(login_url='sign_in')
def doctorBladeCoatingView(request):

    if request.method == 'POST':
        form = DoctorBladeCoatingForm(request.POST)
        if form.is_valid():
            settings = form.save(commit=False)
            settings.author = request.user
            form.save()
            messages.success(
                request, 'Doctor blade coating saved successfully.')
            return redirect('doctor_blade_coating')

    context = {'form': DoctorBladeCoatingForm()}
    return render(request, 'doctor-blade-coating.html', context)


@login_required(login_url='sign_in')
def sprayPyrolysisView(request):

    if request.method == 'POST':

        form = SprayPyrolysisForm(request.POST)
        if form.is_valid():
            settings = form.save(commit=False)
            settings.author = request.user
            form.save()
            messages.success(request, 'Spray pyrolysis saved successfully.')
            return redirect('spray_pyrolysis')

    context = {'form': SprayPyrolysisForm()}
    return render(request, 'spray-pyrolysis.html', context)


@login_required(login_url='sign_in')
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
        form = FormulationForm(initial={'created': datetime.now()})
    context = {'form': form, 'inventory_list': inventory_list,
               'measurement_units': measurement_units}
    return render(request, 'formulation.html', context)


@login_required(login_url='sign-in')
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

@login_required(login_url='sign_in')
def dashboardView(request):

    if request.method == 'POST':
        pass

    users = User.objects.all()
    projects = Project.objects.all()
    experiments = Experiment.objects.all()
    my_experiments = Experiment.objects.filter(author=request.user)

    # experiment added in last 24 hours last week and last month
    # last_24_hours = datetime.now() - timedelta(hours=24)
    # last_week = datetime.now() - timedelta(days=7)
    # last_month = datetime.now() - timedelta(days=30)
    # experiment_24_hours = Experiment.objects.filter(
    #     created__gte=last_24_hours)
    # experiment_week = Experiment.objects.filter(created__gte=last_week)
    # experiment_month = Experiment.objects.filter(created__gte=last_month)

    context = {'users': users, 'experiments': experiments,
               'my_experiments': my_experiments,
               'projects': projects
               #    'experiment_24_hours': experiment_24_hours,
               #    'experiment_week': experiment_week,
               #    'experiment_month': experiment_month
               }
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

    stacks_data = []

    for stack in stacks:
        if stack.hero_device_pce is not None:  # Filter out stacks without PCE data
            stacks_data.append({
                'created': stack.created.strftime('%Y-%m-%d'),
                'hero_device_pce': stack.hero_device_pce,
                'author': f"{stack.author.first_name} {stack.author.last_name}",
                'url': reverse('experiment_page', args=[stack.experiment.id]),
                'color': stack.author.userprofile.color or '#000000'
            })

    return JsonResponse(stacks_data, safe=False)


def get_experiments_by_user(request):

    total_users = User.objects.all()
    experiments_by_user = []

    for user in total_users:
        name = user.first_name + ' ' + user.last_name
        experiments = Experiment.objects.filter(author=user).count()
        experiments_by_user.append({'user': name, 'experiments': experiments})

    return JsonResponse(experiments_by_user, safe=False)


def get_total_experiments(request):
    data = (Experiment.objects
            # Extracts the date from a DateTimeField
            .annotate(date=TruncDate('created'))
            # Groups by the newly created 'date' field
            .values('date')
            .annotate(experiments=Count('id'))    # Counts experiments per day
            .order_by('date'))                    # Orders the results by date
    response = list(data)
    return JsonResponse(response, safe=False)


def get_stacks(request):

    stacks = Stack.objects.all()
    data = []
    for stack in stacks:
        data.append({'name': stack.name, 'pce': stack.hero_device_pce})
    return JsonResponse(data, safe=False)

########################### Dashboard End############################

########################### Home Start############################


def feedView(request):

    experiments = Experiment.objects.all().order_by('-created')

    # FILTER via query
    if request.GET.get('q'):
        experiments = experiments.filter(
            Q(objective__icontains=request.GET.get('q')) |
            Q(notes__icontains=request.GET.get('q')) |
            Q(author__first_name__icontains=request.GET.get('q')) |
            Q(author__last_name__icontains=request.GET.get('q'))
        )

    context = {'experiments': experiments}

    return render(request, 'feed.html', context)


def fetch_comment(request, experiment_id):
    experiment = Experiment.objects.get(id=experiment_id)
    comments = Comment.objects.filter(
        Experiment=experiment).order_by('-created')

    return render(request, 'partials/comment_box.html', {'experiment': experiment, 'comments': comments})


def add_comment(request, experiment_id):
    experiment = Experiment.objects.get(id=experiment_id)
    comments = Comment.objects.filter(
        Experiment=experiment).order_by('-created')
    if request.method == 'POST':
        comment = request.POST.get('comment')
        if comment == '':
            return render(request, 'partials/comments_list.html', {'experiment': experiment, 'comments': comments})

        new_comment = Comment.objects.create(
            Experiment=experiment,
            author=request.user,
            comment=comment
        )
        new_comment.save()

        # notify the author
        CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')
        with open(CONFIG_PATH) as config_file:
            config = json.load(config_file)

        sender_email = config["EMAIL_HOST_USER"]
        password = config["EMAIL_HOST_PASSWORD"]
        smtp_server = "smtp.gmail.com"
        port = config["EMAIL_PORT"]

        # get emails of all users
        # people who have commnented on this experiment before
        receiver_emails = list(
            set(comment.author.email for comment in comments))

        # remove the author of the experiment if it is in the list
        if experiment.author.email in receiver_emails:
            receiver_emails.remove(experiment.author.email)

        # remove the author of the comment
        if new_comment.author.email in receiver_emails:
            receiver_emails.remove(new_comment.author.email)

        # Create server object
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()  # Secure the connection
        server.login(sender_email, password)

        # Send email to each recipient
        if receiver_emails:
            for receiver_email in receiver_emails:
                message = MIMEMultipart()
                message["From"] = sender_email
                message["To"] = receiver_email
                message["Subject"] = f"{new_comment.author.first_name} {new_comment.author.last_name} - Added a Comment on experiment {experiment.objective}"

                # Text message with URL
                body = f"Hello,\n\n {new_comment.author.first_name} {new_comment.author.last_name} also commented on experiment {experiment.objective}. You can view the comment here: https://redmap.xyz/experiment-page/{experiment.id}/  \n\nBest regards,\nReadmap Team\n All HAIL REDMAP!!!!!"
                message.attach(MIMEText(body, "plain"))

                try:
                    text = message.as_string()
                    server.sendmail(sender_email, receiver_email, text)
                except Exception as e:
                    messages.error(
                        request, f'Failed to send email to {receiver_email}. Error: {str(e)}')

        # also send an email to the author of the experiment that there is a new comment on their experiment
        if experiment.author.email != new_comment.author.email:
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = experiment.author.email
            message["Subject"] = f"{new_comment.author.first_name} {new_comment.author.last_name} - Added a Comment on experiment {experiment.objective}"

            # Text message with URL
            body = f"Hello, \n\n There is a new comment on your experiment {experiment.objective}. You can view the comment here: https://redmap.xyz/experiment-page/{experiment.id}/  \n\nBest regards,\nReadmap Team\n All HAIL REDMAP!!!!!"
            message.attach(MIMEText(body, "plain"))

            try:
                text = message.as_string()
                server.sendmail(sender_email, experiment.author.email, text)
            except Exception as e:
                messages.error(
                    request, f'Failed to send email to {receiver_email}. Error: {str(e)}')

        server.quit()

    return render(request, 'partials/comments_list.html', {'experiment': experiment, 'comments': comments})
########################### Home End############################


@login_required(login_url='sign_in')
def fileManager(request, path=''):
    if path == '':
        return redirect('file_manager', path='users/' + request.user.username)

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


@login_required(login_url='sign_in')
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


@login_required(login_url='sign_in')
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


@login_required(login_url='sign_in')
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


@login_required(login_url='sign_in')
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


@login_required(login_url='sign_in')
def downloadFiles(request):
    if request.method == 'POST':
        selected_items = request.POST.get('selected_items')
        current_directory = request.POST.get('current_directory')
        current_directory = os.path.join(
            settings.MEDIA_ROOT, current_directory)

        if not selected_items:
            messages.error(
                request, 'No files or folders selected for download')
            return redirect(request.META.get('HTTP_REFERER'))

        selected_items_list = selected_items.split(',')

        if len(selected_items_list) == 1:
            item_path = os.path.join(current_directory, selected_items_list[0])
            if os.path.exists(item_path):
                if os.path.isdir(item_path):
                    # If it's a directory, create a ZIP file
                    zip_buffer = BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                        for root, dirs, files in os.walk(item_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(
                                    file_path, current_directory)
                                zip_file.write(file_path, arcname)
                    zip_buffer.seek(0)
                    response = HttpResponse(
                        zip_buffer, content_type='application/zip')
                    response[
                        'Content-Disposition'] = f'attachment; filename={os.path.basename(item_path)}.zip'
                else:
                    # If it's a file, download it directly
                    with open(item_path, 'rb') as file:
                        response = HttpResponse(
                            file.read(), content_type=mimetypes.guess_type(item_path)[0])
                        response[
                            'Content-Disposition'] = f'attachment; filename={os.path.basename(item_path)}'
                return response
            else:
                messages.error(request, 'File or folder not found')
                return redirect(request.META.get('HTTP_REFERER'))

        else:
            # If multiple files or directories are selected, create a ZIP file
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for item in selected_items_list:
                    item_path = os.path.join(current_directory, item)
                    if os.path.exists(item_path):
                        if os.path.isdir(item_path):
                            for root, dirs, files in os.walk(item_path):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    arcname = os.path.relpath(
                                        file_path, current_directory)
                                    zip_file.write(file_path, arcname)
                        else:
                            zip_file.write(item_path, os.path.relpath(
                                item_path, current_directory))
                    else:
                        messages.error(
                            request, f'File or folder {item} not found')
                        return redirect(request.META.get('HTTP_REFERER'))

            zip_buffer.seek(0)
            response = HttpResponse(zip_buffer, content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename=selected_items.zip'
            return response

    return redirect(request.META.get('HTTP_REFERER'))


@login_required(login_url='sign_in')
def viewFile(request, file_path):

    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(
                file.read(), content_type=mimetypes.guess_type(file_path)[0])
            response['Content-Disposition'] = 'inline; filename=' + \
                os.path.basename(file_path)
            return response
    else:
        raise Http404("File does not exist")


def formulationIngredient(request):

    return render(request, 'partials/formulation-ingredient.html')
