import time as t
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

# Decorador para medir el tiempo de ejecución
def measure_time(func):
    """
    Decorador para medir el tiempo de ejecución de una función.

    Parameters:
    func (function): Función a ser medida.

    Returns:
    function: Función envuelta que mide el tiempo de ejecución.
    """
    def wrapper(*args, **kwargs):
        start_time = t.time()
        result = func(*args, **kwargs)
        end_time = t.time()
        print(f"Tiempo de ejecución: {end_time - start_time:.4f} segundos")
        return result
    return wrapper

@dataclass
class Signal:
    """
    Clase para representar una señal y generar una señal modulada en frecuencia (FM).

    Attributes:
    time (np.ndarray): Array de tiempos.
    message_frequency (float): Frecuencia de la señal del mensaje.
    carrier_frequency (float): Frecuencia de la señal portadora.
    sampling_rate (int): Tasa de muestreo. Valor por defecto: 1000.
    message_signal (np.ndarray): Señal del mensaje. Generada en __post_init__.
    integrated_message (np.ndarray): Integral acumulativa de la señal del mensaje. Generada en __post_init__.
    fm_signal (np.ndarray): Señal modulada en frecuencia. Generada en __post_init__.
    """
    time: np.ndarray
    message_frequency: float
    carrier_frequency: float
    sampling_rate: int = 1000
    message_signal: np.ndarray = field(init=False)
    integrated_message: np.ndarray = field(init=False)
    fm_signal: np.ndarray = field(init=False)
    
    def __post_init__(self):
        self.message_signal = np.sinc(self.message_frequency * (self.time - 2))
        self.integrated_message = np.cumsum(self.message_signal) / self.sampling_rate
        self.fm_signal = np.cos(2 * np.pi * self.carrier_frequency * self.time + 2 * np.pi * self.integrated_message)

class PlotInterface(ABC):
    """
    Interfaz abstracta para la graficación de señales.
    """
    @abstractmethod
    def plot(self):
        pass

@dataclass
class SignalPlotter(PlotInterface):
    """
    Clase para graficar señales.

    Attributes:
    signal (Signal): Objeto de la clase Signal.
    """
    signal: Signal
    
    @measure_time
    def plot(self):
        """
        Grafica la señal del mensaje y la señal modulada en frecuencia (FM).

        Utiliza matplotlib para crear dos subgráficos, uno para la señal del mensaje
        y otro para la señal FM. Mide el tiempo de ejecución usando el decorador measure_time.
        """
        plt.figure(figsize=(14, 8))  # Ajustar tamaño de la gráfica
        
        plt.subplot(2, 1, 1)
        plt.plot(self.signal.time, self.signal.message_signal)
        plt.title('Message Signal')
        plt.xlabel('Time [s]')
        plt.ylabel('Amplitude')
        
        plt.subplot(2, 1, 2)
        plt.plot(self.signal.time, self.signal.fm_signal)
        plt.title('Frequency Modulated Signal')
        plt.xlabel('Time [s]')
        plt.ylabel('Amplitude')
        
        plt.tight_layout()
        plt.show()

# Uso del código
time = np.linspace(0, 5, 5000)  # Tiempo de 0 a 5 segundos
signal = Signal(time=time, message_frequency=2, carrier_frequency=20)
plotter = SignalPlotter(signal=signal)
plotter.plot()
