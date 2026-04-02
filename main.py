from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
import sqlite3

Window.size = (360, 640) 

class FacturaApp(App):
    def build(self):
        self.conn = sqlite3.connect('facturas.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS ventas (id INTEGER PRIMARY KEY, cliente TEXT, producto TEXT, total REAL)")
        self.conn.commit()

        self.main_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        self.main_layout.add_widget(Label(text='FACTURACION PRO', font_size='26sp', bold=True, size_hint_y=None, height=50, color=(0, 1, 1, 1)))

        self.input_cliente = TextInput(hint_text='Nombre del Cliente', multiline=False, size_hint_y=None, height=45)
        self.input_producto = TextInput(hint_text='Producto / Servicio', multiline=False, size_hint_y=None, height=45)
        self.input_monto = TextInput(hint_text='Monto Neto RD$', multiline=False, size_hint_y=None, height=45, input_filter='float')
        self.input_itbis_val = TextInput(text='18', hint_text='ITBIS %', multiline=False, size_hint_y=None, height=45, input_filter='float')

        self.main_layout.add_widget(self.input_cliente)
        self.main_layout.add_widget(self.input_producto)
        
        row_precios = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=45)
        row_precios.add_widget(self.input_monto)
        row_precios.add_widget(self.input_itbis_val)
        self.main_layout.add_widget(row_precios)

        btn_g = Button(text='GUARDAR FACTURA', background_color=(0, 0.8, 0, 1), bold=True, size_hint_y=None, height=50)
        btn_g.bind(on_press=self.facturar)
        self.main_layout.add_widget(btn_g)

        btn_b = Button(text='BUSCAR Y VER TODO', background_color=(0.2, 0.5, 1, 1), bold=True, size_hint_y=None, height=50)
        btn_b.bind(on_press=self.consultar)
        self.main_layout.add_widget(btn_b)

        self.scroll = ScrollView(size_hint=(1, 1), bar_width=10)
        self.lista_resultados = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.lista_resultados.bind(minimum_height=self.lista_resultados.setter('height'))
        self.scroll.add_widget(self.lista_resultados)
        self.main_layout.add_widget(self.scroll)

        return self.main_layout

    def facturar(self, instance):
        try:
            cli, pro, mon = self.input_cliente.text, self.input_producto.text, self.input_monto.text.strip()
            tasa = float(self.input_itbis_val.text) if self.input_itbis_val.text else 0
            if cli and pro and mon:
                total = float(mon) + (float(mon) * (tasa / 100))
                self.cursor.execute("INSERT INTO ventas (cliente, producto, total) VALUES (?, ?, ?)", (cli, pro, total))
                self.conn.commit()
                self.input_cliente.text = ""; self.input_producto.text = ""; self.input_monto.text = ""
                self.lista_resultados.clear_widgets()
                self.lista_resultados.add_widget(Label(text=f"✅ Guardado: RD$ {total:,.2f}", size_hint_y=None, height=40))
            else: self.lista_resultados.add_widget(Label(text="⚠️ Faltan datos", size_hint_y=None, height=40))
        except: self.lista_resultados.add_widget(Label(text="❌ Error en datos", size_hint_y=None, height=40))

    def consultar(self, instance):
        nombre = self.input_cliente.text
        self.lista_resultados.clear_widgets()
        if nombre:
            self.cursor.execute("SELECT * FROM ventas WHERE cliente LIKE ? ORDER BY id DESC", ('%' + nombre + '%',))
            rows = self.cursor.fetchall()
            if rows:
                for r in rows:
                    txt = f"👤 {r[1]} | 📦 {r[2]}\n💰 Total: RD$ {r[3]:,.2f}\n------------------------"
                    lbl = Label(text=txt, size_hint_y=None, height=80, halign='left', valign='middle')
                    lbl.bind(size=lbl.setter('text_size'))
                    self.lista_resultados.add_widget(lbl)
            else: self.lista_resultados.add_widget(Label(text="❌ No se encontró nada", size_hint_y=None, height=40))
        else: self.lista_resultados.add_widget(Label(text="⚠️ Escribe nombre", size_hint_y=None, height=40))

if __name__ == '__main__':
    FacturaApp().run()
