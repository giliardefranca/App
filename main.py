import math
from datetime import datetime, date
from kivymd.app import MDApp
from kivy.lang import Builder
from botoes import *
from tela import *
from firebase import MyFireBase
import requests
import os
import certifi
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.picker import MDDatePicker, MDTimePicker
from kivy.uix.progressbar import ProgressBar
from kivy.loader import Loader





os.environ["SSL_CERT_FILE"] = certifi.where()


class MainApp(MDApp):


    def build(self):


        self.firebase = MyFireBase()
        screen = Builder.load_file("main.kv")
        self.icon = 'icones/icon.png'



        return screen
    def on_start(self):

        self.carregando_info_automatico()


    def mudartela(self, id_tela):
        gerenciador_tela = self.root.ids["screen_manager"]
        gerenciador_tela.current = id_tela



    def Requisicao_get_banco_dados(self, local_id):
        link_banco_dados = f" https://registradordehoras-9e0d4-default-rtdb.firebaseio.com/{local_id}.json?auth={self.id_token}"
        requisicao = requests.get(link_banco_dados)
        dados_data_minutos = requisicao.json()
        minu = dados_data_minutos['Minutos']
        horas = dados_data_minutos['Horas']
        dias_total_mar = dados_data_minutos['Total Dia']
        data_inicial = dados_data_minutos['Data Inicial']
        minu = int(minu)
        return horas, minu, data_inicial, dias_total_mar

    def Requisicao_patch_banco_dados(self,hora, minuto, local_id):
        link = f" https://registradordehoras-9e0d4-default-rtdb.firebaseio.com/{local_id}.json?auth={self.id_token}"
        horas_atualizada = f'{{"Horas":"{hora}", "Minutos": "{minuto}"}}'
        requests.patch(link, data=horas_atualizada)


    def Adicionar_horas(self, instance, time):

        try:

            self.time = f"{time}".split(":")
            horas = self.time[0]
            minuto = self.time[1]
            hora = int(horas)
            minuto = int(minuto)


            horas_banco, minuitos_banco, data, total_dia = self.Requisicao_get_banco_dados(self.local_id)


            minu = minuitos_banco + minuto
            minutos = (int(minu) / 60)
            horas = "{0:.1f}".format(int(minutos))
            horas = math.floor(float(horas))
            horas = int(horas)


            hora_atual = hora + horas

            horas_convertida_minutos = (minu / 60) % 1 * 60
            minu_formatado = "{0:.0f}".format(horas_convertida_minutos)
            minu_formatado = int(minu_formatado)


            horas = int(horas_banco)
            horas = horas + hora_atual


            self.Requisicao_patch_banco_dados(str(horas), str(minu_formatado), self.local_id)


            self.carregando_info_automatico()


        except Exception as erro:
            msg = 'PREENCHE O CAMPO COM HORAS/MINUTOS \n Exemplo: 1:0, 0:45'
            self.dialogAviso(msg)


    def atualizar_dias_restante(self):
        dias = self.TOTAL_DATA()
        self.bar(int(dias))
        homepage = self.root.ids['homepage']
        homepage.ids['dias_restantes'].text = f"{dias} Dias - De Mar"
        total_dias, data = self.Objetivo_100dias()
        date = datetime.strptime(data, '%Y-%m-%d').date()
        data= "{}/{}/{}".format(date.day, date.month, date.year)
        homepage.ids['comeco'].text = f"Inicio: {data}"


    def carregando_info_automatico(self):
        try:
            with open('refresh.txt', 'r') as arquivo:
                refresh_token = arquivo.read()
                if refresh_token:
                    local_id, id_token = self.firebase.trocar_token(refresh_token)
                    self.local_id = local_id
                    self.id_token = id_token

                    link = f" https://registradordehoras-9e0d4-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}"
                    requisicao = requests.get(link)
                    banco_de_dado = requisicao.json()
                    homepage = self.root.ids['homepage']
                    homepage.ids['minuto_input'].text = banco_de_dado['Minutos']
                    homepage = self.root.ids['homepage']
                    homepage.ids['hora_input'].text = banco_de_dado['Horas']
                    self.mudartela('homepage')
                    self.atualizar_dias_restante()
                    self.Objetivo_completado()
                else:
                    self.mudartela("login")

        except:
            self.dialogAviso("Erro de Conexão, Tente Novamente!")

    def reset(self, obj):
        try:
            link = f" https://registradordehoras-9e0d4-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}"
            horas_atualizada = f'{{"Horas":"{0}", "Minutos": "{0}"}}'
            requests.patch(link, data=horas_atualizada)
            self.carregando_info_automatico()
            self.dialog.dismiss()
        except:
            pass

    def cancelar(self, obj):
        self.dialog.dismiss()

    def dialogConfirmacao(self):
        self.dialog = MDDialog(
            title = "Deletar Horas Registrada",
            text="Você tem Certeza?",
            buttons=[
                MDFlatButton(text="CANCEL", on_release=self.cancelar), MDRaisedButton(text="Confirmar", on_release=self.reset),
            ],
        )
        self.dialog.open()

    def dialogRemoverdia(self):
        self.dialog = MDDialog(
            title = "Remover o Dia de Hoje",
            text="Você tem Certeza?",
            buttons=[
                MDFlatButton(text="CANCEL", on_release=self.cancelar), MDRaisedButton(text="Confirmar", on_release=self.RemoverDia),
            ],
        )
        self.dialog.open()




    def on_save_inicio(self, instance, value, date_range):
        try:
            link = f" https://registradordehoras-9e0d4-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}"
            horas_atualizada = f'{{"Data Inicial": "{value}"}}'
            requests.patch(link, data=horas_atualizada)
            self.atualizar_dias_restante()
        except:
            self.dialogAviso("Sem conexão")




    def Objetivo_100dias(self):
        try:
            hora, minuto, data, total_dias = self.Requisicao_get_banco_dados(self.local_id)
            return int(total_dias), data
        except:
            self.dialogAviso("Sem conexão")

    def TOTAL_DATA(self):
        try:
            hora, minuto, data, total_dias = self.Requisicao_get_banco_dados(self.local_id)
            dias_total = datetime.strptime(str(data), '%Y-%m-%d').date()
            dias_hoje = int((dias_total - date.today()).days)
            self.objetivo, data = self.Objetivo_100dias()
            self.dias_hoje = self.objetivo - dias_hoje
            return self.dias_hoje
        except:
            self.dialogAviso("Sem conexão")

    def data_inicio(self):
        date_dialog = MDDatePicker()

        date_dialog.bind(on_save=self.on_save_inicio)

        date_dialog.open()




    def dialogAviso(self, text):
        self.dialog = MDDialog(
            title="ATENÇÂO",
            text=f"[color=#000000]{text}[/color]",
            radius=[20, 7, 20, 7],
        )
        self.dialog.md_bg_color = ("#00B7C2")
        self.dialog.open()

    def Congratulations(self, horas_mar, dias_mar):
        self.dialog = MDDialog(
            title="Congratulations!!",
            text=f"[color=#000000]Seu Objetivo foi Concluido! \n [s] {horas_mar}Horas de Mar [/s] e [s] {dias_mar} Dias de Mar [/s] [/color]",
            radius=[20, 7, 20, 7],
        )
        self.dialog.md_bg_color = ("#00B7C2")
        self.dialog.open()



    def show_time_picker(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(on_save=self.Adicionar_horas)
        time_dialog.open()



    def RemoverDia(self, obj):
        dia_mar_perdido = 1
        hora, minuto, data, dias_perdido = self.Requisicao_get_banco_dados(self.local_id)
        dias = int(dias_perdido)
        dias -= dia_mar_perdido
        link = f" https://registradordehoras-9e0d4-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}"
        horas_atualizada = f'{{"Total Dia":"{dias}"}}'
        requests.patch(link, data=horas_atualizada)
        self.atualizar_dias_restante()
        self.dialog.dismiss()
        self.mudartela("homepage")



    def Objetivo_completado(self):
        link_banco_dados = f" https://registradordehoras-9e0d4-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}"
        requisicao = requests.get(link_banco_dados)
        banco_de_dado = requisicao.json()
        hora_completado = banco_de_dado['Horas']
        dias_completado = self.TOTAL_DATA()
        if hora_completado >= "3" and dias_completado == 2:
            self.Congratulations(hora_completado, dias_completado)

    def SairAPP(self):
        refresh = open('refresh.txt', 'r+')
        refresh.truncate(0)
        self.mudartela("login")

    def bar(self, progresso):
        page = self.root.ids['homepage']
        value = page.ids['progress'].value = progresso
        page.ids['porcentagem'].text =f"{value}% Progresso"




MainApp().run()