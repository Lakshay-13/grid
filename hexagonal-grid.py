import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import io
import base64
from matplotlib.colors import to_rgba
import colorsys

def generate_color_palette(base_color, n_colors):
    base_rgb = to_rgba(base_color)[:3]
    base_hsv = colorsys.rgb_to_hsv(*base_rgb)
    
    colors = []
    for i in range(n_colors):
        saturation = max(0.3, base_hsv[1] - (i * 0.1))
        value = min(1.0, base_hsv[2] + (i * 0.1))
        rgb = colorsys.hsv_to_rgb(base_hsv[0], saturation, value)
        colors.append(rgb)
    return colors

def create_triangle_pattern(pattern_type, nx, ny):
    if pattern_type == "Solid":
        return np.zeros((ny, nx))
    elif pattern_type == "Checkered":
        return np.fromfunction(lambda i, j: (i + j) % 2, (ny, nx))
    elif pattern_type == "Gradient":
        return np.fromfunction(lambda i, j: (i + j) / (ny + nx), (ny, nx))
    elif pattern_type == "Radial":
        center_y, center_x = ny/2, nx/2
        return np.fromfunction(
            lambda i, j: np.sqrt(((i-center_y)/ny)**2 + ((j-center_x)/nx)**2),
            (ny, nx)
        )
    return np.zeros((ny, nx))

def create_triangle_grid(edge_length, width, height, pattern_type, base_color, border_color, border_width, background_alpha, fill_alpha):
    # Calculate triangle height
    triangle_height = edge_length * np.sin(np.pi/3)
    
    # Calculate number of triangles that can fit
    nx = int(width / (edge_length / 2))
    ny = int(height / triangle_height)
    
    # Create figure with transparency
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111)
    
    # Set transparent background
    fig.patch.set_alpha(background_alpha)
    ax.patch.set_alpha(background_alpha)
    
    # Create pattern matrix
    pattern = create_triangle_pattern(pattern_type, nx, ny)
    colors = generate_color_palette(base_color, 5)
    
    # Generate triangles
    for row in range(ny):
        for col in range(nx):
            # Calculate base point of triangle
            x = col * (edge_length / 2)
            y = row * triangle_height
            
            # Alternate triangle orientation
            points = []
            if (col + row) % 2 == 0:
                points = [
                    [x, y],
                    [x + edge_length, y],
                    [x + edge_length/2, y + triangle_height]
                ]
            else:
                points = [
                    [x, y + triangle_height],
                    [x + edge_length, y + triangle_height],
                    [x + edge_length/2, y]
                ]
            
            # Determine color based on pattern
            if pattern_type == "Solid":
                face_color = base_color
            else:
                color_idx = int(pattern[row, col] * 4)
                face_color = colors[min(color_idx, 4)]
            
            triangle = Polygon(
                points,
                facecolor=face_color if fill_alpha > 0 else 'none',
                edgecolor=border_color,
                linewidth=border_width,
                alpha=fill_alpha if fill_alpha > 0 else 1
            )
            ax.add_patch(triangle)
    
    ax.set_aspect('equal')
    ax.set_xlim(-edge_length, width + edge_length)
    ax.set_ylim(-edge_length, height + edge_length)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')
    
    return fig

def get_image_download_link(fig, filename, text, dpi):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight', transparent=True)
    buf.seek(0)
    b64 = base64.b64encode(buf.getvalue()).decode()
    href = f'<a href="data:image/png;base64,{b64}" download="{filename}">{text}</a>'
    return href

# Streamlit app
st.title("Triangular Tessellation Pattern Generator")

# Sidebar controls
st.sidebar.header("Pattern Settings")

# Basic settings
edge_length = st.sidebar.slider("Triangle Edge Length", 
                              min_value=0.1, 
                              max_value=2.0, 
                              value=1.0,
                              step=0.1)

width = st.sidebar.slider("Pattern Width",
                         min_value=5,
                         max_value=50,
                         value=20)

height = st.sidebar.slider("Pattern Height",
                          min_value=5,
                          max_value=50,
                          value=20)

# Visual settings
st.sidebar.header("Visual Settings")

pattern_type = st.sidebar.selectbox(
    "Pattern Type",
    ["Solid", "Checkered", "Gradient", "Radial"]
)

fill_alpha = st.sidebar.slider(
    "Fill Transparency",
    min_value=0.0,
    max_value=1.0,
    value=0.0,  # Default to transparent fill
    step=0.1,
    help="0 = Transparent fill, 1 = Solid fill"
)

base_color = st.sidebar.color_picker(
    "Fill Color",
    "#1f77b4"
) if fill_alpha > 0 else "#1f77b4"

border_color = st.sidebar.color_picker(
    "Border Color",
    "#ffffff"  # Changed default to white
)

border_width = st.sidebar.slider(
    "Border Width",
    min_value=0.0,
    max_value=2.0,
    value=0.5,
    step=0.1
)

background_alpha = st.sidebar.slider(
    "Background Transparency",
    min_value=0.0,
    max_value=1.0,
    value=0.0,
    step=0.1,
    help="0 = Fully transparent, 1 = Fully opaque"
)

# Generate and display the grid
fig = create_triangle_grid(
    edge_length,
    width,
    height,
    pattern_type,
    base_color,
    border_color,
    border_width,
    background_alpha,
    fill_alpha
)
st.pyplot(fig)

# Download options
st.sidebar.header("Export Options")
filename = st.sidebar.text_input("Filename", "triangular_tessellation.png")

# Add DPI selector
export_dpi = st.sidebar.slider(
    "Export DPI",
    min_value=300,
    max_value=3000,
    value=300,
    step=100,
    help="Higher DPI = Higher resolution but larger file size"
)

if st.sidebar.button("Generate Download Link"):
    st.sidebar.markdown(
        get_image_download_link(fig, filename, f"Click here to download your pattern (DPI: {export_dpi})", export_dpi),
        unsafe_allow_html=True
    )

# Pattern information
st.sidebar.markdown("---")
st.sidebar.markdown("### Pattern Information")
triangle_height = edge_length * np.sin(np.pi/3)
nx = int(width / (edge_length / 2))
ny = int(height / triangle_height)
st.sidebar.write(f"Approximate number of triangles: {nx * ny}")
st.sidebar.write(f"Pattern dimensions: {width:.1f} x {height:.1f} units")