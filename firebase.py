import requests
from kivy.app import App
from datetime import datetime, date


class MyFireBase():
    API_KEY = "AIzaSyCXxw3tEdMIY9hdoJbaQ2klV9DmSt7MdgE"

    def Mensagem_erro_CriarConta(self, mensagem):
        meu_aplicativo = App.get_running_app()
        meu_aplicativo.dialogAviso(mensagem)

    def Mensagem_erro_Trocar_senha(self, mensagem):
        meu_aplicativo = App.get_running_app()
        meu_aplicativo.dialogAviso(mensagem)


    def Mensagem_erro_Login(self, mensagem_erro):
        meu_aplicativo = App.get_running_app()
        meu_aplicativo.dialogAviso(mensagem_erro)

    def CriarConta(self, email, senha):
        try:
            link = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.API_KEY}"

            info = {"email": email,
                    "password": senha,
                    "returnSecureToken": True}

            requisicao = requests.post(link, data=info)
            requisicao_dic = requisicao.json()
            if requisicao.ok:
                refresh_token = requisicao_dic['refreshToken']
                local_id = requisicao_dic['localId']
                id_token = requisicao_dic['idToken']
                meu_aplicativo = App.get_running_app()
                meu_aplicativo.local_id = local_id
                meu_aplicativo.id_token = id_token
                with open('refresh.txt', 'w') as arquivo:
                    arquivo.write(refresh_token)

                link = f" https://registradordehoras-9e0d4-default-rtdb.firebaseio.com/{local_id}.json?auth={id_token}"
                info_usuario = f'{{"Frases":"{0}","Horas":"{00}", "Minutos": "{00}", "Data Inicial": "{date.today()}", "Total Dia": "0"}}'
                requests.patch(link, data=info_usuario)
                meu_aplicativo.dialogAviso("Conta Criada Com Sucesso!")
                meu_aplicativo.mudartela('login')


            else:
                mensagem_erro = requisicao_dic["error"]["message"]
                if mensagem_erro == 'MISSING_EMAIL':
                    erro_messagem = 'Preenche o Campo E-mail Corretamente'
                    self.Mensagem_erro_CriarConta(erro_messagem)
                elif mensagem_erro == 'MISSING_PASSWORD':
                    erro_messagem = 'Preenche o Campo Senha'
                    self.Mensagem_erro_CriarConta(erro_messagem)
                elif 'WEAK_PASSWORD ' in mensagem_erro:
                    erro_messagem = 'Senha deve conter no minimo 6 caracteres'
                    self.Mensagem_erro_CriarConta(erro_messagem)
                elif mensagem_erro == 'EMAIL_EXISTS':
                    erro_messagem = 'Email já existênte'
                    self.Mensagem_erro_CriarConta(erro_messagem)
                elif mensagem_erro == 'INVALID_EMAIL':
                    erro_messagem = 'Preenche o Campo E-mail Corretamente'
                    self.Mensagem_erro_CriarConta(erro_messagem)
                else:
                    pass

        except:
             self.Mensagem_erro_CriarConta("Sem Conexão")



    def FazerLogin(self, email, senha):

        try:
            link = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.API_KEY}"

            info = {"email": email,
                    "password": senha,
                    "returnSecureToken": True}

            requisicao = requests.post(link, data=info)
            requisicao_dic = requisicao.json()
            if requisicao.ok:
                refresh_token = requisicao_dic['refreshToken']
                local_id = requisicao_dic['localId']
                id_token = requisicao_dic['idToken']
                meu_aplicativo = App.get_running_app()
                meu_aplicativo.local_id = local_id
                meu_aplicativo.id_token = id_token
                with open('refresh.txt', 'w') as arquivo:
                    arquivo.write(refresh_token)
                meu_aplicativo.mudartela('homepage')
                meu_aplicativo.carregando_info_automatico()
            else:
                mensagem_erro = requisicao_dic["error"]["message"]
                if mensagem_erro == 'INVALID_EMAIL':
                    self.Mensagem_erro_Login("Preenche o Campo E-mail")
                elif mensagem_erro == 'MISSING_PASSWORD':
                    self.Mensagem_erro_Login("Preenche o Campo Senha")
                elif mensagem_erro == "EMAIL_NOT_FOUND":
                    self.Mensagem_erro_Login("E-mail ou senha Invalido")
                elif mensagem_erro == "INVALID_PASSWORD":
                    self.Mensagem_erro_Login("Senha incorreta")
        except:
            self.Mensagem_erro_Login("Sem Conexão")



    def trocar_token(self, refresh_token):
        link = f"https://securetoken.googleapis.com/v1/token?key={self.API_KEY}"
        info = {"grant_type": "refresh_token",
                "refresh_token": refresh_token}
        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()
        local_id = requisicao_dic['user_id']
        id_token = requisicao_dic['id_token']
        return local_id, id_token


    def reset_password(self, email):
        try:
            link = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={self.API_KEY}"
            info = {"requestType":"PASSWORD_RESET",
                    "email": {email}}
            requisicao = requests.post(link, data=info)
            resposta = requisicao.json()
            if requisicao.ok:
                self.Mensagem_erro_Trocar_senha("Verifique sua caixa de Email")
            else:
                mensagem_erro = resposta["error"]['message']
                if mensagem_erro == "MISSING_EMAIL":
                   self.Mensagem_erro_Trocar_senha("Digite seu E-mail")
                elif mensagem_erro == 'EMAIL_NOT_FOUND':
                    self.Mensagem_erro_Trocar_senha("Seu email nao foi encontrado")

        except:
            self.Mensagem_erro_Trocar_senha("Sem Conexao")





