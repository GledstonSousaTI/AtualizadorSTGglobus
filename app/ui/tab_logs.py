import threading
from pathlib import Path
import customtkinter as ctk

LOG_PATH = Path(__file__).parent.parent.parent / "logs" / "sync.log"


class TabLogs(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._seguindo = True
        self._build()
        self._iniciar_watch()

    def _build(self):
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", padx=16, pady=(16, 4))

        ctk.CTkLabel(topo, text="Logs de Sincronização", font=ctk.CTkFont(size=14, weight="bold")).pack(
            side="left"
        )

        ctk.CTkButton(topo, text="Limpar", width=80, command=self._limpar).pack(side="right", padx=4)
        ctk.CTkButton(topo, text="Atualizar", width=80, command=self._carregar).pack(
            side="right", padx=4
        )

        self._seguir_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(topo, text="Seguir", variable=self._seguir_var).pack(side="right", padx=8)

        self._texto = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Courier New", size=12))
        self._texto.pack(padx=16, pady=(4, 16), fill="both", expand=True)
        self._texto.configure(state="disabled")

        self._carregar()

    def _carregar(self):
        if not LOG_PATH.exists():
            return
        conteudo = LOG_PATH.read_text(encoding="utf-8", errors="replace")
        self._texto.configure(state="normal")
        self._texto.delete("1.0", "end")
        self._texto.insert("end", conteudo)
        self._texto.configure(state="disabled")
        if self._seguir_var.get():
            self._texto.see("end")

    def _limpar(self):
        LOG_PATH.write_text("", encoding="utf-8")
        self._texto.configure(state="normal")
        self._texto.delete("1.0", "end")
        self._texto.configure(state="disabled")

    def _iniciar_watch(self):
        """Atualiza o log a cada 3 segundos em background."""
        def _loop():
            import time
            ultimo_tamanho = 0
            while True:
                time.sleep(3)
                try:
                    if LOG_PATH.exists():
                        tamanho = LOG_PATH.stat().st_size
                        if tamanho != ultimo_tamanho:
                            ultimo_tamanho = tamanho
                            self.after(0, self._carregar)
                except Exception:
                    pass

        threading.Thread(target=_loop, daemon=True).start()

    def append(self, msg: str):
        """Adiciona uma linha ao textbox (chamado pelo sync em tempo real)."""
        self._texto.configure(state="normal")
        self._texto.insert("end", msg + "\n")
        self._texto.configure(state="disabled")
        if self._seguir_var.get():
            self._texto.see("end")
