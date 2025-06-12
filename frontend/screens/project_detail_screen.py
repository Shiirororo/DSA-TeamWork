# File: frontend/screens/project_detail_screen.py
# PHIÊN BẢN NÂNG CẤP GIAO DIỆN VÀ SỬA LỖI LAYOUT

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from middleware import module_project, module_user
from functools import partial

# Lớp TaskColumn không thay đổi nhiều về logic, chỉ về giao diện
class TaskColumn(ctk.CTkFrame):
    def __init__(self, master, title):
        super().__init__(master, fg_color="#2B2B2B", corner_radius=8)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Tiêu đề cột
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(header_frame, text=title, font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w")

        # Khung chứa các task card
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="nsew")

    def add_task_card(self, card_widget):
        card_widget.pack(fill="x", padx=5, pady=5)

    def clear_tasks(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()


# Lớp Dialog Quản lý thành viên (giữ nguyên)
class ManageMembersDialog(ctk.CTkToplevel):
    def __init__(self, master, app, project_data, on_close_callback):
        super().__init__(master)
        self.app, self.project_data, self.on_close_callback = app, project_data, on_close_callback
        self.title("Quản lý thành viên"); self.geometry("500x500")
        self.transient(master); self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.all_users = module_user.get_all_users()
        self.create_widgets()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)
        current_members_frame = ctk.CTkScrollableFrame(main_frame, label_text="Thành viên trong dự án")
        current_members_frame.pack(expand=True, fill="both", padx=10, pady=(10, 5))
        project_member_ids = {member['id'] for member in self.project_data.get('members', [])}
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
        self.search_var.trace_add("write", self._update_add_list)
        search_entry = ctk.CTkEntry(add_member_frame, textvariable=self.search_var, placeholder_text="Nhập tên để tìm kiếm...")
        search_entry.pack(fill="x", pady=(5,5))
        self.add_list_frame = ctk.CTkScrollableFrame(add_member_frame, label_text="Kết quả tìm kiếm", height=150)
        self.add_list_frame.pack(fill="x", expand=True)
        self._update_add_list()

    def _update_add_list(self, *args):
        for widget in self.add_list_frame.winfo_children(): widget.destroy()
        search_term = self.search_var.get().lower()
        project_member_ids = {member['id'] for member in self.project_data.get('members', [])}
        potential_members = [user for user in self.all_users if user['id'] not in project_member_ids]
        found_match = False
        for user in potential_members:
            if search_term in user['name'].lower():
                found_match = True
                result_frame = ctk.CTkFrame(self.add_list_frame, fg_color="transparent")
                result_frame.pack(fill="x", padx=5, pady=2)
                ctk.CTkLabel(result_frame, text=user['name']).pack(side="left", padx=5)
                ctk.CTkButton(result_frame, text="Thêm", width=50, command=lambda uid=user['id'], uname=user['name']: self.add_member(uid, uname)).pack(side="right")
        if not found_match: ctk.CTkLabel(self.add_list_frame, text="Không tìm thấy thành viên nào.").pack(pady=10)

    def add_member(self, member_id, member_name):
        if module_project.add_member_to_project(self.project_data['projectID'], member_id):
            CTkMessagebox(title="Thành công", message=f"Đã thêm thành viên {member_name}.", icon="check"); self.on_close()
        else: CTkMessagebox(master=self, title="Lỗi", message="Không thể thêm thành viên.", icon="cancel")

    def remove_member(self, member_id):
        msg = CTkMessagebox(master=self, title="Xác nhận", message="Bạn có chắc chắn muốn xóa thành viên này?", icon="warning", option_1="Hủy", option_2="Xóa")
        if msg.get() == "Xóa":
            if module_project.remove_member_from_project(self.project_data['projectID'], member_id):
                CTkMessagebox(title="Thành công", message="Đã xóa thành viên.", icon="check"); self.on_close()
            else: CTkMessagebox(master=self, title="Lỗi", message="Không thể xóa thành viên.", icon="cancel")

    def on_close(self):
        self.on_close_callback(); self.destroy()


