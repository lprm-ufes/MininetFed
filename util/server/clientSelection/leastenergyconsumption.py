
# LeastEnergyConsumption: Seleciona os clientes que até o momento usaram menos energia que a média
class LeastEnergyConsumption:
    def __init__(self):
        pass

    def select_trainers_for_round(self, trainer_list, metrics):
        mean_energy_consumption = 0
        for trainer in trainer_list:
            mean_energy_consumption += metrics[trainer]["energy_consumption"]
        mean_energy_consumption /= len(trainer_list)

        s = []
        for trainer in trainer_list:
            if metrics[trainer]["energy_consumption"] <= mean_energy_consumption:
                s.append(trainer)

        return s
