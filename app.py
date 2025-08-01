import plotly.express as px
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
import io

# Theme toggle
mode = st.sidebar.radio("Choose Theme Mode:", ["🌞 Light Mode", "🌚 Dark Mode"])

if mode == "🌞 Light Mode":
    background = "#f9f9f9"
    font = "#111111"
    header = "#2c3e50"
    chart_color = "#2e8b57"
else:
    background = "#000000"
    font = "#f0f0f0"
    header = "#ffffff"
    chart_color = "#90ee90"

st.markdown(
    f"""
    <style>
    body {{
        background-color: {background};
        color: {font};
    }}
    .stApp {{
        background-color: {background};
        color: {font};
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: {header};
    }}
    </style>
    """,
    unsafe_allow_html=True
)
# Enhanced button/input styling
st.markdown(
    """
    <style>
    .stButton>button {
        background-color: #708238;
        color: white;
        border-radius: 8px;
        height: 3em;
        width: auto;
        padding: 0.5em 1em;
        font-weight: bold;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #556B2F;
        color: white;
    }

    .stTextInput>div>div>input, .stNumberInput input {
        border-radius: 5px;
        padding: 6px;
        border: 1px solid #ccc;
    }

    .stFileUploader, .stSelectbox, .stDateInput, .stSlider {
        padding: 6px;
    }

    .stDownloadButton>button {
        background-color: #708238;
        color: white;
        border-radius: 6px;
        font-weight: bold;
        padding: 0.5em 1em;
    }
    .stDownloadButton>button:hover {
        background-color: #556B2F;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Title and Description
st.title("🌿 Plant Energy Usage Estimator")
st.markdown("""
Monitor and improve your plant's energy efficiency by tracking energy used and steel output.  
This tool calculates **energy per ton**, tags performance, estimates CO₂, and supports CSV export.
""")

selected_date = st.date_input("📅 Select report date", help="Used to tag your report by date")



# Threshold
threshold = st.slider("⚙️ Set Energy Efficiency Threshold (kWh per ton)", 
                      min_value=100, max_value=1000, value=600, step=50)


st.markdown("""
📝 **CSV format expected**:  
Upload a file with two columns named:
- `Energy Used (kWh)`
- `Steel Produced (tons)`
""")


# Input Form
st.header("📂 Upload Data (Optional)")
uploaded_file = st.file_uploader("Upload a CSV file with Energy and Steel data", type=["csv"])

st.markdown(
    f"<h3 style='color: {'black' if mode == 'Light' else 'white'};'>Generate random sample data</h3>", 
    unsafe_allow_html=True
)

energy_list = []
steel_list = []

if uploaded_file is not None:
    try:
        df_upload = pd.read_csv(uploaded_file)
        energy_list = df_upload.iloc[:, 0].tolist()
        steel_list = df_upload.iloc[:, 1].tolist()
        days = len(energy_list)
        st.success("📄 CSV data loaded successfully!")
    except Exception as e:
        st.error("❌ Error reading CSV file. Ensure it has 2 numeric columns like: Energy (kWh), Steel (tons)")

elif use_random:
    # 📅 Date Selector
    selected_date = st.date_input("Select report date", help="This helps identify your report by date")

    days = st.number_input("📅 Number of days to generate random data", min_value=1, max_value=31, value=7)
    energy_list = [round(random.uniform(400, 900), 2) for _ in range(days)]
    steel_list = [round(random.uniform(5, 20), 2) for _ in range(days)]
    st.success("✅ Random sample data generated.")

else:
    days = st.number_input("📅 Number of days to enter data manually", min_value=1, max_value=31, value=7)
    st.markdown("### ✍️ Manual Entry")

    for i in range(days):
        st.subheader(f"Day {i + 1}")
        energy = st.number_input(f"→ Energy used (kWh) [Day {i + 1}]", min_value=0.0, key=f"e{i}")
        steel = st.number_input(f"→ Steel produced (tons) [Day {i + 1}]", min_value=0.0, key=f"s{i}")
        energy_list.append(energy)
        steel_list.append(steel)

st.header("📊 Compare Two Time Periods")

# Upload two files
col1, col2 = st.columns(2)
with col1:
    file1 = st.file_uploader("Upload Dataset 1", type="csv", key="file1")
with col2:
    file2 = st.file_uploader("Upload Dataset 2", type="csv", key="file2")

# Proceed if both files uploaded
if file1 and file2:
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Rename columns if needed to match expected
    df1.columns = df1.columns.str.strip()
    df2.columns = df2.columns.str.strip()

    # Calculate efficiency
    df1["Energy per Ton"] = df1["Energy Used (kWh)"] / df1["Steel Produced (tons)"]
    df2["Energy per Ton"] = df2["Energy Used (kWh)"] / df2["Steel Produced (tons)"]

    avg1 = df1["Energy per Ton"].mean()
    avg2 = df2["Energy per Ton"].mean()

    diff = avg2 - avg1
    percent_change = (diff / avg1) * 100

    st.markdown("### 🔁 Efficiency Comparison")
    st.write(f"Average Efficiency in Dataset 1: `{avg1:.2f} kWh/ton`")
    st.write(f"Average Efficiency in Dataset 2: `{avg2:.2f} kWh/ton`")

    if diff < 0:
        st.success(f"✅ Efficiency Improved by `{abs(percent_change):.2f}%`")
    elif diff > 0:
        st.warning(f"⚠️ Efficiency Decreased by `{percent_change:.2f}%`")
    else:
        st.info("⚖️ No change in efficiency.")

    # Optional: Plot the comparison
    st.markdown("#### 📉 Efficiency Trend Comparison")

    comparison_df = pd.DataFrame({
        "Day": range(1, min(len(df1), len(df2)) + 1),
        "Period 1": df1["Energy per Ton"].values[:len(df1)],
        "Period 2": df2["Energy per Ton"].values[:len(df2)],
    })

    fig = px.line(
        comparison_df, 
        x="Day", 
        y=["Period 1", "Period 2"], 
        labels={"value": "Energy per Ton (kWh/ton)", "variable": "Time Period"},
        title="Efficiency Comparison Over Days"
    )
    st.plotly_chart(fig)



# Calculate efficiency
efficiency_list = [e/s if s != 0 else 0 for e, s in zip(energy_list, steel_list)]
alerts = ["⚠️ High" if eff > threshold else "✅ OK" for eff in efficiency_list]

# Efficiency category
def categorize_efficiency(value):
    if value <= threshold * 0.8:
        return "✅ Excellent"
    elif value <= threshold:
        return "🟡 Acceptable"
    else:
        return "🔴 Poor"

efficiency_tags = [categorize_efficiency(eff) for eff in efficiency_list]


# Dataframe for display
df = pd.DataFrame({
    "Date": [selected_date] * days,
    "Day": list(range(1, days+1)),
    "Energy Used (kWh)": energy_list,
    "Steel Produced (tons)": steel_list,
    "Energy per Ton (kWh/ton)": efficiency_list,
    "Alert": alerts
})


# Show Results
st.header("📊 Efficiency Results")
st.dataframe(df.style.format({"Energy per Ton (kWh/ton)": "{:.2f}"}))

# Summary Stats
total_energy = sum(energy_list)
total_steel = sum(steel_list)
avg_efficiency = total_energy / total_steel if total_steel != 0 else 0

st.markdown(f"**Total Energy Used:** `{total_energy:.2f}` kWh")
st.markdown(f"**Total Steel Produced:** `{total_steel:.2f}` tons")
st.markdown(f"**Average Energy per Ton:** `{avg_efficiency:.2f}` kWh/ton")

# CO₂ Emissions Estimator
st.header("🌍 CO₂ Emissions Estimator (Green Focus)")

emission_rate = st.number_input(
    "Enter CO₂ emission rate per kWh (kg CO₂/kWh)", 
    min_value=0.0, value=0.9, step=0.1, 
    help="Average global CO₂ emission factor is about 0.9 kg/kWh"
)

total_emissions = total_energy * emission_rate

tree_offset_rate = 21 
trees_needed = total_co2 / tree_offset_rate

st.markdown("### 🌳 CO₂ Offset Suggestion")
st.markdown(f"To offset **{total_co2:,.2f} kg** of CO₂ emissions annually, you would need to plant approximately **{trees_needed:,.0f} trees**.")
st.progress(min(1.0, trees_needed / 1000))  # Just for a fun visual cap at 1000 trees


# 🏆 Highlight Top 3 Efficient Days
st.header("🏅 Top 3 Most Efficient Days")

# Sort by efficiency (lowest energy per ton is best)
top3_df = df.sort_values(by="Energy per Ton (kWh/ton)").head(3)

# Reset index for clean display
top3_df = top3_df.reset_index(drop=True)

# Show in styled dataframe
st.dataframe(
    top3_df.style.format({
        "Energy per Ton (kWh/ton)": "{:.2f}",
        "Energy Used (kWh)": "{:.2f}",
        "Steel Produced (tons)": "{:.2f}"
    }).highlight_max(subset=["Steel Produced (tons)"], color="lightgreen")
)


# Optional: Badge
if total_emissions < 500:
    st.success("✅ Low Carbon Footprint! Great Job!")
elif total_emissions < 1000:
    st.info("🟡 Moderate Emissions")
else:
    st.warning("🔴 High Carbon Output. Consider efficiency upgrades.")


if avg_efficiency > threshold:
    st.warning("⚠️ Weekly efficiency is high. Investigate for energy waste.")
else:
    st.success("✅ Weekly efficiency is within limit.")


# 🔁 Plotly Chart: Enhanced Efficiency Trend
st.header("📈 Efficiency Trend")

fig = px.line(
    df,
    x="Day",
    y="Energy per Ton (kWh/ton)",
    title="🔍 Daily Energy Efficiency Trend",
    markers=True,
    template="plotly_dark" if dark_mode else "plotly_white",
    labels={"Energy per Ton (kWh/ton)": "Energy (kWh/ton)", "Day": "Day"},
)

fig.update_traces(
    line=dict(color="#2e8b57", width=3),
    marker=dict(size=8, symbol="circle")
)

fig.add_hline(
    y=threshold,
    line_dash="dash",
    line_color="red",
    annotation_text="Threshold",
    annotation_position="top left"
)

fig.update_layout(
    hovermode="x unified",
    margin=dict(l=30, r=30, t=60, b=30),
    title_font_size=20,
    plot_bgcolor="rgba(0,0,0,0)" if dark_mode else "#f9f9f9"
)

st.plotly_chart(fig, use_container_width=True)


# Export Data as CSV
st.header("📥 Export Report")

csv_buffer = io.StringIO()
df.to_csv(csv_buffer, index=False)
csv_data = csv_buffer.getvalue()

st.download_button(
    label="Download CSV Report",
    data=csv_data,
    file_name=f"plant_energy_report_{selected_date}.csv",
    mime="text/csv"
)
