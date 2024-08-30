import glob
import os
import pandas as pd
import chardet
import plotly.graph_objects as go
from .models import *
from django.conf import settings
import re


def dataframe(dir):
    files = glob.glob(f'{dir}/*.SEQ')
    file_location = []
    cell_id = []
    pce_rev = []
    pce_fwd = []
    jsc_rev = []
    jsc_fwd = []
    voc_rev = []
    voc_fwd = []
    ff_rev = []
    ff_fwd = []
    series_rev = []
    series_fwd = []
    shunt_rev = []
    shunt_fwd = []

    for file in files:
        try:
            # Detect file encoding dynamically
            with open(file, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding']

            # Read file using detected encoding
            with open(file, 'r', encoding=encoding) as f:
                split_file = []
                for line in f:
                    line = line.split('\t')
                    split_file.append(line)

                if split_file[28][3] == 'Light':  # Filtering the light current
                    file_location.append(file)
                    cell_id.append(split_file[23][1])
                    jsc_rev.append(float(split_file[28][7]))
                    jsc_fwd.append(float(split_file[29][7]))
                    voc_rev.append(float(split_file[28][5]))
                    voc_fwd.append(float(split_file[29][5]))
                    ff_rev.append(float(split_file[28][8]))
                    ff_fwd.append(float(split_file[29][8]))
                    pce_rev.append(float(split_file[28][9]))
                    pce_fwd.append(float(split_file[29][9]))
                    series_rev.append(split_file[28][15])
                    series_fwd.append(split_file[29][15])
                    shunt_rev.append(abs(float(split_file[28][14])))
                    shunt_fwd.append(abs(float(split_file[29][14])))

                elif split_file[29][3] == 'Light':
                    file_location.append(file)
                    # increase the row number by 1
                    cell_id.append(split_file[23][1])
                    jsc_rev.append(float(split_file[29][7]))
                    jsc_fwd.append(float(split_file[30][7]))
                    voc_rev.append(float(split_file[29][5]))
                    voc_fwd.append(float(split_file[30][5]))
                    ff_rev.append(float(split_file[29][8]))
                    ff_fwd.append(float(split_file[30][8]))
                    pce_rev.append(float(split_file[29][9]))
                    pce_fwd.append(float(split_file[30][9]))
                    series_rev.append(split_file[29][15])
                    series_fwd.append(split_file[30][15])
                    shunt_rev.append(abs(float(split_file[29][14])))
                    shunt_fwd.append(abs(float(split_file[30][14])))

        except Exception as e:
            print(e)
            # Handle other exceptions

    df = pd.DataFrame({
        'File Location': file_location,
        'Cell ID': cell_id,
        'Jsc Rev': jsc_rev,
        'Jsc Fwd': jsc_fwd,
        'Voc Rev': voc_rev,
        'Voc Fwd': voc_fwd,
        'FF Rev': ff_rev,
        'FF Fwd': ff_fwd,
        'PCE Rev': pce_rev,
        'PCE Fwd': pce_fwd,
        'Series Resistance Rev': series_rev,
        'Series Resistance Fwd': series_fwd,
        'Shunt Resistance Rev': shunt_rev,
        'Shunt Resistance Fwd': shunt_fwd
    })

    return df


def dataframe_new(dir):
    file_location = []
    cell_id = []
    pce_rev = []
    pce_fwd = []
    jsc_rev = []
    jsc_fwd = []
    voc_rev = []
    voc_fwd = []
    ff_rev = []
    ff_fwd = []
    series_rev = []
    series_fwd = []
    shunt_rev = []
    shunt_fwd = []

    patterns = {
        'Dark Measurement': r'Dark Measurement:\s*(\w+)',
        'Scan Direction': r'Scan Direction:\s*(\w+)',
        'Device Name': r'Device Name:\s*(\w+)',
        'Pixel': r'Pixel:\s*(\d+)',
        'Reverse Scan Jsc (mA/cm²)': r'Reverse Scan Jsc \(mA/cm\u00B2\):\s*([\d.]+)',
        'Reverse Scan Voc (V)': r'Reverse Scan Voc \(V\):\s*([\d.]+)',
        'Reverse Scan FF': r'Reverse Scan FF:\s*([\d.]+)',
        'Reverse Scan PCE (%)': r'Reverse Scan PCE \(%\):\s*([\d.]+)',
        'Reverse Scan Series Resistance (Ohms)': r'Reverse Scan Series Resistance \(Ohms\):\s*([\d.]+)',
        'Reverse Scan Shunt Resistance (Ohms)': r'Reverse Scan Shunt Resistance \(Ohms\):\s*([\d.]+)',
        'Forward Scan Jsc (mA/cm²)': r'Forward Scan Jsc \(mA/cm\u00B2\):\s*([\d.]+)',
        'Forward Scan Voc (V)': r'Forward Scan Voc \(V\):\s*([\d.]+)',
        'Forward Scan FF': r'Forward Scan FF:\s*([\d.]+)',
        'Forward Scan PCE (%)': r'Forward Scan PCE \(%\):\s*([\d.]+)',
        'Forward Scan Series Resistance (Ohms)': r'Forward Scan Series Resistance \(Ohms\):\s*([\d.]+)',
        'Forward Scan Shunt Resistance (Ohms)': r'Forward Scan Shunt Resistance \(Ohms\):\s*([\d.]+)'
    }

    for filename in os.listdir(dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(dir, filename)
            with open(filepath, 'rb') as file:
                raw_data = file.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                content = raw_data.decode(encoding)

                if (re.search(patterns['Dark Measurement'], content) and
                    re.search(patterns['Dark Measurement'], content).group(1) == 'False' and
                    re.search(patterns['Scan Direction'], content) and
                        re.search(patterns['Scan Direction'], content).group(1) == 'Both'):

                    file_location.append(filepath)
                    cell_id.append(re.search(patterns['Device Name'], content).group(1) + ' ' +
                                   re.search(patterns['Pixel'], content).group(1))

                    # Append values to the respective lists
                    jsc_rev.append(
                        re.search(patterns['Reverse Scan Jsc (mA/cm²)'], content).group(1))

                    voc_rev.append(
                        re.search(patterns['Reverse Scan Voc (V)'], content).group(1))

                    ff_rev.append(
                        re.search(patterns['Reverse Scan FF'], content).group(1))
                    pce_rev.append(
                        re.search(patterns['Reverse Scan PCE (%)'], content).group(1))
                    series_rev.append(
                        re.search(patterns['Reverse Scan Series Resistance (Ohms)'], content).group(1))
                    shunt_rev.append(
                        re.search(patterns['Reverse Scan Shunt Resistance (Ohms)'], content).group(1))
                    jsc_fwd.append(
                        re.search(patterns['Forward Scan Jsc (mA/cm²)'], content).group(1))
                    voc_fwd.append(
                        re.search(patterns['Forward Scan Voc (V)'], content).group(1))
                    ff_fwd.append(
                        re.search(patterns['Forward Scan FF'], content).group(1))
                    pce_fwd.append(
                        re.search(patterns['Forward Scan PCE (%)'], content).group(1))
                    series_fwd.append(
                        re.search(patterns['Forward Scan Series Resistance (Ohms)'], content).group(1))
                    shunt_fwd.append(
                        re.search(patterns['Forward Scan Shunt Resistance (Ohms)'], content).group(1))

    df = pd.DataFrame({
        'File Location': file_location,
        'Cell ID': cell_id,
        'Jsc Rev': jsc_rev,
        'Jsc Fwd': jsc_fwd,
        'Voc Rev': voc_rev,
        'Voc Fwd': voc_fwd,
        'FF Rev': ff_rev,
        'FF Fwd': ff_fwd,
        'PCE Rev': pce_rev,
        'PCE Fwd': pce_fwd,
        'Series Resistance Rev': series_rev,
        'Series Resistance Fwd': series_fwd,
        'Shunt Resistance Rev': shunt_rev,
        'Shunt Resistance Fwd': shunt_fwd
    })

    return df


def jvBoxPlot(experiment_id):
    stacks = Stack.objects.filter(experiment_id=experiment_id)
    jv_software = ''
    # check which jv_software to use

    if all([stack.jv_software == 'new' for stack in stacks]):
        jv_software = 'new'

    elif all([stack.jv_software == 'default' for stack in stacks]):
        jv_software = 'default'

    else:
        raise ValueError('All stacks must have the same jv_software')
    all_jv_dirs = [(stack.name, os.path.join(
        settings.MEDIA_ROOT, stack.jv_dir)) for stack in stacks]

    df_list = []
    # Check if all 'summary_jv.csv' files exist
    if all([os.path.exists(os.path.join(jv_dir, 'summary_jv.csv')) for _, jv_dir in all_jv_dirs]):
        for stack_name, jv_dir in all_jv_dirs:
            df = pd.read_csv(os.path.join(jv_dir, 'summary_jv.csv'))
            df_list.append((stack_name, df))

    else:

        for stack_name, jv_dir in all_jv_dirs:
            if jv_software == 'default':
                df = dataframe(jv_dir)
                df_list.append((stack_name, df))
                df.to_csv(os.path.join(jv_dir, 'summary_jv.csv'), index=False)
            elif jv_software == 'new':
                df = dataframe_new(jv_dir)
                df_list.append((stack_name, df))
                df.to_csv(os.path.join(jv_dir, 'summary_jv.csv'), index=False)

        # find hero PCE
        heroJV(experiment_id)

    fig_jv = go.Figure()
    fig_voc = go.Figure()
    fig_ff = go.Figure()
    fig_pce = go.Figure()
    for stack_name, df in df_list:
        fig_jv.add_trace(go.Box(y=df.iloc[:, 2], boxpoints='all',  # can also be outliers, or suspectedoutliers, or False
                                jitter=0.3,  # add some jitter for a better separation between points
                                pointpos=-1.8,
                                showlegend=False,  # remove legend
                                name=stack_name

                                ))  # relative position of points wrt box))

    for stack_name, df in df_list:
        fig_voc.add_trace(go.Box(y=df.iloc[:, 4], boxpoints='all',  # can also be outliers, or suspectedoutliers, or False
                                 jitter=0.3,  # add some jitter for a better separation between points
                                 pointpos=-1.8,
                                 showlegend=False,  # remove legend
                                 name=stack_name

                                 ))  # relative position of points wrt box))
    for stack_name, df in df_list:
        fig_ff.add_trace(go.Box(y=df.iloc[:, 6], boxpoints='all',  # can also be outliers, or suspectedoutliers, or False
                                jitter=0.3,  # add some jitter for a better separation between points
                                pointpos=-1.8,
                                showlegend=False,  # remove legend
                                name=stack_name
                                ))  # relative position of points wrt box))

    for stack_name, df in df_list:
        fig_pce.add_trace(go.Box(y=df.iloc[:, 8], boxpoints='all',  # can also be outliers, or suspectedoutliers, or False
                                 jitter=0.3,  # add some jitter for a better separation between points
                                 pointpos=-1.8,
                                 showlegend=False,  # remove legend
                                 name=stack_name
                                 ))  # relative position of points wrt box))

    fig_jv.update_layout(
        yaxis_title='Current Density (mA/cm<sup>2</sup>)', width=600)
    fig_voc.update_layout(
        yaxis_title='Open Circuit Voltage (Volts)', width=600)
    fig_ff.update_layout(yaxis_title='Fill Factor (%)', width=600)
    fig_pce.update_layout(
        yaxis_title='Power Conversion Efficiency (%)', width=600)

    # add
    figures = {
        'fig_jv': fig_jv.to_html(),
        'fig_voc': fig_voc.to_html(),
        'fig_ff': fig_ff.to_html(),
        'fig_pce': fig_pce.to_html(),

    }
    return figures


def heroJV(experiment_id):
    stacks = Stack.objects.filter(experiment_id=experiment_id)
    all_jv_dirs = [(stack.id, os.path.join(
        settings.MEDIA_ROOT, stack.jv_dir)) for stack in stacks]

    for stack_id, jv_dir in all_jv_dirs:
        csv_path = f'{jv_dir}/summary_jv.csv'

        df = pd.read_csv(csv_path)

        if df.empty:
            continue

        # first compare between rev and fwd which is higher on average

        # get the average of the columns
        avg_rev = df.iloc[:, 8].mean()
        avg_fwd = df.iloc[:, 9].mean()

        if avg_rev > avg_fwd:
            max_index = df.iloc[:, 8].idxmax()
            hero_device_pce = df.iloc[max_index, 8]
            # get the filename at the max index
            hero_device_jv_dir = df.iloc[max_index, 0]

        else:
            max_index = df.iloc[:, 9].idxmax()
            hero_device_pce = df.iloc[max_index, 9]
            # get the filename at the max index
            hero_device_jv_dir = df.iloc[max_index, 0]

        # get the stack name
        stack = Stack.objects.get(id=stack_id)
        stack.hero_device_jv_dir = hero_device_jv_dir
        stack.hero_device_pce = hero_device_pce
        stack.save()
