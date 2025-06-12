import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from middleware import module_project, module_user
from functools import partial

class TaskColumn(ctk.CTkFrame):
    """Đại diện cho một cột trong Kanban board (ví dụ: To Do, In Progress)."""
    def __init__(self, master, title):
        super().__init__(master, fg_color=("#F0F2F5", "#2B2B2B"), corner_radius=8)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(header_frame, text=title, font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w")

        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="nsew")

    def add_task_card(self, card_widget):
        card_widget.pack(fill="x", padx=5, pady=5)

    def clear_tasks(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

    def add_spacer(self):
        """[MỚI] Thêm một widget rỗng để đẩy các task card lên trên."""
        spacer = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent", height=0)
        spacer.pack(expand=True, fill="y")


class ManageMembersDialog(ctk.CTkToplevel):
    # (Lớp này không thay đổi nhiều)
    def __init__(self, master, app, project_data, on_close_callback):
        super().__init__(master)
        self.app, self.project_data, self.on_close_callback = app, project_data, on_close_callback
        self.title("Quản lý thành viên")
        self.geometry("500x500")
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.all_users = module_user.get_all_users()
        self.create_widgets()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        current_members_frame = ctk.CTkScrollableFrame(main_frame, label_text="Thành viên trong dự án")
        current_members_frame.pack(expand=True, fill="both", padx=10, pady=(10, 5))
        project_member_ids = {member['id'] for member in self.project_data.get('members', [])} if self.project_data else set()
        
        if not project_member_ids:
            ctk.CTkLabel(current_members_frame, text="Chưa có thành viên nào.").pack(pady=10)
        else:
            for user in self.all_users:
                if user['id'] in project_member_ids:
                    member_frame = ctk.CTkFrame(current_members_frame, fg_color="transparent")
                    member_frame.pack(fill="x", pady=2, padx=5)
                    ctk.CTkLabel(member_frame, text=f"{user['name']} ({user.get('email', 'N/A')})").pack(side="left", padx=5)
                    if user['id'] != self.project_data.get('ownerID'):
                        remove_button = ctk.CTkButton(member_frame, text="Xóa", width=60, fg_color="#D83E3E", hover_color="#B22222",
                                                      command=lambda uid=user['id']: self.remove_member(uid))
                        remove_button.pack(side="right", padx=5)

        add_member_frame = ctk.CTkFrame(self, fg_color="transparent")
        add_member_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(add_member_frame, text="Tìm và thêm thành viên mới:", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda name, index, mode: self._update_add_list())
        search_entry = ctk.CTkEntry(add_member_frame, textvariable=self.search_var, placeholder_text="Nhập tên để tìm kiếm...")
        search_entry.pack(fill="x", pady=(5,5))
        
        self.add_list_frame = ctk.CTkScrollableFrame(add_member_frame, label_text="Kết quả tìm kiếm", height=150)
        self.add_list_frame.pack(fill="x", expand=True)
        self._update_add_list()

    def _update_add_list(self):
        for widget in self.add_list_frame.winfo_children(): widget.destroy()
        search_term = self.search_var.get().lower()
        project_member_ids = {member['id'] for member in self.project_data.get('members', [])} if self.project_data else set()
        potential_members = [user for user in self.all_users if user['id'] not in project_member_ids]
        
        found_match = False
        for user in potential_members:
            if search_term in user['name'].lower():
                found_match = True
                result_frame = ctk.CTkFrame(self.add_list_frame, fg_color="transparent")
                result_frame.pack(fill="x", padx=5, pady=2)
                ctk.CTkLabel(result_frame, text=user['name']).pack(side="left", padx=5)
                ctk.CTkButton(result_frame, text="Thêm", width=50, command=lambda uid=user['id'], uname=user['name']: self.add_member(uid, uname)).pack(side="right")
        
        if not found_match and search_term:
            ctk.CTkLabel(self.add_list_frame, text="Không tìm thấy thành viên nào.").pack(pady=10)

    def add_member(self, member_id, member_name):
        if module_project.add_member_to_project(self.project_data['projectID'], member_id):
            CTkMessagebox(title="Thành công", message=f"Đã thêm thành viên {member_name}.", icon="check", master=self.app)
            self.on_close()
        else:
            CTkMessagebox(master=self, title="Lỗi", message="Không thể thêm thành viên.", icon="cancel")

    def remove_member(self, member_id):
        msg = CTkMessagebox(master=self, title="Xác nhận", message="Bạn có chắc chắn muốn xóa thành viên này?", icon="warning", option_1="Hủy", option_2="Xóa")
        if msg.get() == "Xóa":
            if module_project.remove_member_from_project(self.project_data['projectID'], member_id):
                CTkMessagebox(title="Thành công", message="Đã xóa thành viên.", icon="check", master=self.app)
                self.on_close()
            else:
                CTkMessagebox(master=self, title="Lỗi", message="Không thể xóa thành viên.", icon="cancel")

    def on_close(self):
        self.on_close_callback()
        self.destroy()

class ProjectDetailScreen(ctk.CTkFrame):
    def __init__(self, master, app, user_info, project_id):
        super().__init__(master)
        self.app, self.logger, self.user_info, self.project_id = app, app.logger, user_info, project_id
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.user_map = {user['id']: user['name'] for user in module_user.get_all_users()}
        
        if not self.refresh_data():
            self.create_error_widgets()
        else:
            self.create_widgets()

    def create_error_widgets(self):
        # ... (không thay đổi)
        pass

    def create_widgets(self):
        # --- Frame Header (Giao diện mới, cân đối hơn) ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(10, 20), sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)

        # Cột 0: Nút Quay lại
        ctk.CTkButton(header_frame, text="< Quay lại", width=100, command=self.app.show_main_menu).grid(row=0, column=0, rowspan=2, sticky="w", padx=(0, 20))
        
        # Cột 1: Tên và mô tả dự án (tự dãn ra)
        project_name = self.project_data.get("name", "Tên dự án") if self.project_data else "Tên dự án"
        ctk.CTkLabel(header_frame, text=project_name, font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=1, sticky="w")
        
        project_desc = self.project_data.get("description", "Không có mô tả.") if self.project_data else "Không có mô tả."
        ctk.CTkLabel(header_frame, text=project_desc, text_color="gray", justify="left").grid(row=1, column=1, sticky="w")

        # Cột 2: Các nút điều khiển (chỉ tạo nếu là leader)
        is_leader = self.user_info.get('id') == self.project_data.get('ownerID') if self.project_data else False
        if is_leader:
            control_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
            control_frame.grid(row=0, column=2, rowspan=2, sticky="e")
            ctk.CTkButton(control_frame, text="Quản lý thành viên", width=160, command=self.open_manage_members_dialog).pack(side="right")
            ctk.CTkButton(control_frame, text="+ Thêm Task", command=self.open_add_task_form).pack(side="right", padx=10)

        # --- Frame chứa các cột Kanban ---
        kanban_frame = ctk.CTkFrame(self, fg_color="transparent")
        kanban_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        kanban_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="kanban_cols")
        kanban_frame.grid_rowconfigure(0, weight=1)
        
        self.task_columns = {
            "Todo": TaskColumn(kanban_frame, "📝 Cần làm (To Do)"),
            "In Progress": TaskColumn(kanban_frame, "⏳ Đang làm (In Progress)"),
            "Done": TaskColumn(kanban_frame, "✅ Hoàn thành (Done)")
        }
        self.task_columns["Todo"].grid(row=0, column=0, sticky="nsew", padx=10)
        self.task_columns["In Progress"].grid(row=0, column=1, sticky="nsew", padx=10)
        self.task_columns["Done"].grid(row=0, column=2, sticky="nsew", padx=10)
        
        self.populate_tasks()

    def refresh_data(self):
        self.project_data = module_project.get_project_by_id(self.project_id)
        return self.project_data is not None

    def populate_tasks(self):
        for col in self.task_columns.values(): col.clear_tasks()
        
        if self.project_data:
            for task in self.project_data.get("tasks", []):
                status = task.get("status", "Todo")
                target_column = self.task_columns.get(status)
                if target_column:
                    card = self.create_task_card(target_column.scrollable_frame, task)
                    target_column.add_task_card(card)
        
        # [SỬA LỖI] Thêm spacer để đẩy các card lên trên
        for col in self.task_columns.values():
            col.add_spacer()
    def create_task_card(self, master, task_data):
        card = ctk.CTkFrame(master, corner_radius=8, border_width=1, fg_color=("#FFFFFF", "#333333"))
        
        main_info_frame = ctk.CTkFrame(card, fg_color="transparent")
        main_info_frame.pack(fill="x", padx=10, pady=(10,5))
        ctk.CTkLabel(main_info_frame, text=task_data.get("title", "Không có tiêu đề"), font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        ctk.CTkLabel(main_info_frame, text=task_data.get("description", "Không có mô tả"), wraplength=250, justify="left", text_color="gray").pack(anchor="w", pady=(0,5))

        footer_frame = ctk.CTkFrame(card, fg_color="transparent")
        footer_frame.pack(fill="x", padx=10, pady=(5, 10))
        footer_frame.grid_columnconfigure(0, weight=1)

        assignee_id = task_data.get("assigneeID")
        assignee_name = self.user_map.get(assignee_id, "Chưa giao")
        assignee_label = ctk.CTkLabel(footer_frame, text=f"👤 {assignee_name}", font=ctk.CTkFont(size=12, slant="italic"))
        assignee_label.grid(row=0, column=0, sticky="w")

        actions_subframe = ctk.CTkFrame(footer_frame, fg_color="transparent")
        actions_subframe.grid(row=0, column=1, sticky="e")
        
        combo = ctk.CTkComboBox(actions_subframe, values=["Todo", "In Progress", "Done"], command=partial(self.on_status_change, task_data['taskID']), state="readonly", width=120)
        combo.set(task_data.get("status", "Todo"))
        combo.pack(side="left")
        
        is_leader = self.user_info.get('id') == self.project_data.get('ownerID') if self.project_data else False
        if is_leader:
            ctk.CTkButton(actions_subframe, text="Giao", width=40, height=25, command=partial(self.open_assign_task_dialog, task_data)).pack(side="left", padx=5)
            ctk.CTkButton(actions_subframe, text="Xóa", width=40, height=25, fg_color="#D83E3E", hover_color="#B22222", command=partial(self.confirm_delete_task, task_data['taskID'])).pack(side="left")
        
        return card
        return card

    def on_status_change(self, task_id, new_status):
        if module_project.update_task_status(self.project_id, task_id, new_status):
            self.refresh_and_repopulate()
        else:
            CTkMessagebox(title="Lỗi", message="Cập nhật trạng thái thất bại", icon="cancel", master=self.app)

    def confirm_delete_task(self, task_id):
        msg = CTkMessagebox(title="Xác nhận", message="Bạn có chắc chắn muốn xóa task này?", icon="warning", option_1="Hủy", option_2="Xóa", master=self.app)
        if msg.get() == "Xóa":
            if module_project.delete_task(self.project_id, task_id):
                self.refresh_and_repopulate()
            else:
                CTkMessagebox(title="Lỗi", message="Xóa task thất bại.", icon="cancel", master=self.app)
    
    def refresh_and_repopulate(self):
        """Hàm trợ giúp để tải lại dữ liệu và cập nhật giao diện."""
        if self.refresh_data():
            self.populate_tasks()
        else:
            self.create_error_widgets()

    def open_add_task_form(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Thêm Task mới")
        dialog.geometry("400x350")
        dialog.transient(self.app)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Tiêu đề Task:").pack(pady=(20, 0), padx=20, anchor="w")
        title_entry = ctk.CTkEntry(dialog)
        title_entry.pack(pady=5, padx=20, fill="x")
        
        ctk.CTkLabel(dialog, text="Mô tả:").pack(pady=(10, 0), padx=20, anchor="w")
        desc_textbox = ctk.CTkTextbox(dialog, height=100)
        desc_textbox.pack(pady=5, padx=20, fill="x", expand=True)
        
        def submit():
            title, desc = title_entry.get(), desc_textbox.get("1.0", "end-1c")
            if not title:
                CTkMessagebox(master=dialog, title="Lỗi", message="Tiêu đề task không được để trống!", icon="cancel")
                return
            
            if module_project.add_task(self.project_id, title, desc, ""):
                dialog.destroy()
                self.refresh_and_repopulate()
            else:
                CTkMessagebox(master=dialog, title="Lỗi", message="Có lỗi xảy ra khi thêm task.", icon="cancel")
        
        ctk.CTkButton(dialog, text="Thêm Task", command=submit).pack(pady=20)
    def open_assign_task_dialog(self, task_data):
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Giao việc")
        dialog.geometry("400x200")
        dialog.transient(self.app)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text=f"Giao việc cho task: '{task_data['title']}'").pack(pady=(20, 5), padx=20)
        
        project_member_ids = {member['id'] for member in self.project_data.get('members', [])} if self.project_data else set()
        assignee_map = {name: uid for uid, name in self.user_map.items() if uid in project_member_ids}
        assignee_names = ["-- Bỏ giao việc --"] + list(assignee_map.keys())
        
        assignee_combo = ctk.CTkComboBox(dialog, values=assignee_names, state="readonly")
        assignee_combo.pack(pady=5, padx=20, fill="x")
        
        current_assignee_name = self.user_map.get(task_data.get("assigneeID"), assignee_names[0])
        assignee_combo.set(current_assignee_name if current_assignee_name in assignee_names else assignee_names[0])
        
        def submit_assign():
            selected_name = assignee_combo.get()
            new_assignee_id = assignee_map.get(selected_name, "")
            if module_project.assign_task(self.project_id, task_data['taskID'], new_assignee_id):
                dialog.destroy()
                self.refresh_and_repopulate()
            else:
                CTkMessagebox(master=dialog, title="Lỗi", message="Không thể giao việc.", icon="cancel")
        
        ctk.CTkButton(dialog, text="Xác nhận", command=submit_assign).pack(pady=20)
        ctk.CTkButton(dialog, text="Xác nhận", command=submit_assign).pack(pady=20)

    def open_manage_members_dialog(self):
        if self.project_data:
            ManageMembersDialog(self, self.app, self.project_data, on_close_callback=self.refresh_and_repopulate)
