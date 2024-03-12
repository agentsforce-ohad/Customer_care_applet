import streamlit as st
import numpy as np
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

csv_file_path = "/Users/joaomontenegro/Documents/Projects/Customer_care_applet/monthly_tickets_and_costs_baseline.csv"

# Function to load the baseline data from CSV
def load_baseline_data(csv_file_path):
    return pd.read_csv(csv_file_path)

def sigmoid(x, start_val, end_val, k, x0):
    y = start_val + (end_val - start_val) / (1 + np.exp(-k*(x-x0)))
    return y

# Convert Portuguese month names to numerical indices
def month_to_index(month_name):
    months_pt_to_en = {
        'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 
        'mai': 5, 'jun': 6, 'jul': 7, 'ago': 8, 
        'set': 9, 'out': 10, 'nov': 11, 'dez': 12
    }
    return months_pt_to_en.get(month_name.lower(), 0)

def calculate_costs(weeks, base_tickets, ai_ticket_cost_base, ai_ticket_cost_success, agent_ticket_cost, start_deflection, end_deflection, target_time, discount=0.2):
    x0 = target_time / 2  # Midpoint for sigmoid, assuming symmetry
    k = 4 / target_time  # Adjust 'k' to reach ~end_deflection at 'target_time'
    
    weeks_arr = np.arange(weeks)
    deflection_rates = sigmoid(weeks_arr, start_deflection, end_deflection, k, x0)

    ai_handled = base_tickets * deflection_rates
    ai_resolved = ai_handled
    ai_touched_only = ai_handled - ai_resolved
    unsolved_tickets = base_tickets - ai_handled

    ai_cost = (ai_resolved * ai_ticket_cost_success) + (ai_touched_only * ai_ticket_cost_base)
    agent_cost = unsolved_tickets * agent_ticket_cost
    total_cost = ai_cost + agent_cost

    annual_spend = np.cumsum(ai_cost) / weeks * 52
    ai_cost[annual_spend > 36000] *= (1 - discount)  # Applying 20% discount if annual spend exceeds $36,000

    data = {
        "Week": weeks_arr + 1,
        "Deflection Rate": deflection_rates,
        "AI Handled Tickets": ai_handled,
        "AI Resolved Tickets": ai_resolved,
        "Unsolved Tickets": unsolved_tickets,
        "AI Cost": ai_cost,
        "Agent Cost": agent_cost,
        "Total Cost": total_cost
    }
    return pd.DataFrame(data)

def calculate_costs_variable(weeks, weekly_tickets, ai_ticket_cost_base, ai_ticket_cost_success, agent_ticket_cost, start_deflection, end_deflection, target_time, discount=0.2):
    x0 = target_time / 2  # Midpoint for sigmoid, assuming symmetry
    k = 4 / target_time  # Adjust 'k' to reach ~end_deflection at 'target_time'
    weeks_arr = np.arange(weeks)
    deflection_rates = sigmoid(weeks_arr, start_deflection, end_deflection, k, x0)

    ai_handled = np.array(weekly_tickets) * deflection_rates
    ai_resolved = ai_handled
    ai_touched_only = ai_handled - ai_resolved
    unsolved_tickets = np.array(weekly_tickets) - ai_handled

    ai_cost = (ai_resolved * ai_ticket_cost_success) + (ai_touched_only * ai_ticket_cost_base)
    agent_cost = unsolved_tickets * agent_ticket_cost
    total_cost = ai_cost + agent_cost

    annual_spend = np.cumsum(ai_cost) / weeks * 52
    ai_cost[annual_spend > 36000] *= (1 - discount)  # Apply discount if spend exceeds $36k

    data = {
        "Week": weeks_arr + 1,
        "Deflection Rate": deflection_rates,
        "AI Handled Tickets": ai_handled,
        "AI Resolved Tickets": ai_resolved,
        "Unsolved Tickets": unsolved_tickets,
        "AI Cost": ai_cost,
        "Agent Cost": agent_cost,
        "Total Cost": total_cost
    }
    return pd.DataFrame(data)

