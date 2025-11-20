import numpy as np

class SRAMCell:
    """A model of a single Static Random-Access Memory (SRAM) cell.

    This class simulates the behavior of an SRAM cell, including its initial
    value, power-up behavior with a potential for aging-induced bit flips,
    and basic read/write operations.

    Attributes:
        initial_value (int): The stable, preferred startup value (0 or 1) of the cell.
        value (int): The current value of the cell.
    """
    def __init__(self, initial_value=None, stability_param=None):
        """
        Args:
            initial_value: cell的偏好值 (0 or 1)
            stability_param: cell的穩定性參數，代表Vth mismatch的大小
                           值越大越穩定，建議範圍 0-1
        """
        # 決定initial value (power-up偏好)
        if initial_value is None:
            self.initial_value = np.random.randint(2)
        else:
            self.initial_value = initial_value
        
        # 設定stability parameter
        # 如果不指定，從接近現實的分佈中採樣
        if stability_param is None:
            # 使用beta分佈模擬真實分佈：
            # 大部分cell很穩定(接近1)，少數非常不穩定(接近0)
            self.stability = np.random.beta(a=8, b=2)  
        else:
            self.stability = np.clip(stability_param, 0.0, 1.0)
        
        self.value = self.initial_value
        self.age = 0  # 追蹤aging時間

    def power_up(self, temperature=25, voltage_ratio=1.0, 
                 anti_aging=False):
        """
        模擬power-up行為，考慮多種因素
        
        Args:
            temperature: 環境溫度 (°C)，影響noise
            voltage_ratio: 供電電壓比例 (相對於nominal)
            anti_aging: 是否應用anti-aging策略
        """
        # 計算aging對穩定性的影響
        if anti_aging:
            # Anti-aging使cell隨時間變得更穩定
            aging_effect = 0.05 * np.sqrt(self.age / 1000)  
            effective_stability = min(1.0, self.stability + aging_effect)
        else:
            # 沒有anti-aging，NBTI降低穩定性
            aging_effect = 0.1 * np.sqrt(self.age / 1000)
            effective_stability = max(0.0, self.stability - aging_effect)
        
        # 溫度影響: 偏離25°C增加noise
        temp_factor = 1.0 + abs(temperature - 25) / 100.0
        
        # 電壓影響: 偏離nominal增加noise
        voltage_factor = 1.0 + abs(voltage_ratio - 1.0) * 2.0
        
        # 綜合計算flip probability
        # 穩定性高的cell，flip機率接近0
        # 穩定性低的cell，flip機率接近0.5
        base_flip_prob = (1 - effective_stability) * 0.5
        flip_prob = base_flip_prob * temp_factor * voltage_factor
        
        # 決定power-up值
        if np.random.rand() < flip_prob:
            self.value = 1 - self.initial_value  # Flip
        else:
            self.value = self.initial_value
        
        self.age += 1  # 增加age counter
        
    def read(self):
        return self.value
    
    def write(self, value):
        if value in [0, 1]:
            self.value = value
        else:
            raise ValueError("Value must be 0 or 1")
