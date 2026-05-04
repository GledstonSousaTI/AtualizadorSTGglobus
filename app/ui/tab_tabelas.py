import customtkinter as ctk
from app.config import config_manager


class TabTabelas(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self, text="Tabelas Configuradas", font=ctk.CTkFont(size=14, weight="bold")
        ).pack(padx=20, pady=(20, 8), anchor="w")

        ctk.CTkLabel(
            self,
            text="Gerencie quais tabelas do Globus serão sincronizadas com o Supabase.",
            text_color="gray",
        ).pack(padx=20, pady=(0, 12), anchor="w")

        self._frame_lista = ctk.CTkScrollableFrame(self, height=300)
        self._frame_lista.pack(padx=20, pady=4, fill="both", expand=True)

        ctk.CTkButton(self, text="+ Nova Tabela", command=self._nova_tabela).pack(
            padx=20, pady=8, anchor="w"
        )

        self._refresh()

    def _refresh(self):
        for widget in self._frame_lista.winfo_children():
            widget.destroy()

        tabelas = config_manager.get_tabelas()
        if not tabelas:
            ctk.CTkLabel(self._frame_lista, text="Nenhuma tabela configurada.", text_color="gray").pack(
                padx=10, pady=10
            )
            return

        headers = ["Ativo", "ID", "Oracle", "Supabase", "PK", "Horário", ""]
        larguras = [50, 120, 160, 160, 100, 80, 80]
        header_row = ctk.CTkFrame(self._frame_lista, fg_color="transparent")
        header_row.pack(fill="x", padx=4, pady=2)
        for h, w in zip(headers, larguras):
            ctk.CTkLabel(
                header_row, text=h, width=w, font=ctk.CTkFont(weight="bold"), anchor="w"
            ).pack(side="left", padx=2)

        for tab in tabelas:
            self._linha(tab)

    def _linha(self, tab: dict):
        row = ctk.CTkFrame(self._frame_lista, fg_color=("gray90", "gray20"), corner_radius=6)
        row.pack(fill="x", padx=4, pady=3)

        ativo_var = ctk.BooleanVar(value=tab.get("ativo", True))

        def toggle(t=tab, v=ativo_var):
            t["ativo"] = v.get()
            config_manager.upsert_tabela(t)

        ctk.CTkCheckBox(row, text="", variable=ativo_var, command=toggle, width=50).pack(
            side="left", padx=6
        )
        for val, w in [
            (tab.get("id", ""), 120),
            (tab.get("nome_oracle", ""), 160),
            (tab.get("nome_supabase", ""), 160),
            (tab.get("pk", ""), 100),
            (tab.get("horario", "01:00"), 80),
        ]:
            ctk.CTkLabel(row, text=str(val), width=w, anchor="w").pack(side="left", padx=2)

        ctk.CTkButton(
            row,
            text="Editar",
            width=70,
            command=lambda t=tab: self._editar(t),
        ).pack(side="left", padx=4)

    def _nova_tabela(self):
        self._abrir_form(None)

    def _editar(self, tab: dict):
        self._abrir_form(tab)

    def _abrir_form(self, tab: dict | None):
        win = ctk.CTkToplevel(self)
        win.title("Nova Tabela" if tab is None else f"Editar: {tab['id']}")
        win.geometry("460x420")
        win.grab_set()

        campos = [
            ("ID (único)", "id"),
            ("Nome Oracle (tabela/view)", "nome_oracle"),
            ("Nome Supabase (tabela destino)", "nome_supabase"),
            ("Chave Primária (coluna)", "pk"),
            ("Horário (HH:MM)", "horario"),
        ]
        vars_ = {}
        for i, (label, key) in enumerate(campos):
            ctk.CTkLabel(win, text=label).grid(row=i, column=0, padx=16, pady=6, sticky="e")
            var = ctk.StringVar(value=str(tab.get(key, "") if tab else ""))
            ctk.CTkEntry(win, textvariable=var, width=240).grid(
                row=i, column=1, padx=10, pady=6, sticky="w"
            )
            vars_[key] = var

        ativo_var = ctk.BooleanVar(value=tab.get("ativo", True) if tab else True)
        ctk.CTkLabel(win, text="Ativo").grid(row=5, column=0, padx=16, pady=6, sticky="e")
        ctk.CTkCheckBox(win, text="", variable=ativo_var).grid(
            row=5, column=1, padx=10, pady=6, sticky="w"
        )

        def salvar():
            nova = {k: v.get().strip() for k, v in vars_.items()}
            nova["ativo"] = ativo_var.get()
            if tab:
                nova["filtros"] = tab.get("filtros", {})
            config_manager.upsert_tabela(nova)
            win.destroy()
            self._refresh()

        def excluir():
            if tab:
                config_manager.remover_tabela(tab["id"])
            win.destroy()
            self._refresh()

        btn_frame = ctk.CTkFrame(win, fg_color="transparent")
        btn_frame.grid(row=6, column=0, columnspan=2, pady=16)
        ctk.CTkButton(btn_frame, text="Salvar", command=salvar).pack(side="left", padx=8)
        if tab:
            ctk.CTkButton(
                btn_frame, text="Excluir", fg_color="red", command=excluir
            ).pack(side="left", padx=8)
