
  // Assume you have included Chart.js library in your HTML

  // Data preparation
  var X = [];
  var Y = [];
  var user = [];

  // Iterate through Stack objects to collect data (assuming X, Y, and user arrays are populated similarly to your Django/Python code)
  {% for stack in stacks %}
      X.push("{{ stack.created|date:'Y-m-d' }}");
      Y.push({{ stack.hero_device_pce }});
      user.push("{{ stack.author.first_name }} {{ stack.author.last_name }}");
  {% endfor %}
  data = X.map((value, index) => ({ x: value, y: Y[index] }));
  // Chart.js configuration
  var ctx = document.getElementById('scatterChart').getContext('2d');
  var scatterChart = new Chart(ctx, {
      type: 'scatter',
      data: {
          datasets: [{
              label: 'PCE',
              data: data,
              backgroundColor: 'navy',
              borderColor: 'navy',
              borderWidth: 1,
              pointRadius: 5,
              pointHoverRadius: 8,
              pointStyle: 'circle',
              hoverBackgroundColor: 'navy',
              hoverBorderWidth: 2,
              hoverRadius: 15
          }]
      },
      options: {
        scales: {
          x: {
            type: 'time',
            time: {
              unit: 'day',

            },
            title: {
              display: true,
              text: 'Date'
            }
          },
          y: {
            title: {
              display: true,
              text: 'PCE'
            }
        },
        }
      }

  });