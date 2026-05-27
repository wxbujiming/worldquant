# WorldQuant Brain 66 Operators / WorldQuant Brain 66 个操作符

English line followed by Chinese line for easier reading.
每条英文下面紧跟对应中文，方便逐行阅读。

Total operators: 66
操作符总数：66

---

**Arithmetic**<br>
**算术类**

**1. add**<br>
**Category**: Arithmetic<br>
**分类**: 算术类<br>
**Definition**: add(x, y, filter = false), x + y<br>
**定义**: 语法：add(x, y, filter = false), x + y<br>
**Description**: Adds two or more inputs element wise. Set filter=true to treat NaNs as 0 before summing.<br>
**说明**: 对两个或多个输入逐元素相加。设置 filter=true 时，会先把 NaN 当作 0 再求和。<br>
**Documentation**: /operators/add<br>
**文档**: /operators/add

**2. sqrt**<br>
**Category**: Arithmetic<br>
**分类**: 算术类<br>
**Definition**: sqrt(x)<br>
**定义**: 语法：sqrt(x)<br>
**Description**: Returns the non negative square root of x. Equivalent to power(x, 0.5); for signed roots use signed_power(x, 0.5).<br>
**说明**: 返回 x 的非负平方根，等价于 power(x, 0.5)；如果需要保留符号的开方，可使用 signed_power(x, 0.5)。<br>
**Documentation**: /operators/sqrt<br>
**文档**: /operators/sqrt

**3. log**<br>
**Category**: Arithmetic<br>
**分类**: 算术类<br>
**Definition**: log(x)<br>
**定义**: 语法：log(x)<br>
**Description**: Calculates the natural logarithm of the input value. Commonly used to transform data that has positive values.<br>
**说明**: 计算输入值的自然对数，常用于处理取值为正的数据。<br>
**Documentation**: /operators/log<br>
**文档**: /operators/log

**4. subtract**<br>
**Category**: Arithmetic<br>
**分类**: 算术类<br>
**Definition**: subtract(x, y, filter=false), x - y<br>
**定义**: 语法：subtract(x, y, filter=false), x - y<br>
**Description**: Subtracts inputs left to right: x - y - ... Supports two or more inputs. Set filter=true to treat NaNs as 0 before subtraction.<br>
**说明**: 从左到右对输入做减法：x - y - ...。支持两个或多个输入。设置 filter=true 时，会先把 NaN 当作 0 再相减。<br>
**Documentation**: /operators/subtract<br>
**文档**: /operators/subtract

**5. signed_power**<br>
**Category**: Arithmetic<br>
**分类**: 算术类<br>
**Definition**: signed_power(x, y)<br>
**定义**: 语法：signed_power(x, y)<br>
**Description**: x raised to the power of y such that final result preserves sign of x<br>
**说明**: 对 x 做 y 次幂运算，并保留 x 原本的正负号。<br>
**Documentation**: /operators/signed_power<br>
**文档**: /operators/signed_power

**6. sign**<br>
**Category**: Arithmetic<br>
**分类**: 算术类<br>
**Definition**: sign(x)<br>
**定义**: 语法：sign(x)<br>
**Description**: Returns the sign of a number: +1 for positive, -1 for negative, and 0 for zero. If the input is NaN, returns NaN.<br>
**Input**: Value of 7 instruments at day t: (2, -3, 5, 6, 3, NaN, -10)<br>
**Output**: (1, -1, 1, 1, 1, NaN, -1)<br>
**说明**: 返回数字的符号：正数为 +1，负数为 -1，零为 0；如果输入为 NaN，则返回 NaN。<br>
**Documentation**: /operators/sign<br>
**文档**: /operators/sign

**7. reverse**<br>
**Category**: Arithmetic<br>
**分类**: 算术类<br>
**Definition**: reverse(x)<br>
**定义**: 语法：reverse(x)<br>
**Description**: -x<br>
**说明**: 返回 x 的相反数，也就是 -x。

**8. power**<br>
**Category**: Arithmetic<br>
**分类**: 算术类<br>
**Definition**: power(x, y)<br>
**定义**: 语法：power(x, y)<br>
**Description**: x ^ y<br>
**说明**: 计算 x 的 y 次方，即 x ^ y。<br>
**Documentation**: /operators/power<br>
**文档**: /operators/power

