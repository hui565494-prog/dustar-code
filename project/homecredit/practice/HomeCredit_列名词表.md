# HomeCredit 列名 · 英文词表（最小集）

> **列名里的英文不是自由英语，是几十个词的重复。**
> 认识这几十个词，几百列你都能自己读——不用会英语，也不用背整份字典。
> 用法：遇到长列名，**按 `_` 拆开**，逐个词对下表。

## 前缀词（往往 = 一族）

| 词 | 意思 | 例子 |
|---|---|---|
| SK_ID | 主键 / 唯一编号 | SK_ID_CURR = 客户编号 |
| FLAG | 标志（是/否 → 0/1） | FLAG_OWN_CAR = 有车吗 |
| AMT | amount 金额 | AMT_CREDIT = 贷款额 |
| CNT | count 计数（个数） | CNT_CHILDREN = 孩子数 |
| DAYS | 天数（多为"距今多少天"） | DAYS_BIRTH = 出生距今天数 |
| NAME | 名称 / 类别（文字） | NAME_INCOME_TYPE = 收入类型 |
| CODE | 编码 | CODE_GENDER = 性别 |
| REG / REGION | 地区 | REGION_RATING_CLIENT |
| EXT | external 外部（评分） | EXT_SOURCE_1 = 外部评分 1 |
| OWN | 拥有 | OWN_CAR_AGE = 车龄 |
| DEF | default 违约 | DEF_30_CNT_SOCIAL_CIRCLE |
| OBS | observation 观察（社交圈） | OBS_30_CNT_SOCIAL_CIRCLE |
| LIVE | 居住 | LIVE_CITY_NOT_WORK_CITY |
| HOUR / WEEKDAY | 小时 / 星期几 | HOUR_APPR_PROCESS_START |

## 后缀词（同一信息的几种统计）

| 词 | 意思 |
|---|---|
| AVG | average 平均 |
| MODE | 众数（出现最多的值） |
| MEDI | median 中位数 |
| TOTAL | 总计 |

## 常见实词（拆列名时用）

| 词 | 意思 | 词 | 意思 |
|---|---|---|---|
| APPLICATION | 申请 | INCOME | 收入 |
| PREVIOUS | 之前的 | CREDIT | 贷款 / 信用 |
| INSTALLMENTS | 分期付款 | ANNUITY | 月供 / 年金 |
| POS_CASH | 销售点现金分期 | GOODS_PRICE | 商品价格 |
| CREDIT_CARD | 信用卡 | CHILDREN | 孩子 |
| BUREAU | 征信局 | FAM_MEMBERS | 家庭成员 |
| BALANCE | 余额 | EDUCATION | 教育 |
| DOCUMENT | 文件 | FAMILY_STATUS | 婚姻状况 |
| MOBIL / PHONE / EMAIL | 手机 / 电话 / 邮箱 | HOUSING | 住房 |
| EMP_PHONE | 单位电话 | OCCUPATION | 职业 |
| REQ | request 请求 / 查询 | ORGANIZATION | 工作单位类型 |
| EMPLOYED | 在职 | REGISTRATION | 登记 |
| ID_PUBLISH | 证件签发 | SOCIAL_CIRCLE | 社交圈 |
| PHONE_CHANGE | 电话变更 | CONTRACT_TYPE | 合同类型（现金/循环） |
