import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class DataFetcher:
    def __init__(self, url):
        self.url = url

    def fetch_data(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.transfermarkt.com/'
        }
        cookies = {
            'consentCookie': 'true'
        }
        response = requests.get(self.url, headers=headers, cookies=cookies)
        
        if response.status_code == 404:
            raise ValueError("404 Not Found. La URL puede no ser correcta o puede haber restricciones de acceso.")

        soup = BeautifulSoup(response.content, 'html.parser')

        main_div = soup.select_one("#tm-main > div.row.vereinsstartseite > div.large-8.columns > div.box > div.responsive-table")
        if main_div is None:
            raise ValueError("No se encontró el div principal en la página.")
        
        table = main_div.find('table', {'class': 'items'})
        if table is None:
            raise ValueError("No se encontró ninguna tabla con la clase 'items' en la página.")

        rows = table.find_all('tr')

        data = []
        for row in rows[1:]:  # Ignorar la primera fila si es un encabezado
            cells = row.find_all('td')
            if len(cells) >= 5:  # Verifica que haya suficientes celdas en la fila
                player_tag = cells[1].find('a')
                market_value_cell = row.select_one('td.rechts.hauptlink')
                
                if player_tag and market_value_cell:
                    player = player_tag.get_text(strip=True)  # Nombre del jugador
                    market_value_text = market_value_cell.get_text(strip=True)
                    
                    if player and market_value_text:
                        market_value = market_value_text.replace('€', '').replace('m', '000000').replace('bn', '000000000').replace('.', '').replace(',', '.')
                        data.append({
                            'Player': player,
                            'MarketValue': market_value
                        })
        
        df = pd.DataFrame(data)
        df['MarketValue'] = pd.to_numeric(df['MarketValue'], errors='coerce')
        print(df)  # Imprimir los datos obtenidos para depuración
        return df

class DataVisualizer:
    def __init__(self, data):
        self.data = data

    def plot_data(self, x_column, y_column):
        plt.figure(figsize=(10, 7))  # Ajustar el tamaño de la figura
        sns.barplot(data=self.data, x=x_column, y=y_column)
        plt.title(f'{y_column} vs {x_column}')
        plt.xticks(rotation=45, ha='right')  # Ajustar la rotación y la alineación de las etiquetas
        plt.tight_layout()  # Asegurarse de que todo se ajuste en la figura
        plt.show()

class TransferMarkDataFetcher(DataFetcher):
    def __init__(self, url):
        super().__init__(url)

    def fetch_data(self):
        data = super().fetch_data()
        return data.dropna()

class DataInterface:
    def fetch(self):
        pass

    def visualize(self, x_column, y_column):
        pass

class TransferMarkDataInterface(DataInterface):
    def __init__(self, url):
        self.fetcher = TransferMarkDataFetcher(url)
        self.visualizer = None

    def fetch(self):
        data = self.fetcher.fetch_data()
        self.visualizer = DataVisualizer(data)

    def visualize(self, x_column, y_column):
        if self.visualizer:
            self.visualizer.plot_data(x_column, y_column)

class DataHandler:
    def __init__(self, data_interface: DataInterface):
        self.data_interface = data_interface

    def execute(self, x_column, y_column):
        self.data_interface.fetch()
        self.data_interface.visualize(x_column, y_column)

# Ejemplo de uso
url = "https://www.transfermarkt.com/real-madrid/startseite/verein/418"
data_interface = TransferMarkDataInterface(url)
handler = DataHandler(data_interface)
handler.execute('Player', 'MarketValue')