**9. multiply**<br>
**Category**: Arithmetic<br>
**分类**: 算术类<br>
**Definition**: multiply(x, y, ..., filter=false), x * y<br>
**定义**: 语法：multiply(x, y, ..., filter=false), x * y<br>
**Description**: Multiplies two or more inputs element wise. Set filter=true to treat NaNs as 0 before multiplication<br>
**说明**: 对两个或多个输入逐元素相乘。设置 filter=true 时，会先把 NaN 当作 0 再相乘。<br>
**Documentation**: /operators/multiply<br>
**文档**: /operators/multiply

**10. min**<br>
**Category**: Arithmetic<br>
**分类**: 算术类<br>
**Definition**: min(x, y ..)<br>
**定义**: 语法：min(x, y ..)<br>
**Description**: Minimum value of all inputs. At least 2 inputs are required<br>
**说明**: 返回所有输入中的最小值，至少需要 2 个输入。<br>
**Documentation**: /operators/min<br>
**文档**: /operators/min

**11. max**<br>
**Category**: Arithmetic<br>
**分类**: 算术类<br>
**Definition**: max(x, y, ..)<br>
**定义**: 语法：max(x, y, ..)<br>
**Description**: Maximum value of all inputs. At least 2 inputs are required<br>
**说明**: 返回所有输入中的最大值，至少需要 2 个输入。<br>
**Documentation**: /operators/max<br>
**文档**: /operators/max

**12. inverse**<br>
**Category**: Arithmetic<br>
**分类**: 算术类<br>
**Definition**: inverse(x)<br>
**定义**: 语法：inverse(x)<br>
**Description**: 1 / x<br>
**说明**: 返回 x 的倒数，也就是 1 / x。

**13. densify**<br>
**Category**: Arithmetic<br>
**分类**: 算术类<br>
**Definition**: densify(x)<br>
**定义**: 语法：densify(x)<br>
**Description**: Converts a grouping field of many buckets into lesser number of only available buckets so as to make working with grouping fields computationally efficient<br>
**说明**: 把分组字段中大量稀疏桶压缩成较少的实际可用桶，让分组字段的计算更高效。<br>
**Documentation**: /operators/densify<br>
**文档**: /operators/densify

**14. abs**<br>
**Category**: Arithmetic<br>
**分类**: 算术类<br>
**Definition**: abs(x)<br>
**定义**: 语法：abs(x)<br>
**Description**: Returns the absolute value of a number, removing any negative sign.<br>
**说明**: 返回数字的绝对值，去掉负号。<br>
**Documentation**: /operators/abs<br>
**文档**: /operators/abs

**15. divide**<br>
**Category**: Arithmetic<br>
**分类**: 算术类<br>
**Definition**: divide(x, y), x / y<br>
**定义**: 语法：divide(x, y), x / y<br>
**Description**: x / y<br>
**说明**: 计算 x / y。

---

**Logical**<br>
**逻辑类**

**1. and**<br>
**Category**: Logical<br>
**分类**: 逻辑类<br>
**Definition**: and(input1, input2)<br>
**定义**: 语法：and(input1, input2)<br>
**Description**: Returns 1 ('true') if both inputs are 1 ('true'). Otherwise, returns 0 ('false').<br>
**说明**: 当两个输入都为 1（true）时返回 1，否则返回 0。

**2. equal**<br>
**Category**: Logical<br>
**分类**: 逻辑类<br>
**Definition**: input1 == input2<br>
**定义**: 语法：input1 == input2<br>
**Description**: Returns 1 ('true') if input1 and input2 are the same. Otherwise, returns 0 ('false').<br>
**说明**: 当 input1 和 input2 相等时返回 1（true），否则返回 0（false）。

**3. or**<br>
**Category**: Logical<br>
**分类**: 逻辑类<br>
**Definition**: or(input1, input2)<br>
**定义**: 语法：or(input1, input2)<br>
**Description**: Returns 1 if either input is true (either input1 or input2 has a value of 1), otherwise it returns 0.<br>
**说明**: 只要任意一个输入为 true（值为 1）就返回 1，否则返回 0。

**4. not_equal**<br>
**Category**: Logical<br>
**分类**: 逻辑类<br>
**Definition**: input1 != input2<br>
**定义**: 语法：input1 != input2<br>
**Description**: Returns 1 ('true') if input1 and input2 are different numbers. Otherwise, returns 0 ('false').<br>
**说明**: 当 input1 和 input2 不同的时候返回 1（true），否则返回 0（false）。

