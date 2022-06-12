import sqlite3
from kivy.app import App


class Sqlite:

    def __init__(self):
        self.db = sqlite3.connect('sqlite3.db')
        self.db_connect = self.db.cursor()
        self.db_connect.execute("DROP TABLE IF EXISTS SQLITE3")


    def ler_infomacoes(self):
        self.comando = f"""SELECT * from cimv
                    WHERE id = '{1}';
                    """
        inf = self.db_connect.execute(self.comando)
        return inf.fetchall()



    def Atualizar_horas(self, horas):
        self.comando = f"""UPDATE cimv
                        SET Hora = Hora + {horas};
                        """
        self.db_connect.execute(self.comando)
        self.db.commit()


    def Atualizar_minutos(self, minuto):
        self.comando = f"""UPDATE cimv
                SET Minuto = Minuto + {minuto};
                """
        self.db_connect.execute(self.comando)
        self.db.commit()

    def rootHoras(self):
        horas = App.get_running_app()
        hora = horas.root.ids['addhora']
        horas = hora.ids['hora_input']
        return horas







