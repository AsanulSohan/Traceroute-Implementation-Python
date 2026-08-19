#!/usr/bin/env python3
"""
Traceroute GUI Interface
Student: Asanul Hoque Sohan
ID: 2202038
Course: CCE 314 - Computer Networks Lab
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import subprocess
import sys
import os
from datetime import datetime
import re

class TracerouteGUI:
    """
    GUI Interface for Traceroute Implementation
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Traceroute Implementation - CCE 314")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Variables
        self.destination_var = tk.StringVar(value="google.com")
        self.max_hops_var = tk.IntVar(value=30)
        self.timeout_var = tk.DoubleVar(value=1.0)
        self.probes_var = tk.IntVar(value=3)
        self.is_running = False
        self.output_lines = []
        
        # Set icon if available
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        # Configure style
        self.setup_styles()
        
        # Create main interface
        self.create_widgets()
        
        # Bind Enter key
        self.root.bind('<Return>', lambda e: self.start_traceroute())
    
    def setup_styles(self):
        """Setup color scheme and styles"""
        self.colors = {
            'bg': '#1e1e2e',
            'fg': '#cdd6f4',
            'accent': '#89b4fa',
            'success': '#a6e3a1',
            'error': '#f38ba8',
            'warning': '#f9e2af',
            'widget_bg': '#313244',
            'widget_fg': '#cdd6f4',
            'output_bg': '#1e1e2e',
            'output_fg': '#cdd6f4'
        }
        
        self.root.configure(bg=self.colors['bg'])
    
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ===== HEADER =====
        self.create_header(main_frame)
        
        # ===== INPUT SECTION =====
        self.create_input_section(main_frame)
        
        # ===== OUTPUT SECTION =====
        self.create_output_section(main_frame)
        
        # ===== STATUS BAR =====
        self.create_status_bar()
    
    def create_header(self, parent):
        """Create header with title and student info"""
        header_frame = tk.Frame(parent, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="🌐 TRACEROUTE IMPLEMENTATION",
            font=('Arial', 18, 'bold'),
            fg=self.colors['accent'],
            bg=self.colors['bg']
        )
        title_label.pack()
        
        # Subtitle
        subtitle = tk.Label(
            header_frame,
            text="Computer Networks Lab - CCE 314",
            font=('Arial', 10),
            fg=self.colors['fg'],
            bg=self.colors['bg']
        )
        subtitle.pack()
        
        # Student info
        info_frame = tk.Frame(header_frame, bg=self.colors['bg'])
        info_frame.pack(pady=5)
        
        tk.Label(
            info_frame,
            text="Student: Asanul Hoque Sohan  |  ID: 2202038  |  Reg: 11229",
            font=('Arial', 9),
            fg=self.colors['fg'],
            bg=self.colors['bg']
        ).pack()
    
    def create_input_section(self, parent):
        """Create input controls section"""
        input_frame = tk.LabelFrame(
            parent,
            text=" Traceroute Configuration ",
            font=('Arial', 11, 'bold'),
            fg=self.colors['fg'],
            bg=self.colors['bg'],
            bd=2,
            relief=tk.RIDGE
        )
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Row 1: Destination
        row1 = tk.Frame(input_frame, bg=self.colors['bg'])
        row1.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            row1,
            text="🎯 Destination:",
            font=('Arial', 10),
            fg=self.colors['fg'],
            bg=self.colors['bg'],
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self.dest_entry = tk.Entry(
            row1,
            textvariable=self.destination_var,
            font=('Arial', 10),
            bg=self.colors['widget_bg'],
            fg=self.colors['widget_fg'],
            insertbackground=self.colors['fg'],
            relief=tk.FLAT,
            width=30
        )
        self.dest_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Quick destination buttons
        quick_buttons = [
            ("Google", "google.com"),
            ("Facebook", "facebook.com"),
            ("YouTube", "youtube.com"),
            ("8.8.8.8", "8.8.8.8"),
            ("1.1.1.1", "1.1.1.1")
        ]
        
        for text, dest in quick_buttons:
            btn = tk.Button(
                row1,
                text=text,
                font=('Arial', 8),
                bg=self.colors['widget_bg'],
                fg=self.colors['fg'],
                activebackground=self.colors['accent'],
                activeforeground='white',
                relief=tk.FLAT,
                cursor='hand2',
                command=lambda d=dest: self.set_destination(d)
            )
            btn.pack(side=tk.LEFT, padx=2)
        
        # Row 2: Parameters
        row2 = tk.Frame(input_frame, bg=self.colors['bg'])
        row2.pack(fill=tk.X, padx=10, pady=5)
        
        # Max Hops
        tk.Label(
            row2,
            text="📏 Max Hops:",
            font=('Arial', 10),
            fg=self.colors['fg'],
            bg=self.colors['bg'],
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self.hops_spinbox = tk.Spinbox(
            row2,
            from_=1,
            to=60,
            textvariable=self.max_hops_var,
            font=('Arial', 10),
            bg=self.colors['widget_bg'],
            fg=self.colors['widget_fg'],
            relief=tk.FLAT,
            width=8
        )
        self.hops_spinbox.pack(side=tk.LEFT, padx=(0, 15))
        
        # Timeout
        tk.Label(
            row2,
            text="⏱️ Timeout (s):",
            font=('Arial', 10),
            fg=self.colors['fg'],
            bg=self.colors['bg'],
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self.timeout_spinbox = tk.Spinbox(
            row2,
            from_=0.5,
            to=10.0,
            increment=0.5,
            textvariable=self.timeout_var,
            font=('Arial', 10),
            bg=self.colors['widget_bg'],
            fg=self.colors['widget_fg'],
            relief=tk.FLAT,
            width=8
        )
        self.timeout_spinbox.pack(side=tk.LEFT, padx=(0, 15))
        
        # Probes
        tk.Label(
            row2,
            text="📊 Probes:",
            font=('Arial', 10),
            fg=self.colors['fg'],
            bg=self.colors['bg'],
            width=10,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self.probes_spinbox = tk.Spinbox(
            row2,
            from_=1,
            to=10,
            textvariable=self.probes_var,
            font=('Arial', 10),
            bg=self.colors['widget_bg'],
            fg=self.colors['widget_fg'],
            relief=tk.FLAT,
            width=8
        )
        self.probes_spinbox.pack(side=tk.LEFT)
        
        # Row 3: Action Buttons
        row3 = tk.Frame(input_frame, bg=self.colors['bg'])
        row3.pack(fill=tk.X, padx=10, pady=10)
        
        # Start button
        self.start_btn = tk.Button(
            row3,
            text="▶️ Start Traceroute",
            font=('Arial', 11, 'bold'),
            bg=self.colors['success'],
            fg='black',
            activebackground='#7ecb7a',
            activeforeground='black',
            relief=tk.RAISED,
            cursor='hand2',
            padx=20,
            pady=5,
            command=self.start_traceroute
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Stop button
        self.stop_btn = tk.Button(
            row3,
            text="⏹️ Stop",
            font=('Arial', 11, 'bold'),
            bg=self.colors['error'],
            fg='white',
            activebackground='#d95b7a',
            activeforeground='white',
            relief=tk.RAISED,
            cursor='hand2',
            padx=20,
            pady=5,
            command=self.stop_traceroute,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear button
        tk.Button(
            row3,
            text="🗑️ Clear Output",
            font=('Arial', 10),
            bg=self.colors['widget_bg'],
            fg=self.colors['fg'],
            activebackground=self.colors['accent'],
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=5,
            command=self.clear_output
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Export button
        tk.Button(
            row3,
            text="💾 Export Results",
            font=('Arial', 10),
            bg=self.colors['widget_bg'],
            fg=self.colors['fg'],
            activebackground=self.colors['accent'],
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=5,
            command=self.export_results
        ).pack(side=tk.LEFT)
    
    def create_output_section(self, parent):
        """Create output display section"""
        output_frame = tk.LabelFrame(
            parent,
            text=" Traceroute Output ",
            font=('Arial', 11, 'bold'),
            fg=self.colors['fg'],
            bg=self.colors['bg'],
            bd=2,
            relief=tk.RIDGE
        )
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        # Output text area with scrollbar
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            font=('Consolas', 10),
            bg=self.colors['output_bg'],
            fg=self.colors['output_fg'],
            insertbackground=self.colors['fg'],
            wrap=tk.WORD,
            relief=tk.FLAT,
            bd=0,
            height=25
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure tags for colored output
        self.output_text.tag_configure('error', foreground=self.colors['error'])
        self.output_text.tag_configure('success', foreground=self.colors['success'])
        self.output_text.tag_configure('warning', foreground=self.colors['warning'])
        self.output_text.tag_configure('accent', foreground=self.colors['accent'])
        self.output_text.tag_configure('info', foreground='#89b4fa')
        self.output_text.tag_configure('hop', foreground='#f9e2af')
        self.output_text.tag_configure('rtt', foreground='#a6e3a1')
    
    def create_status_bar(self):
        """Create status bar at bottom"""
        status_frame = tk.Frame(self.root, bg=self.colors['widget_bg'], height=25)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(
            status_frame,
            text="✅ Ready - Enter destination and click Start",
            font=('Arial', 9),
            fg=self.colors['fg'],
            bg=self.colors['widget_bg'],
            anchor='w',
            padx=10
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Time display
        self.time_label = tk.Label(
            status_frame,
            text=datetime.now().strftime("%H:%M:%S"),
            font=('Arial', 9),
            fg=self.colors['fg'],
            bg=self.colors['widget_bg'],
            anchor='e',
            padx=10
        )
        self.time_label.pack(side=tk.RIGHT)
        
        # Update time every second
        self.update_time()
    
    def update_time(self):
        """Update status bar time"""
        self.time_label.config(text=datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self.update_time)
    
    def set_destination(self, dest):
        """Set destination from quick buttons"""
        self.destination_var.set(dest)
        self.dest_entry.focus()
    
    def start_traceroute(self):
        """Start traceroute in a separate thread"""
        if self.is_running:
            return
        
        # Validate input
        destination = self.destination_var.get().strip()
        if not destination:
            messagebox.showerror("Error", "Please enter a destination!")
            return
        
        # Disable controls
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.dest_entry.config(state=tk.DISABLED)
        self.hops_spinbox.config(state=tk.DISABLED)
        self.timeout_spinbox.config(state=tk.DISABLED)
        self.probes_spinbox.config(state=tk.DISABLED)
        
        # Clear previous output
        self.clear_output()
        
        # Update status
        self.update_status(f"🚀 Running traceroute to {destination}...")
        
        # Get parameters
        max_hops = self.max_hops_var.get()
        timeout = self.timeout_var.get()
        probes = self.probes_var.get()
        
        # Run in separate thread
        self.traceroute_thread = threading.Thread(
            target=self.run_traceroute,
            args=(destination, max_hops, timeout, probes),
            daemon=True
        )
        self.traceroute_thread.start()
    
    def run_traceroute(self, destination, max_hops, timeout, probes):
        """Execute traceroute command"""
        try:
            # Get the path to traceroute.py
            script_dir = os.path.dirname(os.path.abspath(__file__))
            traceroute_script = os.path.join(script_dir, 'traceroute.py')
            
            # Build command
            cmd = [
                sys.executable,
                traceroute_script,
                destination,
                '--max-hops', str(max_hops),
                '--timeout', str(timeout),
                '--probes', str(probes)
            ]
            
            # Execute and capture output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Read output line by line
            for line in process.stdout:
                if not self.is_running:
                    process.terminate()
                    break
                self.append_output(line)
                self.update_status(f"📡 Processing: {line[:50]}...")
            
            # Check for errors
            stderr = process.stderr.read()
            if stderr and self.is_running:
                self.append_output(f"\n⚠️ Error: {stderr}", 'error')
                self.update_status("❌ Error occurred!")
            
            # Process finished
            if self.is_running:
                self.update_status("✅ Traceroute completed successfully!")
                self.append_output("\n" + "="*60 + "\n✅ Trace Complete!", 'success')
            
        except Exception as e:
            self.append_output(f"\n❌ Error: {str(e)}", 'error')
            self.update_status(f"❌ Error: {str(e)}")
        
        finally:
            # Re-enable controls
            self.root.after(0, self.enable_controls)
    
    def enable_controls(self):
        """Re-enable all controls after traceroute"""
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.dest_entry.config(state=tk.NORMAL)
        self.hops_spinbox.config(state=tk.NORMAL)
        self.timeout_spinbox.config(state=tk.NORMAL)
        self.probes_spinbox.config(state=tk.NORMAL)
        
        if not any(tag == 'error' for tag in self.output_text.tag_names()):
            self.update_status("✅ Ready - Traceroute completed")
    
    def stop_traceroute(self):
        """Stop the running traceroute"""
        self.is_running = False
        self.update_status("⏹️ Stopping traceroute...")
        self.append_output("\n⚠️ Traceroute stopped by user", 'warning')
        self.enable_controls()
    
    def append_output(self, text, tag=None):
        """Append text to output with optional coloring"""
        self.output_text.insert(tk.END, text + "\n")
        if tag:
            # Apply tag to the last line
            end_pos = self.output_text.index(tk.END)
            start_pos = f"{end_pos} - 1 lines"
            self.output_text.tag_add(tag, start_pos, end_pos)
        self.output_text.see(tk.END)
        
        # Update GUI
        self.root.update_idletasks()
    
    def clear_output(self):
        """Clear the output text area"""
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "⏳ Waiting for traceroute...\n\n")
    
    def update_status(self, message):
        """Update status bar"""
        self.root.after(0, lambda: self.status_label.config(text=message))
    
    def export_results(self):
        """Export output results to file"""
        if not self.output_text.get(1.0, tk.END).strip():
            messagebox.showinfo("Info", "No output to export!")
            return
        
        # Ask for filename
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"traceroute_{self.destination_var.get()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.output_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Results exported to:\n{filename}")
                self.update_status(f"💾 Exported results to {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = TracerouteGUI(root)
    
    # Print startup message
    app.append_output("="*60)
    app.append_output("  🌐 TRACEROUTE IMPLEMENTATION", 'accent')
    app.append_output("  Computer Networks Lab - CCE 314", 'info')
    app.append_output(f"  Student: Asanul Hoque Sohan (ID: 2202038)", 'info')
    app.append_output("="*60)
    app.append_output("\n📝 Enter a destination and click 'Start Traceroute'\n")
    app.append_output("💡 Quick tips:")
    app.append_output("  - Use quick buttons for popular destinations")
    app.append_output("  - Adjust parameters as needed")
    app.append_output("  - Export results for your report\n")
    
    root.mainloop()


if __name__ == "__main__":
    main()