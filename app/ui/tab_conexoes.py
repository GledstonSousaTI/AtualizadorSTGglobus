import threading
import customtkinter as ctk
from app.config import config_manager
from app.core import globus_reader, supabase_writer


class TabConexoes(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._build()

    def _build(self):
        cfg_oracle = config_manager.get_oracle()
        cfg_supa = config_manager.get_supabase()

        # --- Oracle ---
        ctk.CTkLabel(self, text="Oracle (Globus)", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=20, pady=(20, 8), sticky="w"
        )

        campos_oracle = [
            ("Host", "host"),
            ("Porta", "port"),
            ("Service Name", "service"),
            ("Usuário", "user"),
            ("Senha", "password"),
        ]
        self._oracle_vars = {}
        for i, (label, key) in enumerate(campos_oracle):
            ctk.CTkLabel(self, text=label).grid(row=i + 1, column=0, padx=20, pady=4, sticky="e")
            show = "*" if key == "password" else ""
            var = ctk.StringVar(value=str(cfg_oracle.get(key, "")))
            entry = ctk.CTkEntry(self, textvariable=var, width=280, show=show)
            entry.grid(row=i + 1, column=1, padx=10, pady=4, sticky="w")
            self._oracle_vars[key] = var

        btn_salvar_oracle = ctk.CTkButton(self, text="Salvar Oracle", command=self._salvar_oracle)
        btn_salvar_oracle.grid(row=6, column=1, padx=10, pady=4, sticky="w")

        btn_testar_oracle = ctk.CTkButton(
            self, text="Testar Conexão Oracle", fg_color="#2d6a4f", command=self._testar_oracle
        )
        btn_testar_oracle.grid(row=7, column=1, padx=10, pady=4, sticky="w")

        self._status_oracle = ctk.CTkLabel(self, text="")
        self._status_oracle.grid(row=8, column=0, columnspan=2, padx=20, pady=2, sticky="w")

        # --- Supabase ---
        ctk.CTkLabel(self, text="Supabase", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=9, column=0, columnspan=2, padx=20, pady=(20, 8), sticky="w"
        )

        campos_supa = [
            ("URL", "url"),
            ("Anon Key", "anon_key"),
            ("Service Key", "service_key"),
        ]
        self._supa_vars = {}
        for i, (label, key) in enumerate(campos_supa):
            ctk.CTkLabel(self, text=label).grid(row=10 + i, column=0, padx=20, pady=4, sticky="e")
            show = "*" if "key" in key else ""
            var = ctk.StringVar(value=str(cfg_supa.get(key, "")))
            entry = ctk.CTkEntry(self, textvariable=var, width=400, show=show)
            entry.grid(row=10 + i, column=1, padx=10, pady=4, sticky="w")
            self._supa_vars[key] = var

        btn_salvar_supa = ctk.CTkButton(self, text="Salvar Supabase", command=self._salvar_supa)
        btn_salvar_supa.grid(row=13, column=1, padx=10, pady=4, sticky="w")

        btn_testar_supa = ctk.CTkButton(
            self, text="Testar Conexão Supabase", fg_color="#2d6a4f", command=self._testar_supa
        )
        btn_testar_supa.grid(row=14, column=1, padx=10, pady=4, sticky="w")

        self._status_supa = ctk.CTkLabel(self, text="")
        self._status_supa.grid(row=15, column=0, columnspan=2, padx=20, pady=2, sticky="w")

    def _salvar_oracle(self):
        dados = {k: v.get() for k, v in self._oracle_vars.items()}
        dados["port"] = int(dados.get("port") or 1521)
        config_manager.update_oracle(dados)
        self._status_oracle.configure(text="Salvo.", text_color="green")

    def _salvar_supa(self):
        dados = {k: v.get() for k, v in self._supa_vars.items()}
        config_manager.update_supabase(dados)
        self._status_supa.configure(text="Salvo.", text_color="green")

    def _testar_oracle(self):
        self._status_oracle.configure(text="Testando...", text_color="gray")
        self._salvar_oracle()

        def _run():
            ok, msg = globus_reader.testar_conexao()
            cor = "green" if ok else "red"
            self._status_oracle.configure(text=msg, text_color=cor)

        threading.Thread(target=_run, daemon=True).start()

    def _testar_supa(self):
        self._status_supa.configure(text="Testando...", text_color="gray")
        self._salvar_supa()

        def _run():
            ok, msg = supabase_writer.testar_conexao()
            cor = "green" if ok else "red"
            self._status_supa.configure(text=msg, text_color=cor)

        threading.Thread(target=_run, daemon=True).start()
