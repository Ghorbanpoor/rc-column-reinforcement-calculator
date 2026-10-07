import streamlit as st

st.set_page_config(
    page_title="RC Column Reinforcement Calculator",
    page_icon="🏗️",
    layout="centered"
)

st.title("🏗️ RC Column Reinforcement Calculator")
st.subheader("Equivalent Area Balance Method")

st.write(
    "This preliminary calculator estimates the longitudinal reinforcement "
    "area of a reinforced-concrete column using the proposed "
    "Concrete–Steel Equivalent Area Balance Method."
)

st.divider()

# ---------------------------------------------------------
# General inputs
# ---------------------------------------------------------

st.header("1. General Building Information")

n_stories = st.number_input(
    "Number of stories above the designed column",
    min_value=1,
    max_value=100,
    value=5,
    step=1
)

column_height = st.number_input(
    "Story height of the designed column (m)",
    min_value=2.0,
    max_value=20.0,
    value=3.0,
    step=0.1
)

st.divider()

# ---------------------------------------------------------
# Column dimensions
# ---------------------------------------------------------

st.header("2. Column Dimensions")

col1, col2 = st.columns(2)

with col1:
    column_width = st.number_input(
        "Column width (cm)",
        min_value=10.0,
        max_value=200.0,
        value=40.0,
        step=5.0
    )

with col2:
    column_depth = st.number_input(
        "Column depth (cm)",
        min_value=10.0,
        max_value=200.0,
        value=40.0,
        step=5.0
    )

column_area_m2 = (column_width / 100.0) * (column_depth / 100.0)

st.info(
    f"Gross concrete column area = {column_area_m2:.4f} m²"
)

st.divider()

# ---------------------------------------------------------
# Equivalent steel coefficient
# ---------------------------------------------------------

st.header("3. Equivalent Steel Coefficient")

steel_factor = st.number_input(
    "Equivalent-area coefficient",
    min_value=1.0,
    max_value=500.0,
    value=100.0,
    step=1.0
)

st.caption(
    "The proposed preliminary method uses 100 as the equivalent "
    "steel-to-concrete area coefficient."
)

st.divider()

# ---------------------------------------------------------
# Amplification factor
# ---------------------------------------------------------

st.header("4. Load Amplification Factor")

amplification_factor = st.number_input(
    "Amplification factor (> 1)",
    min_value=1.0,
    max_value=10.0,
    value=1.5,
    step=0.1
)

st.caption(
    "This factor is used in the proposed preliminary method to "
    "approximately represent additional loads and seismic effects."
)

st.divider()

# ---------------------------------------------------------
# Floor data
# ---------------------------------------------------------

st.header("5. Tributary Area and Slab Thickness")

st.write(
    "Enter the tributary area and slab thickness associated with "
    "the column for each floor."
)

floor_data = []

for i in range(n_stories):

    st.markdown(f"### Floor {i + 1}")

    c1, c2 = st.columns(2)

    with c1:
        tributary_area = st.number_input(
            f"Tributary area – Floor {i + 1} (m²)",
            min_value=0.1,
            max_value=10000.0,
            value=20.0,
            step=1.0,
            key=f"area_{i}"
        )

    with c2:
        slab_thickness = st.number_input(
            f"Slab thickness – Floor {i + 1} (cm)",
            min_value=5.0,
            max_value=100.0,
            value=20.0,
            step=1.0,
            key=f"thickness_{i}"
        )

    floor_data.append({
        "area": tributary_area,
        "thickness": slab_thickness / 100.0
    })

st.divider()

# ---------------------------------------------------------
# Calculation
# ---------------------------------------------------------

if st.button(
    "Calculate Column Reinforcement",
    type="primary",
    use_container_width=True
):

    # Total tributary slab volume
    total_slab_volume = 0.0

    for floor in floor_data:
        volume = floor["area"] * floor["thickness"]
        total_slab_volume += volume

    # Amplified representative volume
    effective_volume = (
        total_slab_volume * amplification_factor
    )

    # Volume of concrete column
    column_volume = (
        column_area_m2 * column_height
    )

    # -----------------------------------------------------
    # Proposed equivalent-volume balance
    #
    # effective_volume =
    # column_volume +
    # steel_factor * As * column_height
    #
    # Therefore:
    #
    # As =
    # (effective_volume - column_volume)
    # / (steel_factor * column_height)
    # -----------------------------------------------------

    required_steel_area = (
        effective_volume - column_volume
    ) / (
        steel_factor * column_height
    )

    # -----------------------------------------------------
    # Results
    # -----------------------------------------------------

    st.divider()

    st.header("📊 Results")

    if required_steel_area < 0:

        st.warning(
            "The calculated equivalent steel area is negative. "
            "The assumed concrete column volume is already greater "
            "than the amplified tributary volume."
        )

        required_steel_area = 0.0

    steel_area_cm2 = required_steel_area * 10000

    reinforcement_ratio = (
        steel_area_cm2 /
        (column_width * column_depth)
    ) * 100

    # Results cards
    r1, r2 = st.columns(2)

    with r1:
        st.metric(
            "Required Steel Area",
            f"{steel_area_cm2:.2f} cm²"
        )

    with r2:
        st.metric(
            "Reinforcement Ratio",
            f"{reinforcement_ratio:.2f}%"
        )

    st.divider()

    st.write("### Calculation Summary")

    st.write(
        f"**Total tributary slab volume:** "
        f"{total_slab_volume:.3f} m³"
    )

    st.write(
        f"**Amplified effective volume:** "
        f"{effective_volume:.3f} m³"
    )

    st.write(
        f"**Column concrete volume:** "
        f"{column_volume:.3f} m³"
    )

    st.write(
        f"**Equivalent steel coefficient:** "
        f"{steel_factor:.1f}"
    )

    st.write(
        f"**Required longitudinal reinforcement area:** "
        f"{steel_area_cm2:.2f} cm²"
    )

    st.write(
        f"**Approximate reinforcement ratio:** "
        f"{reinforcement_ratio:.2f}%"
    )

    # -----------------------------------------------------
    # Basic reinforcement suggestion
    # -----------------------------------------------------

    st.divider()

    st.header("🔩 Preliminary Rebar Suggestion")

    common_bars = [12, 14, 16, 18, 20, 22, 25, 28, 32]

    best_option = None

    for diameter in common_bars:

        bar_area = 3.14159265359 * diameter**2 / 4

        for number_of_bars in range(4, 41):

            provided_area = (
                number_of_bars * bar_area
            )

            if provided_area >= steel_area_cm2:

                best_option = (
                    number_of_bars,
                    diameter,
                    provided_area
                )

                break

        if best_option:
            break

    if best_option:

        n_bars, diameter, provided_area = best_option

        st.success(
            f"Preliminary option: "
            f"**{n_bars} × Ø{diameter} mm**  "
            f"→ Provided steel area = "
            f"**{provided_area:.2f} cm²**"
        )

    st.warning(
        "This is a preliminary conceptual calculation and is NOT "
        "a code-compliant structural design. Final column reinforcement "
        "must be checked for axial load, bending, P-M interaction, "
        "slenderness, second-order effects, seismic load combinations, "
        "minimum/maximum reinforcement ratios, confinement and "
        "applicable building codes."
    )