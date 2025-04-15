
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Desarrollo de Chapa Plegada", layout="centered")
st.title("📋 Calculadora de Desarrollo y Croquis de Chapa")

st.markdown("""
Sube un archivo **Excel** con los siguientes campos:
- `Tipo de tramo`: "Recto" o "Pliegue"
- `Long. exterior (mm)`
- `Ángulo (°)`: solo para pliegues
- `Dirección`: "Montana" o "Valle"
- `Espesor e (mm)`
- `Ri (mm)` (radio interior)
- `K-Factor`

La app calculará:
- Longitud neutra
- Desarrollo total
- Un croquis 2D con cotas y espesor
""")

file = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])
if file:
    df = pd.read_excel(file)
    st.subheader("Vista previa de la tabla cargada")
    st.dataframe(df)

    # Calcular longitud neutra y desarrollo
    dev_list = []
    x, y = [0], [0]
    angle = 0
    espesor = df["Espesor e (mm)"].iloc[0] if "Espesor e (mm)" in df.columns else 1.5

    for idx, row in df.iterrows():
        if row["Tipo de tramo"] == "Recto":
            L_ext = row["Long. exterior (mm)"]
            L_neutro = L_ext - espesor / 2
            dev_list.append(L_neutro)
            dx = L_neutro * np.cos(np.radians(angle))
            dy = L_neutro * np.sin(np.radians(angle))
            x.append(x[-1] + dx)
            y.append(y[-1] + dy)
        elif row["Tipo de tramo"] == "Pliegue":
            Ri = row["Ri (mm)"]
            K = row["K-Factor"]
            theta = row["Ángulo (°)"]
            Rn = Ri + K * espesor
            desarrollo = theta * Rn * np.pi / 180
            dev_list.append(desarrollo)
            if row["Dirección"].lower() == "montana":
                angle += theta
            else:
                angle -= theta

    df["Desarrollo (mm)"] = dev_list
    total = sum(dev_list)
    st.subheader(f"Desarrollo total: {total:.2f} mm")

    # Mostrar croquis
    st.subheader("Croquis de la pieza plegada")
    fig, ax = plt.subplots(figsize=(8,6))
    x = np.array(x)
    y = np.array(y)
    dx = np.gradient(x)
    dy = np.gradient(y)
    length = np.hypot(dx, dy)
    nx = -dy / length
    ny = dx / length
    x_out = x + espesor / 2 * nx
    y_out = y + espesor / 2 * ny
    x_in = x - espesor / 2 * nx
    y_in = y - espesor / 2 * ny
    ax.plot(x_out, y_out, color="black")
    ax.plot(x_in, y_in, color="black")
    ax.fill_betweenx(y_out, x_out, x_in, color="lightgray", alpha=0.5)
    ax.plot(x, y, 'r--', label="Eje neutro")
    for i in range(len(x)-1):
        mx = (x[i] + x[i+1])/2
        my = (y[i] + y[i+1])/2
        seg_len = np.hypot(x[i+1]-x[i], y[i+1]-y[i])
        ax.text(mx, my, f"{seg_len:.1f} mm", fontsize=8, ha='center', va='center', backgroundcolor='w')
    ax.axis('equal')
    ax.grid(True)
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.set_title("Vista lateral con espesor")
    st.pyplot(fig)

    st.download_button(
        label="📹 Descargar tabla con desarrollo",
        data=df.to_excel(index=False, engine='openpyxl'),
        file_name="Desarrollo_Pieza_Resultante.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
