import customtkinter as ctk
from app.config import config_manager


class TabAgendamentos(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self, text="Agendamentos", font=ctk.CTkFont(size=14, weight="bold")
        ).pack(padx=20, pady=(20, 4), anchor="w")

        ctk.CTkLabel(
            self,
            text="Defina o horário de sincronização de cada tabela. "
            "Use registrar_tarefa.bat para aplicar no Windows.",
            text_color="gray",
            wraplength=560,
        ).pack(padx=20, pady=(0, 12), anchor="w")

        self._frame = ctk.CTkScrollableFrame(self, height=320)
        self._frame.pack(padx=20, pady=4, fill="both", expand=True)

        ctk.CTkButton(self, text="Salvar Horários", command=self._salvar).pack(
            padx=20, pady=12, anchor="w"
        )

        self._status = ctk.CTkLabel(self, text="")
        self._status.pack(padx=20, anchor="w")

        self._refresh()

    def _refresh(self):
        for w in self._frame.winfo_children():
            w.destroy()
        self._horario_vars = {}

        tabelas = config_manager.get_tabelas()
        if not tabelas:
            ctk.CTkLabel(self._frame, text="Nenhuma tabela configurada.", text_color="gray").pack(
                padx=10, pady=10
            )
            return

        header = ctk.CTkFrame(self._frame, fg_color="transparent")
        header.pack(fill="x", padx=4, pady=2)
        for txt, w in [("Tabela", 200), ("Oracle", 180), ("Horário (HH:MM)", 140)]:
            ctk.CTkLabel(header, text=txt, width=w, font=ctk.CTkFont(weight="bold"), anchor="w").pack(
                side="left", padx=4
            )

        for tab in tabelas:
            row = ctk.CTkFrame(self._frame, fg_color=("gray90", "gray20"), corner_radius=6)
            row.pack(fill="x", padx=4, pady=3)

            ctk.CTkLabel(row, text=tab.get("id", ""), width=200, anchor="w").pack(
                side="left", padx=6
            )
            ctk.CTkLabel(row, text=tab.get("nome_oracle", ""), width=180, anchor="w").pack(
                side="left", padx=4
            )
            var = ctk.StringVar(value=tab.get("horario", "01:00"))
            ctk.CTkEntry(row, textvariable=var, width=100).pack(side="left", padx=4)
            self._horario_vars[tab["id"]] = var

    def _salvar(self):
        tabelas = config_manager.get_tabelas()
        for tab in tabelas:
            if tab["id"] in self._horario_vars:
                tab["horario"] = self._horario_vars[tab["id"]].get().strip()
                config_manager.upsert_tabela(tab)
        self._status.configure(text="Horários salvos.", text_color="green")