**5. not**<br>
**Category**: Logical<br>
**分类**: 逻辑类<br>
**Definition**: not(x)<br>
**定义**: 语法：not(x)<br>
**Description**: Returns the logical negation of x. Returns 0 when x is 1 ('true') and 1 when x is 0 ('false').<br>
**说明**: 返回 x 的逻辑取反：x 为 1（true）时返回 0，x 为 0（false）时返回 1。

**6. greater**<br>
**Category**: Logical<br>
**分类**: 逻辑类<br>
**Definition**: input1 > input2<br>
**定义**: 语法：input1 > input2<br>
**Description**: Returns 1 ('true') if input1 is a larger than input2. Otherwise, returns 0 ('false').<br>
**说明**: 当 input1 大于 input2 时返回 1（true），否则返回 0（false）。

**7. greater_equal**<br>
**Category**: Logical<br>
**分类**: 逻辑类<br>
**Definition**: input1 >= input2<br>
**定义**: 语法：input1 >= input2<br>
**Description**: Returns 1 ('true') if input1 is a larger or the same as input2. Otherwise, returns 0 ('false').<br>
**说明**: 当 input1 大于或等于 input2 时返回 1（true），否则返回 0（false）。

**8. less_equal**<br>
**Category**: Logical<br>
**分类**: 逻辑类<br>
**Definition**: input1 <= input2<br>
**定义**: 语法：input1 <= input2<br>
**Description**: Returns 1 ('true') if input1 is a smaller or the same as input2. Otherwise, returns 0 ('false').<br>
**说明**: 当 input1 小于或等于 input2 时返回 1（true），否则返回 0（false）。

**9. is_nan**<br>
**Category**: Logical<br>
**分类**: 逻辑类<br>
**Definition**: is_nan(input)<br>
**定义**: 语法：is_nan(input)<br>
**Description**: If (input == NaN) return 1 else return 0<br>
**说明**: 如果输入是 NaN，则返回 1；否则返回 0。<br>
**Documentation**: /operators/is_nan<br>
**文档**: /operators/is_nan

**10. if_else**<br>
**Category**: Logical<br>
**分类**: 逻辑类<br>
**Definition**: if_else(input1, input2, input3)<br>
**定义**: 语法：if_else(input1, input2, input3)<br>
**Description**: The if_else operator returns one of two values based on a condition. If the condition is true, it returns the first value; if false, it returns the second value.<br>
**说明**: 根据条件返回两个值之一：条件为真时返回第一个值，条件为假时返回第二个值。<br>
**Documentation**: /operators/if_else<br>
**文档**: /operators/if_else

**11. less**<br>
**Category**: Logical<br>
**分类**: 逻辑类<br>
**Definition**: input1 < input2<br>
**定义**: 语法：input1 < input2<br>
**Description**: Returns 1 ('true') if input1 is a smaller than input2. Otherwise, returns 0 ('false').<br>
**说明**: 当 input1 小于 input2 时返回 1（true），否则返回 0（false）。

---

**Time Series**<br>
**时间序列类**

**1. ts_sum**<br>
**Category**: Time Series<br>
**分类**: 时间序列类<br>
**Definition**: ts_sum(x, d)<br>
**定义**: 语法：ts_sum(x, d)<br>
**Description**: Sum values of x for the past d days.<br>
**说明**: 计算过去 d 天内 x 的总和。

**2. ts_zscore**<br>
**Category**: Time Series<br>
**分类**: 时间序列类<br>
**Definition**: ts_zscore(x, d)<br>
**定义**: 语法：ts_zscore(x, d)<br>
**Description**: Calculates the Z-score of a time series, showing how far today's value is from the recent average, measured in standard deviations. Useful for standardizing and comparing values over time.<br>
**说明**: 计算时间序列的 Z-score，表示今天的值距离近期均值有多少个标准差，常用于时间维度上的标准化和比较。<br>
**Documentation**: /operators/ts_zscore<br>
**文档**: /operators/ts_zscore

**3. ts_std_dev**<br>
**Category**: Time Series<br>
**分类**: 时间序列类<br>
**Definition**: ts_std_dev(x, d)<br>
**定义**: 语法：ts_std_dev(x, d)<br>
**Description**: Calculates the standard deviation of a data series x over the past d days, measuring how much the values deviate from their mean during that period.<br>
**说明**: 计算过去 d 天内数据序列 x 的标准差，用来衡量这段时间内数值偏离均值的程度。<br>
**Documentation**: /operators/ts_std_dev<br>
**文档**: /operators/ts_std_dev

