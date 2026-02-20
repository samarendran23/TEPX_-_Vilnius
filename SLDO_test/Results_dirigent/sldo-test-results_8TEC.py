import os
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# USER SETTINGS
# -----------------------------
base_folders = [
    "sldo_vi_curves_TEC1",
    "sldo_vi_curves_TEC2",
    "sldo_vi_curves_TEC3",
    "sldo_vi_curves_TEC4",
    "sldo_vi_curves_TEC5",
    "sldo_vi_curves_TEC6",
    "sldo_vi_curves_TEC7",
    "sldo_vi_curves_TEC8",
]

module_files = [
    "Module1_full.csv",
    "Module2_full.csv",
    "Module3_full.csv",
    "Module4_full.csv",
    "Module5_full.csv",
    "Module6_full.csv",
    "Module7_full.csv",
    "Module8_full.csv",
]

# Parameters to overlay across all 8 CB positions
params_to_plot = [
    "Voltage (V)",
    "VIN",
    "VOFS",
    "VDDD_ROC0",
    "VDDA_ROC0",
    "VDDD_ROC1",
    "VDDA_ROC1",
    "VDDD_ROC2",
    "VDDA_ROC2",
    "VDDD_ROC3",
    "VDDA_ROC3",
]

# Special parameter
vin_expected_col = "VIN expected (2x2 HDI V3)"

# X axis
x_col = "Current (A)"

# Output
output_dir = "overlay_plots"
os.makedirs(output_dir, exist_ok=True)

# -----------------------------
# LOAD ALL MODULE DATA
# -----------------------------
all_data = []

for i in range(8):
    folder = base_folders[i]
    filename = module_files[i]
    path = os.path.join(folder, filename)

    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing file: {path}")

    df = pd.read_csv(path)

    # Sort by current (important for clean curves)
    df = df.sort_values(x_col)

    # Tag CB position
    df["CB_position"] = i + 1

    all_data.append(df)

print("Loaded all 8 modules successfully.")

# -----------------------------
# PLOT OVERLAYS FOR ALL PARAMETERS
# -----------------------------
df_cb1 = all_data[0]  # CB1 data for VIN expected

for param in params_to_plot:

    plt.figure(figsize=(10, 6))

    # Plot each CB position
    for df in all_data:
        cb_pos = df["CB_position"].iloc[0]

        if param not in df.columns:
            print(f"WARNING: Column '{param}' not found for CB position {cb_pos}")
            continue

        plt.plot(
            df[x_col],
            df[param],
            marker="o",
            linewidth=2,
            markersize=4,
            label=f"CB position {cb_pos}"
        )

    # Plot VIN expected as reference in every plot
    if vin_expected_col in df_cb1.columns:
        plt.plot(
            df_cb1[x_col],
            df_cb1[vin_expected_col],
            linestyle="--",
            linewidth=3,
            label="VIN expected (2x2 HDI V3)"
        )

    plt.xlabel("Current (A)")
    plt.ylabel(param)
    plt.title(f"{param} vs Current (overlay of 8 positions + VIN expected)")
    plt.grid(True)
    plt.legend()
    plt.xlim(0, 10)

    safe_name = param.replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")
    outpath = os.path.join(output_dir, f"overlay_{safe_name}_vs_Current_v1.png")

    plt.tight_layout()
    plt.savefig(outpath, dpi=200)
    plt.close()

    print(f"Saved: {outpath}")

print(f"\nAll plots saved in: {output_dir}")

