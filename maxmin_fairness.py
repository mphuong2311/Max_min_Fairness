import traci
import pandas as pd

def max_min_fairness(speeds):
    if not speeds:
        return 0  # Hoặc giá trị mặc định khác tuỳ thuộc vào yêu cầu

    avg_speed = sum(speeds) / len(speeds)
    fair_speed = avg_speed * len(speeds)
    return fair_speed

sumoCmd = ["sumo", "-c", "osm.sumocfg"]
traci.start(sumoCmd)

# Khởi tạo danh sách biến
average_speeds = [] # Vận tốc trung bình
average_waitingTimes = [] # Thời gian chờ trung bình
num_station = 0  # Biến đếm số bến
num_bus = 0  # Biến đếm số lượng xe Bus

while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    vehicles = traci.vehicle.getIDList()
    speeds = []
    waitingTimes = []
    vehicle_speeds = {}

    for vehicle_id in vehicles:
        # Vận tốc xe
        speed = round(traci.vehicle.getSpeed(vehicle_id) * 3.6, 2)
        speeds.append(speed)
        waitingTime = traci.vehicle.getWaitingTime(vehicle_id)
        waitingTimes.append(waitingTime)
        vehicle_speeds[vehicle_id] = speed
        route = traci.vehicle.getRoute(vehicle_id)
        # Số bến xe bus đi qua
        num_stops = len(route) - 2  # Trừ 2 bến đầu cuối
        num_station += num_stops
        num_bus += 1

    fair_speed = max_min_fairness(speeds)

    for vehicle_id, speed in vehicle_speeds.items():
        if speed < fair_speed:
            traci.vehicle.setSpeed(vehicle_id, fair_speed)

    if speeds:
        average_speed = sum(speeds) / len(speeds)
        average_speeds.append(average_speed)
    
    if waitingTimes:
        average_waitingTime = sum(waitingTimes) / len(waitingTimes)
        average_waitingTimes.append(average_waitingTime)

traci.close()

if num_bus > 0:
    avg_num_station = num_station / num_bus
    print(f"Số bến trung bình mà tất cả xe Bus đi qua: {avg_num_station}")
else:
    print("Không có xe Bus trong mô phỏng.")

# Tạo DataFrame từ danh sách tốc độ trung bình
df = pd.DataFrame(average_speeds, columns=['AverageSpeed'])
# Ghi DataFrame vào file Excel
df.to_excel('maxmin-avgSpeed.xlsx', index=False)

# Tạo DataFrame từ danh sách thời gian chờ trung bình
df = pd.DataFrame(average_waitingTimes, columns=['AverageWaitingTime'])
# Ghi DataFrame vào file Excel
df.to_excel('maxmin-avgTripWaitingTime.xlsx', index=False)
