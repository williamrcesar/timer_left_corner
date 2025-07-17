import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.slider import Slider
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.scrollview import ScrollView
from kivy.uix.colorpicker import ColorPicker
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Ellipse, Mesh, Line
from kivy.properties import NumericProperty, BooleanProperty, StringProperty, ListProperty
from kivy.lang import Builder
from datetime import datetime, timedelta
import json
import os
import sys
import platform
import math

# --- Kivy Window Configuration ---
# Set window to be fully transparent (per-pixel alpha blending)
Window.clearcolor = (0, 0, 0, 0)
# Remove window borders (title bar, resize handles)
Window.borderless = True
# Keep window always on top
Window.always_on_top = True

# --- KV Language Definition for UI ---
# This defines the structure and styling of the widgets
Builder.load_string("""
<ConfigPopup>:
    title: 'Configurações Avançadas'
    size_hint: None, None
    size: 950, 800 # Fixed size for consistency
    background_color: 0.12, 0.13, 0.15, 1 # Dark background for popup
    separator_color: 0.2, 0.2, 0.2, 1

    TabbedPanel:
        do_default_tab: False
        tab_pos: 'top_mid'
        tab_width: self.width / 3
        background_color: 0.12, 0.13, 0.15, 1
        tab_height: 40
        font_size: 16
        color: 0.79, 0.82, 0.85, 1 # Light gray text

        TabbedPanelItem:
            text: '🎨 Aparência'
            background_color: 0.12, 0.13, 0.15, 1
            ScrollView:
                GridLayout:
                    cols: 1
                    size_hint_y: None
                    height: self.minimum_height
                    padding: 15
                    spacing: 10

                    # --- Font and Text Section ---
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        padding: 10
                        spacing: 5
                        canvas.before:
                            Color:
                                rgba: 0.15, 0.16, 0.18, 1 # Darker background for section
                            Rectangle:
                                pos: self.pos
                                size: self.size
                        Label:
                            text: '🔤 Fonte e Texto'
                            size_hint_y: None
                            height: 30
                            font_size: 18
                            color: 0.79, 0.82, 0.85, 1
                            halign: 'left'
                            text_size: self.width - 20, None
                        
                        GridLayout:
                            cols: 2
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: 10
                            padding: 5

                            Label:
                                text: 'Família:'
                                size_hint_x: None
                                width: 100
                                color: 0.79, 0.82, 0.85, 1
                                halign: 'left'
                                text_size: self.width, None
                            GridLayout:
                                cols: 4
                                size_hint_x: 1
                                size_hint_y: None
                                height: self.minimum_height
                                spacing: 2
                                id: font_family_grid
                                # Buttons will be added dynamically in Python

                            Label:
                                text: 'Tamanho:'
                                size_hint_x: None
                                width: 100
                                color: 0.79, 0.82, 0.85, 1
                                halign: 'left'
                                text_size: self.width, None
                            BoxLayout:
                                orientation: 'horizontal'
                                size_hint_x: 1
                                size_hint_y: None
                                height: 40
                                Label:
                                    id: font_size_label
                                    text: str(app.font_size)
                                    color: 0.34, 0.65, 1, 1 # Blue color
                                    font_size: 20
                                    size_hint_x: 0.3
                                Button:
                                    text: '−'
                                    size_hint_x: 0.35
                                    on_release: app.font_size = max(8, app.font_size - 2)
                                    background_normal: ''
                                    background_color: 0.13, 0.15, 0.18, 1
                                    color: 1, 1, 1, 1
                                Button:
                                    text: '+'
                                    size_hint_x: 0.35
                                    on_release: app.font_size = min(200, app.font_size + 2)
                                    background_normal: ''
                                    background_color: 0.13, 0.15, 0.18, 1
                                    color: 1, 1, 1, 1

                            Label:
                                text: 'Formato:'
                                size_hint_x: None
                                width: 100
                                color: 0.79, 0.82, 0.85, 1
                                halign: 'left'
                                text_size: self.width, None
                            BoxLayout:
                                orientation: 'horizontal'
                                size_hint_x: 1
                                size_hint_y: None
                                height: 40
                                spacing: 10
                                ToggleButton:
                                    text: 'HH:MM:SS'
                                    group: 'time_format'
                                    state: 'down' if app.time_format == 'HH:MM:SS' else 'normal'
                                    on_release: app.time_format = self.text if self.state == 'down' else app.time_format
                                    background_normal: ''
                                    background_color: 0.13, 0.15, 0.18, 1
                                    color: 1, 1, 1, 1
                                ToggleButton:
                                    text: 'MM:SS'
                                    group: 'time_format'
                                    state: 'down' if app.time_format == 'MM:SS' else 'normal'
                                    on_release: app.time_format = self.text if self.state == 'down' else app.time_format
                                    background_normal: ''
                                    background_color: 0.13, 0.15, 0.18, 1
                                    color: 1, 1, 1, 1
                                ToggleButton:
                                    text: 'HH:MM'
                                    group: 'time_format'
                                    state: 'down' if app.time_format == 'HH:MM' else 'normal'
                                    on_release: app.time_format = self.text if self.state == 'down' else app.time_format
                                    background_normal: ''
                                    background_color: 0.13, 0.15, 0.18, 1
                                    color: 1, 1, 1, 1

                            CheckBox:
                                id: show_millis_checkbox
                                active: app.show_milliseconds
                                on_active: app.show_milliseconds = self.active
                                size_hint_x: None
                                width: 40
                                color: 0.79, 0.82, 0.85, 1
                            Label:
                                text: 'Mostrar milissegundos'
                                color: 0.79, 0.82, 0.85, 1
                                halign: 'left'
                                text_size: self.width, None

                    # --- Colors and Transparency Section ---
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        padding: 10
                        spacing: 5
                        canvas.before:
                            Color:
                                rgba: 0.15, 0.16, 0.18, 1
                            Rectangle:
                                pos: self.pos
                                size: self.size
                        Label:
                            text: '🎨 Cores e Transparência'
                            size_hint_y: None
                            height: 30
                            font_size: 18
                            color: 0.79, 0.82, 0.85, 1
                            halign: 'left'
                            text_size: self.width - 20, None
                        
                        GridLayout:
                            cols: 2
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: 10
                            padding: 5

                            Label:
                                text: 'Tipo de Fundo:'
                                size_hint_x: None
                                width: 150
                                color: 0.79, 0.82, 0.85, 1
                                halign: 'left'
                                text_size: self.width, None
                            CheckBox:
                                id: transparent_bg_checkbox
                                active: app.background_type == 'transparent'
                                on_active: app.background_type = 'transparent' if self.active else 'solid'
                                size_hint_x: None
                                width: 40
                                color: 0.79, 0.82, 0.85, 1
                            Label:
                                text: 'Transparente'
                                color: 0.79, 0.82, 0.85, 1
                                halign: 'left'
                                text_size: self.width, None

                            Label:
                                text: 'Transparência:'
                                size_hint_x: None
                                width: 150
                                color: 0.79, 0.82, 0.85, 1
                                halign: 'left'
                                text_size: self.width, None
                            Slider:
                                id: transparency_slider
                                min: 0.0
                                max: 1.0
                                value: app.transparency
                                on_value: app.transparency = self.value
                                disabled: app.background_type != 'transparent'
                                step: 0.01 # Allow finer control
                                size_hint_x: 1

                            Label:
                                text: 'Cor do Texto:'
                                size_hint_x: None
                                width: 150
                                color: 0.79, 0.82, 0.85, 1
                                halign: 'left'
                                text_size: self.width, None
                            Button:
                                text: 'Escolher'
                                on_release: app.open_color_picker('text_color')
                                background_normal: ''
                                background_color: 0.13, 0.15, 0.18, 1
                                color: 1, 1, 1, 1

                            Label:
                                text: 'Cor da Borda:'
                                size_hint_x: None
                                width: 150
                                color: 0.79, 0.82, 0.85, 1
                                halign: 'left'
                                text_size: self.width, None
                            Button:
                                text: 'Escolher'
                                on_release: app.open_color_picker('border_color')
                                background_normal: ''
                                background_color: 0.13, 0.15, 0.18, 1
                                color: 1, 1, 1, 1

                            Label:
                                text: 'Espessura da borda:'
                                size_hint_x: None
                                width: 150
                                color: 0.79, 0.82, 0.85, 1
                                halign: 'left'
                                text_size: self.width, None
                            Slider:
                                min: 0.0
                                max: 20.0
                                value: app.border_thickness
                                on_value: app.border_thickness = self.value
                                step: 0.1 # Allow decimal values
                                size_hint_x: 1

                            Label:
                                text: 'Espaçamento:'
                                size_hint_x: None
                                width: 150
                                color: 0.79, 0.82, 0.85, 1
                                halign: 'left'
                                text_size: self.width, None
                            Slider:
                                min: 0.0
                                max: 20.0
                                value: app.letter_spacing
                                on_value: app.letter_spacing = self.value
                                step: 0.1 # Allow decimal values
                                size_hint_x: 1

                    # --- Background and Shape Section ---
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        padding: 10
                        spacing: 5
                        canvas.before:
                            Color:
                                rgba: 0.15, 0.16, 0.18, 1
                            Rectangle:
                                pos: self.pos
                                size: self.size
                        Label:
                            text: '🎭 Fundo e Forma'
                            size_hint_y: None
                            height: 30
                            font_size: 18
                            color: 0.79, 0.82, 0.85, 1
                            halign: 'left'
                            text_size: self.width - 20, None
                        
                        GridLayout:
                            cols: 2
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: 10
                            padding: 5

                            Label:
                                text: 'Cor de Fundo:'
                                size_hint_x: None
                                width: 150
                                color: 0.79, 0.82, 0.85, 1
                                halign: 'left'
                                text_size: self.width, None
                            Button:
                                text: 'Escolher Cor'
                                on_release: app.open_color_picker('custom_background_color')
                                disabled: app.background_type == 'transparent' or app.gradient_active
                                background_normal: ''
                                background_color: 0.13, 0.15, 0.18, 1
                                color: 1, 1, 1, 1

                            CheckBox:
                                id: gradient_checkbox
                                active: app.gradient_active
                                on_active: app.gradient_active = self.active
                                disabled: app.background_type == 'transparent'
                                size_hint_x: None
                                width: 40
                                color: 0.79, 0.82, 0.85, 1
                            Label:
                                text: 'Gradiente'
                                color: 0.79, 0.82, 0.85, 1
                                halign: 'left'
                                text_size: self.width, None

                            Label:
                                text: 'Cor Início:'
                                size_hint_x: None
                                width: 150
                                color: 0.79, 0.82, 0.85, 1
                                halign: 'left'
                                text_size: self.width, None
                            Button:
                                text: 'Escolher'
                                on_release: app.open_color_picker('gradient_start_color')
                                disabled: not app.gradient_active or app.background_type == 'transparent'
                                background_normal: ''
                                background_color: 0.13, 0.15, 0.18, 1
                                color: 1, 1, 1, 1

                            Label:
                                text: 'Cor Fim:'
                                size_hint_x: None
                                width: 150
                                color: 0.79, 0.82, 0.85, 1
                                halign: 'left'
                                text_size: self.width, None
                            Button:
                                text: 'Escolher'
                                on_release: app.open_color_picker('gradient_end_color')
                                disabled: not app.gradient_active or app.background_type == 'transparent'
                                background_normal: ''
                                background_color: 0.13, 0.15, 0.18, 1
                                color: 1, 1, 1, 1

                            Label:
                                text: 'Forma:'
                                size_hint_x: None
                                width: 150
                                color: 0.79, 0.82, 0.85, 1
                                halign: 'left'
                                text_size: self.width, None
                            BoxLayout:
                                orientation: 'horizontal'
                                size_hint_x: 1
                                size_hint_y: None
                                height: 40
                                spacing: 5
                                ToggleButton:
                                    text: 'Retângulo'
                                    group: 'shape'
                                    state: 'down' if app.box_shape == 'retangulo' else 'normal'
                                    on_release: app.box_shape = self.text.lower() if self.state == 'down' else app.box_shape
                                    disabled: app.background_type == 'transparent'
                                    background_normal: ''
                                    background_color: 0.13, 0.15, 0.18, 1
                                    color: 1, 1, 1, 1
                                ToggleButton:
                                    text: 'Oval'
                                    group: 'shape'
                                    state: 'down' if app.box_shape == 'oval' else 'normal'
                                    on_release: app.box_shape = self.text.lower() if self.state == 'down' else app.box_shape
                                    disabled: app.background_type == 'transparent'
                                    background_normal: ''
                                    background_color: 0.13, 0.15, 0.18, 1
                                    color: 1, 1, 1, 1
                                ToggleButton:
                                    text: 'Losango'
                                    group: 'shape'
                                    state: 'down' if app.box_shape == 'losango' else 'normal'
                                    on_release: app.box_shape = self.text.lower() if self.state == 'down' else app.box_shape
                                    disabled: app.background_type == 'transparent'
                                    background_normal: ''
                                    background_color: 0.13, 0.15, 0.18, 1
                                    color: 1, 1, 1, 1
                                ToggleButton:
                                    text: 'Hexágono'
                                    group: 'shape'
                                    state: 'down' if app.box_shape == 'hexagono' else 'normal'
                                    on_release: app.box_shape = self.text.lower() if self.state == 'down' else app.box_shape
                                    disabled: app.background_type == 'transparent'
                                    background_normal: ''
                                    background_color: 0.13, 0.15, 0.18, 1
                                    color: 1, 1, 1, 1

                            Label:
                                text: 'Bordas Arredondadas:'
                                size_hint_x: None
                                width: 150
                                color: 0.79, 0.82, 0.85, 1
                                halign: 'left'
                                text_size: self.width, None
                            Slider:
                                min: 0
                                max: 50
                                value: app.rounded_border
                                on_value: app.rounded_border = int(self.value)
                                disabled: app.box_shape != 'retangulo' or app.background_type == 'transparent'
                                size_hint_x: 1

                    # --- Dimensions Section ---
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        padding: 10
                        spacing: 5
                        canvas.before:
                            Color:
                                rgba: 0.15, 0.16, 0.18, 1
                            Rectangle:
                                pos: self.pos
                                size: self.size
                        Label:
                            text: '📐 Dimensões'
                            size_hint_y: None
                            height: 30
                            font_size: 18
                            color: 0.79, 0.82, 0.85, 1
                            halign: 'left'
                            text_size: self.width - 20, None
                        
                        GridLayout:
                            cols: 2
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: 10
                            padding: 5

                            Label:
                                text: 'Largura:'
                                size_hint_x: None
                                width: 100
                                color: 0.79, 0.82, 0.85, 1
                                halign: 'left'
                                text_size: self.width, None
                            BoxLayout:
                                orientation: 'horizontal'
                                size_hint_x: 1
                                size_hint_y: None
                                height: 40
                                Label:
                                    id: width_label
                                    text: str(app.window_width)
                                    color: 0.34, 0.65, 1, 1
                                    font_size: 20
                                    size_hint_x: 0.3
                                Button:
                                    text: '−'
                                    size_hint_x: 0.35
                                    on_release: app.window_width = max(1, app.window_width - 20)
                                    background_normal: ''
                                    background_color: 0.13, 0.15, 0.18, 1
                                    color: 1, 1, 1, 1
                                Button:
                                    text: '+'
                                    size_hint_x: 0.35
                                    on_release: app.window_width = min(1000, app.window_width + 20)
                                    background_normal: ''
                                    background_color: 0.13, 0.15, 0.18, 1
                                    color: 1, 1, 1, 1

                            Label:
                                text: 'Altura:'
                                size_hint_x: None
                                width: 100
                                color: 0.79, 0.82, 0.85, 1
                                halign: 'left'
                                text_size: self.width, None
                            BoxLayout:
                                orientation: 'horizontal'
                                size_hint_x: 1
                                size_hint_y: None
                                height: 40
                                Label:
                                    id: height_label
                                    text: str(app.window_height)
                                    color: 0.34, 0.65, 1, 1
                                    font_size: 20
                                    size_hint_x: 0.3
                                Button:
                                    text: '−'
                                    size_hint_x: 0.35
                                    on_release: app.window_height = max(1, app.window_height - 10)
                                    background_normal: ''
                                    background_color: 0.13, 0.15, 0.18, 1
                                    color: 1, 1, 1, 1
                                Button:
                                    text: '+'
                                    size_hint_x: 0.35
                                    on_release: app.window_height = min(300, app.window_height + 10)
                                    background_normal: ''
                                    background_color: 0.13, 0.15, 0.18, 1
                                    color: 1, 1, 1, 1

                            Label:
                                text: 'Presets:'
                                size_hint_x: None
                                width: 100
                                color: 0.79, 0.82, 0.85, 1
                                halign: 'left'
                                text_size: self.width, None
                            BoxLayout:
                                orientation: 'horizontal'
                                size_hint_x: 1
                                size_hint_y: None
                                height: 40
                                spacing: 2
                                Button:
                                    text: 'Pequeno'
                                    on_release: app.apply_size_preset(200, 60)
                                    background_normal: ''
                                    background_color: 0.13, 0.15, 0.18, 1
                                    color: 1, 1, 1, 1
                                Button:
                                    text: 'Médio'
                                    on_release: app.apply_size_preset(280, 80)
                                    background_normal: ''
                                    background_color: 0.13, 0.15, 0.18, 1
                                    color: 1, 1, 1, 1
                                Button:
                                    text: 'Grande'
                                    on_release: app.apply_size_preset(400, 120)
                                    background_normal: ''
                                    background_color: 0.13, 0.15, 0.18, 1
                                    color: 1, 1, 1, 1
                                Button:
                                    text: 'Extra'
                                    on_release: app.apply_size_preset(600, 150)
                                    background_normal: ''
                                    background_color: 0.13, 0.15, 0.18, 1
                                    color: 1, 1, 1, 1

        TabbedPanelItem:
            text: '⚙️ Comportamento'
            background_color: 0.12, 0.13, 0.15, 1
            ScrollView:
                GridLayout:
                    cols: 1
                    size_hint_y: None
                    height: self.minimum_height
                    padding: 15
                    spacing: 10

                    # --- Visibility Section ---
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        padding: 10
                        spacing: 5
                        canvas.before:
                            Color:
                                rgba: 0.15, 0.16, 0.18, 1
                            Rectangle:
                                pos: self.pos
                                size: self.size
                        Label:
                            text: '👁️ Visibilidade'
                            size_hint_y: None
                            height: 30
                            font_size: 18
                            color: 0.79, 0.82, 0.85, 1
                            halign: 'left'
                            text_size: self.width - 20, None
                        
                        GridLayout:
                            cols: 2
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: 10
                            padding: 5
                            CheckBox:
                                id: always_on_top_checkbox
                                active: app.always_on_top
                                on_active: app.always_on_top = self.active
                                size_hint_x: None
                                width: 40
                                color: 0.79, 0.82, 0.85, 1
                            Label:
                                text: 'Sempre visível (sempre em cima)'
                                color: 0.79, 0.82, 0.85, 1
                                halign: 'left'
                                text_size: self.width, None

                    # --- Initialization Section ---
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        padding: 10
                        spacing: 5
                        canvas.before:
                            Color:
                                rgba: 0.15, 0.16, 0.18, 1
                            Rectangle:
                                pos: self.pos
                                size: self.size
                        Label:
                            text: '🚀 Inicialização'
                            size_hint_y: None
                            height: 30
                            font_size: 18
                            color: 0.79, 0.82, 0.85, 1
                            halign: 'left'
                            text_size: self.width - 20, None
                        
                        GridLayout:
                            cols: 2
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: 10
                            padding: 5
                            CheckBox:
                                id: auto_start_checkbox
                                active: app.auto_start
                                on_active: app.auto_start = self.active
                                size_hint_x: None
                                width: 40
                                color: 0.79, 0.82, 0.85, 1
                            Label:
                                text: 'Iniciar cronômetro automaticamente'
                                color: 0.79, 0.82, 0.85, 1
                                halign: 'left'
                                text_size: self.width, None

                    # --- Effects Section ---
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        padding: 10
                        spacing: 5
                        canvas.before:
                            Color:
                                rgba: 0.15, 0.16, 0.18, 1
                            Rectangle:
                                pos: self.pos
                                size: self.size
                        Label:
                            text: '✨ Efeitos'
                            size_hint_y: None
                            height: 30
                            font_size: 18
                            color: 0.79, 0.82, 0.85, 1
                            halign: 'left'
                            text_size: self.width - 20, None
                        
                        GridLayout:
                            cols: 2
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: 10
                            padding: 5
                            CheckBox:
                                id: animation_checkbox
                                active: app.animation_active
                                on_active: app.animation_active = self.active
                                size_hint_x: None
                                width: 40
                                color: 0.79, 0.82, 0.85, 1
                            Label:
                                text: 'Animação de pulsação'
                                color: 0.79, 0.82, 0.85, 1
                                halign: 'left'
                                text_size: self.width, None

                    # --- Shortcuts Section ---
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        padding: 10
                        spacing: 5
                        canvas.before:
                            Color:
                                rgba: 0.15, 0.16, 0.18, 1
                            Rectangle:
                                pos: self.pos
                                size: self.size
                        Label:
                            text: '⌨️ Atalhos'
                            size_hint_y: None
                            height: 30
                            font_size: 18
                            color: 0.79, 0.82, 0.85, 1
                            halign: 'left'
                            text_size: self.width - 20, None
                        
                        GridLayout:
                            cols: 2
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: 10
                            padding: 5
                            CheckBox:
                                id: global_shortcuts_checkbox
                                active: app.global_shortcuts
                                on_active: app.global_shortcuts = self.active
                                size_hint_x: None
                                width: 40
                                color: 0.79, 0.82, 0.85, 1
                            Label:
                                text: 'Atalhos de teclado ativos'
                                color: 0.79, 0.82, 0.85, 1
                                halign: 'left'
                                text_size: self.width, None
                            
                            Label:
                                text: 'Atalhos disponíveis:'
                                size_hint_y: None
                                height: 20
                                color: 0.79, 0.82, 0.85, 1
                                halign: 'left'
                                text_size: self.width, None
                                font_size: 14
                            Label:
                                text: '• ESPAÇO - Iniciar/Pausar\\n• R - Resetar\\n• C - Centralizar\\n• S - Configurações\\n• Duplo clique - Iniciar/Pausar'
                                size_hint_y: None
                                height: 100
                                color: 0.79, 0.82, 0.85, 1
                                halign: 'left'
                                text_size: self.width, None
                                font_size: 14

        TabbedPanelItem:
            text: '🔧 Avançado'
            background_color: 0.12, 0.13, 0.15, 1
            ScrollView:
                GridLayout:
                    cols: 1
                    size_hint_y: None
                    height: self.minimum_height
                    padding: 15
                    spacing: 10

                    # --- Performance Section ---
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        padding: 10
                        spacing: 5
                        canvas.before:
                            Color:
                                rgba: 0.15, 0.16, 0.18, 1
                            Rectangle:
                                pos: self.pos
                                size: self.size
                        Label:
                            text: '⚡ Performance'
                            size_hint_y: None
                            height: 30
                            font_size: 18
                            color: 0.79, 0.82, 0.85, 1
                            halign: 'left'
                            text_size: self.width - 20, None
                        
                        GridLayout:
                            cols: 2
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: 10
                            padding: 5
                            Label:
                                text: 'Intervalo de atualização (ms):'
                                color: 0.79, 0.82, 0.85, 1
                                halign: 'left'
                                text_size: self.width, None
                            Slider:
                                min: 50
                                max: 1000
                                value: app.update_interval
                                on_value: app.update_interval = int(self.value)
                                step: 10
                                size_hint_x: 1

                    # --- Data Section ---
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        padding: 10
                        spacing: 5
                        canvas.before:
                            Color:
                                rgba: 0.15, 0.16, 0.18, 1
                            Rectangle:
                                pos: self.pos
                                size: self.size
                        Label:
                            text: '💾 Dados'
                            size_hint_y: None
                            height: 30
                            font_size: 18
                            color: 0.79, 0.82, 0.85, 1
                            halign: 'left'
                            text_size: self.width - 20, None
                        
                        GridLayout:
                            cols: 2
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: 10
                            padding: 5
                            CheckBox:
                                id: auto_save_checkbox
                                active: app.auto_save
                                on_active: app.auto_save = self.active
                                size_hint_x: None
                                width: 40
                                color: 0.79, 0.82, 0.85, 1
                            Label:
                                text: 'Salvar configurações automaticamente'
                                color: 0.79, 0.82, 0.85, 1
                                halign: 'left'
                                text_size: self.width, None
                            
                            Button:
                                text: '💾 Salvar Agora'
                                on_release: app.save_config()
                                background_normal: ''
                                background_color: 0.14, 0.52, 0.21, 1 # Green
                                color: 1, 1, 1, 1
                            Button:
                                text: '🔄 Resetar Config'
                                on_release: app.reset_config_prompt()
                                background_normal: ''
                                background_color: 0.86, 0.21, 0.27, 1 # Red
                                color: 1, 1, 1, 1
                            Button:
                                text: '📂 Abrir Pasta'
                                on_release: app.open_config_folder()
                                background_normal: ''
                                background_color: 0.05, 0.43, 0.99, 1 # Blue
                                color: 1, 1, 1, 1
                            Label: # Placeholder for alignment
                                text: ''

                    # --- Information Section ---
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        padding: 10
                        spacing: 5
                        canvas.before:
                            Color:
                                rgba: 0.15, 0.16, 0.18, 1
                            Rectangle:
                                pos: self.pos
                                size: self.size
                        Label:
                            text: 'ℹ️ Informações'
                            size_hint_y: None
                            height: 30
                            font_size: 18
                            color: 0.79, 0.82, 0.85, 1
                            halign: 'left'
                            text_size: self.width - 20, None
                        
                        Label:
                            id: info_text_label
                            text: '' # Set dynamically in Python
                            size_hint_y: None
                            height: 100
                            color: 0.79, 0.82, 0.85, 1
                            halign: 'left'
                            text_size: self.width - 20, None
                            font_size: 14
""")

