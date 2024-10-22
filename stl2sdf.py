import sys
import trimesh
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QFileDialog, QMessageBox

# Function to generate Shader Park SDF code
def generate_shader_park_sdf_code(stl_file_path, scaling_factor, output_file_path):
    try:
        # Load the mesh file
        mesh = trimesh.load_mesh(stl_file_path)
        mesh.apply_scale(scaling_factor)

        # Start generating Shader Park code with the sdTriangle function
        shader_park_code = [
            """
// Function to calculate the signed distance to a triangle
function sdTriangle(p, a, b, c) {
    let ba = subtract(b, a);
    let ca = subtract(c, a);
    let pa = subtract(p, a);
    let nor = cross(ba, ca);
    return dot(nor, pa) / length(nor);
}

// Combine all triangles into a single SDF function
function sdf(pos) {
    let d = 1e10; // Start with a large initial value
            """
        ]

        # Iterate over each triangle in the mesh and add to the SDF function
        for i, face in enumerate(mesh.faces):
            vertices = mesh.vertices[face]
            p1, p2, p3 = vertices
            sdf_function = f"""
    let p1_{i} = [{p1[0]}, {p1[1]}, {p1[2]}];
    let p2_{i} = [{p2[0]}, {p2[1]}, {p2[2]}];
    let p3_{i} = [{p3[0]}, {p3[1]}, {p3[2]}];
    d = min(d, sdTriangle(pos, p1_{i}, p2_{i}, p3_{i}));
            """
            shader_park_code.append(sdf_function)

        # Close the SDF function and directly set the SDF using setSDF()
        shader_park_code.append("""
    return d;
}

function main() {
    let pos = getPosition();
    let d = sdf(pos); // Call the SDF function
    setSDF(d);  // Directly set the SDF for rendering
}
""")

        # Join the code into a single string
        sdf_code_output = "\n".join(shader_park_code)

        # Write the generated Shader Park code to the output file
        with open(output_file_path, 'w') as f:
            f.write(sdf_code_output)

        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

class SDFConverterApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('STL to Shader Park Converter')

        layout = QtWidgets.QVBoxLayout()

        # Input STL File
        self.stl_file_label = QtWidgets.QLabel('Select STL File:')
        layout.addWidget(self.stl_file_label)
        self.stl_file_path = QtWidgets.QLineEdit(self)
        layout.addWidget(self.stl_file_path)
        self.stl_file_btn = QtWidgets.QPushButton('Browse', self)
        self.stl_file_btn.clicked.connect(self.browse_stl_file)
        layout.addWidget(self.stl_file_btn)

        # Scaling Factor
        self.scale_label = QtWidgets.QLabel('Scaling Factor:')
        layout.addWidget(self.scale_label)
        self.scale_factor = QtWidgets.QDoubleSpinBox(self)
        self.scale_factor.setValue(1.0)
        layout.addWidget(self.scale_factor)

        # Output File
        self.output_file_label = QtWidgets.QLabel('Save Shader Park Code:')
        layout.addWidget(self.output_file_label)
        self.output_file_path = QtWidgets.QLineEdit(self)
        layout.addWidget(self.output_file_path)
        self.output_file_btn = QtWidgets.QPushButton('Browse', self)
        self.output_file_btn.clicked.connect(self.save_output_file)
        layout.addWidget(self.output_file_btn)

        # Convert Button
        self.convert_btn = QtWidgets.QPushButton('Generate Shader Park Code', self)
        self.convert_btn.clicked.connect(self.convert_stl_to_sdf)
        layout.addWidget(self.convert_btn)

        self.setLayout(layout)

    def browse_stl_file(self):
        stl_file, _ = QFileDialog.getOpenFileName(self, 'Select STL File', '', 'STL Files (*.stl)')
        if stl_file:
            self.stl_file_path.setText(stl_file)

    def save_output_file(self):
        output_file, _ = QFileDialog.getSaveFileName(self, 'Save Shader Park Code', '', 'JavaScript Files (*.js)')
        if output_file:
            self.output_file_path.setText(output_file)

    def convert_stl_to_sdf(self):
        stl_file = self.stl_file_path.text()
        scaling_factor = self.scale_factor.value()
        output_file = self.output_file_path.text()

        if not stl_file or not output_file:
            QMessageBox.warning(self, 'Input Error', 'Please specify the STL file and output file path.')
            return

        success = generate_shader_park_sdf_code(stl_file, scaling_factor, output_file)

        if success:
            QMessageBox.information(self, 'Success', 'Shader Park code has been generated successfully!')
        else:
            QMessageBox.critical(self, 'Error', 'Failed to generate Shader Park code.')

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = SDFConverterApp()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
