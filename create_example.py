import pandas as pd

# 创建示例数据
diseases = pd.DataFrame({
    '疾病名称': ['乳腺结节或肿块'],
    '疾病编码': ['rxjj']
})

questions = pd.DataFrame({
    '问题编码': ['v21_rxjj'],
    '问题内容': ['您的乳腺结节符合哪种情况?'],
    '问题类型': ['P'],
    '答案类型': ['1']
})

answers = pd.DataFrame({
    '问题编码': ['v21_rxjj', 'v21_rxjj', 'v21_rxjj'],
    '答案选项': [
        '未手术或穿刺 BI-RADS分级1级',
        '未手术或穿刺 BI-RADS分级2级',
        '不符合上述任一情况'
    ],
    '医疗险结论': ['25', '25', '拒保'],
    '医疗特殊编码': ['01', '01', '']
})

# 创建Excel文件
with pd.ExcelWriter('example.xlsx') as writer:
    diseases.to_excel(writer, sheet_name='疾病表', index=False)
    questions.to_excel(writer, sheet_name='问题表', index=False)
    answers.to_excel(writer, sheet_name='答案表', index=False)

print("示例Excel文件已创建：example.xlsx") 