**4. ts_mean**<br>
**Category**: Time Series<br>
**分类**: 时间序列类<br>
**Definition**: ts_mean(x, d)<br>
**定义**: 语法：ts_mean(x, d)<br>
**Description**: Calculates the simple average (mean) value of a variable x over the past d days.<br>
**说明**: 计算变量 x 在过去 d 天内的简单平均值。<br>
**Documentation**: /operators/ts_mean<br>
**文档**: /operators/ts_mean

**5. ts_scale**<br>
**Category**: Time Series<br>
**分类**: 时间序列类<br>
**Definition**: ts_scale(x, d, constant = 0)<br>
**定义**: 语法：ts_scale(x, d, constant = 0)<br>
**Description**: Scales a time series to a 0-1 range based on its minimum and maximum values over a specified period, with an optional constant shift.<br>
**说明**: 根据指定窗口内的最小值和最大值，把时间序列缩放到 0-1 区间，并可加入一个常数偏移。<br>
**Documentation**: /operators/ts_scale<br>
**文档**: /operators/ts_scale

**6. ts_rank**<br>
**Category**: Time Series<br>
**分类**: 时间序列类<br>
**Definition**: ts_rank(x, d, constant = 0)<br>
**定义**: 语法：ts_rank(x, d, constant = 0)<br>
**Description**: Ranks the value of a variable for each instrument over a specified number of past days, returning the rank of the current value (optionally adjusted by a constant). Useful for normalizing time-series data and highlighting relative performance over time.<br>
**说明**: 在过去 d 天窗口内，对当前值在该工具自身历史值中的位置做排名，返回当前值的时间序列排名，可用 constant 调整。<br>
**Documentation**: /operators/ts_rank<br>
**文档**: /operators/ts_rank

**7. ts_quantile**<br>
**Category**: Time Series<br>
**分类**: 时间序列类<br>
**Definition**: ts_quantile(x, d, driver="gaussian")<br>
**定义**: 语法：ts_quantile(x, d, driver="gaussian")<br>
**Description**: Calculates the ts_rank of the input and transforms it using the inverse cumulative distribution function (quantile function) of a specified probability distribution (default: Gaussian/normal). This helps to normalize or reshape the distribution of your data over a rolling window.<br>
**说明**: 先计算输入的 ts_rank，再用指定分布的反累积分布函数进行转换，默认使用高斯分布，用于滚动窗口内的数据归一化或分布重塑。<br>
**Documentation**: /operators/ts_quantile<br>
**文档**: /operators/ts_quantile

**8. ts_arg_min**<br>
**Category**: Time Series<br>
**分类**: 时间序列类<br>
**Definition**: ts_arg_min(x, d)<br>
**定义**: 语法：ts_arg_min(x, d)<br>
**Description**: Returns the number of days since the minimum value occurred in a time series over the past d days. If today's value is the minimum, returns 0; if it was yesterday, returns 1, and so on.<br>
**说明**: 返回过去 d 天内最小值距离今天的天数；如果今天就是最小值返回 0，昨天为最小值返回 1，依此类推。<br>
**Documentation**: /operators/ts_arg_min<br>
**文档**: /operators/ts_arg_min

**9. ts_regression**<br>
**Category**: Time Series<br>
**分类**: 时间序列类<br>
**Definition**: ts_regression(y, x, d, lag = 0, rettype = 0)<br>
**定义**: 语法：ts_regression(y, x, d, lag = 0, rettype = 0)<br>
**Description**: Returns various parameters related to regression function<br>
**说明**: 返回与回归函数相关的多个参数，具体返回内容通常由 rettype 控制。<br>
**Documentation**: /operators/ts_regression<br>
**文档**: /operators/ts_regression

**10. kth_element**<br>
**Category**: Time Series<br>
**分类**: 时间序列类<br>
**Definition**: kth_element(x, d, k, ignore="NaN")<br>
**定义**: 语法：kth_element(x, d, k, ignore="NaN")<br>
**Description**: Returns the K-th value from a time series by looking back over a specified number of ('d') days, with the option to ignore certain values. Commonly used for backfilling missing data.<br>
**说明**: 在过去 d 天窗口内返回第 k 个值，并可选择忽略某些值，常用于缺失值回填。<br>
**Documentation**: /operators/kth_element<br>
**文档**: /operators/kth_element