class ConfigPopup(Popup):
    # This class is just a placeholder for the KV definition
    pass

class TimerApp(App):
    # --- Kivy Properties (Reactive Configuration) ---
    # Appearance
    font_size = NumericProperty(48)
    font_family = StringProperty("Roboto") # Kivy default, can be changed to custom .ttf
    text_color = ListProperty([1, 1, 1, 1]) # RGBA for white
    border_color = ListProperty([1, 1, 1, 1]) # RGBA for white
    border_thickness = NumericProperty(2.0)
    letter_spacing = NumericProperty(0.0)
    background_type = StringProperty("transparent") # "transparent" or "solid"
    transparency = NumericProperty(0.95)
    custom_background_color = ListProperty([0.1, 0.1, 0.1, 1]) # Dark gray
    gradient_active = BooleanProperty(False)
    gradient_start_color = ListProperty([0.1, 0.1, 0.1, 1])
    gradient_end_color = ListProperty([0.2, 0.2, 0.2, 1])
    box_shape = StringProperty("retangulo") # "retangulo", "oval", "losango", "hexagono"
    rounded_border = NumericProperty(10)
    window_width = NumericProperty(280)
    window_height = NumericProperty(80)
    time_format = StringProperty("HH:MM:SS")
    show_milliseconds = BooleanProperty(False)

    # Behavior
    always_on_top = BooleanProperty(True)
    auto_start = BooleanProperty(False)
    animation_active = BooleanProperty(True)
    global_shortcuts = BooleanProperty(True)

    # Advanced
    update_interval = NumericProperty(100) # in ms
    auto_save = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config_file = "kivy_timer_config.json" # Initialize config_file here
        self.config_data = {} # Initialize config_data here

    def build(self):
        self.load_config()

        # Main layout for the timer - MUST BE INITIALIZED FIRST
        self.root_layout = FloatLayout()
        self.root_layout.bind(size=self.update_background_shape)
        self.root_layout.bind(pos=self.update_background_shape)

        # Apply initial window settings from config
        Window.size = (self.window_width, self.window_height)
        Window.left = self.config_data.get("pos_x", 100)
        Window.top = self.config_data.get("pos_y", 100)
        Window.always_on_top = self.always_on_top
        self.apply_transparency_setting() # Now self.root_layout exists

        self.start_time = None
        self.paused_time = timedelta(0)
        self.is_running = False
        self.is_paused = False
        self.drag_start_pos = None # For window dragging

        # Timer Label
        self.timer_label = Label(
            text="00:00:00",
            font_size=self.font_size,
            color=self.text_color,
            outline_width=self.border_thickness,
            outline_color=self.border_color,
            halign='center',
            valign='middle',
            size_hint=(1, 1), # Make label fill the layout
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.root_layout.add_widget(self.timer_label)

        # Bind Kivy properties to update UI
        self.bind(font_size=self.update_label_properties)
        self.bind(font_family=self.update_label_properties)
        self.bind(text_color=self.update_label_properties)
        self.bind(border_color=self.update_label_properties)
        self.bind(border_thickness=self.update_label_properties)
        self.bind(letter_spacing=self.update_label_properties) # Kivy Label doesn't have direct letter spacing, will need custom drawing if truly needed. For now, it's a config value.
        self.bind(background_type=self.on_background_type_change)
        self.bind(transparency=self.apply_transparency_setting)
        self.bind(custom_background_color=self.update_background_shape)
        self.bind(gradient_active=self.update_background_shape)
        self.bind(gradient_start_color=self.update_background_shape)
        self.bind(gradient_end_color=self.update_background_shape)
        self.bind(box_shape=self.update_background_shape)
        self.bind(rounded_border=self.update_background_shape)
        self.bind(window_width=self.update_window_size)
        self.bind(window_height=self.update_window_height) # Corrected binding
        self.bind(always_on_top=self.apply_always_on_top)
        self.bind(update_interval=self.reschedule_timer_update)
        self.bind(time_format=self.update_timer_display)
        self.bind(show_milliseconds=self.update_timer_display)

        # Schedule timer updates
        self.timer_event = Clock.schedule_interval(self.update_timer_display, self.update_interval / 1000.0)

        # Bind window events for dragging and context menu
        Window.bind(on_touch_down=self.on_window_touch_down)
        Window.bind(on_touch_move=self.on_window_touch_move)
        Window.bind(on_key_down=self.on_keyboard_shortcut)

        # Auto start if configured
        if self.auto_start:
            Clock.schedule_once(lambda dt: self.toggle_timer(), 1)

        # Initial draw of background shape
        self.update_background_shape()

        return self.root_layout

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Update Kivy properties from loaded config
                    self.font_size = loaded_config.get("tamanho_fonte", self.font_size)
                    self.font_family = loaded_config.get("fonte_familia", self.font_family)
                    self.text_color = self.hex_to_rgba(loaded_config.get("cor_preenchimento", "#FFFFFF"))
                    self.border_color = self.hex_to_rgba(loaded_config.get("cor_borda", "#FFFFFF"))
                    self.border_thickness = loaded_config.get("espessura_borda", self.border_thickness)
                    self.letter_spacing = loaded_config.get("espacamento_letras", self.letter_spacing)
                    self.background_type = loaded_config.get("tipo_fundo", self.background_type)
                    self.transparency = loaded_config.get("transparencia", self.transparency)
                    self.custom_background_color = self.hex_to_rgba(loaded_config.get("cor_fundo_personalizada", "#2d2d2d"))
                    self.gradient_active = loaded_config.get("gradiente_ativo", self.gradient_active)
                    self.gradient_start_color = self.hex_to_rgba(loaded_config.get("cor_gradiente_inicio", "#1a1a1a"))
                    self.gradient_end_color = self.hex_to_rgba(loaded_config.get("cor_gradiente_fim", "#3a3a3a"))
                    self.box_shape = loaded_config.get("forma_caixa", self.box_shape)
                    self.rounded_border = loaded_config.get("borda_arredondada", self.rounded_border)
                    self.window_width = loaded_config.get("largura", self.window_width)
                    self.window_height = loaded_config.get("altura", self.window_height)
                    self.time_format = loaded_config.get("formato_tempo", self.time_format)
                    self.show_milliseconds = loaded_config.get("mostrar_milissegundos", self.show_milliseconds)
                    self.always_on_top = loaded_config.get("sempre_visivel", self.always_on_top)
                    self.auto_start = loaded_config.get("auto_iniciar", self.auto_start)
                    self.animation_active = loaded_config.get("animacao", self.animation_active)
                    self.global_shortcuts = loaded_config.get("atalhos_globais", self.global_shortcuts)
                    self.update_interval = loaded_config.get("intervalo_atualizacao", self.update_interval)

                    # Load window position separately as it's not a Kivy Property
                    self.config_data = loaded_config # Store full config for pos_x/y
            except Exception as e:
                print(f"Error loading config: {e}")
                self.config_data = {} # Reset to empty if corrupted
        else:
            self.config_data = {}

    def save_config(self):
        if self.auto_save:
            try:
                config_to_save = {
                    "largura": self.window_width,
                    "altura": self.window_height,
                    "pos_x": Window.left,
                    "pos_y": Window.top,
                    "tamanho_fonte": self.font_size,
                    "fonte_familia": self.font_family,
                    "cor_preenchimento": self.rgba_to_hex(self.text_color),
                    "cor_borda": self.rgba_to_hex(self.border_color),
                    "espessura_borda": self.border_thickness,
                    "espacamento_letras": self.letter_spacing,
                    "tipo_fundo": self.background_type,
                    "transparencia": self.transparency,
                    "cor_fundo_personalizada": self.rgba_to_hex(self.custom_background_color),
                    "gradiente_ativo": self.gradient_active,
                    "cor_gradiente_inicio": self.rgba_to_hex(self.gradient_start_color),
                    "cor_gradiente_fim": self.rgba_to_hex(self.gradient_end_color),
                    "forma_caixa": self.box_shape,
                    "borda_arredondada": self.rounded_border,
                    "formato_tempo": self.time_format,
                    "mostrar_milissegundos": self.show_milliseconds,
                    "sempre_visivel": self.always_on_top,
                    "auto_iniciar": self.auto_start,
                    "animacao": self.animation_active,
                    "atalhos_globais": self.global_shortcuts,
                    "auto_salvar": self.auto_save,
                    "intervalo_atualizacao": self.update_interval,
                }
                with open(self.config_file, "w") as f:
                    json.dump(config_to_save, f, indent=4)
                print("Configurações salvas com sucesso.")
            except Exception as e:
                print(f"Erro ao salvar configurações: {e}")

    def hex_to_rgba(self, hex_color, alpha=1.0):
        if not isinstance(hex_color, str): # Already RGBA
            return hex_color
        hex_color = hex_color.lstrip('#')
        lv = len(hex_color)
        rgb = tuple(int(hex_color[i:i + lv // 3], 16) / 255.0 for i in range(0, lv, lv // 3))
        return rgb + (alpha,)

    def rgba_to_hex(self, rgba_color):
        if len(rgba_color) == 4:
            r, g, b, a = rgba_color
        elif len(rgba_color) == 3:
            r, g, b = rgba_color
            a = 1.0 # Default alpha if not provided
        else:
            return "#000000" # Fallback

        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

    def update_label_properties(self, instance, value):
        # This method is called when font_size, font_family, text_color, border_color, border_thickness change
        self.timer_label.font_size = self.font_size
        self.timer_label.color = self.text_color
        self.timer_label.outline_width = self.border_thickness
        self.timer_label.outline_color = self.border_color
        # Kivy Label doesn't have direct letter spacing, so this property is mostly for config saving.
        # For true letter spacing, custom text rendering would be needed.
        self.timer_label.font_name = self.font_family # Kivy uses font_name for font family
        self.update_timer_display(0) # Force redraw

    def update_window_size(self, instance, value):
        Window.size = (self.window_width, self.window_height)
        self.update_background_shape() # Redraw shape on size change

    def update_window_height(self, instance, value):
        Window.size = (self.window_width, self.window_height)
        self.update_background_shape() # Redraw shape on size change

    def apply_always_on_top(self, instance, value):
        Window.always_on_top = value

    def reschedule_timer_update(self, instance, value):
        self.timer_event.cancel()
        self.timer_event = Clock.schedule_interval(self.update_timer_display, self.update_interval / 1000.0)

    def on_background_type_change(self, instance, value):
        self.apply_transparency_setting()
        self.update_background_shape()

    def apply_transparency_setting(self, *args):
        if self.background_type == "transparent":
            Window.clearcolor = (0, 0, 0, 0) # Fully transparent background
            Window.opacity = self.transparency # Apply overall window opacity
        else:
            # When not transparent, Kivy will draw the background color/gradient
            Window.clearcolor = (0, 0, 0, 1) # Opaque black, so our canvas drawing is visible
            Window.opacity = 1.0 # Full opacity for the window itself
        self.update_background_shape() # Redraw shape based on new background type

    def update_timer_display(self, dt):
        if self.is_running:
            elapsed_time = datetime.now() - self.start_time
            total_delta = elapsed_time + self.paused_time
        else:
            total_delta = self.paused_time

        self.timer_label.text = self.format_time(total_delta)

    def format_time(self, delta):
        total_seconds = int(delta.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        formato = self.time_format
        
        if formato == "MM:SS" and hours == 0:
            text = f"{minutes:02d}:{seconds:02d}"
        elif formato == "HH:MM":
            text = f"{hours:02d}:{minutes:02d}"
        else:  # HH:MM:SS (default)
            text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        if self.show_milliseconds:
            millis = int(delta.microseconds / 1000)
            text += f".{millis:03d}"
        
        return text

    def toggle_timer(self):
        if not self.is_running and not self.is_paused: # Start from scratch
            self.start_time = datetime.now()
            self.is_running = True
            self.is_paused = False
        elif self.is_running: # Pause
            self.paused_time += (datetime.now() - self.start_time)
            self.is_running = False
            self.is_paused = True
        elif self.is_paused: # Resume
            self.start_time = datetime.now()
            self.is_running = True
            self.is_paused = False
        self.update_timer_display(0) # Force immediate update

    def reset_timer(self):
        self.start_time = None
        self.paused_time = timedelta(0)
        self.is_running = False
        self.is_paused = False
        self.update_timer_display(0) # Force immediate update

    def centralize_window(self):
        screen_width = Window.width
        screen_height = Window.height
        x = (screen_width - self.window_width) // 2
        y = 100  # Keep near top
        Window.left = x
        Window.top = y
        self.save_config() # Save new position

    def copy_time(self):
        # Kivy doesn't have a direct clipboard module in core, usually requires plyer
        # For simplicity, we'll just print for now or use a messagebox
        try:
            from kivy.app import platform as kivy_platform
            if kivy_platform == 'android' or kivy_platform == 'ios':
                # Mobile platforms might have different clipboard access
                pass
            else:
                import pyperclip
                pyperclip.copy(self.timer_label.text)
                print(f"Tempo copiado: {self.timer_label.text}")
        except ImportError:
            print("pyperclip not installed. Cannot copy to clipboard.")
            print(f"Tempo: {self.timer_label.text}")
        except Exception as e:
            print(f"Error copying to clipboard: {e}")

    def set_time(self):
        # This would require a custom popup with TextInput for time input
        # For now, we'll skip this complex UI part for brevity in Kivy
        print("Set time functionality not yet implemented in Kivy version.")
        pass

    def on_window_touch_down(self, window, touch):
        if self.root_layout.collide_point(*touch.pos): # Only drag if touch is on the timer window
            self.drag_start_pos = touch.pos
            if touch.button == 'right': # Simulate right-click for context menu
                self.open_context_menu(touch.x, touch.y)
            elif touch.is_double_tap: # Double click to toggle
                self.toggle_timer()
            return True
        return False

    def on_window_touch_move(self, window, touch):
        if self.drag_start_pos:
            # Calculate new window position based on drag
            dx = touch.x - self.drag_start_pos[0]
            dy = touch.y - self.drag_start_pos[1]
            Window.left += dx
            Window.top += dy
            return True
        return False

    def on_window_touch_up(self, window, touch):
        self.drag_start_pos = None
        self.save_config() # Save position after drag ends
        return True

    def on_keyboard_shortcut(self, window, key, scancode, codepoint, modifier):
        if not self.global_shortcuts:
            return False # Don't process if shortcuts are disabled

        if codepoint == ' ': # Spacebar
            self.toggle_timer()
            return True
        elif codepoint == 'r': # R key
            self.reset_timer()
            return True
        elif codepoint == 'c': # C key
            self.centralize_window()
            return True
        elif codepoint == 's': # S key
            self.open_config_window()
            return True
        return False

    def open_context_menu(self, x, y):
        # Kivy doesn't have a native context menu. We create a simple Popup.
        content = BoxLayout(orientation='vertical', spacing=5, padding=10)
        
        btn_toggle = Button(text="▶️ Iniciar / ⏸️ Pausar", size_hint_y=None, height=40,
                            on_release=lambda btn: (self.toggle_timer(), popup.dismiss()))
        btn_reset = Button(text="🔄 Resetar", size_hint_y=None, height=40,
                           on_release=lambda btn: (self.reset_timer(), popup.dismiss()))
        btn_config = Button(text="⚙️ Configurações", size_hint_y=None, height=40,
                            on_release=lambda btn: (self.open_config_window(), popup.dismiss()))
        btn_centralize = Button(text="📍 Centralizar", size_hint_y=None, height=40,
                                on_release=lambda btn: (self.centralize_window(), popup.dismiss()))
        btn_exit = Button(text="❌ Sair", size_hint_y=None, height=40,
                          on_release=lambda btn: (self.stop(), popup.dismiss()))

        content.add_widget(btn_toggle)
        content.add_widget(btn_reset)
        content.add_widget(btn_centralize)
        content.add_widget(btn_config)
        content.add_widget(btn_exit)

        popup = Popup(title='Opções do Cronômetro', content=content,
                      size_hint=(None, None), width=250, # Set width, height will be adjusted
                      pos=(x, y - content.minimum_height - 50), # Initial pos, might need adjustment
                      auto_dismiss=True,
                      background_color=(0.12, 0.13, 0.15, 1))
        
        # Schedule a call to adjust height after the popup is opened and content is laid out
        # This is a common Kivy pattern for dynamic sizing
        def adjust_popup_size(dt):
            popup.height = content.minimum_height + 50 # Add some padding
            popup.pos = (x, y - popup.height) # Adjust position based on new height
        
        popup.bind(on_open=adjust_popup_size) # Bind to on_open event
        popup.open()

    def open_config_window(self):
        # Create and open the configuration popup
        config_popup = ConfigPopup()
        
        # Populate font family buttons dynamically
        font_family_grid = config_popup.content.ids.font_family_grid
        font_family_grid.clear_widgets()
        fontes = ["Roboto", "Arial", "Times", "Courier", "Impact", "Georgia", "Verdana"] # Kivy default fonts or common ones
        for f in fontes:
            btn = ToggleButton(text=f, group='font_family', size_hint_x=None, width=100,
                               state='down' if self.font_family == f else 'normal',
                               on_release=lambda b, font=f: self.set_font_family(font) if b.state == 'down' else None,
                               background_normal='', background_color=(0.13, 0.15, 0.18, 1), color=(1,1,1,1))
            font_family_grid.add_widget(btn)

        # Set info text for Advanced tab
        info_text_label = config_popup.content.ids.info_text_label
        info_text_label.text = f"""Sistema: {platform.system()} {platform.release()}
Versão Python: {sys.version.split()[0]}
Arquivo de config: {os.path.abspath(self.config_file)}
Cronômetro Premium v3.0 (Kivy)"""

        config_popup.open()

    def set_font_family(self, font_name):
        self.font_family = font_name

    def open_color_picker(self, target_property):
        def on_color_select(instance, value):
            if target_property == 'text_color':
                self.text_color = value
            elif target_property == 'border_color':
                self.border_color = value
            elif target_property == 'custom_background_color':
                self.custom_background_color = value
            elif target_property == 'gradient_start_color':
                self.gradient_start_color = value
            elif target_property == 'gradient_end_color':
                self.gradient_end_color = value
            color_picker_popup.dismiss()

        # Set initial color for the picker
        initial_color = [0,0,0,1]
        if target_property == 'text_color': initial_color = self.text_color
        elif target_property == 'border_color': initial_color = self.border_color
        elif target_property == 'custom_background_color': initial_color = self.custom_background_color
        elif target_property == 'gradient_start_color': initial_color = self.gradient_start_color
        elif target_property == 'gradient_end_color': initial_color = self.gradient_end_color

        color_picker = ColorPicker(color=initial_color)
        color_picker.bind(color=on_color_select)

        color_picker_popup = Popup(title="Escolher Cor", content=color_picker,
                                   size_hint=(0.9, 0.9), auto_dismiss=False)
        
        # Add a close button to the color picker popup
        close_button = Button(text="Fechar", size_hint_y=None, height=40,
                              on_release=color_picker_popup.dismiss)
        color_picker.add_widget(close_button) # Add to the color picker content

        color_picker_popup.open()

    def update_background_shape(self, *args):
        self.root_layout.canvas.before.clear()
        with self.root_layout.canvas.before:
            if self.background_type == "solid":
                if self.gradient_active:
                    self.draw_gradient(self.root_layout.width, self.root_layout.height)
                else:
                    Color(*self.custom_background_color)
                    self.draw_shape(self.root_layout.width, self.root_layout.height)
            # If transparent, Window.clearcolor handles it, no drawing needed here.

    def draw_shape(self, w, h):
        if self.box_shape == "retangulo":
            # Kivy's Rectangle supports radius directly
            Rectangle(pos=self.root_layout.pos, size=self.root_layout.size,
                      radius=[self.rounded_border]*4)
        elif self.box_shape == "oval":
            Ellipse(pos=self.root_layout.pos, size=self.root_layout.size)
        elif self.box_shape == "losango":
            # Draw a diamond using Line instructions
            center_x, center_y = self.root_layout.pos[0] + w/2, self.root_layout.pos[1] + h/2
            points = [
                center_x, self.root_layout.pos[1], # Top
                self.root_layout.pos[0] + w, center_y, # Right
                center_x, self.root_layout.pos[1] + h, # Bottom
                self.root_layout.pos[0], center_y # Left
            ]
            # Use Mesh for filled polygon
            Mesh(vertices=points, indices=[0,1,2,0,2,3], mode='triangles')
        elif self.box_shape == "hexagono":
            # Draw a hexagon using Line instructions
            center_x, center_y = self.root_layout.pos[0] + w/2, self.root_layout.pos[1] + h/2
            size_x = w / 2.5 # Adjust for aspect ratio
            size_y = h / 2.5
            points = [
                center_x, center_y + size_y,           # Top
                center_x + size_x * math.cos(math.pi/6), center_y + size_y * math.sin(math.pi/6), # Top-right
                center_x + size_x * math.cos(math.pi/6), center_y - size_y * math.sin(math.pi/6), # Bottom-right
                center_x, center_y - size_y,           # Bottom
                center_x - size_x * math.cos(math.pi/6), center_y - size_y * math.sin(math.pi/6), # Bottom-left
                center_x - size_x * math.cos(math.pi/6), center_y + size_y * math.sin(math.pi/6)  # Top-left
            ]
            # Use Mesh for filled polygon
            Mesh(vertices=points, indices=[0,1,2,0,2,5,2,3,4], mode='triangles') # Simplified indices for a convex polygon

    def draw_gradient(self, w, h):
        # Kivy's Mesh instruction can be used for gradients
        # We'll create a simple vertical gradient using two triangles
        start_r, start_g, start_b, start_a = self.gradient_start_color
        end_r, end_g, end_b, end_a = self.gradient_end_color

        # Vertices for a rectangle (two triangles) with color at each corner
        # Format: (x, y, u, v, r, g, b, a) - u,v are texture coords, not used here
        vertices = [
            self.root_layout.x, self.root_layout.y, 0, 0, start_r, start_g, start_b, start_a, # Bottom-left (start color)
            self.root_layout.x + w, self.root_layout.y, 1, 0, start_r, start_g, start_b, start_a, # Bottom-right (start color)
            self.root_layout.x + w, self.root_layout.y + h, 1, 1, end_r, end_g, end_b, end_a, # Top-right (end color)
            self.root_layout.x, self.root_layout.y + h, 0, 1, end_r, end_g, end_b, end_a, # Top-left (end color)
        ]
        indices = [0, 1, 2, 2, 3, 0] # Two triangles to form a rectangle

        Mesh(vertices=vertices, indices=indices, mode='triangles')

    def apply_size_preset(self, width, height):
        self.window_width = width
        self.window_height = height
        # Window.size is updated by the window_width/height property binding

    def reset_config_prompt(self):
        # Kivy doesn't have a direct messagebox, so we use a simple Popup
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text="Tem certeza que deseja resetar todas as configurações?", color=(0.79, 0.82, 0.85, 1)))
        
        button_layout = BoxLayout(spacing=10, size_hint_y=None, height=40)
        btn_yes = Button(text="Sim", on_release=lambda btn: (self.reset_all_config(), popup.dismiss()))
        btn_no = Button(text="Não", on_release=lambda btn: popup.dismiss())
        button_layout.add_widget(btn_yes)
        button_layout.add_widget(btn_no)
        content.add_widget(button_layout)

        popup = Popup(title="Confirmar Reset", content=content,
                      size_hint=(None, None), size=(400, 200), auto_dismiss=False)
        popup.open()

    def reset_all_config(self):
        # Delete config file
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
            print("Configurações resetadas e arquivo removido.")
        
        # Restart the app to load default config
        self.stop() # Stop current Kivy app
        # Re-launch the app (platform-dependent)
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def open_config_folder(self):
        pasta = os.path.dirname(os.path.abspath(self.config_file))
        if platform.system() == "Windows":
            os.startfile(pasta)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", pasta])
        else:  # Linux
            subprocess.run(["xdg-open", pasta])

    def on_stop(self):
        # This method is called when the app is about to close
        self.save_config()
        # Unbind keyboard to prevent issues if app is not fully closed
        Window.unbind(on_key_down=self.on_keyboard_shortcut)
        print("Kivy Timer App stopped.")

if __name__ == '__main__':
    TimerApp().run()
