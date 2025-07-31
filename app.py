import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
import io

# Title and Description
st.title("🌿 Plant Energy Usage Estimator")
st.markdown("""
Monitor and improve your plant's energy efficiency by tracking energy used and steel output.  
This tool calculates **energy per ton** and gives alerts when usage exceeds a threshold.
""")

# Threshold
threshold = st.slider("⚙️ Set Energy Efficiency Threshold (kWh per ton)", 
                      min_value=100, max_value=1000, value=600, step=50)


st.header("📂 Upload Data (Optional)")

uploaded_file = st.file_uploader("Upload a CSV file with Energy and Steel data", type=["csv"])

st.markdown("""
📝 **CSV format expected**:  
Upload a file with two columns named:
- `Energy Used (kWh)`
- `Steel Produced (tons)`
""")


# Input Form
st.header("📂 Upload Data (Optional)")
uploaded_file = st.file_uploader("Upload a CSV file with Energy and Steel data", type=["csv"])

use_random = st.checkbox("🎲 Generate random sample data")
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
    "Day": list(range(1, days+1)),
    "Energy Used (kWh)": energy_list,
    "Steel Produced (tons)": steel_list,
    "Energy per Ton (kWh/ton)": efficiency_list,
    "Alert": alerts,
    "Efficiency Tag": efficiency_tags
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

if avg_efficiency > threshold:
    st.warning("⚠️ Weekly efficiency is high. Investigate for energy waste.")
else:
    st.success("✅ Weekly efficiency is within limit.")

# Plotting
st.header("📈 Efficiency Trend")
fig, ax = plt.subplots()
ax.plot(df["Day"], df["Energy per Ton (kWh/ton)"], marker='o')
ax.axhline(y=threshold, color='r', linestyle='--', label='threshold')
ax.set_xlabel("Day")
ax.set_ylabel("kWh per ton")
ax.set_title("Daily Energy Efficiency")
ax.legend()
st.pyplot(fig)

# Export Data as CSV
st.header("📥 Export Report")

csv_buffer = io.StringIO()
df.to_csv(csv_buffer, index=False)
csv_data = csv_buffer.getvalue()

st.download_button(
    label="Download CSV Report",
    data=csv_data,
    file_name="plant_energy_report.csv",
    mime="text/csv"
)
