import requests
import os
from zExceptions import BadRequest

class EventCreator():

    def __init__(self, event_data):
        self.event_data = event_data
        self.token = None
        self.is_authenticated = False
        self.login_name = os.environ.get('home_user', False)
        self.password = os.environ.get('home_pass', False)
        self.BASE_URL = os.environ.get('home_url', 'https://webupcpre.upc.edu')
        self.headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    def authenticate(self):
        if not self.login_name or not self.password:
            raise BadRequest("No s'han trobat les credencials per fer la petició")
        
        response = requests.post(f'{self.BASE_URL}/@login', headers=self.headers, 
                                json={'login': self.login_name, 'password': self.password})
        
        if not response.ok:
            raise BadRequest("Hi ha hagut un error en el procés d'autenticació")
        
        self.token = response.json().get('token')
        self.is_authenticated = True
        self.headers['Authorization'] = f'Bearer {self.token}'

    def create_event(self):
        if not self.is_authenticated:
            raise BadRequest("No es pot fer la petició. Ha fallat l'autenticació.")
        
        response = requests.post(f'{self.BASE_URL}/ca/agenda/esdeveniments', headers=self.headers, json=self.event_data)
        if not response.ok:
            raise BadRequest("Hi ha hagut un error creant l'esdeveniment")
        
        return response.json()



        
    

    