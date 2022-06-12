import math
from kivymd.app import MDApp
from kivy.lang import Builder
from botoes import *
from tela import *
from db_sqlite import Sqlite





class MainApp(MDApp):


    def build(self):
        self.sqlite = Sqlite()
        return Builder.load_file("main.kv")

    def on_start(self):
        self.Minutos()
        self.Horas()

    def mudartela(self, id_tela):
        gerenciador_tela = self.root.ids["screen_manager"]
        gerenciador_tela.current = id_tela



    def Adicionar_horas(self):
        minuto = self.root.ids['addhora']
        minutos = minuto.ids['minuto_input'].text
        horas = self.sqlite.rootHoras()
        try:
            self.sqlite.Atualizar_horas(int(horas.text))
            self.sqlite.Atualizar_minutos(int(minutos))
            minuto.ids['hora_input'].text = ""
            minuto.ids['minuto_input'].text =""
            self.Horas()
            self.Minutos()
            self.mudartela("homepage")
            pagina_addhr = self.root.ids['addhora']
            pagina_addhr.ids['mensagem_erro'].text = ""
        except:
            pagina_addhr = self.root.ids['addhora']
            pagina_addhr.ids['mensagem_erro'].text = 'PREENCHE O CAMPO COM HORAS/MINUTOS \n Exemplo: 1:0, 0:45'
            pagina_addhr.ids['mensagem_erro'].color = (1, 0, 0, 1)



    def Minutos(self):
        id, hr, minu = self.sqlite.ler_infomacoes()[0]
        mi = (minu / 60) % 1 * 60
        minu = "{0:.0f}".format(mi)
        minuto = self.root.ids['homepage']
        minuto.ids['minuto_input'].text = minu


    def Horas(self):
        id, hra, minu = self.sqlite.ler_infomacoes()[0]
        minutos = (minu / 60)
        horas = "{0:.1f}".format(int(minutos))
        horas = math.floor(float(horas))
        horas = str(horas + hra)
        minuto = self.root.ids['homepage']
        minuto.ids['hora_input'].text = horas

    def reset(self):
            self.comando = f"""UPDATE cimv
                       SET Hora = 00, Minuto = 00;
                       """
            self.sqlite.db_connect.execute(self.comando)
            self.sqlite.db.commit()
            self.Horas()
            self.Minutos()








MainApp().run()