# Màn hình chi tiết dự án - được làm mới hoàn toàn
class ProjectDetailScreen(ctk.CTkFrame):
    def __init__(self, master, app, user_info, project_id, **kwargs):
        super().__init__(master)
        self.app, self.logger, self.user_info, self.project_id = app, app.logger, user_info, project_id
        
        # Cấu hình grid cho toàn bộ màn hình
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.project_data = module_project.get_project_by_id(self.project_id)
        self.user_map = {user['id']: user['name'] for user in module_user.get_all_users()}
        
        if not self.project_data:
            self.create_error_widgets()
            return
            
        self.create_widgets()

    def create_error_widgets(self):
        error_frame = ctk.CTkFrame(self)
        error_frame.pack(expand=True)
        ctk.CTkLabel(error_frame, text="Lỗi: Không tìm thấy dự án hoặc file dữ liệu bị hỏng.", font=("Arial", 18)).pack(pady=20, padx=20)
        ctk.CTkButton(error_frame, text="< Quay lại Menu Chính", command=self.app.show_main_menu).pack(pady=10)

    def create_widgets(self):
        # --- Frame Header ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(10, 20), sticky="ew")
        
        ctk.CTkButton(header_frame, text="< Quay lại", width=100, command=self.app.show_main_menu).pack(side="left")
        project_name = self.project_data.get("name", "Tên dự án") if self.project_data else "Tên dự án"
        ctk.CTkLabel(header_frame, text=project_name, font=ctk.CTkFont(size=24, weight="bold")).pack(side="left", padx=20)
        if self.project_data and (self.user_info.get('role') == 'Admin' or self.user_info.get('id') == self.project_data.get('ownerID')):
             ctk.CTkButton(header_frame, text="Quản lý thành viên", width=160, command=self.open_manage_members_dialog).pack(side="right")
             ctk.CTkButton(header_frame, text="+ Thêm Task", command=self.open_add_task_form).pack(side="right", padx=10)

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
        
        self.refresh_tasks()

    def refresh_tasks(self):
        for col in self.task_columns.values(): col.clear_tasks()
        self.project_data = module_project.get_project_by_id(self.project_id)
        if not self.project_data:
            self.create_error_widgets(); return
            
        for task in self.project_data.get("tasks", []):
            status = task.get("status", "Todo")
            target_column = self.task_columns.get(status)
            if target_column:
                card = self.create_task_card(target_column.scrollable_frame, task)
                target_column.add_task_card(card)

    def create_task_card(self, master, task_data):
        card = ctk.CTkFrame(master, corner_radius=8, border_width=1)
        card.grid_columnconfigure(0, weight=1)

        # Main content
        main_info_frame = ctk.CTkFrame(card, fg_color="transparent")
        main_info_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10,5))
        ctk.CTkLabel(main_info_frame, text=task_data.get("title", "Không có tiêu đề"), font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        ctk.CTkLabel(main_info_frame, text=task_data.get("description", "Không có mô tả"), wraplength=250, justify="left", text_color="gray").pack(anchor="w", pady=(0,5))

        # Assignee
        assignee_id = task_data.get("assigneeID")
        assignee_name = self.user_map.get(assignee_id, "Chưa giao")
        assignee_label = ctk.CTkLabel(card, text=f"👤 Giao cho: {assignee_name}", font=ctk.CTkFont(size=12, slant="italic"))
        assignee_label.grid(row=1, column=0, sticky="w", padx=10)

        # Actions
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        actions_frame.grid_columnconfigure(1, weight=1)
        
        # Status dropdown
        combo = ctk.CTkComboBox(actions_frame, values=["Todo", "In Progress", "Done"], command=partial(self.on_status_change, task_data['taskID']), state="readonly", width=120)
        combo.set(task_data.get("status", "Todo")); combo.grid(row=0, column=0, sticky="w")
        
        # Buttons frame
        buttons_subframe = ctk.CTkFrame(actions_frame, fg_color="transparent")
        buttons_subframe.grid(row=0, column=1, sticky="e")
        if self.project_data and self.user_info.get('id') == self.project_data.get('ownerID'):
            ctk.CTkButton(buttons_subframe, text="Giao", width=40, command=partial(self.open_assign_task_dialog, task_data)).pack(side="left", padx=5)
        ctk.CTkButton(buttons_subframe, text="Xóa", width=40, fg_color="#D83E3E", hover_color="#B22222", command=partial(self.confirm_delete_task, task_data['taskID'])).pack(side="left")
        
        return card

    def on_status_change(self, task_id, new_status):
        self.logger.info(f"Người dùng thay đổi trạng thái task ID {task_id} thành {new_status}")
        if task_id and module_project.update_task_status(self.project_id, task_id, new_status):
            self.refresh_tasks()
        else: CTkMessagebox(title="Lỗi", message="Cập nhật trạng thái thất bại", icon="cancel")

    def confirm_delete_task(self, task_id):
        if not task_id: return
        msg = CTkMessagebox(title="Xác nhận", message="Bạn có chắc chắn muốn xóa task này?", icon="warning", option_1="Hủy", option_2="Xóa")
        if msg.get() == "Xóa":
            if module_project.delete_task(self.project_id, task_id):
                self.refresh_tasks()
            else: CTkMessagebox(title="Lỗi", message="Xóa task thất bại.", icon="cancel")

    def open_add_task_form(self):
        if not self.project_data:
            self.logger.error("Attempted to open Add Task form with no project data.")
            CTkMessagebox(title="Lỗi", message="Dữ liệu dự án không hợp lệ, không thể thêm task.", icon="cancel"); return
        dialog = ctk.CTkToplevel(self); dialog.title("Thêm Task mới"); dialog.geometry("400x350"); dialog.transient(self.app); dialog.grab_set()
        ctk.CTkLabel(dialog, text="Tiêu đề Task:").pack(pady=(10, 0), padx=20, anchor="w")
        title_entry = ctk.CTkEntry(dialog, width=360); title_entry.pack(pady=5, padx=20)
        ctk.CTkLabel(dialog, text="Mô tả:").pack(pady=(10, 0), padx=20, anchor="w")
        desc_textbox = ctk.CTkTextbox(dialog, width=360, height=100); desc_textbox.pack(pady=5, padx=20)
        ctk.CTkLabel(dialog, text="Giao cho:").pack(pady=(10, 0), padx=20, anchor="w")
        project_member_ids = {member['id'] for member in self.project_data.get('members', [])}
        assignee_map = {name: uid for uid, name in self.user_map.items() if uid in project_member_ids}
        assignee_names = ["-- Chưa giao --"] + list(assignee_map.keys())
        assignee_combo = ctk.CTkComboBox(dialog, values=assignee_names, width=360, state="readonly"); assignee_combo.pack(pady=5, padx=20); assignee_combo.set(assignee_names[0])
        if self.user_info.get('id') != self.project_data.get('ownerID'): assignee_combo.configure(state="disabled")
        def submit():
            title, desc = title_entry.get(), desc_textbox.get("1.0", "end-1c")
            selected_name = assignee_combo.get()
            assignee_id = assignee_map.get(selected_name, "")
            if title:
                if module_project.add_task(self.project_id, title, desc, assignee_id):
                    dialog.destroy(); self.refresh_tasks()
                else: CTkMessagebox(master=dialog, title="Lỗi", message="Có lỗi xảy ra khi thêm task.", icon="cancel")
            else: CTkMessagebox(master=dialog, title="Lỗi", message="Tiêu đề task không được để trống!", icon="cancel")
        ctk.CTkButton(dialog, text="Thêm Task", command=submit).pack(pady=20)

    def open_assign_task_dialog(self, task_data):
        if not self.project_data:
            self.logger.error("Attempted to open Assign Task dialog with no project data.")
            CTkMessagebox(title="Lỗi", message="Dữ liệu dự án không hợp lệ, không thể giao việc.", icon="cancel"); return
        dialog = ctk.CTkToplevel(self); dialog.title(f"Giao việc cho Task"); dialog.geometry("400x150"); dialog.transient(self.app); dialog.grab_set()
        ctk.CTkLabel(dialog, text=f"Giao việc cho: {task_data['title']}").pack(pady=(10, 5), padx=20)
        project_member_ids = {member['id'] for member in self.project_data.get('members', [])}
        assignee_map = {name: uid for uid, name in self.user_map.items() if uid in project_member_ids}
        assignee_names = ["-- Bỏ giao việc --"] + list(assignee_map.keys())
        assignee_combo = ctk.CTkComboBox(dialog, values=assignee_names, width=360, state="readonly"); assignee_combo.pack(pady=5, padx=20)
        current_assignee_name = self.user_map.get(task_data.get("assigneeID"), assignee_names[0])
        if current_assignee_name in assignee_names: assignee_combo.set(current_assignee_name)
        else: assignee_combo.set(assignee_names[0])
        def submit_assign():
            selected_name = assignee_combo.get()
            new_assignee_id = assignee_map.get(selected_name, "")
            if module_project.assign_task(self.project_id, task_data['taskID'], new_assignee_id):
                dialog.destroy(); self.refresh_tasks()
            else: CTkMessagebox(master=dialog, title="Lỗi", message="Không thể giao việc.", icon="cancel")
        ctk.CTkButton(dialog, text="Xác nhận", command=submit_assign).pack(pady=15)

    def open_manage_members_dialog(self):
        if self.project_data:
            ManageMembersDialog(self, self.app, self.project_data, on_close_callback=self.refresh_screen)

    def refresh_screen(self):
        self.logger.info("Làm mới màn hình chi tiết dự án...")
        self.app.show_project_detail_screen(self.project_id)