# Streamlit sidebar inputs
st.sidebar.title("Simulation Parameters")
weeks = st.sidebar.slider("Weeks to simulate:", 1, 104, 52, help="Number of weeks over which to simulate the model.")
base_tickets = st.sidebar.number_input("Base weekly ticket volume:", min_value=0, value=1000, help="Average number of tickets received per week.")
ai_ticket_cost_base = st.sidebar.number_input("Cost per AI-handled (touched) ticket ($):", min_value=0.0, value=0.75, help="Cost for each ticket that AI interacts with but doesn't fully resolve.")
ai_ticket_cost_success = st.sidebar.number_input("Additional cost for AI-resolved ticket ($):", min_value=0.0, value=1.5, help="Additional cost for tickets that AI successfully resolves on top of the base cost.")
agent_ticket_cost = st.sidebar.number_input("Cost per agent-handled ticket ($):", min_value=0.0, value=5.0, help="Cost for each ticket handled by a human agent.")
discount = st.sidebar.number_input("Discount for purchases larger than $36k (%):", min_value=0.0, max_value=1.0, value=0.2, help="Discount applied to the total cost if annual spend exceeds $36,000.")
deflection_range = st.sidebar.slider("Deflection rate range:", 0.0, 1.0, (0.05, 0.4), help="Range of percentage of tickets that AI can handle.")
start_deflection, end_deflection = deflection_range
target_time = st.sidebar.number_input("Target time to reach end deflection rate (weeks):", min_value=1, value=24, help="Number of weeks over which the deflection rate reaches the target value.")
st.sidebar.info(f"A total of {weeks} weeks will be simulated, with {base_tickets} tickets received per week, and the following costs: \${ai_ticket_cost_base} for AI-handled tickets, \${ai_ticket_cost_success} for AI-resolved tickets, and \${agent_ticket_cost} for agent-handled tickets. Then, the deflection rate will increase from {start_deflection:.0%} to {end_deflection:.0%} over {target_time} weeks.")

df = calculate_costs(weeks, base_tickets, ai_ticket_cost_base, ai_ticket_cost_success, agent_ticket_cost, start_deflection, end_deflection, target_time)

# Load and process the baseline data
baseline_data = pd.read_csv(csv_file_path)
baseline_data['Month Index'] = baseline_data['Month'].apply(month_to_index)

# Expand monthly data to a weekly format and adjust values for a weekly scale
weekly_data = []
for _, row in baseline_data.iterrows():
    for week in range(1, 5):  # Assuming 4 weeks per month
        weekly_row = row.to_dict()
        weekly_row['Week'] = (row['Month Index'] - 1) * 4 + week
        weekly_row['Total Cases'] /= 4
        weekly_row['Contact Center COST'] /= 4
        weekly_data.append(weekly_row)

baseline_data_weekly = pd.DataFrame(weekly_data)

# Merge the weekly baseline data with your simulation DataFrame 'df'
df['Week'] = np.arange(1, len(df) + 1)  # Ensure df has a 'Week' column for merging
merged_df = pd.merge(df, baseline_data_weekly, on='Week', how='left', suffixes=('', '_current'))


st.title("Customer Care Cost Simulation")

tab1, tab2 = st.tabs(["Simple Simulation", "Complex Simulation with Baseline Data"])

with tab1:
    # Plotting with Plotly and displaying DataFrame
    fig_tickets = px.line(merged_df, x="Week", y=["AI Handled Tickets", "AI Resolved Tickets", "Unsolved Tickets"], title="Ticket Handling Over Time")
    fig_tickets.add_trace(go.Scatter(x=merged_df['Week'], y=merged_df['Total Cases'], mode='lines+markers', name='current Weekly Tickets'))
    fig_tickets.add_trace(go.Scatter(x=merged_df['Week'], y=np.poly1d(np.polyfit(merged_df['Week'], merged_df['Total Cases'], 1))(merged_df['Week']), mode='lines', name='Trendline'))
    fig_tickets.update_layout(hovermode="x unified")
    st.plotly_chart(fig_tickets, use_container_width=True)
    st.caption("Here's the number of tickets handled by AI over time. It includes the number of AI-handled tickets, AI-resolved tickets, and unsolved tickets.")

    st.write("---")

    fig_costs = px.line(merged_df, x="Week", y=["AI Cost", "Agent Cost", "Total Cost"], title="Costs Over Time")
    fig_costs.add_trace(
        go.Scatter(x=merged_df['Week'], y=merged_df['Contact Center COST'], mode='lines+markers', name='current Weekly Costs', line=dict(color='firebrick', dash='dot'))
    )
    fig_costs.update_layout(hovermode="x unified")
    st.plotly_chart(fig_costs, use_container_width=True)
    st.caption("This graph shows the cost of handling tickets over time, including both AI-handled and agent-handled tickets, along with the current weekly costs.")

    st.write("---")

    merged_df['Current price Per Ticket'] = merged_df['Contact Center COST'] / merged_df['Total Cases']
    fig_prices = px.line(merged_df, x="Week", y=["Current price Per Ticket"], title="Price Per Ticket Over Time")
    # Adding simulated data for comparison (adjust column names as per your simulation DataFrame)
    fig_prices.add_trace(
        go.Scatter(x=merged_df['Week'], y=merged_df['Total Cost'] / (merged_df['AI Handled Tickets'] + merged_df['Unsolved Tickets']), mode='lines+markers', name='Simulated Price Per Ticket', line=dict(color='green', dash='dot'))
    )
    fig_prices.update_layout(hovermode="x unified")
    st.plotly_chart(fig_prices, use_container_width=True)
    st.caption("This graph shows the price per ticket over time, comparing the current weekly price to the simulated price per ticket.")

    st.write("---")

    st.header("Data from simulation")
    st.dataframe(df)

    st.write("---")


