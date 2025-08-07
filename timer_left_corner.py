import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from datetime import datetime, timedelta
import threading, time, json, os, sys
import subprocess
import platform
import os
from dotenv import load_dotenv

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
            "espacamento_letras": 0, "sempre_visivel": True,
            "auto_iniciar": False, "som_notificacao": False,
            "formato_tempo": "HH:MM:SS", "mostrar_milissegundos": False,
            "tema": "escuro", "animacao": True, "minimizar_tray": False,
            "atalhos_globais": True, "auto_salvar": True,
            "intervalo_atualizacao": 100, "cor_fundo_solido": "#1a1a1a",
            "forma_caixa": "retangulo", "borda_arredondada": 10,
            "largura_personalizada": True, "altura_personalizada": True,
            "cor_fundo_personalizada": "#2d2d2d", "gradiente_ativo": False,
            "cor_gradiente_inicio": "#1a1a1a", "cor_gradiente_fim": "#3a3a3a"
        }
        self.carregar_configuracoes()

        self.inicio = None
        self.pausado = False
        self.tempo_pausado = timedelta(0)
        self.rodando = False
        self.tempo_atual_texto = "00:00:00"
        self.config_window = None
        self.topmost_thread_running = True

        self.setup_janela()
        self.setup_ui()
        self.iniciar_threads()
        
    def abrir_url_no_chrome(self):
        """
        Carrega as configurações de um arquivo .env e abre uma URL específica
        em um perfil do Google Chrome.
        """
        try:
            # Carrega as variáveis do .env
            load_dotenv()

            chrome_path = os.getenv("CHROME_PATH")
            profile_name = os.getenv("CHROME_PROFILE")
            url = os.getenv("TARGET_URL")

            # Verifica se as variáveis foram carregadas
            if not all([chrome_path, profile_name, url]):
                messagebox.showerror(
                    "Erro de Configuração",
                    "Verifique se o arquivo .env existe e contém as variáveis "
                    "CHROME_PATH, CHROME_PROFILE e TARGET_URL."
                )
                return
            
            # Verifica se o caminho do Chrome existe
            if not os.path.exists(chrome_path):
                 messagebox.showerror(
                    "Erro de Caminho",
                    f"O caminho para o Chrome não foi encontrado:\n{chrome_path}\n"
                    "Verifique a variável CHROME_PATH no arquivo .env."
                )
                 return

            # Comando para abrir o Chrome com o perfil e a URL
            subprocess.Popen([
                chrome_path,
                f"--profile-directory={profile_name}",
                url
            ])
        except NameError:
             messagebox.showerror(
                "Erro de Dependência",
                "A biblioteca 'python-dotenv' não foi encontrada.\n"
                "Por favor, instale-a com: pip install python-dotenv"
            )
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro ao tentar abrir o Chrome: {e}")

    def abrir_url_no_chrome_github(self):
        """
        Carrega as configurações de um arquivo .env e abre uma URL específica
        em um perfil do Google Chrome.
        """
        try:
            # Carrega as variáveis do .env
            load_dotenv()

            chrome_path = os.getenv("CHROME_PATH")
            profile_name = os.getenv("CHROME_PROFILE_GITHUB")
            url = os.getenv("TARGET_URL_GITHUB")

            # Verifica se as variáveis foram carregadas
            if not all([chrome_path, profile_name, url]):
                messagebox.showerror(
                    "Erro de Configuração",
                    "Verifique se o arquivo .env existe e contém as variáveis "
                    "CHROME_PATH, CHROME_PROFILE e TARGET_URL."
                )
                return
            
            # Verifica se o caminho do Chrome existe
            if not os.path.exists(chrome_path):
                 messagebox.showerror(
                    "Erro de Caminho",
                    f"O caminho para o Chrome não foi encontrado:\n{chrome_path}\n"
                    "Verifique a variável CHROME_PATH no arquivo .env."
                )
                 return

            # Comando para abrir o Chrome com o perfil e a URL
            subprocess.Popen([
                chrome_path,
                f"--profile-directory={profile_name}",
                url
            ])
        except NameError:
             messagebox.showerror(
                "Erro de Dependência",
                "A biblioteca 'python-dotenv' não foi encontrada.\n"
                "Por favor, instale-a com: pip install python-dotenv"
            )
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro ao tentar abrir o Chrome: {e}")

    def carregar_configuracoes(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
            except:
                pass

    def salvar_configuracoes(self):
        if self.config.get("auto_salvar", True):
            try:
                self.config["pos_x"] = self.root.winfo_x()
                self.config["pos_y"] = self.root.winfo_y()
                with open(self.config_file, "w") as f:
                    json.dump(self.config, f, indent=4)
            except:
                pass

    def setup_janela(self):
        self.root.geometry(
            f"{self.config['largura']}x{self.config['altura']}+{self.config['pos_x']}+{self.config['pos_y']}"
        )
        self.root.overrideredirect(True)
        
        # Sistema mais robusto para manter sempre em cima
        if self.config.get("sempre_visivel", True):
            self.root.attributes('-topmost', True)
            self.root.lift()
            self.root.focus_force()
        
        self.aplicar_fundo()
        
        # Auto iniciar se configurado
        if self.config.get("auto_iniciar", False):
            self.root.after(1000, self.toggle)

    def manter_sempre_visivel(self):
        """Thread para garantir que a janela fique sempre visível"""
        while self.topmost_thread_running:
            try:
                if self.config.get("sempre_visivel", True) and self.root.winfo_exists():
                    self.root.attributes('-topmost', True)
                    self.root.lift()
                time.sleep(2)  # Verifica a cada 2 segundos
            except:
                break

    def aplicar_fundo(self):
        # Define a unique, unlikely-to-be-used color for transparency
        # CORRIGIDO: Alterado para preto puro para evitar o contorno magenta
        TRANSPARENT_KEY_COLOR = '#000000' 

        if self.config["tipo_fundo"] == "transparente":
            self.root.configure(bg=TRANSPARENT_KEY_COLOR) # Set root background to the key color
            self.root.wm_attributes('-transparentcolor', TRANSPARENT_KEY_COLOR)
            self.root.wm_attributes('-alpha', self.config["transparencia"])
        else:
            cor_fundo = self.config.get("cor_fundo_personalizada", "#1a1a1a")
            self.root.configure(bg=cor_fundo)
            self.root.wm_attributes('-transparentcolor', '')
            self.root.wm_attributes('-alpha', 1.0)

    def setup_ui(self):
        # CORRIGIDO: Canvas background agora usa a nova cor chave de transparência (preto)
        TRANSPARENT_KEY_COLOR = '#000000' # Pure black
        bg_canvas = TRANSPARENT_KEY_COLOR if self.config["tipo_fundo"] == "transparente" else self.config.get("cor_fundo_personalizada", "#1a1a1a")
        
        if hasattr(self, 'canvas') and self.canvas.winfo_exists():
            self.canvas.destroy()
    
        self.canvas = tk.Canvas(self.root, bg=bg_canvas, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
    
        # Aplicar forma personalizada se não for transparente
        if self.config["tipo_fundo"] != "transparente":
            self.aplicar_forma_personalizada()
    
        self.canvas.bind("<Configure>", lambda e: self.redesenhar_texto())
        self.bind_eventos()
        self.redesenhar_texto()

    def aplicar_forma_personalizada(self):
        """Aplica forma personalizada ao fundo quando não é transparente"""
        if self.config["tipo_fundo"] == "transparente":
            return

        def desenhar_fundo():
            if not self.canvas.winfo_exists():
                return
    
            w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
            if w <= 1 or h <= 1:
                self.canvas.after(50, desenhar_fundo)  # Tenta novamente
                return
    
            # Limpar canvas completamente
            self.canvas.delete("all")
    
            forma = self.config.get("forma_caixa", "retangulo")
            cor_fundo = self.config.get("cor_fundo_personalizada", "#1a1a1a")
            # print(f"Desenhando fundo: forma={forma}, cor={cor_fundo}") # Debug print
    
            # Aplicar cor de fundo do canvas (importante para áreas não preenchidas pela forma)
            self.canvas.configure(bg=cor_fundo) 
    
            if self.config.get("gradiente_ativo", False):
                self.desenhar_gradiente(w, h)
            elif forma == "retangulo":
                raio = self.config.get("borda_arredondada", 10)
                if raio > 0:
                    self.desenhar_retangulo_arredondado(w, h, raio, cor_fundo)
                else:
                    self.canvas.create_rectangle(0, 0, w, h, fill=cor_fundo, outline="", tags="fundo")
            elif forma == "oval":
                self.canvas.create_oval(0, 0, w, h, fill=cor_fundo, outline="", tags="fundo")
            elif forma == "losango":
                self.canvas.create_polygon(w//2, 0, w, h//2, w//2, h, 0, h//2, 
                                         fill=cor_fundo, outline="", tags="fundo")
            elif forma == "hexagono":
                self.desenhar_hexagono(w, h, cor_fundo)
    
            # Redesenhar o texto por cima
            self.redesenhar_texto()

        self.canvas.after(10, desenhar_fundo)

    def desenhar_retangulo_arredondado(self, w, h, raio, cor):
        """Desenha um retângulo com bordas arredondadas de forma mais robusta"""
        raio = min(raio, w/2, h/2) # Limitar o raio para não exceder as dimensões
        
        points = [
            raio, 0,
            w - raio, 0,
            w, raio,
            w, h - raio,
            w - raio, h,
            raio, h,
            0, h - raio,
            0, raio
        ]
        self.canvas.create_polygon(points, fill=cor, outline="", smooth=True, tags="fundo")


    def desenhar_hexagono(self, w, h, cor):
        """Desenha um hexágono"""
        cx, cy = w//2, h//2
        size_x = w//3
        size_y = h//3
        points = [
            cx, cy-size_y,           # topo
            cx+size_x, cy-size_y//2, # direita superior
            cx+size_x, cy+size_y//2, # direita inferior
            cx, cy+size_y,           # baixo
            cx-size_x, cy+size_y//2, # esquerda inferior
            cx-size_x, cy-size_y//2  # esquerda superior
        ]
        self.canvas.create_polygon(points, fill=cor, outline="", tags="fundo")

    def desenhar_gradiente(self, w, h):
        """Desenha um fundo com gradiente"""
        cor_inicio = self.config.get("cor_gradiente_inicio", "#1a1a1a")
        cor_fim = self.config.get("cor_gradiente_fim", "#3a3a3a")
    
        # Converter cores hex para RGB
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
        def rgb_to_hex(rgb):
            return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
        try:
            rgb_inicio = hex_to_rgb(cor_inicio)
            rgb_fim = hex_to_rgb(cor_fim)
        except:
            # Fallback para cores padrão se houver erro
            rgb_inicio = (26, 26, 26)
            rgb_fim = (58, 58, 58)
    
        # Criar gradiente vertical
        for i in range(h):
            ratio = i / h if h > 0 else 0
            r = int(rgb_inicio[0] + (rgb_fim[0] - rgb_inicio[0]) * ratio)
            g = int(rgb_inicio[1] + (rgb_fim[1] - rgb_inicio[1]) * ratio)
            b = int(rgb_inicio[2] + (rgb_fim[2] - rgb_inicio[2]) * ratio)
            cor_linha = rgb_to_hex((r, g, b))
            self.canvas.create_line(0, i, w, i, fill=cor_linha, tags="fundo")

    def bind_eventos(self):
        for w in (self.root, self.canvas):
            w.bind("<Button-1>", self.iniciar_drag)
            w.bind("<B1-Motion>", self.arrastar)
            w.bind("<Button-3>", self.mostrar_menu_contexto)
            w.bind("<Double-Button-1>", lambda e: self.toggle())
        
        if self.config.get("atalhos_globais", True):
            self.root.bind("<KeyPress>", self.processar_tecla)
            self.root.focus_set()

    def obter_fonte_pillow(self):
        fam = self.config["fonte_familia"]
        mapeamento = {
            "Digital": "digital-7.mono.ttf", "Windows": "segoeui.ttf",
            "Moderna": "calibri.ttf", "Clássica": "times.ttf",
            "Técnica": "cour.ttf", "Elegante": "georgia.ttf",
            "Simples": "arial.ttf", "Mono": "lucon.ttf", "System": "tahoma.ttf",
            "Impact": "impact.ttf", "Comic": "comic.ttf"
        }
        try:
            return ImageFont.truetype(mapeamento.get(fam, "arial.ttf"), self.config["tamanho_fonte"])
        except:
            return ImageFont.load_default()

    def formatar_tempo(self, delta):
        """Formata o tempo de acordo com as configurações"""
        total_seconds = int(delta.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        formato = self.config.get("formato_tempo", "HH:MM:SS")
        
        if formato == "MM:SS" and hours == 0:
            texto = f"{minutes:02d}:{seconds:02d}"
        elif formato == "HH:MM":
            texto = f"{hours:02d}:{minutes:02d}"
        else:  # HH:MM:SS (padrão)
            texto = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        if self.config.get("mostrar_milissegundos", False):
            millis = int(delta.microseconds / 1000)
            texto += f".{millis:03d}"
        
        return texto

    def desenhar_texto(self, txt):
        if not self.canvas.winfo_exists():
            return
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        
        # Só limpa o texto, não o fundo
        self.canvas.delete("texto")
        
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        font = self.obter_fonte_pillow()
        
        cor_b = self.config["cor_borda"]
        cor_p = self.config["cor_preenchimento"]
        stroke = self.config["espessura_borda"]
        
        # CORRIGIDO: Ajusta a cor da borda do texto para evitar o halo magenta quando transparente
        # Agora, a cor da borda do texto será a mesma do preenchimento quando transparente,
        # e o anti-aliasing ocorrerá com o fundo preto transparente.
        if self.config["tipo_fundo"] == "transparente":
            stroke_fill_color = cor_p 
        else:
            stroke_fill_color = cor_b
        
        # Efeito de animação (pulsação)
        if self.config.get("animacao", True) and self.rodando:
            import math
            pulse = abs(math.sin(time.time() * 2)) * 0.1 + 0.9
            font_size = int(self.config["tamanho_fonte"] * pulse)
            try:
                font = ImageFont.truetype(font.path, font_size)
            except:
                pass
        
        draw.text((w/2, h/2), txt, font=font, fill=cor_p,
                  stroke_width=int(stroke), stroke_fill=stroke_fill_color, anchor="mm")
        self._photo = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, image=self._photo, anchor="nw", tags="texto")

    def redesenhar_texto(self):
        self.desenhar_texto(self.tempo_atual_texto)

    def mostrar_menu_contexto(self, event):
        cor_fundo = self.config.get("cor_fundo_personalizada", "#1a1a1a")
        m = tk.Menu(self.root, tearoff=0, bg=cor_fundo, fg='white')
        label = "⏸️ Pausar" if self.rodando else ("▶️ Continuar" if self.pausado else "▶️ Iniciar")
        m.add_command(label=label, command=self.toggle)
        m.add_command(label="🔄 Resetar", command=self.resetar)
        m.add_separator()
        m.add_command(label="🔗 Abrir Planilha", command=self.abrir_url_no_chrome)
        m.add_command(label="🐙 GitHub Projetos", command=self.abrir_url_no_chrome_github)
        m.add_separator()
        # Submenu de tempo
        tempo_menu = tk.Menu(m, tearoff=0, bg=cor_fundo, fg='white')
        tempo_menu.add_command(label="📋 Copiar Tempo", command=self.copiar_tempo)
        tempo_menu.add_command(label="⏰ Definir Tempo", command=self.definir_tempo)
        m.add_cascade(label="⏱️ Tempo", menu=tempo_menu)
        
        # Submenu de visibilidade
        vis_menu = tk.Menu(m, tearoff=0, bg=cor_fundo, fg='white')
        vis_text = "❌ Desativar Sempre Visível" if self.config.get("sempre_visivel") else "✅ Ativar Sempre Visível"
        vis_menu.add_command(label=vis_text, command=self.toggle_sempre_visivel)
        vis_menu.add_command(label="📍 Centralizar", command=self.centralizar)
        vis_menu.add_command(label="🔒 Bloquear Posição", command=self.toggle_bloqueio)
        # m.add_cascade(label="👁️ Visibilidade", menu=vis_menu)
        
        m.add_separator()
        m.add_command(label="⚙️ Configurações", command=self.abrir_configuracoes)
        # m.add_command(label="🔧 Config Simples", command=self.criar_configuracoes_simples)  # Opção alternativa
        # m.add_command(label="🐛 Debug Config", command=self.debug_janela_config)  # Para debug
        # m.add_command(label="💾 Salvar Config", command=self.salvar_configuracoes)

        m.add_separator()
        m.add_command(label="❌ Sair", command=self.fechar_app)
        
        try:
            m.tk_popup(event.x_root, event.y_root)
        except Exception as e:
            print(f"Erro ao mostrar menu: {e}")

    def copiar_tempo(self):
        """Copia o tempo atual para a área de transferência"""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.tempo_atual_texto)
        self.root.update()

    def definir_tempo(self):
        """Permite definir um tempo específico"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Definir Tempo")
        dialog.geometry("300x150")
        dialog.configure(bg='#1e2227')
        dialog.attributes('-topmost', True)
        
        tk.Label(dialog, text="Formato: HH:MM:SS", fg='white', bg='#1e2227').pack(pady=10)
        
        entry = tk.Entry(dialog, font=('Segoe UI', 12), justify='center')
        entry.pack(pady=10)
        entry.insert(0, self.tempo_atual_texto)
        entry.focus()
        
        def aplicar():
            try:
                tempo_str = entry.get()
                partes = tempo_str.split(':')
                if len(partes) == 3:
                    h, m, s = map(int, partes)
                    delta = timedelta(hours=h, minutes=m, seconds=s)
                    self.inicio = datetime.now() - delta
                    self.tempo_pausado = delta
                    dialog.destroy()
            except:
                messagebox.showerror("Erro", "Formato inválido!")
        
        tk.Button(dialog, text="Aplicar", command=aplicar, bg='#0d6efd', fg='white').pack(pady=10)

    def toggle_sempre_visivel(self):
        """Alterna o modo sempre visível"""
        self.config["sempre_visivel"] = not self.config.get("sempre_visivel", True)
        if self.config["sempre_visivel"]:
            self.root.attributes('-topmost', True)
            self.root.lift()
        else:
            self.root.attributes('-topmost', False)
        self.salvar_configuracoes()

    def toggle_bloqueio(self):
        """Bloqueia/desbloqueia a posição da janela"""
        # Implementação futura para bloquear arrastar
        pass

    def abrir_configuracoes(self):
        try:
            # Força o fechamento da janela anterior se existir
            if hasattr(self, 'config_window') and self.config_window:
                try:
                    if self.config_window.winfo_exists():
                        self.config_window.destroy()
                except:
                    pass
                self.config_window = None
        
            # Pequena pausa para garantir que a janela anterior foi fechada
            self.root.after(50, self._criar_configuracoes_delayed)
        
        except Exception as e:
            print(f"Erro ao abrir configurações: {e}")
            # Força criação mesmo com erro
            self.root.after(100, self._criar_configuracoes_delayed)

    def _criar_configuracoes_delayed(self):
        """Cria a janela de configurações com delay para evitar problemas de timing"""
        try:
            self.config_window = None
            self.criar_janela_configuracoes()
        except Exception as e:
            print(f"Erro ao criar janela de configurações: {e}")

    def criar_janela_configuracoes(self):
        try:
            # Cria nova janela
            self.config_window = tk.Toplevel(self.root)
            self.config_window.title("Configurações Avançadas")
            self.config_window.configure(bg='#1e2227')
    
            # Configurações de janela mais robustas
            self.config_window.transient(self.root)  # Faz a janela ser filha da principal
            self.config_window.grab_set()  # Torna modal
    
            # Define tamanho fixo e centraliza
            width = 950
            height = 800  # AUMENTADO de 700 para 800 para melhor visualização das dimensões
            screen_width = self.config_window.winfo_screenwidth()
            screen_height = self.config_window.winfo_screenheight()
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            self.config_window.geometry(f'{width}x{height}+{x}+{y}')
        
            # Força a janela a aparecer
            self.config_window.lift()
            self.config_window.attributes('-topmost', True)
            self.config_window.focus_force()
        
            # Impede redimensionamento
            self.config_window.resizable(False, False)
    
            # Protocolo de fechamento
            self.config_window.protocol("WM_DELETE_WINDOW", self.fechar_configuracoes)
    
            # Notebook para abas
            notebook = ttk.Notebook(self.config_window)
            notebook.pack(fill='both', expand=True, padx=10, pady=10)

            # Aba 1: Aparência
            aba_aparencia = tk.Frame(notebook, bg='#1e2227')
            notebook.add(aba_aparencia, text="🎨 Aparência")
            self.criar_aba_aparencia(aba_aparencia)

            # Aba 2: Comportamento
            aba_comportamento = tk.Frame(notebook, bg='#1e2227')
            notebook.add(aba_comportamento, text="⚙️ Comportamento")
            self.criar_aba_comportamento(aba_comportamento)

            # Aba 3: Avançado
            aba_avancado = tk.Frame(notebook, bg='#1e2227')
            notebook.add(aba_avancado, text="🔧 Avançado")
            self.criar_aba_avancado(aba_avancado)
    
            # Força atualização final
            self.config_window.update()
            self.config_window.deiconify()  # Garante que a janela seja mostrada
    
            print("Janela de configurações criada com sucesso")
    
        except Exception as e:
            print(f"Erro crítico ao criar configurações: {e}")
            # Tenta criar uma versão simplificada
            self.criar_configuracoes_simples()

    def fechar_configuracoes(self):
        """Fecha a janela de configurações de forma segura"""
        try:
            if hasattr(self, 'config_window') and self.config_window:
                self.config_window.grab_release()  # Remove o grab modal
                self.config_window.destroy()
                self.config_window = None
        except:
            pass

    def criar_configuracoes_simples(self):
        """Versão simplificada das configurações em caso de erro"""
        try:
            self.config_window = tk.Toplevel(self.root)
            self.config_window.title("Configurações (Modo Simples)")
            self.config_window.configure(bg='#1e2227')
            self.config_window.geometry("400x300")
            self.config_window.attributes('-topmost', True)
            self.config_window.lift()
            self.config_window.focus_force()
        
            # Controles básicos
            frame = tk.Frame(self.config_window, bg='#1e2227')
            frame.pack(fill='both', expand=True, padx=20, pady=20)
        
            tk.Label(frame, text="Configurações Básicas", fg='white', bg='#1e2227', 
                    font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
            # Botões essenciais
            tk.Button(frame, text="📍 Centralizar", bg='#238636', fg='white', bd=0, pady=8,
                      command=self.centralizar).pack(fill='x', pady=5)
        
            tk.Button(frame, text="🔄 Resetar", bg='#dc3545', fg='white', bd=0, pady=8,
                      command=self.resetar).pack(fill='x', pady=5)
        
            tk.Button(frame, text="💾 Salvar Config", bg='#0d6efd', fg='white', bd=0, pady=8,
                      command=self.salvar_configuracoes).pack(fill='x', pady=5)
        
            tk.Button(frame, text="❌ Fechar", bg='#6c757d', fg='white', bd=0, pady=8,
                      command=self.fechar_configuracoes).pack(fill='x', pady=5)
        
            print("Configurações simples criadas")
        
        except Exception as e:
            print(f"Erro mesmo na versão simples: {e}")

    def debug_janela_config(self):
        """Método para debug da janela de configurações"""
        try:
            if hasattr(self, 'config_window'):
                if self.config_window is None:
                    print("config_window é None")
                else:
                    try:
                        exists = self.config_window.winfo_exists()
                        print(f"Estado da janela: {self.config_window.state()}")
                        print(f"Posição: {self.config_window.winfo_x()}, {self.config_window.winfo_y()}")
                    except Exception as e:
                        print(f"Erro ao verificar janela: {e}")
            else:
                print("config_window não existe como atributo")
        except Exception as e:
            print(f"Erro no debug: {e}")

    def criar_aba_aparencia(self, parent):
        # Adicionar scrollbar para acessar todas as seções
        main_frame = tk.Frame(parent, bg='#1e2227')
        main_frame.pack(fill='both', expand=True)
        
        # Canvas com scrollbar
        canvas = tk.Canvas(main_frame, bg='#1e2227', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1e2227')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        container = scrollable_frame

        # Seção de Fontes
        font_lb = tk.LabelFrame(container, text="🔤 Fonte e Texto", font=('Segoe UI', 11, 'bold'),
                                fg='#c9d1d9', bg='#1e2227', relief='groove', bd=1)
        font_lb.pack(fill='x', pady=10, padx=15)

        # Família da fonte
        tk.Label(font_lb, text="Família:", fg='#c9d1d9', bg='#1e2227').grid(row=0, column=0, sticky='w', padx=10, pady=5)
        fam_frame = tk.Frame(font_lb, bg='#1e2227')
        fam_frame.grid(row=0, column=1, sticky='ew', padx=10, pady=5)
        fontes = ["Digital", "Windows", "Moderna", "Clássica", "Técnica", "Elegante", "Simples", "Mono", "System", "Impact", "Comic"]
        self.fam_vars = []
        for i, f in enumerate(fontes):
            btn = tk.Button(fam_frame, text=f, bg='#21262d', fg='white', bd=0, width=8,
                            command=lambda ff=f: self.mudar_fonte(ff))
            btn.grid(row=i // 4, column=i % 4, padx=2, pady=2)
            if f == self.config["fonte_familia"]:
                btn.config(bg='#0d6efd')
            self.fam_vars.append(btn)

        # Tamanho da fonte
        tk.Label(font_lb, text="Tamanho:", fg='#c9d1d9', bg='#1e2227').grid(row=2, column=0, sticky='w', padx=10, pady=5)
        size_frame = tk.Frame(font_lb, bg='#1e2227')
        size_frame.grid(row=2, column=1, sticky='ew', padx=10, pady=5)
        self.lbl_size = tk.Label(size_frame, text=str(self.config["tamanho_fonte"]),
                                 width=4, fg='#58a6ff', bg='#1e2227', font=('Segoe UI', 12, 'bold'))
        self.lbl_size.pack(side='left', padx=5)
        tk.Button(size_frame, text="−", width=3, bg='#21262d', fg='white', bd=0,
                  command=self.diminuir_fonte).pack(side='left', padx=2)
        tk.Button(size_frame, text="+", width=3, bg='#21262d', fg='white', bd=0,
                  command=self.aumentar_fonte).pack(side='left', padx=2)

        # Formato do tempo
        tk.Label(font_lb, text="Formato:", fg='#c9d1d9', bg='#1e2227').grid(row=3, column=0, sticky='w', padx=10, pady=5)
        formato_frame = tk.Frame(font_lb, bg='#1e2227')
        formato_frame.grid(row=3, column=1, sticky='ew', padx=10, pady=5)
        
        self.formato_var = tk.StringVar(value=self.config.get("formato_tempo", "HH:MM:SS"))
        formatos = ["HH:MM:SS", "MM:SS", "HH:MM"]
        for i, fmt in enumerate(formatos):
            tk.Radiobutton(formato_frame, text=fmt, variable=self.formato_var, value=fmt,
                          fg='#c9d1d9', bg='#1e2227', selectcolor='#1e2227',
                          command=lambda: self.mudar_formato()).grid(row=0, column=i, padx=10)

        # Milissegundos
        self.var_millis = tk.BooleanVar(value=self.config.get("mostrar_milissegundos", False))
        tk.Checkbutton(font_lb, text="Mostrar milissegundos", variable=self.var_millis,
                      command=self.toggle_milissegundos, fg='#c9d1d9', bg='#1e2227',
                      selectcolor='#1e2227').grid(row=4, column=0, columnspan=2, sticky='w', padx=10, pady=5)

        # Seção de Cores
        cor_lb = tk.LabelFrame(container, text="🎨 Cores e Transparência", font=('Segoe UI', 11, 'bold'),
                               fg='#c9d1d9', bg='#1e2227', relief='groove', bd=1)
        cor_lb.pack(fill='x', pady=10, padx=15)

        # Tipo de fundo
        tk.Label(cor_lb, text="Tipo de Fundo:", fg='#c9d1d9', bg='#1e2227').grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.var_transparente = tk.BooleanVar(value=self.config["tipo_fundo"] == "transparente")
        tk.Checkbutton(cor_lb, text="Transparente", variable=self.var_transparente, command=self.toggle_transparencia,
                       fg='#c9d1d9', bg='#1e2227', selectcolor='#1e2227').grid(row=0, column=1, padx=10, pady=5)

        # Controle de transparência
        self.trans_frame = tk.Frame(cor_lb, bg='#1e2227')
        if self.config["tipo_fundo"] == "transparente":
            self.trans_frame.grid(row=1, column=0, columnspan=3, sticky='ew', padx=10, pady=5)
            tk.Label(self.trans_frame, text="Transparência:", fg='#c9d1d9', bg='#1e2227').pack(side='left')
            self.scl_trans = ttk.Scale(self.trans_frame, from_=0.0, to=1.0, value=self.config["transparencia"],
                                       orient='horizontal', command=lambda v: self.mudar_trans(float(v)))
            self.scl_trans.pack(fill='x', expand=True)

        # Cores
        tk.Label(cor_lb, text="Cor do Texto:", fg='#c9d1d9', bg='#1e2227').grid(row=2, column=0, sticky='w', padx=10, pady=5)
        self.btn_cor_preench = tk.Button(cor_lb, text="Escolher", bg='#21262d', fg='white', bd=0,
                                         command=lambda: self.escolher_cor("cor_preenchimento"))
        self.btn_cor_preench.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(cor_lb, text="Cor da Borda:", fg='#c9d1d9', bg='#1e2227').grid(row=3, column=0, sticky='w', padx=10, pady=5)
        self.btn_cor_borda = tk.Button(cor_lb, text="Escolher", bg='#21262d', fg='white', bd=0,
                                       command=lambda: self.escolher_cor("cor_borda"))
        self.btn_cor_borda.grid(row=3, column=1, padx=10, pady=5)

        # Espessura da borda
        tk.Label(cor_lb, text="Espessura da borda:", fg='#c9d1d9', bg='#1e2227').grid(row=4, column=0, sticky='w', padx=10, pady=5)
        self.scl_borda = ttk.Scale(cor_lb, from_=0.0, to=20.0, value=self.config["espessura_borda"],
                                   orient='horizontal', command=lambda v: self.mudar_borda(v))
        self.scl_borda.grid(row=4, column=1, sticky='ew', padx=10, pady=5)

        # Espaçamento
        tk.Label(cor_lb, text="Espaçamento:", fg='#c9d1d9', bg='#1e2227').grid(row=5, column=0, sticky='w', padx=10, pady=5)
        self.scl_espacamento = ttk.Scale(cor_lb, from_=0.0, to=20.0, value=self.config["espacamento_letras"],
                                         orient='horizontal', command=lambda v: self.mudar_espacamento(v))
        self.scl_espacamento.grid(row=5, column=1, sticky='ew', padx=10, pady=5)

        # Seção de Fundo e Forma
        fundo_lb = tk.LabelFrame(container, text="🎭 Fundo e Forma", font=('Segoe UI', 11, 'bold'),
                                 fg='#c9d1d9', bg='#1e2227', relief='groove', bd=1)
        fundo_lb.pack(fill='x', pady=10, padx=15)

        # Cor de fundo personalizada
        tk.Label(fundo_lb, text="Cor de Fundo:", fg='#c9d1d9', bg='#1e2227').grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.btn_cor_fundo_pers = tk.Button(fundo_lb, text="Escolher Cor", bg='#21262d', fg='white', bd=0,
                                            command=lambda: self.escolher_cor("cor_fundo_personalizada"))
        self.btn_cor_fundo_pers.grid(row=0, column=1, padx=10, pady=5)

        # Gradiente
        self.var_gradiente = tk.BooleanVar(value=self.config.get("gradiente_ativo", False))
        tk.Checkbutton(fundo_lb, text="Gradiente", variable=self.var_gradiente, command=self.toggle_gradiente,
                       fg='#c9d1d9', bg='#1e2227', selectcolor='#1e2227').grid(row=0, column=2, padx=10, pady=5)

        # Controles de gradiente
        self.grad_frame = tk.Frame(fundo_lb, bg='#1e2227')
        if self.config.get("gradiente_ativo", False):
            self.grad_frame.grid(row=1, column=0, columnspan=3, sticky='ew', padx=10, pady=5)
            tk.Label(self.grad_frame, text="Cor Início:", fg='#c9d1d9', bg='#1e2227').pack(side='left')
            tk.Button(self.grad_frame, text="Escolher", bg='#21262d', fg='white', bd=0,
                      command=lambda: self.escolher_cor("cor_gradiente_inicio")).pack(side='left', padx=5)
            tk.Label(self.grad_frame, text="Cor Fim:", fg='#c9d1d9', bg='#1e2227').pack(side='left', padx=(10,0))
            tk.Button(self.grad_frame, text="Escolher", bg='#21262d', fg='white', bd=0,
                      command=lambda: self.escolher_cor("cor_gradiente_fim")).pack(side='left', padx=5)

        # Forma da caixa
        tk.Label(fundo_lb, text="Forma:", fg='#c9d1d9', bg='#1e2227').grid(row=2, column=0, sticky='w', padx=10, pady=5)
        forma_frame = tk.Frame(fundo_lb, bg='#1e2227')
        forma_frame.grid(row=2, column=1, columnspan=2, sticky='ew', padx=10, pady=5)

        self.forma_var = tk.StringVar(value=self.config.get("forma_caixa", "retangulo"))
        formas = [("Retângulo", "retangulo"), ("Oval", "oval"), ("Losango", "losango"), ("Hexágono", "hexagono")]
        for i, (nome, valor) in enumerate(formas):
            tk.Radiobutton(forma_frame, text=nome, variable=self.forma_var, value=valor,
                          fg='#c9d1d9', bg='#1e2227', selectcolor='#1e2227',
                          command=self.mudar_forma).grid(row=0, column=i, padx=5)

        # Bordas arredondadas (só para retângulo)
        self.borda_frame = tk.Frame(fundo_lb, bg='#1e2227')
        if self.config.get("forma_caixa", "retangulo") == "retangulo":
            self.borda_frame.grid(row=3, column=0, columnspan=3, sticky='ew', padx=10, pady=5)
            tk.Label(self.borda_frame, text="Bordas Arredondadas:", fg='#c9d1d9', bg='#1e2227').pack(side='left')
            self.scl_borda_arred = ttk.Scale(self.borda_frame, from_=0, to=50, 
                                             value=self.config.get("borda_arredondada", 10),
                                             orient='horizontal', command=lambda v: self.mudar_borda_arredondada(v))
            self.scl_borda_arred.pack(fill='x', expand=True, padx=10)

        # Seção de Dimensões
        dim_lb = tk.LabelFrame(container, text="📐 Dimensões", font=('Segoe UI', 11, 'bold'),
                               fg='#c9d1d9', bg='#1e2227', relief='groove', bd=1)
        dim_lb.pack(fill='x', pady=10, padx=15)

        # Largura
        tk.Label(dim_lb, text="Largura:", fg='#c9d1d9', bg='#1e2227').grid(row=0, column=0, sticky='w', padx=10, pady=5)
        largura_frame = tk.Frame(dim_lb, bg='#1e2227')
        largura_frame.grid(row=0, column=1, sticky='ew', padx=10, pady=5)
        self.lbl_largura = tk.Label(largura_frame, text=str(self.config["largura"]),
                                   width=4, fg='#58a6ff', bg='#1e2227', font=('Segoe UI', 12, 'bold'))
        self.lbl_largura.pack(side='left', padx=5)
        tk.Button(largura_frame, text="−", width=3, bg='#21262d', fg='white', bd=0,
                  command=self.diminuir_largura).pack(side='left', padx=2)
        tk.Button(largura_frame, text="+", width=3, bg='#21262d', fg='white', bd=0,
                  command=self.aumentar_largura).pack(side='left', padx=2)

        # Altura
        tk.Label(dim_lb, text="Altura:", fg='#c9d1d9', bg='#1e2227').grid(row=1, column=0, sticky='w', padx=10, pady=5)
        altura_frame = tk.Frame(dim_lb, bg='#1e2227')
        altura_frame.grid(row=1, column=1, sticky='ew', padx=10, pady=5)
        self.lbl_altura = tk.Label(altura_frame, text=str(self.config["altura"]),
                                  width=4, fg='#58a6ff', bg='#1e2227', font=('Segoe UI', 12, 'bold'))
        self.lbl_altura.pack(side='left', padx=5)
        tk.Button(altura_frame, text="−", width=3, bg='#21262d', fg='white', bd=0,
                  command=self.diminuir_altura).pack(side='left', padx=2)
        tk.Button(altura_frame, text="+", width=3, bg='#21262d', fg='white', bd=0,
                  command=self.aumentar_altura).pack(side='left', padx=2)

        # Botões de preset
        preset_frame = tk.Frame(dim_lb, bg='#1e2227')
        preset_frame.grid(row=2, column=0, columnspan=2, pady=10)
        tk.Label(preset_frame, text="Presets:", fg='#c9d1d9', bg='#1e2227').pack()
        presets = [("Pequeno", 200, 60), ("Médio", 280, 80), ("Grande", 400, 120), ("Extra", 600, 150)]
        for nome, w, h in presets:
            tk.Button(preset_frame, text=nome, bg='#21262d', fg='white', bd=0, width=8,
                  command=lambda ww=w, hh=h: self.aplicar_preset_tamanho(ww, hh)).pack(side='left', padx=2)

    def criar_aba_comportamento(self, parent):
        container = tk.Frame(parent, bg='#1e2227')
        container.pack(fill='both', expand=True, padx=15, pady=15)

        # Seção de Visibilidade
        vis_lb = tk.LabelFrame(container, text="👁️ Visibilidade", font=('Segoe UI', 11, 'bold'),
                               fg='#c9d1d9', bg='#1e2227', relief='groove', bd=1)
        vis_lb.pack(fill='x', pady=10)

        self.var_sempre_visivel = tk.BooleanVar(value=self.config.get("sempre_visivel", True))
        tk.Checkbutton(vis_lb, text="Sempre visível (sempre em cima)", variable=self.var_sempre_visivel,
                      command=self.toggle_sempre_visivel_config, fg='#c9d1d9', bg='#1e2227',
                      selectcolor='#1e2227').pack(anchor='w', padx=10, pady=5)

        # Seção de Inicialização
        init_lb = tk.LabelFrame(container, text="🚀 Inicialização", font=('Segoe UI', 11, 'bold'),
                                fg='#c9d1d9', bg='#1e2227', relief='groove', bd=1)
        init_lb.pack(fill='x', pady=10)

        self.var_auto_iniciar = tk.BooleanVar(value=self.config.get("auto_iniciar", False))
        tk.Checkbutton(init_lb, text="Iniciar cronômetro automaticamente", variable=self.var_auto_iniciar,
                      command=self.toggle_auto_iniciar, fg='#c9d1d9', bg='#1e2227',
                      selectcolor='#1e2227').pack(anchor='w', padx=10, pady=5)

        # Seção de Efeitos
        efeitos_lb = tk.LabelFrame(container, text="✨ Efeitos", font=('Segoe UI', 11, 'bold'),
                                   fg='#c9d1d9', bg='#1e2227', relief='groove', bd=1)
        efeitos_lb.pack(fill='x', pady=10)

        self.var_animacao = tk.BooleanVar(value=self.config.get("animacao", True))
        tk.Checkbutton(efeitos_lb, text="Animação de pulsação", variable=self.var_animacao,
                      command=self.toggle_animacao, fg='#c9d1d9', bg='#1e2227',
                      selectcolor='#1e2227').pack(anchor='w', padx=10, pady=5)

        # Seção de Atalhos
        atalhos_lb = tk.LabelFrame(container, text="⌨️ Atalhos", font=('Segoe UI', 11, 'bold'),
                                   fg='#c9d1d9', bg='#1e2227', relief='groove', bd=1)
        atalhos_lb.pack(fill='x', pady=10)

        self.var_atalhos = tk.BooleanVar(value=self.config.get("atalhos_globais", True))
        tk.Checkbutton(atalhos_lb, text="Atalhos de teclado ativos", variable=self.var_atalhos,
                      command=self.toggle_atalhos, fg='#c9d1d9', bg='#1e2227',
                      selectcolor='#1e2227').pack(anchor='w', padx=10, pady=5)

        # Lista de atalhos
        atalhos_info = tk.Text(atalhos_lb, height=6, bg='#21262d', fg='#c9d1d9', bd=0)
        atalhos_info.pack(fill='x', padx=10, pady=5)
        atalhos_info.insert('1.0', """Atalhos disponíveis:
• ESPAÇO - Iniciar/Pausar
• R - Resetar
• C - Centralizar
• S - Configurações
• Duplo clique - Iniciar/Pausar""")
        atalhos_info.config(state='disabled')

    def criar_aba_avancado(self, parent):
        container = tk.Frame(parent, bg='#1e2227')
        container.pack(fill='both', expand=True, padx=15, pady=15)

        # Seção de Performance
        perf_lb = tk.LabelFrame(container, text="⚡ Performance", font=('Segoe UI', 11, 'bold'),
                                fg='#c9d1d9', bg='#1e2227', relief='groove', bd=1)
        perf_lb.pack(fill='x', pady=10)

        tk.Label(perf_lb, text="Intervalo de atualização (ms):", fg='#c9d1d9', bg='#1e2227').grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.scl_intervalo = ttk.Scale(perf_lb, from_=50, to=1000, value=self.config.get("intervalo_atualizacao", 100),
                                       orient='horizontal', command=lambda v: self.mudar_intervalo(int(float(v))))
        self.scl_intervalo.grid(row=0, column=1, sticky='ew', padx=10, pady=5)

        # Seção de Dados
        dados_lb = tk.LabelFrame(container, text="💾 Dados", font=('Segoe UI', 11, 'bold'),
                                 fg='#c9d1d9', bg='#1e2227', relief='groove', bd=1)
        dados_lb.pack(fill='x', pady=10)

        self.var_auto_salvar = tk.BooleanVar(value=self.config.get("auto_salvar", True))
        tk.Checkbutton(dados_lb, text="Salvar configurações automaticamente", variable=self.var_auto_salvar,
                      command=self.toggle_auto_salvar, fg='#c9d1d9', bg='#1e2227',
                      selectcolor='#1e2227').pack(anchor='w', padx=10, pady=5)

        # Botões de ação
        btn_frame = tk.Frame(dados_lb, bg='#1e2227')
        btn_frame.pack(fill='x', padx=10, pady=10)

        tk.Button(btn_frame, text="💾 Salvar Agora", bg='#238636', fg='white', bd=0,
                  command=self.salvar_configuracoes).pack(side='left', padx=5)
        tk.Button(btn_frame, text="🔄 Resetar Config", bg='#dc3545', fg='white', bd=0,
                  command=self.resetar_configuracoes).pack(side='left', padx=5)
        tk.Button(btn_frame, text="📂 Abrir Pasta", bg='#0d6efd', fg='white', bd=0,
                  command=self.abrir_pasta_config).pack(side='left', padx=5)

        # Informações do sistema
        info_lb = tk.LabelFrame(container, text="ℹ️ Informações", font=('Segoe UI', 11, 'bold'),
                                fg='#c9d1d9', bg='#1e2227', relief='groove', bd=1)
        info_lb.pack(fill='x', pady=10)

        info_text = tk.Text(info_lb, height=4, bg='#21262d', fg='#c9d1d9', bd=0)
        info_text.pack(fill='x', padx=10, pady=5)
        info_text.insert('1.0', f"""Sistema: {platform.system()} {platform.release()}
Versão Python: {sys.version.split()[0]}
Arquivo de config: {os.path.abspath(self.config_file)}
Cronômetro Premium v2.0""")
        info_text.config(state='disabled')

    # Métodos para as novas funcionalidades
    def mudar_formato(self):
        self.config["formato_tempo"] = self.formato_var.get()
        self.salvar_configuracoes()

    def toggle_milissegundos(self):
        self.config["mostrar_milissegundos"] = self.var_millis.get()
        self.salvar_configuracoes()

    def toggle_sempre_visivel_config(self):
        self.config["sempre_visivel"] = self.var_sempre_visivel.get()
        self.toggle_sempre_visivel()

    def toggle_auto_iniciar(self):
        self.config["auto_iniciar"] = self.var_auto_iniciar.get()
        self.salvar_configuracoes()

    def toggle_animacao(self):
        self.config["animacao"] = self.var_animacao.get()
        self.salvar_configuracoes()

    def toggle_atalhos(self):
        self.config["atalhos_globais"] = self.var_atalhos.get()
        self.salvar_configuracoes()

    def toggle_auto_salvar(self):
        self.config["auto_salvar"] = self.var_auto_salvar.get()
        self.salvar_configuracoes()

    def mudar_intervalo(self, valor):
        self.config["intervalo_atualizacao"] = valor
        self.salvar_configuracoes()

    def resetar_configuracoes(self):
        if messagebox.askyesno("Confirmar", "Resetar todas as configurações?"):
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
            self.root.quit()

    def abrir_pasta_config(self):
        pasta = os.path.dirname(os.path.abspath(self.config_file))
        if platform.system() == "Windows":
            os.startfile(pasta)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", pasta])
        else:  # Linux
            subprocess.run(["xdg-open", pasta])

    # Métodos para as novas funcionalidades
    def atualizar_visual_completo(self):
        """Força atualização completa da interface visual"""
        self.aplicar_fundo()
        self.setup_ui()
        self.aplicar_forma_personalizada()

    # Métodos existentes adaptados
    def escolher_cor(self, chave):
        cor = colorchooser.askcolor(color=self.config[chave])[1]
        if cor:
            self.config[chave] = cor
            if chave == "cor_fundo_personalizada":
                self.aplicar_fundo() # Atualiza o bg da root e do canvas
                self.aplicar_forma_personalizada() # Redesenha a forma com a nova cor
            elif chave in ["cor_preenchimento", "cor_borda"]:
                self.redesenhar_texto()
            elif chave in ["cor_gradiente_inicio", "cor_gradiente_fim"]:
                if self.config.get("gradiente_ativo", False):
                    self.aplicar_forma_personalizada()
            self.salvar_configuracoes()

    def toggle_transparencia(self):
        if self.var_transparente.get():
            self.config["tipo_fundo"] = "transparente"
            self.trans_frame.grid(row=1, column=0, columnspan=3, sticky='ew', padx=10, pady=5)
        else:
            self.config["tipo_fundo"] = "cor"
            self.trans_frame.grid_forget()
        self.aplicar_fundo() # Atualiza o bg da root e do canvas
        self.setup_ui() # Recria o canvas com o novo bg e chama aplicar_forma_personalizada
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
        self.config["espessura_borda"] = float(v) 
        self.redesenhar_texto()
        self.salvar_configuracoes()

    def mudar_espacamento(self, v):
        self.config["espacamento_letras"] = float(v) 
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
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.root.winfo_width()) // 2
        y = 100  # Mantém no topo
        self.root.geometry(f"+{x}+{y}")
        self.salvar_configuracoes()

    def iniciar_drag(self, ev):
        self._drag_x, self._drag_y = ev.x, ev.y

    def arrastar(self, ev):
        x = self.root.winfo_x() + ev.x - self._drag_x
        y = self.root.winfo_y() + ev.y - self._drag_y
        self.root.geometry(f"+{x}+{y}")

    def processar_tecla(self, ev):
        if not self.config.get("atalhos_globais", True):
            return
        try:
            k = ev.keysym.lower()
            if k == 'space': self.toggle()
            elif k == 'r': self.resetar()
            elif k == 'c': self.centralizar()
            elif k == 's': 
                print("Tecla S pressionada - abrindo configurações")
                self.abrir_configuracoes()
            elif k == 'd':  # Debug
                self.debug_janela_config()
        except Exception as e:
            print(f"Erro ao processar tecla: {e}")

    def fechar_app(self):
        self.topmost_thread_running = False
        self.salvar_configuracoes()
        self.root.quit()

    def atualizar_display(self, txt):
        if self.tempo_atual_texto != txt:
            self.tempo_atual_texto = txt
            self.redesenhar_texto()

    def atualizar_cronometro(self):
        while True:
            try:
                if self.rodando and self.root.winfo_exists():
                    delta = datetime.now() - self.inicio
                    txt = self.formatar_tempo(delta)
                    self.root.after(0, self.atualizar_display, txt)
                intervalo = self.config.get("intervalo_atualizacao", 100) / 1000.0
                time.sleep(intervalo)
            except:
                break

    def iniciar_threads(self):
        # Thread para atualizar o cronômetro
        threading.Thread(target=self.atualizar_cronometro, daemon=True).start()
        # Thread para manter sempre visível
        threading.Thread(target=self.manter_sempre_visivel, daemon=True).start()

    def executar(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.fechar_app()

    def mudar_forma(self):
        self.config["forma_caixa"] = self.forma_var.get()
        # print(f"Mudar forma para: {self.config['forma_caixa']}") # Debug print
        if hasattr(self, 'borda_frame'):
            if self.config["forma_caixa"] == "retangulo":
                self.borda_frame.grid(row=3, column=0, columnspan=3, sticky='ew', padx=10, pady=5)
            else:
                self.borda_frame.grid_forget()
        self.aplicar_forma_personalizada() # Chama para redesenhar a forma
        self.salvar_configuracoes()

    def toggle_gradiente(self):
        self.config["gradiente_ativo"] = self.var_gradiente.get()
        if hasattr(self, 'grad_frame'):
            if self.config["gradiente_ativo"]:
                self.grad_frame.grid(row=1, column=0, columnspan=3, sticky='ew', padx=10, pady=5)
            else:
                self.grad_frame.grid_forget()
        self.aplicar_forma_personalizada()
        self.salvar_configuracoes()

    def mudar_borda_arredondada(self, v):
        self.config["borda_arredondada"] = int(float(v))
        self.aplicar_forma_personalizada()
        self.salvar_configuracoes()

    def aumentar_largura(self):
        self.config["largura"] = min(self.config["largura"] + 20, 1000)
        self.lbl_largura.config(text=str(self.config["largura"]))
        self.atualizar_interface()
        self.salvar_configuracoes()

    def diminuir_largura(self):
        self.config["largura"] = max(self.config["largura"] - 20, 1) 
        self.lbl_largura.config(text=str(self.config["largura"]))
        self.atualizar_interface()
        self.salvar_configuracoes()

    def aumentar_altura(self):
        self.config["altura"] = min(self.config["altura"] + 10, 300)
        self.lbl_altura.config(text=str(self.config["altura"]))
        self.atualizar_interface()
        self.salvar_configuracoes()

    def diminuir_altura(self):
        self.config["altura"] = max(self.config["altura"] - 10, 1) 
        self.lbl_altura.config(text=str(self.config["altura"]))
        self.atualizar_interface()
        self.salvar_configuracoes()

    def aplicar_preset_tamanho(self, largura, altura):
        self.config["largura"] = largura
        self.config["altura"] = altura
        self.lbl_largura.config(text=str(largura))
        self.lbl_altura.config(text=str(altura))
        self.atualizar_interface()
        self.salvar_configuracoes()

if __name__ == "__main__":
    try:
        cronometro = CronometroPremium()
        cronometro.executar()
    except Exception as e:
        print(f"Erro: {e}")
        input("Pressione Enter para sair...")
