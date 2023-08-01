import traci
import pandas as pd
import numpy as np

def max_min_fairness(speeds):
    if not speeds:
        return 0  # Hoặc giá trị mặc định khác tuỳ thuộc vào yêu cầu
    avg_speed = np.mean(speeds)
    fair_speed = avg_speed * len(speeds)
    return fair_speed

sumoCmd = ["sumo", "-c", "osm.sumocfg"]
traci.start(sumoCmd)

# Khởi tạo danh sách biến
average_speeds = [] # Vận tốc trung bình
average_waitingTimes = [] # Thời gian chờ trung bình
num_station = 0  # Biến đếm số bến
num_bus = 0  # Biến đếm số lượng xe Bus
vehicle_start_times = {}
vehicle_travel_times = {}

while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    vehicles = traci.vehicle.getIDList()

    if not vehicles:
        print("Không có xe Bus trong mô phỏng.")
        break

    speeds = []
    waitingTimes = []
    vehicle_speeds = {}

    for vehicle_id in vehicles:
        # Vận tốc xe
        speed = round(traci.vehicle.getSpeed(vehicle_id), 2)
        speeds.append(speed)
        waitingTime = traci.vehicle.getAccumulatedWaitingTime(vehicle_id)
        waitingTimes.append(waitingTime)
        vehicle_speeds[vehicle_id] = speed
        route = traci.vehicle.getRoute(vehicle_id)
        # Số bến xe bus đi qua
        num_stops = len(route) - 2  # Trừ 2 bến đầu cuối
        num_station += num_stops
        num_bus += 1

        if vehicle_id not in vehicle_start_times:
            vehicle_start_times[vehicle_id] = traci.simulation.getTime()

    # Update the travel time for the vehicle
        vehicle_travel_times[vehicle_id] = traci.simulation.getTime() - vehicle_start_times[vehicle_id]

    fair_speed = max_min_fairness(speeds)

    for vehicle_id, speed in vehicle_speeds.items():
        if speed < fair_speed:
            traci.vehicle.setSpeed(vehicle_id, fair_speed)

    if speeds:
        average_speeds.append(np.mean(speeds))
    
    if waitingTimes:
        average_waitingTimes.append(np.mean(waitingTimes))

traci.close()

if num_bus > 0:
    avg_num_station = num_station / num_bus
    print(f"Số bến trung bình mà tất cả xe Bus đi qua: {avg_num_station}")

# Tạo DataFrame từ danh sách tốc độ trung bình và thời gian chờ trung bình
df = pd.DataFrame({'MMF Speed': average_speeds, 'MMF Waiting Time': average_waitingTimes})
# Ghi DataFrame vào file Excel
df.to_excel('maxmin-summary.xlsx', index=False)

# Convert the dictionary to a DataFrame and save it as an Excel file
df_travel_times = pd.DataFrame(list(vehicle_travel_times.items()), columns=['Vehicle ID', 'Travel Time'])
df_travel_times.to_excel('travel_times.xlsx', index=False)