import numpy as np
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class DropSimulationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Drop Simulation")
        self.root.geometry("600x700")

        tk.Label(root, text="To automatically generate all drop orientations, three files are required:\n"
                            "1. System model\n2. System initial conditions\n3. Drop orientations\n"
                            "Units: length in mm, time in ms, mass in g", justify="left").pack(pady=10)

        self.system_model_path = tk.StringVar()
        self.init_conditions_path = tk.StringVar()
        self.drop_orientations_path = tk.StringVar()

        tk.Label(root, text="System Model File:").pack()
        tk.Entry(root, textvariable=self.system_model_path, width=50).pack()
        frame = tk.Frame(root)
        tk.Button(frame, text="Browse", command=self.browse_system_model).pack(side=tk.LEFT)
        tk.Button(frame, text="Visualize System Model", command=self.visualize_system_model).pack(side=tk.LEFT, padx=5)
        frame.pack()

        tk.Label(root, text="System Initial Conditions File:").pack()
        tk.Entry(root, textvariable=self.init_conditions_path, width=50).pack()
        tk.Button(root, text="Browse", command=self.browse_init_conditions).pack()

        tk.Label(root, text="Drop Orientations Input:").pack()
        self.drop_input_method = tk.StringVar(value="file")
        tk.Radiobutton(root, text="Load from file", variable=self.drop_input_method, value="file", command=self.toggle_drop_input).pack()
        tk.Radiobutton(root, text="Manual input", variable=self.drop_input_method, value="manual", command=self.toggle_drop_input).pack()

        self.drop_file_frame = tk.Frame(root)
        tk.Entry(self.drop_file_frame, textvariable=self.drop_orientations_path, width=50).pack(side=tk.LEFT)
        tk.Button(self.drop_file_frame, text="Browse", command=self.browse_drop_orientations).pack(side=tk.LEFT)
        self.drop_file_frame.pack()

        self.drop_manual_frame = tk.Frame(root)
        self.drop_manual_text = scrolledtext.ScrolledText(self.drop_manual_frame, width=50, height=5)
        self.drop_manual_text.pack()
        self.drop_manual_frame.pack()
        self.drop_manual_frame.pack_forget()

        tk.Label(root, text="Simulation Log:").pack(pady=5)
        self.log = scrolledtext.ScrolledText(root, width=70, height=15)
        self.log.pack()

        tk.Button(root, text="Run Simulation", command=self.run_simulation).pack(pady=20)

    def browse_system_model(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if path:
            self.system_model_path.set(path)

    def browse_init_conditions(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if path:
            self.init_conditions_path.set(path)

    def browse_drop_orientations(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if path:
            self.drop_orientations_path.set(path)

    def toggle_drop_input(self):
        if self.drop_input_method.get() == "file":
            self.drop_file_frame.pack()
            self.drop_manual_frame.pack_forget()
        else:
            self.drop_file_frame.pack_forget()
            self.drop_manual_frame.pack()

    def log_message(self, message):
        self.log.insert(tk.END, message + "\n")
        self.log.see(tk.END)

    def read_system_model(self, file_path):
        with open(file_path, "r") as f:
            lines = f.readlines()

        system_model = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("*node"):
                i += 1
                while i < len(lines):
                    next_line = lines[i].strip()
                    if next_line.startswith("**"):
                        i += 1
                        continue
                    if next_line.startswith("*") and not next_line.startswith("*node"):
                        break
                    if next_line and next_line[0].isdigit():
                        cleaned_line = next_line.replace(",", " ")
                        parts = cleaned_line.split()
                        if len(parts) == 4:
                            try:
                                values = [float(parts[0])] + [float(x) for x in parts[1:]]
                                if all(c.isdigit() or c in "., -" for c in next_line):
                                    system_model.append(values)
                                else:
                                    self.log_message(f"Skipping invalid line (unexpected characters): {next_line}")
                            except ValueError:
                                self.log_message(f"Skipping invalid line (non-numeric): {next_line}")
                        else:
                            self.log_message(f"Skipping invalid line (wrong number of values): {next_line}")
                    i += 1
            else:
                i += 1

        return np.array(system_model)

    def visualize_system_model(self):
        try:
            system_model_path = self.system_model_path.get()
            if not system_model_path:
                messagebox.showerror("Error", "Please select a system model file first!")
                return

            system_model = self.read_system_model(system_model_path)
            if system_model.size == 0:
                messagebox.showerror("Error", "No valid data found in system model file!")
                return

            coords = system_model[:, 1:4]
            fig = plt.figure(figsize=(8, 8))
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(coords[:, 0], coords[:, 1], coords[:, 2], c='b', marker='o')
            ax.set_xlabel('X (mm)')
            ax.set_ylabel('Y (mm)')
            ax.set_zlabel('Z (mm)')
            ax.set_title('System Model 3D Visualization')
            plt.show()

            self.log_message("System model visualization displayed successfully.")

        except Exception as e:
            self.log_message(f"Error visualizing system model: {str(e)}")
            messagebox.showerror("Error", f"Failed to visualize system model: {str(e)}")

    def rotation_matrix(self, xn, yn, zn):
        xn, yn, zn = np.radians(xn), np.radians(yn), np.radians(zn)
        Rx = np.array([[1, 0, 0], [0, np.cos(xn), -np.sin(xn)], [0, np.sin(xn), np.cos(xn)]])
        Ry = np.array([[np.cos(yn), 0, np.sin(yn)], [0, 1, 0], [-np.sin(yn), 0, np.cos(yn)]])
        Rz = np.array([[np.cos(zn), -np.sin(zn), 0], [np.sin(zn), np.cos(zn), 0], [0, 0, 1]])
        return Rz @ Ry @ Rx

    def visualize_all_grounds(self, system_model, results, ground_width, drop_orientations):
        coords = system_model[:, 1:4].copy()
        num_orientations = len(results)
        cols = int(np.ceil(np.sqrt(num_orientations)))
        rows = int(np.ceil(num_orientations / cols))

        fig = plt.figure(figsize=(5 * cols, 5 * rows))
        current_coords = coords.copy()

        for i, (result, orientation) in enumerate(zip(results, drop_orientations[:, 1:4])):
            p_new = result["p_new"]
            speed = result["speed"]
            xn, yn, zn = -orientation  # Opposite of drop orientation
            R = self.rotation_matrix(xn, yn, zn)
            normal = R @ np.array([0, 0, 1])  # Ground normal

            # Debugging: Log normal vector
            self.log_message(f"Orientation {i}: Normal = {normal}")

            ax = fig.add_subplot(rows, cols, i + 1, projection='3d')
            ax.scatter(current_coords[:, 0], current_coords[:, 1], current_coords[:, 2], c='b', marker='o', label='System Model')

            # Generate circle on plane perpendicular to normal
            radius = ground_width / 2
            theta = np.linspace(0, 2 * np.pi, 100)
            u = np.cross(normal, [1, 0, 0]) if not np.allclose(normal, [1, 0, 0]) else np.cross(normal, [0, 1, 0])
            u = u / (np.linalg.norm(u) + 1e-10)  # Avoid division by zero
            v = np.cross(normal, u)
            v = v / (np.linalg.norm(v) + 1e-10)
            x_circle = p_new[0] + radius * (np.cos(theta) * u[0] + np.sin(theta) * v[0])
            y_circle = p_new[1] + radius * (np.cos(theta) * u[1] + np.sin(theta) * v[1])
            z_circle = p_new[2] + radius * (np.cos(theta) * u[2] + np.sin(theta) * v[2])
            ax.plot(x_circle, y_circle, z_circle, c='gray', label='Ground')

            # Velocity arrow
            ax.quiver(p_new[0], p_new[1], p_new[2], speed[0], speed[1], speed[2], color='r', label='Velocity')

            ax.set_xlabel('X (mm)')
            ax.set_ylabel('Y (mm)')
            ax.set_zlabel('Z (mm)')
            ax.set_title(f"Orientation {i}")
            ax.legend()

            # Update coordinates
            if i < len(results) - 1:
                next_displacement = results[i + 1]["p_new"] - p_new
                current_coords += next_displacement

        plt.tight_layout()
        plt.show()

    def run_simulation(self):
        self.log.delete(1.0, tk.END)
        try:
            # 1. Load system model
            system_model_path = self.system_model_path.get()
            if not system_model_path:
                raise ValueError("System model file not specified")
            system_model = self.read_system_model(system_model_path)
            if system_model.size == 0:
                raise ValueError("No valid data found in system model file")
            self.log_message(f"System model read from file (coordinates in mm):\nFirst 5 rows:\n{system_model[:5]}\nTotal points: {len(system_model)}")

            # 2. Calculate dimensions
            coords = system_model[:, 1:4]
            L = np.max(coords[:, 0]) - np.min(coords[:, 0])
            W = np.max(coords[:, 1]) - np.min(coords[:, 1])
            H = np.max(coords[:, 2]) - np.min(coords[:, 2])
            self.log_message(f"Object spatial dimensions: L={L:.2f} mm, W={W:.2f} mm, H={H:.2f} mm")

            # 3. Calculate center point
            o = np.mean(coords, axis=0)
            self.log_message(f"Center point o: ({o[0]:.2f}, {o[1]:.2f}, {o[2]:.2f}) mm")

            # 4. Define circular ground
            ground_width = max(L, W, H)
            p = o.copy()
            self.log_message(f"Circular ground diameter: {ground_width:.2f} mm, Initial center p: ({p[0]:.2f}, {p[1]:.2f}, {p[2]:.2f}) mm")

            # 5. Load initial conditions and process drop_height
            init_file = self.init_conditions_path.get()
            if not init_file:
                raise ValueError("System initial conditions file not specified")
            with open(init_file, "r") as f:
                init_content = f.readlines()

            drop_height = None
            gravity = 9.8e-3
            for line in init_content:
                if "drop_height" in line.lower():
                    try:
                        drop_height = float(line.split("=")[1].strip())
                        self.log_message(f"Found drop_height = {drop_height} mm in {init_file}")
                        if messagebox.askyesno("Confirm", f"Is drop_height = {drop_height} mm correct?"):
                            break
                        else:
                            drop_height = None
                    except (IndexError, ValueError):
                        self.log_message(f"Invalid drop_height format in line: {line.strip()}")
            if drop_height is None:
                drop_height = float(tk.simpledialog.askstring("Input", "No valid drop_height found. Please enter drop_height (in mm):"))
            initial_velocity = np.sqrt(2 * drop_height * gravity)
            self.log_message(f"Calculated initial_velocity = {initial_velocity:.2f} mm/ms based on drop_height = {drop_height} mm and gravity = {gravity} mm/ms^2")

            # 6. Load drop orientations
            if self.drop_input_method.get() == "file":
                drop_file = self.drop_orientations_path.get()
                if not drop_file:
                    raise ValueError("Drop orientations file not specified")
                with open(drop_file, "r") as f:
                    lines = f.readlines()
                drop_orientations = []
                for line in lines:
                    stripped_line = line.strip()
                    if stripped_line and stripped_line[0].isdigit():
                        values = list(map(float, stripped_line.split()))
                        if len(values) == 4:
                            drop_orientations.append(values)
            else:
                manual_input = self.drop_manual_text.get(1.0, tk.END).strip()
                if not manual_input:
                    raise ValueError("Manual drop orientations input is empty")
                drop_orientations = []
                for line in manual_input.split("\n"):
                    values = list(map(float, line.split()))
                    if len(values) == 4:
                        drop_orientations.append(values)
            drop_orientations = np.array(drop_orientations)
            if drop_orientations.shape[0] > 25 or drop_orientations.shape[1] != 4 or not np.all((drop_orientations[:, 0] >= 0) & (drop_orientations[:, 0] <= 25) & (drop_orientations[:, 0] == drop_orientations[:, 0].astype(int))) or not np.all((drop_orientations[:, 1:4] >= -1) & (drop_orientations[:, 1:4] <= 1)):
                raise ValueError("Invalid drop_orientations format")
            self.log_message(f"Valid drop orientations array:\n{drop_orientations}")

            # 7. Process each orientation
            results = []
            angles = drop_orientations[:, 1:4]
            for i, angle in enumerate(angles):
                xn, yn, zn = angle
                R = self.rotation_matrix(xn, yn, zn)
                vn = R @ np.array([0, 0, 1])

                relative_coords = coords - p
                distances = np.dot(relative_coords, vn)
                positive_distances = distances[distances > 0]
                d = np.max(positive_distances) if len(positive_distances) > 0 else 0
                move_distance = d + 0.0001
                displacement = move_distance * vn

                p_new = p + displacement
                speed = np.array([initial_velocity * xn, initial_velocity * yn, initial_velocity * zn])

                base_name = os.path.splitext(init_file)[0]
                file_name = f"{base_name}_ori_{int(drop_orientations[i, 0])}_{xn:.2f}_{yn:.2f}_{zn:.2f}.txt"
                with open(file_name, "w") as f:
                    f.write("".join(init_content))
                    f.write(f"\n*parameters\nVx={speed[0]:.2f};\nVy={speed[1]:.2f};\nVz={speed[2]:.2f}")
                    f.write(f"\n*node\n{90000000 + int(drop_orientations[i, 0])}, {p_new[0]:.6f}, {p_new[1]:.6f}, {p_new[2]:.6f}")
                    f.write(f"\n*orientations, name=local_coord_ori_{int(drop_orientations[i, 0])}\n{p_new[0]:.6f}, {p_new[1]:.6f}, {p_new[2]:.6f}, {-xn:.6f}, {-yn:.6f}, {-zn:.6f}")
                    f.write(f"\n*SURFACE, TYPE=analytical_surface_type, NAME=ground_{int(drop_orientations[i, 0])}, FILLET RADIUS={ground_width:.2f}")
                    f.write(f"\n*RIGID BODY, NAME=ground_{int(drop_orientations[i, 0])}, REFERENCE NODE={90000000 + int(drop_orientations[i, 0])}, SURFACE=ground_{int(drop_orientations[i, 0])}")

                results.append({"angle": (xn, yn, zn), "p_new": p_new, "speed": speed})
                p = p_new
                coords = coords + displacement

            self.log_message(f"Generated {len(angles)} drop orientation files based on {init_file}")
            messagebox.showinfo("Success", "Simulation completed successfully!")

            self.visualize_all_grounds(system_model, results, ground_width, drop_orientations)
            self.log_message("Visualized all grounds and system model positions.")

        except Exception as e:
            self.log_message(f"Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DropSimulationGUI(root)
    root.mainloop()