import traci
import pandas as pd
import numpy as np
from scipy.optimize import minimize

# Định nghĩa hàm mục tiêu để tối ưu hóa: thời gian chờ trung bình
def objective(speeds, *args):
    waiting_times, max_speeds = args
    speeds = np.minimum(speeds, max_speeds)
    new_waiting_times = waiting_times - speeds
    return np.mean(new_waiting_times)

# Định nghĩa hàm ràng buộc: tốc độ không vượt quá tốc độ tối đa
def constraint(speeds, max_speeds):
    return max_speeds - speeds

sumoCmd = ["sumo", "-c", "osm.sumocfg"]
traci.start(sumoCmd)

# Khởi tạo danh sách biến
average_speeds = []  # Vận tốc trung bình
average_waitingTimes = []  # Thời gian chờ trung bình
num_station = 0  # Biến đếm số bến
num_bus = 0  # Biến đếm số lượng xe Bus

while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    vehicles = traci.vehicle.getIDList()

    if not vehicles:
        print("Không có xe Bus trong mô phỏng.")
        break

    speeds = []
    waitingTimes = []
    max_speeds = []
    vehicle_speeds = {}
    vehicle_waitingTimes = {}

    for vehicle_id in vehicles:
        # Vận tốc xe
        speed = round(traci.vehicle.getSpeed(vehicle_id), 2)
        speeds.append(speed)
        waitingTime = traci.vehicle.getWaitingTime(vehicle_id)
        waitingTimes.append(waitingTime)
        max_speed = traci.vehicle.getMaxSpeed(vehicle_id)
        max_speeds.append(max_speed)
        vehicle_speeds[vehicle_id] = speed
        vehicle_waitingTimes[vehicle_id] = waitingTime
        route = traci.vehicle.getRoute(vehicle_id)
        # Số bến xe bus đi qua
        num_stops = len(route) - 2  # Trừ 2 bến đầu cuối
        num_station += num_stops
        num_bus += 1

    # Khởi tạo tốc độ ban đầu cho mỗi xe là 0
    initial_speeds = np.zeros(len(vehicles))

    # Sử dụng hàm tối ưu hóa để tìm ra tốc độ tối ưu cho mỗi xe
    cons = {'type': 'ineq', 'fun': constraint, 'args': [max_speeds]}
    res = minimize(objective, initial_speeds, args=(waitingTimes, max_speeds), constraints=cons, method='SLSQP')

    fair_speeds = {vehicle: speed for vehicle, speed in zip(vehicles, res.x)}
    fair_waitingTimes = {vehicle: waitingTime for vehicle, waitingTime in vehicle_waitingTimes.items()}

    # Đặt tốc độ mới cho mỗi xe
    for vehicle_id, new_speed in zip(vehicles, res.x):
        traci.vehicle.setSpeed(vehicle_id, new_speed)

    average_speeds.append(np.mean(speeds))
    average_waitingTimes.append(np.mean(waitingTimes))

def resource_ratio(vehicle_speeds, fair_speeds, vehicle_waitingTimes, fair_waitingTimes):
    less_speed_resources = sum(1 for vehicle, speed in vehicle_speeds.items() if speed < fair_speeds[vehicle])
    more_speed_resources = sum(1 for vehicle, speed in vehicle_speeds.items() if speed > fair_speeds[vehicle])
    less_waiting_resources = sum(1 for vehicle, waitingTime in vehicle_waitingTimes.items() if waitingTime > fair_waitingTimes[vehicle])
    more_waiting_resources = sum(1 for vehicle, waitingTime in vehicle_waitingTimes.items() if waitingTime < fair_waitingTimes[vehicle])

    speed_resource_ratio = less_speed_resources / more_speed_resources if more_speed_resources != 0 else 'Infinity'
    waiting_resource_ratio = less_waiting_resources / more_waiting_resources if more_waiting_resources != 0 else 'Infinity'

    print('Speed Resource Ratio:', speed_resource_ratio)
    print('Waiting Time Resource Ratio:', waiting_resource_ratio)

resource_ratio(vehicle_speeds, fair_speeds, vehicle_waitingTimes, fair_waitingTimes)

# Tạo DataFrame từ danh sách tốc độ trung bình và thời gian chờ trung bình
df = pd.DataFrame({'MMF Speed': average_speeds, 'MMF Waiting Time': average_waitingTimes})

# Ghi DataFrame vào file Excel
df.to_excel('maxmin-summary.xlsx', index=False)

traci.close()