with tab2:
    st.header("Costs based on current values")

    # This will be your variable weekly_tickets input to the calculate_costs_variable function.
    weekly_ticket_volumes = baseline_data_weekly['Total Cases'].tolist()

    # The number of weeks to simulate should be set to the length of the `weekly_ticket_volumes`.
    weeks = len(weekly_ticket_volumes)

    # Now calculate costs with actual weekly ticket volumes
    df_actual = calculate_costs_variable(weeks, weekly_ticket_volumes, ai_ticket_cost_base, ai_ticket_cost_success, agent_ticket_cost, start_deflection, end_deflection, target_time)

    # Finally, create a new graph using df_actual for the base weekly ticket volume
    fig_base_weekly_volume = px.line(df_actual, x="Week", y="Unsolved Tickets", title="Current Base Weekly Ticket Volume")
    # Add the original actual data line
    fig_base_weekly_volume.add_trace(go.Scatter(x=df_actual['Week'], y=weekly_ticket_volumes, mode='lines+markers', name='Current Weekly Volume', line=dict(color='red', dash='dot')))
    fig_base_weekly_volume.update_layout(hovermode="x unified", showlegend=True)
    st.plotly_chart(fig_base_weekly_volume, use_container_width=True)

    st.write("---")

    # Cost over time comparing the actual and calculated costs based on actual weekly ticket volumes
    fig_costs_actual = px.line(df_actual, x="Week", y="Total Cost", title="Costs Over Time")

    # calculate costs per week based on actual weekly ticket volumes
    weekly_costs = baseline_data_weekly['Contact Center COST'].tolist()

    # Add the original actual data line
    fig_costs_actual.add_trace(go.Scatter(
        x=df_actual['Week'], y=weekly_costs, mode='lines+markers', name='Current Weekly Costs', line=dict(color='red', dash='dot'))
    )

    fig_costs_actual.update_layout(hovermode="x unified", showlegend=True)
    st.plotly_chart(fig_costs_actual, use_container_width=True)

    st.write(f"Total cost for the year: ${df_actual['Total Cost'].sum():,.2f}")

    # calculate price per ticket based on actual weekly ticket volumes
    merged_df['Current price Per Ticket'] = np.array(merged_df['Contact Center COST']) / np.array(merged_df['Total Cases'])

    # Price per ticket over time comparing the actual and calculated price per ticket based on actual weekly ticket volumes
    # Get the lengths of the arrays
    merged_df_len = len(merged_df)
    weekly_costs_len = len(weekly_costs)
    weekly_ticket_volumes_len = len(weekly_ticket_volumes)

    # Determine the length to slice the arrays
    slice_len = min(merged_df_len, weekly_costs_len, weekly_ticket_volumes_len)

    # Slice the arrays to the determined length
    merged_df = merged_df[:slice_len]
    weekly_costs = weekly_costs[:slice_len]
    weekly_ticket_volumes = weekly_ticket_volumes[:slice_len]

    # Calculate the actual price per ticket
    merged_df['Actual price Per Ticket'] = np.array(weekly_costs) / np.array(weekly_ticket_volumes)

    fig_prices_actual = px.line(merged_df, x="Week", y=["Current price Per Ticket", "Actual price Per Ticket"], title="Price Per Ticket Over Time")
    fig_prices_actual.update_layout(hovermode="x unified")
    st.plotly_chart(fig_prices_actual, use_container_width=True)

    st.write("---")

    st.header("Data from baseline")
    st.dataframe(baseline_data_weekly)

    st.write("---")

    st.header("Data from complex simulation with baseline data")
    st.dataframe(merged_df)
