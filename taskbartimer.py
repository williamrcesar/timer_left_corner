import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import threading
import time
import json
import os

class CronometroPremium:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cronômetro Premium")
        
        # Arquivo de configurações
        self.config_file = "cronometro_config.json"
        
        # Configurações padrão
        self.config = {
            "largura": 280,
            "altura": 80,
            "tamanho_fonte": 32,
            "fonte_familia": "Windows",
            "cor_texto": "#FFFFFF",
            "tipo_fundo": "preto",
            "transparencia": 0.95,
            "pos_x": 100,
            "pos_y": 100
        }
        
        # Carregar configurações salvas
        self.carregar_configuracoes()
        
        # Melhorar qualidade DPI (pode ser ajustado para telas de alta resolução)
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass # Funciona apenas no Windows
        
        # Obter dimensões da tela
        self.largura_tela = self.root.winfo_screenwidth()
        self.altura_tela = self.root.winfo_screenheight()
        
        # Variáveis do cronômetro
        self.inicio = None
        self.pausado = False
        self.tempo_pausado = timedelta(0)
        self.rodando = False
        self.tempo_atual_texto = "00:00:00"
        
        # Variáveis de interface
        self.main_frame = None # Inicializa como None
        self.drag_data = {"x": 0, "y": 0}
        self.config_window = None
        self.botoes_fonte = {} # Para atualizar o estado visual dos botões de fonte
        self.botoes_fundo = {} # Para atualizar o estado visual dos botões de fundo
        
        # Configurar janela principal
        self.setup_janela()
        self.setup_ui()
        
        # Iniciar threads
        self.iniciar_threads()
    
    def carregar_configuracoes(self):
        """Carrega configurações do arquivo"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config_salva = json.load(f)
                    self.config.update(config_salva)
        except:
            pass
    
    def salvar_configuracoes(self):
        """Salva configurações no arquivo automaticamente"""
        try:
            self.config["pos_x"] = self.root.winfo_x()
            self.config["pos_y"] = self.root.winfo_y()
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4) # Usei indent 4 para melhor leitura
        except:
            pass
    
    def calcular_dimensoes(self):
        """Calcula dimensões baseadas no tamanho da fonte"""
        base_width = max(280, self.config["tamanho_fonte"] * 9)
        base_height = max(80, self.config["tamanho_fonte"] * 2.5)
        
        self.config["largura"] = int(base_width)
        self.config["altura"] = int(base_height)
    
    def setup_janela(self):
        """Configura a janela principal"""
        self.calcular_dimensoes()
        
        self.root.geometry(f"{self.config['largura']}x{self.config['altura']}+{self.config['pos_x']}+{self.config['pos_y']}")
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        self.root.resizable(False, False)
        
        self.aplicar_fundo()
    
    def aplicar_fundo(self):
        """Aplica o tipo de fundo selecionado"""
        tipo = self.config["tipo_fundo"]
        
        if tipo == "transparente":
            self.root.configure(bg='black')
            self.root.wm_attributes('-transparentcolor', 'black')
            self.root.wm_attributes('-alpha', self.config["transparencia"])
        else:
            cores_fundo = {
                "preto": "#000000", "cinza_escuro": "#1a1a1a", "cinza": "#2d2d2d",
                "azul_escuro": "#0f1419", "azul": "#1e3a8a", "verde_escuro": "#0d1b0d",
                "verde": "#166534", "roxo_escuro": "#1a0d2e", "roxo": "#7c3aed",
                "vermelho_escuro": "#2d0a0a", "vermelho": "#dc2626", "branco": "#ffffff"
            }
            cor = cores_fundo.get(tipo, "#000000")
            self.root.configure(bg=cor)
            self.root.wm_attributes('-transparentcolor', '')
            self.root.wm_attributes('-alpha', 1.0)
    
    def setup_ui(self):
        """Configura a interface principal"""
        ### CORREÇÃO 2: Destruir apenas o frame principal, não todos os widgets filhos de root.
        ### Isso impede que a janela de configurações seja fechada.
        if self.main_frame and self.main_frame.winfo_exists():
            self.main_frame.destroy()
        
        # Determinar cor de fundo para os widgets
        if self.config["tipo_fundo"] == "transparente":
            bg_cor = 'black'
        else:
            cores_fundo = {
                "preto": "#000000", "cinza_escuro": "#1a1a1a", "cinza": "#2d2d2d",
                "azul_escuro": "#0f1419", "azul": "#1e3a8a", "verde_escuro": "#0d1b0d",
                "verde": "#166534", "roxo_escuro": "#1a0d2e", "roxo": "#7c3aed",
                "vermelho_escuro": "#2d0a0a", "vermelho": "#dc2626", "branco": "#ffffff"
            }
            bg_cor = cores_fundo.get(self.config["tipo_fundo"], "#000000")
        
        self.main_frame = tk.Frame(self.root, bg=bg_cor)
        self.main_frame.pack(fill='both', expand=True)
        
        fonte_info = self.obter_fonte_hd()
        
        self.label_tempo = tk.Label(
            self.main_frame, text=self.tempo_atual_texto, font=fonte_info,
            fg=self.config["cor_texto"], bg=bg_cor, justify='center',
            bd=0, highlightthickness=0, anchor='center'
        )
        self.label_tempo.pack(fill='both', expand=True, padx=0, pady=0)
        
        self.setup_eventos()
    
    def obter_fonte_hd(self):
        """Retorna a fonte configurada com melhor qualidade."""
        familia = self.config["fonte_familia"]
        tamanho = self.config["tamanho_fonte"]
        
        ### CORREÇÃO 1: Remover as chaves "{}" dos nomes de fontes.
        ### Isso corrige o TclError e permite que as fontes de alta qualidade sejam carregadas.
        fontes = {
            "Digital": ("Consolas", tamanho, "bold"),
            "Windows": ("Segoe UI", tamanho, "normal"),
            "Moderna": ("Calibri", tamanho, "bold"),
            "Clássica": ("Times New Roman", tamanho, "bold"),
            "Técnica": ("Courier New", tamanho, "bold"),
            "Elegante": ("Georgia", tamanho, "bold"),
            "Simples": ("Arial", tamanho, "bold"),
            "Mono": ("Lucida Console", tamanho, "bold"),
            "System": ("Tahoma", tamanho, "bold") # Troquei "MS Sans Serif" por "Tahoma" para melhor qualidade
        }
        
        return fontes.get(familia, ("Segoe UI", tamanho, "normal"))
    
    def setup_eventos(self):
        """Configura eventos de mouse e teclado"""
        # Os widgets são recriados, então os eventos precisam ser vinculados aos novos.
        widgets = [self.root, self.main_frame, self.label_tempo]
        
        for widget in widgets:
            widget.bind('<Button-1>', self.iniciar_drag)
            widget.bind('<B1-Motion>', self.arrastar)
            widget.bind('<Button-3>', self.mostrar_menu_contexto)
        
        self.root.bind('<KeyPress>', self.processar_tecla)
        self.root.focus_set()

    def mostrar_menu_contexto(self, event):
        """Mostra menu de contexto"""
        menu = tk.Menu(self.root, tearoff=0, bg='#2d2d2d', fg='white',
                       activebackground='#404040', activeforeground='white',
                       relief='flat', bd=1, font=('Segoe UI', 10))
        
        label_iniciar = "▶️ Continuar" if self.pausado else "▶️ Iniciar"
        label_pausar = "⏸️ Pausar"
        
        if self.rodando:
            menu.add_command(label=label_pausar, command=self.toggle_cronometro)
        else:
            menu.add_command(label=label_iniciar, command=self.toggle_cronometro)

        menu.add_command(label="🔄 Resetar", command=self.resetar_cronometro)
        menu.add_separator()
        menu.add_command(label="⚙️ Configurações", command=self.abrir_configuracoes)
        menu.add_separator()
        menu.add_command(label="❌ Sair", command=self.fechar_app)
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def abrir_configuracoes(self):
        """Abre a janela de configurações"""
        if self.config_window and self.config_window.winfo_exists():
            self.config_window.lift()
            self.config_window.focus_force()
            return
        
        self.config_window = tk.Toplevel(self.root)
        self.config_window.title("Configurações do Cronômetro")
        self.config_window.configure(bg='#1a1a1a')
        self.config_window.attributes('-topmost', True)
        
        largura_config, altura_config = 520, 750
        x = (self.largura_tela - largura_config) // 2
        y = (self.altura_tela - altura_config) // 2
        self.config_window.geometry(f"{largura_config}x{altura_config}+{x}+{y}")
        self.config_window.minsize(largura_config, altura_config)
        
        self.config_window.protocol("WM_DELETE_WINDOW", self.fechar_configuracoes)
        
        self.setup_janela_configuracoes_tempo_real()

    def setup_janela_configuracoes_tempo_real(self):
        """Cria os widgets da janela de configurações"""
        main_frame = tk.Frame(self.config_window, bg='#1a1a1a')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # --- Seção Fonte ---
        fonte_frame = tk.LabelFrame(main_frame, text="🔤 Configurações de Fonte", font=('Segoe UI', 12, 'bold'), fg='#f0f6fc', bg='#1a1a1a', relief='groove', bd=2)
        fonte_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(fonte_frame, text="Família da Fonte:", font=('Segoe UI', 10), fg='#8b949e', bg='#1a1a1a').pack(anchor='w', padx=10, pady=(10, 5))
        fontes_container = tk.Frame(fonte_frame, bg='#1a1a1a')
        fontes_container.pack(fill='x', padx=10, pady=(0, 10))
        fontes = ["Digital", "Windows", "Moderna", "Clássica", "Técnica", "Elegante", "Simples", "Mono", "System"]
        self.botoes_fonte = {}
        for i, fonte in enumerate(fontes):
            if i % 3 == 0:
                linha_frame = tk.Frame(fontes_container, bg='#1a1a1a')
                linha_frame.pack(fill='x', pady=2)
            btn = tk.Button(linha_frame, text=fonte, font=('Segoe UI', 9), fg='white', border=0, command=lambda f=fonte: self.mudar_fonte_familia_tempo_real(f), relief='flat', cursor='hand2', pady=8)
            btn.pack(side='left', padx=2, fill='x', expand=True)
            self.botoes_fonte[fonte] = btn
        self.atualizar_botoes_fonte_visual() # Atualiza a cor inicial
        
        tamanho_container = tk.Frame(fonte_frame, bg='#1a1a1a')
        tamanho_container.pack(fill='x', padx=10, pady=(10, 10))
        tk.Label(tamanho_container, text="Tamanho:", font=('Segoe UI', 10), fg='#8b949e', bg='#1a1a1a').pack(side='left')
        
        tk.Button(tamanho_container, text="−", font=('Segoe UI', 14, 'bold'), bg='#3d3d3d', fg='white', border=0, width=3, command=self.diminuir_fonte_tempo_real, relief='flat', cursor='hand2').pack(side='right', padx=2)
        self.label_tamanho = tk.Label(tamanho_container, text=str(self.config["tamanho_fonte"]), font=('Segoe UI', 14, 'bold'), fg='#58a6ff', bg='#1a1a1a', width=4)
        self.label_tamanho.pack(side='right', padx=5)
        tk.Button(tamanho_container, text="+", font=('Segoe UI', 14, 'bold'), bg='#3d3d3d', fg='white', border=0, width=3, command=self.aumentar_fonte_tempo_real, relief='flat', cursor='hand2').pack(side='right', padx=2)

        # --- Seção Cores ---
        cores_frame = tk.LabelFrame(main_frame, text="🎨 Cor dos Números", font=('Segoe UI', 12, 'bold'), fg='#f0f6fc', bg='#1a1a1a', relief='groove', bd=2)
        cores_frame.pack(fill='x', pady=(0, 20))
        cores_container = tk.Frame(cores_frame, bg='#1a1a1a')
        cores_container.pack(fill='x', padx=10, pady=10)
        cores = [("Verde", "#00FF88"), ("Azul", "#58a6ff"), ("Amarelo", "#f9e71e"), ("Vermelho", "#ff6b6b"), ("Branco", "#FFFFFF"), ("Roxo", "#bc8cff"), ("Laranja", "#fd7e14"), ("Rosa", "#ff69b4")]
        for i, (nome, cor) in enumerate(cores):
            if i % 4 == 0:
                linha_cores = tk.Frame(cores_container, bg='#1a1a1a')
                linha_cores.pack(fill='x', pady=2)
            btn = tk.Button(linha_cores, text=" ", font=('Segoe UI', 9, 'bold'), bg=cor, border=1, relief='solid', command=lambda c=cor: self.mudar_cor_tempo_real(c), cursor='hand2', width=10, height=2)
            btn.pack(side='left', padx=5, fill='x', expand=True)

        # --- Seção Fundo ---
        fundo_frame = tk.LabelFrame(main_frame, text="🖼️ Fundo da Janela", font=('Segoe UI', 12, 'bold'), fg='#f0f6fc', bg='#1a1a1a', relief='groove', bd=2)
        fundo_frame.pack(fill='x', pady=(0, 20))
        fundo_container = tk.Frame(fundo_frame, bg='#1a1a1a')
        fundo_container.pack(fill='x', padx=10, pady=10)
        fundos = [("Transparente", "transparente"), ("Preto", "preto"), ("Cinza Escuro", "cinza_escuro"), ("Cinza", "cinza"), ("Azul Escuro", "azul_escuro"), ("Azul", "azul"), ("Verde Escuro", "verde_escuro"), ("Verde", "verde"), ("Branco", "branco")]
        self.botoes_fundo = {}
        for i, (nome, tipo) in enumerate(fundos):
            if i % 3 == 0:
                linha_fundos = tk.Frame(fundo_container, bg='#1a1a1a')
                linha_fundos.pack(fill='x', pady=2)
            btn = tk.Button(linha_fundos, text=nome, font=('Segoe UI', 9), fg='white', border=0, command=lambda t=tipo: self.mudar_fundo_tempo_real(t), relief='flat', cursor='hand2', pady=8)
            btn.pack(side='left', padx=2, fill='x', expand=True)
            self.botoes_fundo[tipo] = btn
        self.atualizar_botoes_fundo_visual()

        self.trans_frame = tk.Frame(fundo_frame, bg='#1a1a1a')
        if self.config["tipo_fundo"] == "transparente":
            self.trans_frame.pack(fill='x', padx=10, pady=(0, 10))
            self.criar_controles_transparencia()
            
        botoes_frame = tk.Frame(main_frame, bg='#1a1a1a')
        botoes_frame.pack(fill='x', pady=(20, 0), side='bottom')
        tk.Button(botoes_frame, text="📍 Centralizar Cronômetro", font=('Segoe UI', 11, 'bold'), bg='#0969da', fg='white', border=0, command=self.centralizar, relief='flat', cursor='hand2', pady=10).pack(fill='x', pady=5)
        tk.Label(botoes_frame, text="💾 Configurações salvas automaticamente", font=('Segoe UI', 9, 'italic'), fg='#7ce38b', bg='#1a1a1a').pack(pady=10)

    def criar_controles_transparencia(self):
        """Cria os widgets de controle de transparência"""
        for widget in self.trans_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.trans_frame, text="Nível de Transparência:", font=('Segoe UI', 10), fg='#8b949e', bg='#1a1a1a').pack(anchor='w', pady=(5, 5))
        self.trans_slider = ttk.Scale(self.trans_frame, from_=0.3, to=1.0, value=self.config['transparencia'], orient='horizontal', command=lambda v: self.mudar_transparencia_tempo_real(float(v)))
        self.trans_slider.pack(fill='x', padx=5)

    # --- Métodos de configuração em tempo real ---
    def mudar_fonte_familia_tempo_real(self, familia):
        self.config["fonte_familia"] = familia
        self.atualizar_interface_tempo_real()
        self.atualizar_botoes_fonte_visual()
        self.salvar_configuracoes()
    
    def aumentar_fonte_tempo_real(self):
        if self.config["tamanho_fonte"] < 120:
            self.config["tamanho_fonte"] += 2
            self.atualizar_interface_tempo_real()
            self.label_tamanho.config(text=str(self.config["tamanho_fonte"]))
            self.salvar_configuracoes()
    
    def diminuir_fonte_tempo_real(self):
        if self.config["tamanho_fonte"] > 16:
            self.config["tamanho_fonte"] -= 2
            self.atualizar_interface_tempo_real()
            self.label_tamanho.config(text=str(self.config["tamanho_fonte"]))
            self.salvar_configuracoes()
    
    def mudar_cor_tempo_real(self, cor):
        self.config["cor_texto"] = cor
        if hasattr(self, 'label_tempo'):
            self.label_tempo.config(fg=cor)
        self.salvar_configuracoes()
    
    def mudar_fundo_tempo_real(self, tipo):
        self.config["tipo_fundo"] = tipo
        self.aplicar_fundo()
        self.atualizar_interface_tempo_real()
        self.atualizar_botoes_fundo_visual()
        
        if tipo == "transparente":
            if not self.trans_frame.winfo_ismapped():
                self.trans_frame.pack(fill='x', padx=10, pady=(5, 10))
                self.criar_controles_transparencia()
        else:
            if self.trans_frame.winfo_ismapped():
                self.trans_frame.pack_forget()
        
        self.salvar_configuracoes()
    
    def mudar_transparencia_tempo_real(self, valor):
        valor = round(valor, 2)
        self.config["transparencia"] = valor
        if self.config["tipo_fundo"] == "transparente":
            self.root.wm_attributes('-alpha', valor)
        # Salva apenas quando o mouse é liberado (para não sobrecarregar o arquivo)
        if hasattr(self, 'trans_slider'):
             self.trans_slider.bind("<ButtonRelease-1>", lambda e: self.salvar_configuracoes())
    
    def atualizar_botoes_fonte_visual(self):
        if self.config_window and self.config_window.winfo_exists():
            for fonte, btn in self.botoes_fonte.items():
                cor = '#58a6ff' if fonte == self.config["fonte_familia"] else '#2d2d2d'
                btn.config(bg=cor)
    
    def atualizar_botoes_fundo_visual(self):
        if self.config_window and self.config_window.winfo_exists():
            for tipo, btn in self.botoes_fundo.items():
                cor = '#58a6ff' if tipo == self.config["tipo_fundo"] else '#2d2d2d'
                btn.config(bg=cor)
    
    def atualizar_interface_tempo_real(self):
        """Atualiza a interface principal sem fechar as configurações"""
        try:
            if hasattr(self, 'label_tempo'):
                self.tempo_atual_texto = self.label_tempo.cget('text')
            
            self.calcular_dimensoes()
            self.root.geometry(f"{self.config['largura']}x{self.config['altura']}+{self.root.winfo_x()}+{self.root.winfo_y()}")
            self.setup_ui()
        except Exception as e:
            print(f"Erro ao atualizar interface: {e}")

    # --- Controles da Janela e Cronômetro ---
    def iniciar_drag(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
    
    def arrastar(self, event):
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        x = self.root.winfo_x() + dx
        y = self.root.winfo_y() + dy
        self.root.geometry(f"+{x}+{y}")
    
    def processar_tecla(self, event):
        if event.keysym.lower() == 'space': self.toggle_cronometro()
        elif event.keysym.lower() == 'r': self.resetar_cronometro()
        elif event.keysym.lower() == 'c': self.centralizar()
    
    def toggle_cronometro(self):
        if not self.rodando:
            self.inicio = datetime.now() - self.tempo_pausado if self.pausado else datetime.now()
            self.rodando, self.pausado = True, False
        else:
            self.rodando, self.pausado = False, True
            self.tempo_pausado = datetime.now() - self.inicio
    
    def resetar_cronometro(self):
        self.inicio, self.rodando, self.pausado = None, False, False
        self.tempo_pausado = timedelta(0)
        self.tempo_atual_texto = "00:00:00"
        self.atualizar_display("00:00:00")
    
    def centralizar(self, event=None):
        self.root.update_idletasks()
        x = (self.largura_tela - self.root.winfo_width()) // 2
        y = 100
        self.root.geometry(f"+{x}+{y}")
        self.salvar_configuracoes()
    
    def fechar_configuracoes(self):
        if self.config_window:
            self.salvar_configuracoes()
            self.config_window.destroy()
            self.config_window = None
    
    def fechar_app(self):
        self.salvar_configuracoes()
        self.root.quit()
    
    # --- Threads e Atualização ---
    def atualizar_cronometro(self):
        while True:
            try:
                if self.rodando and not self.pausado and self.inicio:
                    delta = datetime.now() - self.inicio
                    self.tempo_atual_texto = str(delta).split('.')[0].zfill(8)
                    self.root.after(0, self.atualizar_display, self.tempo_atual_texto)
                time.sleep(0.1)
            except:
                break
    
    def atualizar_display(self, texto):
        try:
            if self.label_tempo and self.label_tempo.winfo_exists():
                self.label_tempo.config(text=texto)
        except:
            pass
    
    def iniciar_threads(self):
        threading.Thread(target=self.atualizar_cronometro, daemon=True).start()
    
    def executar(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CronometroPremium()
    app.executar()