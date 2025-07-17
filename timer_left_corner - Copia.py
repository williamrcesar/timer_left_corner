import tkinter as tk
from tkinter import ttk, colorchooser
from datetime import datetime, timedelta
import threading, time, json, os, sys

try:
    from PIL import Image, ImageDraw, ImageFont, ImageTk
except ImportError:
    print("pip install Pillow")
    sys.exit()

class CronometroPremium:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cronômetro Premium")
        self.config_file = "cronometro_config.json"

        self.config = {
            "largura": 280, "altura": 80,
            "tamanho_fonte": 48, "fonte_familia": "Windows",
            "cor_borda": "#FFFFFF", "cor_preenchimento": "#FFFFFF",
            "espessura_borda": 2, "tipo_fundo": "transparente",
            "transparencia": 0.95, "pos_x": 100, "pos_y": 100,
            "espacamento_letras": 0
        }
        self.carregar_configuracoes()

        self.inicio = None
        self.pausado = False
        self.tempo_pausado = timedelta(0)
        self.rodando = False
        self.tempo_atual_texto = "00:00:00"
        self.config_window = None

        self.setup_janela()
        self.setup_ui()
        self.iniciar_threads()

    def carregar_configuracoes(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config.update(json.load(f))

    def salvar_configuracoes(self):
        self.config["pos_x"] = self.root.winfo_x()
        self.config["pos_y"] = self.root.winfo_y()
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)

    def setup_janela(self):
        self.root.geometry(
            f"{self.config['largura']}x{self.config['altura']}+{self.config['pos_x']}+{self.config['pos_y']}"
        )
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.aplicar_fundo()

    def aplicar_fundo(self):
        if self.config["tipo_fundo"] == "transparente":
            self.root.configure(bg='black')
            self.root.wm_attributes('-transparentcolor', 'black')
            self.root.wm_attributes('-alpha', self.config["transparencia"])
        else:
            self.root.configure(bg="#1a1a1a")
            self.root.wm_attributes('-transparentcolor', '')
            self.root.wm_attributes('-alpha', 1.0)

    def setup_ui(self):
        bg = 'black' if self.config["tipo_fundo"] == "transparente" else self.root.cget('bg')
        if hasattr(self, 'canvas') and self.canvas.winfo_exists():
            self.canvas.config(bg=bg)
        else:
            self.canvas = tk.Canvas(self.root, bg=bg, highlightthickness=0)
            self.canvas.pack(fill='both', expand=True)
            self.canvas.bind("<Configure>", lambda e: self.redesenhar_texto())
            self.bind_eventos()
        self.redesenhar_texto()

    def bind_eventos(self):
        for w in (self.root, self.canvas):
            w.bind("<Button-1>", self.iniciar_drag)
            w.bind("<B1-Motion>", self.arrastar)
            w.bind("<Button-3>", self.mostrar_menu_contexto)
        self.root.bind("<KeyPress>", self.processar_tecla)
        self.root.focus_set()

    def obter_fonte_pillow(self):
        fam = self.config["fonte_familia"]
        mapeamento = {
            "Digital": "digital-7.mono.ttf", "Windows": "segoeui.ttf",
            "Moderna": "calibri.ttf", "Clássica": "times.ttf",
            "Técnica": "cour.ttf", "Elegante": "georgia.ttf",
            "Simples": "arial.ttf", "Mono": "lucon.ttf", "System": "tahoma.ttf"
        }
        try:
            return ImageFont.truetype(mapeamento.get(fam, "arial.ttf"), self.config["tamanho_fonte"])
        except:
            return ImageFont.load_default()

    def desenhar_texto(self, txt):
        if not self.canvas.winfo_exists():
            return
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        font = self.obter_fonte_pillow()
        espacamento = self.config["espacamento_letras"]
        texto_com_espaco = ' '.join(txt[i:i+1] for i in range(len(txt))).replace(' ', ' ' * espacamento)
        cor_b = self.config["cor_borda"]
        cor_p = self.config["cor_preenchimento"]
        stroke = self.config["espessura_borda"]
        draw.text((w/2, h/2), texto_com_espaco, font=font, fill=cor_p,
                  stroke_width=stroke, stroke_fill=cor_b, anchor="mm")
        self._photo = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self._photo, anchor="nw")

    def redesenhar_texto(self):
        self.desenhar_texto(self.tempo_atual_texto)

    def mostrar_menu_contexto(self, event):
        m = tk.Menu(self.root, tearoff=0, bg='#2d2d2d', fg='white')
        label = "⏸️ Pausar" if self.rodando else ("▶️ Continuar" if self.pausado else "▶️ Iniciar")
        m.add_command(label=label, command=self.toggle)
        m.add_command(label="🔄 Resetar", command=self.resetar)
        m.add_separator()
        m.add_command(label="⚙️ Configurações", command=self.abrir_configuracoes)
        m.add_separator()
        m.add_command(label="❌ Sair", command=self.fechar_app)
        m.tk_popup(event.x_root, event.y_root)

    def abrir_configuracoes(self):
        if self.config_window and self.config_window.winfo_exists():
            self.config_window.lift()
            self.config_window.focus_force()
            return
        self.criar_janela_configuracoes()

    def criar_janela_configuracoes(self):
        self.config_window = tk.Toplevel(self.root)
        self.config_window.title("Configurações")
        self.config_window.configure(bg='#1e2227')
        self.config_window.attributes('-topmost', True)
        self.config_window.state('zoomed')

        container = tk.Frame(self.config_window, bg='#1e2227')
        container.pack(fill='both', expand=True, padx=15, pady=15)

        # Seção de Fontes
        font_lb = tk.LabelFrame(container, text="🔤 Fonte, Tamanho e Borda", font=('Segoe UI', 11, 'bold'),
                                fg='#c9d1d9', bg='#1e2227', relief='groove', bd=1)
        font_lb.pack(fill='x', pady=10)

        tk.Label(font_lb, text="Família:", fg='#c9d1d9', bg='#1e2227').grid(row=0, column=0, sticky='w', padx=10, pady=5)
        fam_frame = tk.Frame(font_lb, bg='#1e2227')
        fam_frame.grid(row=0, column=1, sticky='ew', padx=10, pady=5)
        fontes = ["Digital", "Windows", "Moderna", "Clássica", "Técnica", "Elegante", "Simples", "Mono", "System"]
        self.fam_vars = []
        for i, f in enumerate(fontes):
            btn = tk.Button(fam_frame, text=f, bg='#21262d', fg='white', bd=0, width=9,
                            command=lambda ff=f: self.mudar_fonte(ff))
            btn.grid(row=i // 3, column=i % 3, padx=2, pady=2)
            if f == self.config["fonte_familia"]:
                btn.config(bg='#0d6efd')
            self.fam_vars.append(btn)

        tk.Label(font_lb, text="Tamanho:", fg='#c9d1d9', bg='#1e2227').grid(row=1, column=0, sticky='w', padx=10, pady=5)
        size_frame = tk.Frame(font_lb, bg='#1e2227')
        size_frame.grid(row=1, column=1, sticky='ew', padx=10, pady=5)
        self.lbl_size = tk.Label(size_frame, text=str(self.config["tamanho_fonte"]),
                                 width=4, fg='#58a6ff', bg='#1e2227', font=('Segoe UI', 12, 'bold'))
        self.lbl_size.pack(side='left', padx=5)
        tk.Button(size_frame, text="−", width=3, bg='#21262d', fg='white', bd=0,
                  command=self.diminuir_fonte).pack(side='left', padx=2)
        tk.Button(size_frame, text="+", width=3, bg='#21262d', fg='white', bd=0,
                  command=self.aumentar_fonte).pack(side='left', padx=2)

        tk.Label(font_lb, text="Espessura da borda:", fg='#c9d1d9', bg='#1e2227').grid(row=2, column=0, sticky='w', padx=10, pady=5)
        self.scl_borda = ttk.Scale(font_lb, from_=0, to=10, value=self.config["espessura_borda"],
                                   orient='horizontal', command=lambda v: self.mudar_borda(v))
        self.scl_borda.grid(row=2, column=1, sticky='ew', padx=10, pady=5)

        # Seção de Espaçamento
        espacamento_lb = tk.LabelFrame(container, text="📏 Espaçamento", font=('Segoe UI', 11, 'bold'),
                                       fg='#c9d1d9', bg='#1e2227', relief='groove', bd=1)
        espacamento_lb.pack(fill='x', pady=10)

        tk.Label(espacamento_lb, text="Espaçamento entre letras:", fg='#c9d1d9', bg='#1e2227').grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.scl_espacamento = ttk.Scale(espacamento_lb, from_=0, to=10, value=self.config["espacamento_letras"],
                                         orient='horizontal', command=lambda v: self.mudar_espacamento(v))
        self.scl_espacamento.grid(row=0, column=1, sticky='ew', padx=10, pady=5)

        # Seção de Cores
        cor_lb = tk.LabelFrame(container, text="🎨 Cores", font=('Segoe UI', 11, 'bold'),
                               fg='#c9d1d9', bg='#1e2227', relief='groove', bd=1)
        cor_lb.pack(fill='x', pady=10)

        tk.Label(cor_lb, text="Cor do Fundo:", fg='#c9d1d9', bg='#1e2227').grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.btn_cor_fundo = tk.Button(cor_lb, text="Escolher Cor", bg='#21262d', fg='white', bd=0,
                                       command=lambda: self.escolher_cor("cor_fundo"))
        self.btn_cor_fundo.grid(row=0, column=1, padx=10, pady=5)
        self.var_transparente = tk.BooleanVar(value=self.config["tipo_fundo"] == "transparente")
        tk.Checkbutton(cor_lb, text="Transparente", variable=self.var_transparente, command=self.toggle_transparencia,
                       fg='#c9d1d9', bg='#1e2227', selectcolor='#1e2227').grid(row=0, column=2, padx=10, pady=5)

        self.trans_frame = tk.Frame(cor_lb, bg='#1e2227')
        if self.config["tipo_fundo"] == "transparente":
            self.trans_frame.grid(row=1, column=0, columnspan=3, sticky='ew', padx=10, pady=5)
            tk.Label(self.trans_frame, text="Transparência:", fg='#c9d1d9', bg='#1e2227').pack(side='left')
            self.scl_trans = ttk.Scale(self.trans_frame, from_=0.3, to=1.0, value=self.config["transparencia"],
                                       orient='horizontal', command=lambda v: self.mudar_trans(float(v)))
            self.scl_trans.pack(fill='x', expand=True)

        tk.Label(cor_lb, text="Cor do Preenchimento:", fg='#c9d1d9', bg='#1e2227').grid(row=2, column=0, sticky='w', padx=10, pady=5)
        self.btn_cor_preench = tk.Button(cor_lb, text="Escolher Cor", bg='#21262d', fg='white', bd=0,
                                         command=lambda: self.escolher_cor("cor_preenchimento"))
        self.btn_cor_preench.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(cor_lb, text="Cor das Bordas:", fg='#c9d1d9', bg='#1e2227').grid(row=3, column=0, sticky='w', padx=10, pady=5)
        self.btn_cor_borda = tk.Button(cor_lb, text="Escolher Cor", bg='#21262d', fg='white', bd=0,
                                       command=lambda: self.escolher_cor("cor_borda"))
        self.btn_cor_borda.grid(row=3, column=1, padx=10, pady=5)

        tk.Button(container, text="📍 Centralizar", bg='#238636', fg='white', bd=0, pady=8,
                  command=self.centralizar).pack(fill='x', pady=10)
        tk.Label(container, text="💾 As alterações são salvas automaticamente", fg='#7ce38b',
                 bg='#1e2227', font=('Segoe UI', 9, 'italic')).pack()

        self.config_window.update_idletasks()  # Garante que a interface seja atualizada

    def escolher_cor(self, chave):
        cor = colorchooser.askcolor(color=self.config[chave])[1]
        if cor:
            self.config[chave] = cor
            if chave == "cor_fundo" and self.config["tipo_fundo"] != "transparente":
                self.aplicar_fundo()
            elif chave in ["cor_preenchimento", "cor_borda"]:
                self.redesenhar_texto()
            self.salvar_configuracoes()

    def toggle_transparencia(self):
        if self.var_transparente.get():
            self.config["tipo_fundo"] = "transparente"
            self.trans_frame.grid(row=1, column=0, columnspan=3, sticky='ew', padx=10, pady=5)
        else:
            self.config["tipo_fundo"] = "cor"
            self.trans_frame.grid_forget()
        self.aplicar_fundo()
        self.setup_ui()
        self.salvar_configuracoes()

    def mudar_trans(self, v):
        self.config["transparencia"] = round(float(v), 2)
        self.aplicar_fundo()
        self.salvar_configuracoes()

    def mudar_fonte(self, fam):
        self.config["fonte_familia"] = fam
        for btn in self.fam_vars:
            btn.config(bg='#21262d')
            if btn['text'] == fam:
                btn.config(bg='#0d6efd')
        self.atualizar_interface()
        self.salvar_configuracoes()

    def aumentar_fonte(self):
        self.config["tamanho_fonte"] = min(self.config["tamanho_fonte"] + 2, 200)
        self.lbl_size.config(text=str(self.config["tamanho_fonte"]))
        self.atualizar_interface()
        self.salvar_configuracoes()

    def diminuir_fonte(self):
        self.config["tamanho_fonte"] = max(self.config["tamanho_fonte"] - 2, 8)
        self.lbl_size.config(text=str(self.config["tamanho_fonte"]))
        self.atualizar_interface()
        self.salvar_configuracoes()

    def mudar_borda(self, v):
        self.config["espessura_borda"] = int(float(v))
        self.redesenhar_texto()
        self.salvar_configuracoes()

    def mudar_espacamento(self, v):
        self.config["espacamento_letras"] = int(float(v))
        self.redesenhar_texto()
        self.salvar_configuracoes()

    def atualizar_interface(self):
        self.root.geometry(f"{self.config['largura']}x{self.config['altura']}+{self.root.winfo_x()}+{self.root.winfo_y()}")
        self.setup_ui()

    def toggle(self):
        if not self.rodando:
            self.inicio = datetime.now() - (self.tempo_pausado if self.pausado else timedelta(0))
            self.rodando, self.pausado = True, False
        else:
            self.tempo_pausado = datetime.now() - self.inicio
            self.rodando, self.pausado = False, True

    def resetar(self):
        self.inicio = None
        self.rodando = False
        self.pausado = False
        self.tempo_pausado = timedelta(0)
        self.atualizar_display("00:00:00")

    def centralizar(self):
        self.root.geometry(f"+{(self.root.winfo_screenwidth() - self.root.winfo_width()) // 2}+100")
        self.salvar_configuracoes()

    def iniciar_drag(self, ev):
        self._drag_x, self._drag_y = ev.x, ev.y

    def arrastar(self, ev):
        x = self.root.winfo_x() + ev.x - self._drag_x
        y = self.root.winfo_y() + ev.y - self._drag_y
        self.root.geometry(f"+{x}+{y}")

    def processar_tecla(self, ev):
        k = ev.keysym.lower()
        if k == 'space': self.toggle()
        elif k == 'r': self.resetar()
        elif k == 'c': self.centralizar()
        elif k == 's': self.abrir_configuracoes()

    def fechar_app(self):
        self.salvar_configuracoes()
        self.root.quit()

    def atualizar_display(self, txt):
        if self.tempo_atual_texto != txt:
            self.tempo_atual_texto = txt
            self.redesenhar_texto()

    def atualizar_cronometro(self):
        while True:
            if self.rodando and self.root.winfo_exists():
                delta = datetime.now() - self.inicio
                txt = str(delta).split('.')[0].zfill(8)
                self.root.after(0, self.atualizar_display, txt)
            time.sleep(0.1)

    def iniciar_threads(self):
        threading.Thread(target=self.atualizar_cronometro, daemon=True).start()

    def executar(self):
        self.root.mainloop()

if __name__ == "__main__":
    CronometroPremium().executar()