**11. ts_corr**<br>
**Category**: Time Series<br>
**分类**: 时间序列类<br>
**Definition**: ts_corr(x, y, d)<br>
**定义**: 语法：ts_corr(x, y, d)<br>
**Description**: Calculates the Pearson correlation between two variables, x and y, over the past d days, showing how closely they move together.<br>
**说明**: 计算两个变量 x 和 y 在过去 d 天内的 Pearson 相关系数，用来衡量二者是否同步变化。<br>
**Documentation**: /operators/ts_corr<br>
**文档**: /operators/ts_corr

**12. ts_count_nans**<br>
**Category**: Time Series<br>
**分类**: 时间序列类<br>
**Definition**: ts_count_nans(x, d)<br>
**定义**: 语法：ts_count_nans(x, d)<br>
**Description**: Counts the number of missing (NaN) values in a data series over a specified number of days.<br>
**说明**: 统计过去 d 天内数据序列中的 NaN 缺失值数量。<br>
**Documentation**: /operators/ts_count_nans<br>
**文档**: /operators/ts_count_nans

**13. ts_covariance**<br>
**Category**: Time Series<br>
**分类**: 时间序列类<br>
**Definition**: ts_covariance(y, x, d)<br>
**定义**: 语法：ts_covariance(y, x, d)<br>
**Description**: Calculates the covariance between two time-series variables, y and x, over the past d days. Useful for measuring how two variables move together within a specified historical window.<br>
**说明**: 计算两个时间序列变量 y 和 x 在过去 d 天内的协方差，用来衡量二者在历史窗口内是否一起变动。<br>
**Documentation**: /operators/ts_covariance<br>
**文档**: /operators/ts_covariance

**14. ts_decay_linear**<br>
**Category**: Time Series<br>
**分类**: 时间序列类<br>
**Definition**: ts_decay_linear(x, d, dense = false)<br>
**定义**: 语法：ts_decay_linear(x, d, dense = false)<br>
**Description**: Applies a linear decay to time-series data over a set number of days, smoothing the data by averaging recent values and reducing the impact of older or missing data.<br>
**说明**: 对时间序列应用线性衰减，使近期数据权重更高、较早数据权重更低，从而起到平滑作用。<br>
**Documentation**: /operators/ts_decay_linear<br>
**文档**: /operators/ts_decay_linear

**15. ts_product**<br>
**Category**: Time Series<br>
**分类**: 时间序列类<br>
**Definition**: ts_product(x, d)<br>
**定义**: 语法：ts_product(x, d)<br>
**Description**: Returns the product of the values of x over the past d days. Useful for calculating geometric means and compounding returns or growth rates.<br>
**说明**: 返回过去 d 天内 x 的连乘积，常用于计算几何均值、复合收益或增长率。<br>
**Documentation**: /operators/ts_product<br>
**文档**: /operators/ts_product

**16. ts_delay**<br>
**Category**: Time Series<br>
**分类**: 时间序列类<br>
**Definition**: ts_delay(x, d)<br>
**定义**: 语法：ts_delay(x, d)<br>
**Description**: Returns the value of a variable x from d days ago. Use this operator to access historical data points by specifying the desired time lag in days.<br>
**说明**: 返回变量 x 在 d 天前的值，用于取历史滞后数据。<br>
**Documentation**: /operators/ts_delay<br>
**文档**: /operators/ts_delay

**17. ts_backfill**<br>
**Category**: Time Series<br>
**分类**: 时间序列类<br>
**Definition**: ts_backfill(x, lookback = d, k = 1)<br>
**定义**: 语法：ts_backfill(x, lookback = d, k = 1)<br>
**Description**: Replaces missing (NaN) values in a time series with the most recent valid value from a specified lookback window, improving data coverage and reducing risk from missing data.<br>
**说明**: 用指定回看窗口内最近的有效值替换时间序列中的 NaN，提高数据覆盖率并减少缺失值风险。<br>
**Documentation**: /operators/ts_backfill<br>
**文档**: /operators/ts_backfill

**18. ts_av_diff**<br>
**Category**: Time Series<br>
**分类**: 时间序列类<br>
**Definition**: ts_av_diff(x, d)<br>
**定义**: 语法：ts_av_diff(x, d)<br>
**Description**: Calculates the difference between a value and its mean over a specified period, ignoring NaN values in the mean calculation. In short, it returns x - ts_mean(x, d) with NaNs ignored.<br>
**说明**: 计算当前值与过去 d 天均值之间的差，均值计算会忽略 NaN；简单理解就是 x - ts_mean(x, d)。<br>
**Documentation**: /operators/ts_av_diff<br>
**文档**: /operators/ts_av_diff

