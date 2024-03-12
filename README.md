# Customer Care Cost Simulation Applet

This Streamlit application is designed to simulate customer care costs based on various parameters related to ticket handling and resolution through AI and human agents. It utilizes libraries such as Streamlit, Pandas, NumPy, and Plotly for interactive visualization and data manipulation.

## Features

- **Simulation of ticket handling costs**: Estimate costs over time for handling customer care tickets using both AI and human agents.
- **Dynamic parameter adjustment**: Users can adjust simulation parameters such as weekly ticket volume, AI handling costs, agent costs, and deflection rates through an interactive sidebar.
- **Complex simulation with baseline data**: Incorporates baseline data from a CSV file to simulate and compare with current values, enhancing the simulation's realism.
- **Interactive visualizations**: Utilizes Plotly for generating dynamic graphs that depict ticket handling metrics and costs over time.

## How It Works

1. **Loading Data**: The application begins by loading baseline data from a specified CSV file, containing historical ticket volumes and costs.

2. **Parameter Input**: Users input simulation parameters through the sidebar, including the number of weeks to simulate, base weekly ticket volume, costs associated with AI and human agent handling, and deflection rates.

3. **Simulation Execution**: The application calculates the costs associated with handling tickets based on the provided parameters, using a sigmoid function for modeling deflection rates over time.

4. **Visualization**: The results of the simulation are visualized in several graphs, showcasing the number of tickets handled by AI, costs over time, and price per ticket.

5. **Comparison with Baseline Data**: The application compares the simulated data with baseline historical data, allowing for a detailed analysis of potential cost savings and efficiency gains.

## Usage

To run this application, you'll need to have Streamlit and the required libraries (Pandas, NumPy, and Plotly) installed in your Python environment. Start the application by navigating to the directory containing this script and running:

```shell
streamlit run app.py
```

Replace `app.py` with the name of this script. The application will start in your default web browser, where you can interact with the simulation parameters and view the results.

## Customizing the Simulation

- **CSV File Path**: The path to the baseline data CSV file is hardcoded in the script. You may need to adjust this path to point to the correct location of your baseline data file.

- **Simulation Parameters**: The sidebar allows for dynamic adjustment of simulation parameters. Experiment with different values to understand how they impact the overall costs and efficiency of ticket handling.

- **Advanced Customization**: For more advanced users, the simulation functions (`calculate_costs` and `calculate_costs_variable`) can be modified to include additional parameters or to adjust the calculation logic to better fit specific use cases.

## Notes

- Ensure that the baseline CSV file is formatted correctly, with columns for monthly ticket volumes and costs.

- The application uses a sigmoid function to model the change in deflection rate over time, which assumes a specific shape of the transition. This may need adjustment based on real-world data.

- Visualizations are meant to provide insights at a glance but can be further customized using Plotly's extensive charting options.

Enjoy exploring different scenarios and gaining insights into the potential costs and efficiencies of using AI in customer care operations.
