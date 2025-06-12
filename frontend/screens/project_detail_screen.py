import customtkinter as ctk
from middleware.module_project import get_all_projects, add_task, update_task_status, delete_task
from CTkMessagebox import CTkMessagebox
from functools import partial

class TaskColumn(ctk.CTkFrame):
    def __init__(self, master, title):
        super().__init__(master, fg_color="transparent")
        ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 10))
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="#3c3c3c")
        self.scrollable_frame.pack(fill="both", expand=True)
    def add_task_card(self, card_widget):
        card_widget.pack(fill="x", padx=5, pady=5)
    def clear_tasks(self):
        for widget in self.scrollable_frame.winfo_children(): widget.destroy()

class ProjectDetailScreen(ctk.CTkFrame):
    def __init__(self, master, app, user_info, project_id, **kwargs):
        super().__init__(master)
        self.app, self.logger, self.user_info, self.project_id = app, app.logger, user_info, project_id
        self.pack(fill="both", expand=True)
        self.project_data = self.get_project_data()
        if not self.project_data: self.create_error_widgets()
        else: self.create_widgets()

    def get_project_data(self):
        return next((p for p in get_all_projects() if p.get('projectID') == self.project_id), None)

    def create_error_widgets(self):
        ctk.CTkLabel(self, text="Lỗi: Không tìm thấy dự án.", font=("Arial", 18)).pack(pady=20)
        ctk.CTkButton(self, text="< Quay lại", command=self.app.show_main_menu).pack(pady=10)

    def create_widgets(self):
        if not self.project_data: return
        header = ctk.CTkFrame(self, fg_color="transparent"); header.pack(fill="x", padx=20, pady=10)
        ctk.CTkButton(header, text="< Quay lại", width=100, command=self.app.show_main_menu).pack(side="left", padx=(0, 20))
        ctk.CTkLabel(header, text=self.project_data.get("name"), font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        ctk.CTkLabel(self, text=self.project_data.get("description"), wraplength=800, justify="left").pack(fill="x", padx=20, pady=5)
        
        task_columns_frame = ctk.CTkFrame(self, fg_color="transparent"); task_columns_frame.pack(fill="both", expand=True, padx=20, pady=10)
        task_columns_frame.grid_columnconfigure((0, 1, 2), weight=1); task_columns_frame.grid_rowconfigure(0, weight=1)
        self.task_columns = { "Todo": TaskColumn(task_columns_frame, "Todo"), "In Progress": TaskColumn(task_columns_frame, "In Progress"), "Done": TaskColumn(task_columns_frame, "Done") }
        self.task_columns["Todo"].grid(row=0, column=0, sticky="nsew", padx=5)
        self.task_columns["In Progress"].grid(row=0, column=1, sticky="nsew", padx=5)
        self.task_columns["Done"].grid(row=0, column=2, sticky="nsew", padx=5)
        
        ctk.CTkButton(self, text="Thêm Task mới", command=self.open_add_task_form).pack(pady=10)
        self.refresh_tasks()

    def refresh_tasks(self):
        for col in self.task_columns.values(): col.clear_tasks()
        self.project_data = self.get_project_data()
        if not self.project_data: return
        for task in self.project_data.get("tasks", []):
            status = task.get("status", "Todo")
            target_column = self.task_columns.get(status)
            if target_column:
                card = self.create_task_card(target_column.scrollable_frame, task)
                target_column.add_task_card(card)
    
    def create_task_card(self, master, task_data):
        card = ctk.CTkFrame(master)
        
        ctk.CTkLabel(card, text=task_data.get("title"), font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=(5,0))
        ctk.CTkLabel(card, text=task_data.get("description"), wraplength=250, justify="left").pack(anchor="w", padx=5, pady=(5,5))
        
        task_id = task_data.get('taskID')
        bottom_frame = ctk.CTkFrame(card, fg_color="transparent"); bottom_frame.pack(fill="x", padx=5, pady=(0,5))
        
        # --- Nút Xóa Task ---
        delete_button = ctk.CTkButton(bottom_frame, text="Xóa", width=40, fg_color="#D83E3E", hover_color="#B22222", command=partial(self.confirm_delete_task, task_id))
        delete_button.pack(side="left")

        # --- Combobox đổi Status ---
        command_with_id = partial(self.on_status_change, task_id)
        combo = ctk.CTkComboBox(bottom_frame, values=["Todo", "In Progress", "Done"], command=command_with_id)
        combo.set(task_data.get("status", "Todo")); combo.pack(side="right")
        return card

    def on_status_change(self, task_id, new_status):
        self.logger.info(f"Người dùng thay đổi trạng thái task ID {task_id} thành {new_status}")
        if task_id and update_task_status(self.project_id, task_id, new_status):
            self.refresh_tasks()
        else:
            CTkMessagebox(title="Lỗi", message="Cập nhật trạng thái thất bại", icon="cancel")

    # =============================================================
    # ==================== HÀM MỚI ĐƯỢC THÊM ======================
    # =============================================================
    def confirm_delete_task(self, task_id):
        """Hỏi xác nhận trước khi xóa một task."""
        if not task_id: return
        msg = CTkMessagebox(title="Xác nhận", message="Bạn có chắc chắn muốn xóa task này?", icon="warning", option_1="Hủy", option_2="Xóa")
        if msg.get() == "Xóa":
            if delete_task(self.project_id, task_id):
                CTkMessagebox(title="Thành công", message="Đã xóa task.")
                self.refresh_tasks()
            else:
                CTkMessagebox(title="Lỗi", message="Xóa task thất bại.", icon="cancel")
    # =============================================================

    def open_add_task_form(self):
        dialog = ctk.CTkToplevel(self); dialog.title("Thêm Task mới"); dialog.geometry("400x300"); dialog.transient(self.app); dialog.grab_set()
        ctk.CTkLabel(dialog, text="Tiêu đề Task:").pack(pady=(10, 0), padx=20, anchor="w")
        title_entry = ctk.CTkEntry(dialog, width=360); title_entry.pack(pady=5, padx=20)
        ctk.CTkLabel(dialog, text="Mô tả:").pack(pady=(10, 0), padx=20, anchor="w")
        desc_textbox = ctk.CTkTextbox(dialog, width=360, height=100); desc_textbox.pack(pady=5, padx=20)

        def submit():
            title, desc = title_entry.get(), desc_textbox.get("1.0", "end-1c")
            if title:
                if add_task(self.project_id, title, desc):
                    CTkMessagebox(master=dialog, title="Thành công", message="Đã thêm task thành công!"); dialog.destroy(); self.refresh_tasks()
                else: CTkMessagebox(master=dialog, title="Lỗi", message="Có lỗi xảy ra khi thêm task.", icon="cancel")
            else: CTkMessagebox(master=dialog, title="Lỗi", message="Tiêu đề task không được để trống!", icon="cancel")
        ctk.CTkButton(dialog, text="Thêm Task", command=submit).pack(pady=20)