**19. hump**<br>
**Category**: Time Series<br>
**分类**: 时间序列类<br>
**Definition**: hump(x, hump = 0.01)<br>
**定义**: 语法：hump(x, hump = 0.01)<br>
**Description**: Limits amount and magnitude of changes in input (thus reducing turnover)<br>
**说明**: 限制输入值变化的幅度和频率，从而降低换手率。<br>
**Documentation**: /operators/hump<br>
**文档**: /operators/hump

**20. ts_arg_max**<br>
**Category**: Time Series<br>
**分类**: 时间序列类<br>
**Definition**: ts_arg_max(x, d)<br>
**定义**: 语法：ts_arg_max(x, d)<br>
**Description**: Returns the number of days since the maximum value occurred in the last d days of a time series. If today's value is the maximum, returns 0; if it was yesterday, returns 1, and so on.<br>
**说明**: 返回过去 d 天内最大值距离今天的天数；如果今天就是最大值返回 0，昨天为最大值返回 1，依此类推。<br>
**Documentation**: /operators/ts_arg_max<br>
**文档**: /operators/ts_arg_max

**21. last_diff_value**<br>
**Category**: Time Series<br>
**分类**: 时间序列类<br>
**Definition**: last_diff_value(x, d)<br>
**定义**: 语法：last_diff_value(x, d)<br>
**Description**: Returns the most recent value of x from the past d days that is different from the current value of x.<br>
**说明**: 返回过去 d 天中最近一个与当前 x 不同的历史值。<br>
**Documentation**: /operators/last_diff_value<br>
**文档**: /operators/last_diff_value

**22. ts_step**<br>
**Category**: Time Series<br>
**分类**: 时间序列类<br>
**Definition**: ts_step(1)<br>
**定义**: 语法：ts_step(1)<br>
**Description**: Returns a counter of days, incrementing by one each day.<br>
**说明**: 返回一个按天递增的计数器，每天加 1。<br>
**Documentation**: /operators/ts_step<br>
**文档**: /operators/ts_step

**23. ts_delta**<br>
**Category**: Time Series<br>
**分类**: 时间序列类<br>
**Definition**: ts_delta(x, d)<br>
**定义**: 语法：ts_delta(x, d)<br>
**Description**: Calculates the difference between a value and its delayed version over a specified period. Useful for measuring changes or momentum in time-series data.<br>
**说明**: 计算当前值与 d 天前滞后值之间的差，用于衡量变化量或动量。<br>
**Documentation**: /operators/ts_delta<br>
**文档**: /operators/ts_delta

**24. days_from_last_change**<br>
**Category**: Time Series<br>
**分类**: 时间序列类<br>
**Definition**: days_from_last_change(x)<br>
**定义**: 语法：days_from_last_change(x)<br>
**Description**: Calculates the number of days since the last change in the value of a given variable.<br>
**说明**: 计算某个变量距离上一次发生变化已经过去多少天。<br>
**Documentation**: /operators/days_from_last_change<br>
**文档**: /operators/days_from_last_change

---

**Cross Sectional**<br>
**横截面类**

**1. winsorize**<br>
**Category**: Cross Sectional<br>
**分类**: 横截面类<br>
**Definition**: winsorize(x, std = 4)<br>
**定义**: 语法：winsorize(x, std = 4)<br>
**Description**: Winsorize limits values in a data to within a specified number of standard deviations from the mean, reducing the impact of extreme outliers.<br>
**说明**: 把数据限制在均值附近指定标准差范围内，降低极端异常值的影响。<br>
**Documentation**: /operators/winsorize<br>
**文档**: /operators/winsorize

**2. normalize**<br>
**Category**: Cross Sectional<br>
**分类**: 横截面类<br>
**Definition**: normalize(x, useStd = false, limit = 0.0)<br>
**定义**: 语法：normalize(x, useStd = false, limit = 0.0)<br>
**Description**: Centers a daily cross section by subtracting the market mean; optionally divide by the cross sectional standard deviation and clamp the result to [-limit, +limit]. NaNs are ignored in mean/std.<br>
**说明**: 对每日横截面做中心化：减去市场均值；可选择除以横截面标准差，并把结果限制在 [-limit, +limit] 范围内。均值和标准差计算会忽略 NaN。<br>
**Documentation**: /operators/normalize<br>
**文档**: /operators/normalize

