import streamlit as st
import numpy as np
import pandas as pd
from data_utils import load_baseline_data, preprocess_baseline_data
from cost_calculation import calculate_costs
from visualization import create_ticket_handling_plot, create_costs_plot, create_price_per_ticket_plot, display_key_metrics
import plotly.graph_objects as go
import plotly.express as px

# Function to load the baseline data from CSV
csv_file_path = "monthly_tickets_and_costs_baseline.csv"
baseline_data = load_baseline_data(csv_file_path)
baseline_data_daily = preprocess_baseline_data(baseline_data)

# Streamlit sidebar inputs
st.sidebar.title("Simulation Parameters")
days = st.sidebar.slider("Days to simulate:", 1, 730, 365, help="Number of days over which to simulate the model.")
base_tickets = st.sidebar.number_input("Base daily ticket volume:", min_value=0, value=150, help="Average number of tickets received per day.")
ai_ticket_cost_base = st.sidebar.number_input("Cost per AI-handled (touched) ticket ($):", min_value=0.0, value=0.75, help="Cost for each ticket that AI interacts with but doesn't fully resolve.")
ai_ticket_cost_success = st.sidebar.number_input("Additional cost for AI-resolved ticket ($):", min_value=0.0, value=1.5, help="Additional cost for tickets that AI successfully resolves on top of the base cost.")
agent_ticket_cost = st.sidebar.number_input("Cost per agent-handled ticket ($):", min_value=0.0, value=5.0, help="Cost for each ticket handled by a human agent.")
discount = st.sidebar.number_input("Discount for purchases larger than $36k (%):", min_value=0.0, max_value=1.0, value=0.2, help="Discount applied to the total cost if annual spend exceeds $36,000.")
deflection_range = st.sidebar.slider("Deflection rate range:", 0.0, 1.0, (0.05, 0.4), help="Range of percentage of tickets that AI can handle.")
start_deflection, end_deflection = deflection_range
target_time = st.sidebar.number_input("Target time to reach end deflection rate (days):", min_value=1, value=180, help="Number of days over which the deflection rate reaches the target value.")
st.sidebar.info(f"A total of {days} days will be simulated, with {base_tickets} tickets received per day, and the following costs: \${ai_ticket_cost_base} for AI-handled tickets, \${ai_ticket_cost_success} for AI-resolved tickets, and \${agent_ticket_cost} for agent-handled tickets. Then, the deflection rate will increase from {start_deflection:.0%} to {end_deflection:.0%} over {target_time} days.")

# Calculate costs
df = calculate_costs(base_tickets, days, ai_ticket_cost_base, ai_ticket_cost_success, agent_ticket_cost, start_deflection, end_deflection, target_time, discount)

st.title("Customer Care Cost Simulation")

tab1, tab2 = st.tabs(["Simple Simulation", "Complex Simulation with Baseline Data"])

with tab1:
    # Total cost for the simulated period
    total_cost = df['Total Cost'].sum()
    baseline_total_cost = baseline_data_daily['Contact Center COST'].sum()
    # Metrics
    display_key_metrics(df, baseline_data_daily)

    # Plotting with Plotly and displaying DataFrame
    fig_tickets = create_ticket_handling_plot(df, baseline_data_daily)  # Assuming create_ticket_handling_plot is adjusted for daily data
    st.plotly_chart(fig_tickets, use_container_width=True)
    st.caption("Here's the number of tickets handled by AI over time, displayed on a daily basis. It includes the number of AI-handled tickets, AI-resolved tickets, and unsolved tickets.")

    st.write("---")

    fig_costs = create_costs_plot(df, baseline_data_daily)  # Assuming create_costs_plot is adjusted for daily data
    st.plotly_chart(fig_costs, use_container_width=True)
    st.caption("This graph shows the cost of handling tickets over time on a daily basis, including both AI-handled and agent-handled tickets, along with the current daily costs.")

    st.write("---")

    fig_prices = create_price_per_ticket_plot(df, baseline_data_daily)  # Assuming create_price_per_ticket_plot is adjusted for daily data
    st.plotly_chart(fig_prices, use_container_width=True)
    st.caption("This graph shows the price per ticket over time, comparing the current daily price to the simulated price per ticket.")

    st.write("---")

    st.header("Data from simulation")
    st.dataframe(df)

    st.write("---")

with tab2:
    st.write("**Costs based on current values**")

    # Adjusting to work with daily ticket volumes.
    daily_ticket_volumes = baseline_data_daily['Total Cases'].tolist()

    # The number of days to simulate should be set to the length of the `daily_ticket_volumes`.
    days = len(daily_ticket_volumes)

    # Now calculate costs with actual daily ticket volumes
    df_actual = calculate_costs(daily_ticket_volumes, days, ai_ticket_cost_base, ai_ticket_cost_success, agent_ticket_cost, start_deflection, end_deflection, target_time, discount)

    # Metrics comparing the simulation results with the baseline data
    display_key_metrics(df_actual, baseline_data_daily)

    # Creating a new graph using df_actual for the base daily ticket volume
    fig_base_daily_volume = px.line(df_actual, x="Day", y="Unsolved Tickets", title="Current Base Daily Ticket Volume")
    # Add the original actual data line
    fig_base_daily_volume.add_trace(go.Scatter(x=df_actual['Day'], y=daily_ticket_volumes, mode='lines+markers', name='Current Daily Volume', line=dict(color='red', dash='dot')))
    fig_base_daily_volume.update_layout(hovermode="x unified", showlegend=True)
    st.plotly_chart(fig_base_daily_volume, use_container_width=True)

    st.write("---")

    # Cost over time comparing the actual and calculated costs based on actual daily ticket volumes
    fig_costs_actual = create_costs_plot(df_actual, baseline_data_daily)  # Assume this is updated for daily data

    # Daily costs from the baseline
    daily_costs = baseline_data_daily['Contact Center COST'].tolist()

    fig_costs_actual.update_layout(hovermode="x unified", showlegend=True)
    st.plotly_chart(fig_costs_actual, use_container_width=True)

    st.write(f"Total cost for the simulation period: ${df_actual['Total Cost'].sum():,.2f}")

    # Price per ticket over time comparing the actual and calculated price per ticket based on actual daily ticket volumes
    fig_prices_actual = create_price_per_ticket_plot(df_actual, baseline_data_daily)  # Assume this is updated for daily data
    st.plotly_chart(fig_prices_actual, use_container_width=True)

    st.write("---")

    st.header("Data from baseline (Daily)")
    st.dataframe(baseline_data_daily)

    st.write("---")

    st.header("Data from complex simulation with baseline data (Daily)")

    st.dataframe(df_actual)
