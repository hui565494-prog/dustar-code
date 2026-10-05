import pandas as pd
import warnings

warnings.filterwarnings("ignore")  # 忽略警告信息

# 读取 application_train 数据集
app_train = pd.read_csv("./data/application_train.csv")

# 查看数据集规模
record_count, feature_count = (
    app_train.shape[0],
    app_train.shape[1],
)  # 样本数量和字段数量
# 查看目标变量分布
target_count = app_train["TARGET"].value_counts()
# 统计客户数量
customer_count = app_train["SK_ID_CURR"].nunique()
# 统计不同类型字段数量
numeric_count = app_train.select_dtypes(include=["int64", "float64"]).shape[1]
category_count = app_train.select_dtypes(include=["object"]).shape[1]
# 统计部分重要字段的信息
gender_count = app_train["CODE_GENDER"].value_counts()
income_type_count = app_train["NAME_INCOME_TYPE"].value_counts()
education_count = app_train["NAME_EDUCATION_TYPE"].value_counts()
family_status_count = app_train["NAME_FAMILY_STATUS"].value_counts()
# 统计金额类字段的基本情况
credit_min = app_train["AMT_CREDIT"].min()
credit_max = app_train["AMT_CREDIT"].max()
credit_mean = app_train["AMT_CREDIT"].mean()

income_min = app_train["AMT_INCOME_TOTAL"].min()
income_max = app_train["AMT_INCOME_TOTAL"].max()
income_mean = app_train["AMT_INCOME_TOTAL"].mean()

annuity_min = app_train["AMT_ANNUITY"].min()
annuity_max = app_train["AMT_ANNUITY"].max()
annuity_mean = app_train["AMT_ANNUITY"].mean()

# 输出统计结果
print("样本数量：", record_count)
print("客户数量：", customer_count)

print("\n字段数量：", feature_count)
print("数值型字段数量：", numeric_count)
print("类别型字段数量：", category_count)

print("\n目标变量分布：")
print(target_count)

print("\n性别分布：")
print(gender_count)

print("\n收入类型分布：")
print(income_type_count)

print("\n教育程度分布：")
print(education_count)

print("\n婚姻状态分布：")
print(family_status_count)

print("\n贷款金额 AMT_CREDIT：")
print("最小值：", credit_min)
print("最大值：", credit_max)
print("平均值：", credit_mean)

print("\n收入金额 AMT_INCOME_TOTAL：")
print("最小值：", income_min)
print("最大值：", income_max)
print("平均值：", income_mean)

print("\n年金 AMT_ANNUITY：")
print("最小值：", annuity_min)
print("最大值：", annuity_max)
print("平均值：", annuity_mean)