**3. quantile**<br>
**Category**: Cross Sectional<br>
**分类**: 横截面类<br>
**Definition**: quantile(x, driver = gaussian, sigma = 1.0)<br>
**定义**: 语法：quantile(x, driver = gaussian, sigma = 1.0)<br>
**Description**: Ranks and shifts a vector of Alpha values, then applies a chosen statistical distribution (gaussian, cauchy, or uniform) to reduce outliers. The sigma parameter controls the scale of the output.<br>
**说明**: 先对 Alpha 值向量排名并平移，再套用指定统计分布（gaussian、cauchy 或 uniform）以减少异常值影响；sigma 控制输出尺度。<br>
**Documentation**: /operators/quantile<br>
**文档**: /operators/quantile

**4. rank**<br>
**Category**: Cross Sectional<br>
**分类**: 横截面类<br>
**Definition**: rank(x, rate = 2)<br>
**定义**: 语法：rank(x, rate = 2)<br>
**Description**: Ranks the values of the input x among all instruments, returning numbers evenly spaced between 0.0 and 1.0. Useful for normalizing data and reducing the impact of outliers.<br>
**说明**: 在所有股票/工具的横截面上对输入 x 排名，返回 0.0 到 1.0 之间的均匀数值，常用于标准化并降低异常值影响。<br>
**Documentation**: /operators/rank<br>
**文档**: /operators/rank

**5. scale**<br>
**Category**: Cross Sectional<br>
**分类**: 横截面类<br>
**Definition**: scale(x, scale = 1, longscale = 1, shortscale = 1)<br>
**定义**: 语法：scale(x, scale = 1, longscale = 1, shortscale = 1)<br>
**Description**: Scales the input so that the sum of absolute values across all instruments equals a specified book size. Allows separate scaling for long and short positions using optional parameters.<br>
**说明**: 把输入缩放到所有工具绝对值之和等于指定账面规模；也支持对多头和空头分别设置缩放参数。<br>
**Documentation**: /operators/scale<br>
**文档**: /operators/scale

**6. zscore**<br>
**Category**: Cross Sectional<br>
**分类**: 横截面类<br>
**Definition**: zscore(x)<br>
**定义**: 语法：zscore(x)<br>
**Description**: Z-score is a numerical measurement that describes a value's relationship to the mean of a group of values. Z-score is measured in terms of standard deviations from the mean.<br>
**说明**: Z-score 表示一个值相对于同组均值的位置，单位是标准差。<br>
**Documentation**: /operators/zscore<br>
**文档**: /operators/zscore

---

**Vector**<br>
**向量类**

**1. vec_sum**<br>
**Category**: Vector<br>
**分类**: 向量类<br>
**Definition**: vec_sum(x)<br>
**定义**: 语法：vec_sum(x)<br>
**Description**: Calculates the sum of all values in a vector field.<br>
**说明**: 计算向量字段中所有元素的总和。<br>
**Documentation**: /operators/vec_sum<br>
**文档**: /operators/vec_sum

**2. vec_avg**<br>
**Category**: Vector<br>
**分类**: 向量类<br>
**Definition**: vec_avg(x)<br>
**定义**: 语法：vec_avg(x)<br>
**Description**: Calculates the mean (average) of all elements in a vector field for each instrument and date, converting vector data to a single matrix value.<br>
**说明**: 计算每个工具、每个日期的向量字段元素平均值，把向量数据转换成单个矩阵值。<br>
**Documentation**: /operators/vec_avg<br>
**文档**: /operators/vec_avg

---

**Transformational**<br>
**转换类**

**1. bucket**<br>
**Category**: Transformational<br>
**分类**: 转换类<br>
**Definition**: bucket(rank(x), range="0, 1, 0.1", skipBoth=False, NaNGroup=False) or bucket(rank(x), buckets="2,5,6,7,10", skipBoth=False, NaNGroup=False)<br>
**定义**: 语法：bucket(rank(x), range="0, 1, 0.1", skipBoth=False, NaNGroup=False) 或 bucket(rank(x), buckets="2,5,6,7,10", skipBoth=False, NaNGroup=False)<br>
**Description**: The bucket operator creates custom groups by dividing data into buckets (ranges) based on ranked values of any data field. These buckets can then be used with group operators like group_neutralize, group_rank, group_zscore etc.<br>
**说明**: 根据某个数据字段的排名值创建自定义分桶/分组，这些桶可用于 group_neutralize、group_rank、group_zscore 等分组操作符。<br>
**Documentation**: /operators/bucket<br>
**文档**: /operators/bucket

