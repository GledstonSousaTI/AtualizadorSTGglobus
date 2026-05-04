import threading
import customtkinter as ctk

from app.core import sync_engine
from app.ui.tab_conexoes import TabConexoes
from app.ui.tab_tabelas import TabTabelas
from app.ui.tab_agendamentos import TabAgendamentos
from app.ui.tab_logs import TabLogs

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AppWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AtualizadorSTG Globus")
        self.geometry("760x620")
        self.resizable(True, True)
        self._build()

    def _build(self):
        # topo
        topo = ctk.CTkFrame(self, fg_color=("gray85", "gray15"), corner_radius=0)
        topo.pack(fill="x")

        ctk.CTkLabel(
            topo,
            text="AtualizadorSTG Globus",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(side="left", padx=20, pady=12)

        self._btn_sync = ctk.CTkButton(
            topo,
            text="▶ Sincronizar Agora",
            fg_color="#1a7f5a",
            hover_color="#145f43",
            command=self._sincronizar_agora,
        )
        self._btn_sync.pack(side="right", padx=16, pady=10)

        self._lbl_status = ctk.CTkLabel(topo, text="", text_color="gray")
        self._lbl_status.pack(side="right", padx=8)

        # abas
        self._tabs = ctk.CTkTabview(self)
        self._tabs.pack(fill="both", expand=True, padx=12, pady=12)

        for nome in ["Conexões", "Tabelas", "Agendamentos", "Logs"]:
            self._tabs.add(nome)

        self._tab_conexoes = TabConexoes(self._tabs.tab("Conexões"))
        self._tab_conexoes.pack(fill="both", expand=True)

        self._tab_tabelas = TabTabelas(self._tabs.tab("Tabelas"))
        self._tab_tabelas.pack(fill="both", expand=True)

        self._tab_agendamentos = TabAgendamentos(self._tabs.tab("Agendamentos"))
        self._tab_agendamentos.pack(fill="both", expand=True)

        self._tab_logs = TabLogs(self._tabs.tab("Logs"))
        self._tab_logs.pack(fill="both", expand=True)

    def _sincronizar_agora(self):
        self._btn_sync.configure(state="disabled", text="Sincronizando...")
        self._lbl_status.configure(text="Em andamento...", text_color="yellow")
        self._tabs.set("Logs")

        def _run():
            def log_fn(msg):
                self._tab_logs.append(msg)

            resultados = sync_engine.run(log_fn=log_fn)

            erros = sum(1 for r in resultados if r.get("status") == "erro")
            if erros:
                self.after(0, lambda: self._lbl_status.configure(
                    text=f"Concluído com {erros} erro(s)", text_color="orange"
                ))
            else:
                self.after(0, lambda: self._lbl_status.configure(
                    text="Sincronização concluída!", text_color="green"
                ))
            self.after(0, lambda: self._btn_sync.configure(
                state="normal", text="▶ Sincronizar Agora"
            ))

        threading.Thread(target=_run, daemon=True).start()
