import glob
import os
import pandas as pd
import chardet
import plotly.graph_objects as go
from .models import *
from django.conf import settings
import re
import urllib.parse
from plotly.colors import qualitative


def dataframe(dir):
  
    if os.path.isdir(dir):
        files = glob.glob(f'{dir}/*.SEQ')  # All SEQ files in the directory
    elif os.path.isfile(dir):
        files = [dir]  # Single file case
   
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

                elif split_file[30][3] == 'Light':
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
    if os.path.isdir(dir):
        files = [os.path.join(dir, filename) for filename in os.listdir(dir) if filename.endswith(".txt")]
    elif os.path.isfile(dir):
        files = [dir]  # Single file case
    else:
        raise ValueError("Provided path is neither a file nor a directory.")
    for filepath in files:
        
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



def jvBoxPlot(experiment_id, update_jv_summary):
    stacks = Stack.objects.filter(experiment_id=experiment_id)
    jv_software = ''

    if all([stack.jv_software == 'new' for stack in stacks]):
        jv_software = 'new'
    elif all([stack.jv_software == 'default' for stack in stacks]):
        jv_software = 'default'
    else:
        raise ValueError('All stacks must have the same jv_software')
    
    all_jv_dirs = [(stack.name, os.path.join(settings.MEDIA_ROOT, stack.jv_dir)) for stack in stacks]
    df_list = []

    # Load data from 'summary_jv.csv' or generate it
    if all([os.path.exists(os.path.join(jv_dir, 'summary_jv.csv')) for _, jv_dir in all_jv_dirs]) and update_jv_summary != 'true':
        for stack_name, jv_dir in all_jv_dirs:
            df = pd.read_csv(os.path.join(jv_dir, 'summary_jv.csv'))
            df_list.append((stack_name, df))
    else:
        for stack_name, jv_dir in all_jv_dirs:
            if jv_software == 'default':
                df = dataframe(jv_dir)
            elif jv_software == 'new':
                df = dataframe_new(jv_dir)
            df_list.append((stack_name, df))
            df.to_csv(os.path.join(jv_dir, 'summary_jv.csv'), index=False)

    # Define the figures dictionary to store each metric's plot
    figures = {}
    for metric, fwd_col, rev_col, yaxis_title in [
        ('JSc', 'Jsc Fwd', 'Jsc Rev', 'Current Density (mA/cm<sup>2</sup>)'),
        ('Voc', 'Voc Fwd', 'Voc Rev', 'Open Circuit Voltage (Volts)'),
        ('FF', 'FF Fwd', 'FF Rev', 'Fill Factor (%)'),
        ('PCE', 'PCE Fwd', 'PCE Rev', 'Power Conversion Efficiency (%)')
    ]:
        fig_fwd = go.Figure()
        fig_rev = go.Figure()
        fig_combined = go.Figure()

        color_palette = qualitative.Plotly  # A palette with several distinct colors

        # Select a color based on the index of the trace in the palette
        color_index = 0  # Adjust this index as needed for each trace

        for stack_name, df in df_list:
            # Forward scan box plot (individual)
            fig_fwd.add_trace(go.Box(
                y=df[fwd_col], name=stack_name,
                boxpoints='all', jitter=0.3, pointpos=-1.8
            ))

            # Reverse scan box plot (individual)
            fig_rev.add_trace(go.Box(
                y=df[rev_col], name=stack_name,
                boxpoints='all', jitter=0.3, pointpos=-1.8
            ))

# Combined box plot: Forward as filled, Reverse as outline only
            fig_combined.add_trace(go.Box(
                y=df[fwd_col], name=stack_name,
                marker=dict(color=color_palette[color_index]),  # Use color from the palette
                fillcolor=color_palette[color_index],  # Fill color for forward scan
                showlegend=False,

                ))

# Add reverse scan with the same color outline but transparent fill
            fig_combined.add_trace(go.Box(
                y=df[rev_col], name=stack_name,

                marker=dict(color=color_palette[color_index]),  # Same color for reverse outline
                fillcolor='rgba(0,0,0,0)',  # Transparent fill for reverse scan
                 showlegend=False,

            ))

            # Update color_index for the next pair of traces, if needed
            color_index += 1  # Move to the next color in the palette




        fig_combined.add_trace(go.Box(
            y=[None], name="Forward", marker_color='grey', fillcolor='grey',
            boxpoints=False, showlegend=True, opacity=0.6  # Filled grey box for "Forward"
        ))
        fig_combined.add_trace(go.Box(
            y=[None], name="Reverse", marker_color='grey', fillcolor='rgba(0,0,0,0)',
            line=dict(color='grey'), boxpoints=False, showlegend=True, opacity=0.6  # Outline grey box for "Reverse"
        ))
        # Layout for forward and reverse plots (no styling changes)
        fig_fwd.update_layout(yaxis_title=yaxis_title, width=600)
        fig_rev.update_layout(yaxis_title=yaxis_title, width=600)

        # Layout for combined plot with grouped box mode
        fig_combined.update_layout(
            yaxis_title=yaxis_title,
            width=600,
            boxmode = 'group'
            
        )

        # Store each plot in the figures dictionary
        figures[f'fig_{metric.lower()}_fwd'] = fig_fwd.to_html(full_html=False, div_id=f'fig_{metric.lower()}_fwd_div', include_plotlyjs='cdn')
        figures[f'fig_{metric.lower()}_rev'] = fig_rev.to_html(full_html=False, div_id=f'fig_{metric.lower()}_rev_div', include_plotlyjs='cdn')
        figures[f'fig_{metric.lower()}_combined'] = fig_combined.to_html(full_html=False, div_id=f'fig_{metric.lower()}_combined_div', include_plotlyjs='cdn')

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