**2. trade_when**<br>
**Category**: Transformational<br>
**分类**: 转换类<br>
**Definition**: trade_when(x, y, z)<br>
**定义**: 语法：trade_when(x, y, z)<br>
**Description**: The trade_when operator changes Alpha values only when a specific condition is met, keeps previous values otherwise, and can close positions by assigning NaN under an exit condition. It is useful for reducing turnover and controlling when trades are executed.<br>
**说明**: 只有当特定条件满足时才更新 Alpha 值，否则保留之前的值；当退出条件满足时可通过赋 NaN 平仓。常用于降低换手和控制交易时机。<br>
**Documentation**: /operators/trade_when<br>
**文档**: /operators/trade_when

---

**Group**<br>
**分组类**

**1. group_scale**<br>
**Category**: Group<br>
**分类**: 分组类<br>
**Definition**: group_scale(x, group)<br>
**定义**: 语法：group_scale(x, group)<br>
**Description**: Normalizes values within each group to a range between 0 and 1, making data comparable across different groups.<br>
**说明**: 在每个分组内部把数值归一化到 0 到 1 区间，使不同分组之间更可比较。<br>
**Documentation**: /operators/group_scale<br>
**文档**: /operators/group_scale

**2. group_neutralize**<br>
**Category**: Group<br>
**分类**: 分组类<br>
**Definition**: group_neutralize(x, group)<br>
**定义**: 语法：group_neutralize(x, group)<br>
**Description**: Neutralizes Alpha values within each specified group by subtracting the group mean from each value. Groups can be industry, sector, country, or any custom grouping.<br>
**说明**: 在指定分组内对 Alpha 值做中性化：每个值减去该组均值。分组可以是行业、部门、国家或自定义分组。<br>
**Documentation**: /operators/group_neutralize<br>
**文档**: /operators/group_neutralize

**3. group_zscore**<br>
**Category**: Group<br>
**分类**: 分组类<br>
**Definition**: group_zscore(x, group)<br>
**定义**: 语法：group_zscore(x, group)<br>
**Description**: Calculates the Z-score of each value within its group, showing how far each value is from the group mean in terms of standard deviations. Useful for comparing values relative to their group.<br>
**说明**: 在每个分组内部计算 Z-score，表示每个值距离组内均值有多少个标准差，适合同组内比较。<br>
**Documentation**: /operators/group_zscore<br>
**文档**: /operators/group_zscore

**4. group_backfill**<br>
**Category**: Group<br>
**分类**: 分组类<br>
**Definition**: group_backfill(x, group, d, std = 4.0)<br>
**定义**: 语法：group_backfill(x, group, d, std = 4.0)<br>
**Description**: Fills missing (NaN) values for instruments within the same group by calculating a winsorized mean of all non-NaN values over the past d days. The winsorized mean is computed by trimming extreme values based on a specified standard deviation multiplier (std, default 4.0).<br>
**说明**: 对同一分组内缺失的 NaN 值进行填充：在过去 d 天内取非 NaN 值的 winsorized 均值，std 控制极端值裁剪强度，默认 4.0。<br>
**Documentation**: /operators/group_backfill<br>
**文档**: /operators/group_backfill

**5. group_mean**<br>
**Category**: Group<br>
**分类**: 分组类<br>
**Definition**: group_mean(x, weight, group)<br>
**定义**: 语法：group_mean(x, weight, group)<br>
**Description**: Calculates the harmonic mean of a data field within each specified group.<br>
**说明**: 在指定分组内计算某个数据字段的调和均值。<br>
**Documentation**: /operators/group_mean<br>
**文档**: /operators/group_mean

**6. group_rank**<br>
**Category**: Group<br>
**分类**: 分组类<br>
**Definition**: group_rank(x, group)<br>
**定义**: 语法：group_rank(x, group)<br>
**Description**: Ranks each element within its group based on the input field, assigning a value between 0.0 and 1.0. This helps compare items within the same group, such as stocks in the same industry.<br>
**说明**: 在每个分组内部对元素进行排名，返回 0.0 到 1.0 之间的值，适合同一行业/同一组内比较。<br>
**Documentation**: /operators/group_rank<br>
**文档**: /operators/group_rank
