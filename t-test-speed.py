import pandas as pd
import scipy.stats as stats

# Đọc dữ liệu từ Excel
data = pd.read_excel('compare-speed.xlsx')

# Lấy dữ liệu từ hai cột
data_group1 = data['maxmin']
data_group2 = data['default']

# Thực hiện t-test độc lập (independent t-test)
t_statistic, p_value = stats.ttest_ind(data_group1, data_group2)

# Hiển thị kết quả
print("T-Statistic:", t_statistic)
print("P-Value:", p_value)