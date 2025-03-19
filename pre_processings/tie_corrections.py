import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

class TieCorrectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tie Correction Tool")
        self.root.geometry("600x700")

        tk.Label(root, text="Tie Correction Tool\nLoad a system model file to check *tie entries", justify="left").pack(pady=10)

        self.file_path = tk.StringVar()
        tk.Label(root, text="System Model File:").pack()
        tk.Entry(root, textvariable=self.file_path, width=50).pack()
        tk.Button(root, text="Browse", command=self.browse_file).pack(pady=5)

        tk.Button(root, text="Run Check", command=self.run_check).pack(pady=10)

        tk.Label(root, text="Results:").pack()
        self.log = scrolledtext.ScrolledText(root, width=70, height=30)
        self.log.pack()

    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if path:
            self.file_path.set(path)

    def log_message(self, message):
        self.log.insert(tk.END, message + "\n")
        self.log.see(tk.END)

    def parse_tie_entries(self, file_path):
        try:
            with open(file_path, "r") as f:
                lines = [line.strip() for line in f.readlines()]
        except Exception as e:
            self.log_message(f"Error reading file: {str(e)}")
            return None

        p = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith("*tie,"):
                i += 1
                while i < len(lines) and not lines[i]:
                    i += 1
                if i >= len(lines):
                    break

                next_line = lines[i]
                if next_line.startswith("**"):
                    i += 1
                    continue
                elif next_line.startswith("*") and not next_line.startswith("**"):
                    self.log_message(f"Error: Unexpected keyword '{next_line}' after '*tie,' at line {i+1}")
                    return None
                else:
                    # 分割 a 和 b，按第一个空格或逗号
                    if " " in next_line:
                        separator = " "
                    elif "," in next_line:
                        separator = ","
                    else:
                        self.log_message(f"Error: No space or comma found in line '{next_line}' at line {i+1}")
                        return None

                    parts = next_line.split(separator, 1)  # 分割成两部分
                    a = parts[0].strip()
                    b = parts[1].strip()  # 逗号或空格后的剩余内容
                    p.append([a, b])
                    i += 1
            else:
                i += 1

        return p

    def check_duplicates_and_swaps(self, p):
        if not p:
            return

        self.log_message(f"Parsed *tie entries:\n{p}\n")

        # 检查重复
        seen = set()
        duplicates = []
        for i, (a, b) in enumerate(p):
            entry = (a, b)
            if entry in seen:
                duplicates.append((i, a, b))
            seen.add(entry)

        if duplicates:
            self.log_message("Found duplicate entries:")
            for idx, a, b in duplicates:
                self.log_message(f"Line {idx}: {a}, {b}")
        else:
            self.log_message("No duplicate entries found.")

        # 检查交换
        swaps = []
        for i, (a1, b1) in enumerate(p):
            for j, (a2, b2) in enumerate(p):
                if i < j and a1 == b2 and b1 == a2:
                    swaps.append((i, j, a1, b1))

        if swaps:
            self.log_message("Found swap phenomena:")
            for i, j, a, b in swaps:
                self.log_message(f"Line {i} ({a}, {b}) swaps with Line {j} ({b}, {a})")
        else:
            self.log_message("No swap phenomena found.")

    def run_check(self):
        self.log.delete(1.0, tk.END)
        file_path = self.file_path.get()
        if not file_path:
            messagebox.showerror("Error", "Please select a system model file!")
            return

        self.log_message(f"Loading file: {file_path}")
        p = self.parse_tie_entries(file_path)
        if p is None:
            messagebox.showerror("Error", "Failed to parse *tie entries. Check log for details.")
            return

        self.log_message(f"Found {len(p)} *tie entries.")
        self.check_duplicates_and_swaps(p)
        messagebox.showinfo("Success", "Check completed! See results in the log.")



if __name__ == "__main__":
    root = tk.Tk()
    app = TieCorrectionApp(root)
    root.mainloop()