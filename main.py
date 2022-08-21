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
        dados = requisicao.json()
        minu = dados['Minutos']
        horas = dados['Horas']
        dias_total_mar = dados['Total Dia']
        data_inicial = dados['Data Inicial']
        frases = dados["Frases"]

        minu = int(minu)
        return horas, minu, data_inicial, dias_total_mar, frases



    def Requisicao_patch_banco_dados(self,frases, hora, minuto, local_id):
        link = f" https://registradordehoras-9e0d4-default-rtdb.firebaseio.com/{local_id}.json?auth={self.id_token}"
        horas_atualizada = f'{{"Frases": "{frases}","Horas":"{hora}", "Minutos": "{minuto}"}}'
        requests.patch(link, data=horas_atualizada)


    def Adicionar_horas_minutos(self, instance, time):
        try:
            self.time = f"{time}".split(":")
            horas = self.time[0]
            minuto = self.time[1]
            hora = int(horas)
            minuto = int(minuto)
            horas_banco, minuitos_banco, data, total_dia, frases = self.Requisicao_get_banco_dados(self.local_id)

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



            self.Requisicao_patch_banco_dados(frases, str(horas), str(minu_formatado), self.local_id)
            self.atualizar_outinput_horas_minutos()

        except:
            msg = 'Sem conexão'
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
                    homepage.ids['frases'].text = f'Frases Mineradas: {banco_de_dado["Frases"]}'
                    self.mudartela('homepage')
                    self.atualizar_dias_restante()


                else:
                    self.mudartela("login")
        except:
            self.dialogAviso("Erro de Conexão, Tente Novamente!")


    def reset(self, obj):
        try:
            link = f"https://registradordehoras-9e0d4-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}"
            horas_atualizada = f'{{"Horas":"{0}", "Minutos": "{0}"}}'
            requests.patch(link, data=horas_atualizada)
            self.atualizar_outinput_horas_minutos()
            self.dialog.dismiss()
        except:
            pass

    def cancelar(self, obj):
        self.dialog.dismiss()



    def DeletarFrases(self, *args):
        try:
            link = f"https://registradordehoras-9e0d4-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}"
            horas_atualizada = f'{{"Frases":"{0}"}}'
            requests.patch(link, data=horas_atualizada)
            self.AtualizarCampoFrases()
            self.dialog.dismiss()
        except:
            pass


    def dialogConfirmacao(self):
        self.dialog = MDDialog(
            title = "Deletar Horas Registrada/Frases",
            text="O que deseja apagar?",
            buttons=[
                MDFlatButton(text="CANCEL", on_release=self.cancelar),
                MDRaisedButton(text="Frases", on_release=self.DeletarFrases), MDRaisedButton(text="Horas", on_release=self.reset),
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





    def on_save_data_inicio(self, instance, value, date_range):
        try:
            link = f"https://registradordehoras-9e0d4-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}"
            horas_atualizada = f'{{"Data Inicial": "{value}"}}'
            requests.patch(link, data=horas_atualizada)
            self.atualizar_dias_restante()
        except:
            self.dialogAviso("Sem conexão")




    def Objetivo_100dias(self):
        try:
            hora, minuto, data, total_dias, frases = self.Requisicao_get_banco_dados(self.local_id)
            return int(total_dias), data
        except:
            self.dialogAviso("Sem conexão")


    def TOTAL_DATA(self):
        try:
            hora, minuto, data, total_dias, frases = self.Requisicao_get_banco_dados(self.local_id)
            dias_total = datetime.strptime(str(data), '%Y-%m-%d').date()
            dias_hoje = int((dias_total - date.today()).days)
            self.objetivo, data = self.Objetivo_100dias()
            self.dias_hoje = self.objetivo - dias_hoje
            return self.dias_hoje
        except:
            self.dialogAviso("Sem conexão")



    def data_inicio(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save_data_inicio)
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
        time_dialog.bind(on_save=self.Adicionar_horas_minutos)
        time_dialog.title = "Selecione Horas/Minutos"
        time_dialog.open()




    def RemoverDia(self, obj):
        dia_mar_perdido = 1
        hora, minuto, data, dias_perdido, frases = self.Requisicao_get_banco_dados(self.local_id)
        dias = int(dias_perdido)
        dias -= dia_mar_perdido
        link = f" https://registradordehoras-9e0d4-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}"
        horas_atualizada = f'{{"Total Dia":"{dias}"}}'
        requests.patch(link, data=horas_atualizada)
        self.atualizar_dias_restante()
        self.dialog.dismiss()
        self.mudartela("homepage")




    def SairAPP(self):
        refresh = open('refresh.txt', 'r+')
        refresh.truncate(0)
        self.mudartela("login")

    def bar(self, progresso):
        page = self.root.ids['homepage']
        value = page.ids['progress'].value = progresso
        page.ids['porcentagem'].text =f"{value}% Progresso"


    def atualizar_outinput_horas_minutos(self):
        link = f" https://registradordehoras-9e0d4-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}"
        requisicao = requests.get(link)
        banco_de_dado = requisicao.json()
        homepage = self.root.ids['homepage']
        homepage.ids['minuto_input'].text = banco_de_dado['Minutos']
        homepage = self.root.ids['homepage']
        homepage.ids['hora_input'].text = banco_de_dado['Horas']
        hora_completado = banco_de_dado['Horas']
        dias_completado = self.TOTAL_DATA()
        if hora_completado >= "100" and dias_completado >= 100:
            self.Congratulations(hora_completado, dias_completado)




    def Total_Frases_mineradas(self, *args):
        try:
            page = self.root.ids['homepage']
            qdt_frases = page.ids['qtd'].value
            hora, minuto, data, total_dias, frases = self.Requisicao_get_banco_dados(self.local_id)
            qdt_frase = int(frases) + int(qdt_frases)
            self.Requisicao_patch_banco_dados(int(qdt_frase), str(hora), str(minuto), self.local_id)
            self.AtualizarCampoFrases()
            page.ids['qtd'].value = 0
        except:
            self.dialogAviso("Sem Internet...")



    def AtualizarCampoFrases(self):
        link = f" https://registradordehoras-9e0d4-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}"
        requisicao = requests.get(link)
        banco_de_dado = requisicao.json()
        homepage = self.root.ids['homepage']
        homepage.ids['frases'].text = f'Frases Mineradas: {banco_de_dado["Frases"]}'





MainApp().run()