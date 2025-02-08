import React, { useState, useEffect } from 'react';
import { Card, Table, Select, Form, Input, Button, message } from 'antd';
import { getDiseases, getDiseaseCategories, getDiseaseQuestions } from '@/api/underwriting';
import './index.less';

const { Option } = Select;

interface Disease {
    code: string;
    name: string;
    category_name: string;
    first_question_code: string;
}

interface Question {
    code: string;
    content: string;
    question_type: string;
    attribute: string;
}

interface Answer {
    code: string;
    content: string;
    decision: string;
    em_value: number | null;
}

const UnderwritingRules: React.FC = () => {
    const [form] = Form.useForm();
    const [diseases, setDiseases] = useState<Disease[]>([]);
    const [categories, setCategories] = useState<any[]>([]);
    const [selectedDisease, setSelectedDisease] = useState<string>('');
    const [question, setQuestion] = useState<Question | null>(null);
    const [answers, setAnswers] = useState<Answer[]>([]);
    const [loading, setLoading] = useState(false);

    // 获取疾病列表和疾病大类
    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const [diseasesRes, categoriesRes] = await Promise.all([
                    getDiseases(),
                    getDiseaseCategories()
                ]);
                setDiseases(diseasesRes.data);
                setCategories(categoriesRes.data);
            } catch (error) {
                message.error('获取数据失败');
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    // 选择疾病时获取对应的问题和答案
    const handleDiseaseSelect = async (diseaseCode: string) => {
        try {
            setLoading(true);
            setSelectedDisease(diseaseCode);
            const res = await getDiseaseQuestions(diseaseCode);
            const { question, answers } = res.data;
            setQuestion(question);
            setAnswers(answers);
        } catch (error) {
            message.error('获取问题失败');
        } finally {
            setLoading(false);
        }
    };

    // 疾病列表表格列定义
    const columns = [
        {
            title: '疾病编码',
            dataIndex: 'code',
            key: 'code',
        },
        {
            title: '疾病名称',
            dataIndex: 'name',
            key: 'name',
        },
        {
            title: '疾病类别',
            dataIndex: 'category_name',
            key: 'category_name',
        },
        {
            title: '操作',
            key: 'action',
            render: (_: any, record: Disease) => (
                <Button type="link" onClick={() => handleDiseaseSelect(record.code)}>
                    查看问题
                </Button>
            ),
        },
    ];

    return (
        <div className="underwriting-rules">
            <Card title="核保规则管理" bordered={false}>
                {/* 搜索表单 */}
                <Form form={form} layout="inline" className="search-form">
                    <Form.Item name="category" label="疾病类别">
                        <Select style={{ width: 200 }} placeholder="请选择疾病类别" allowClear>
                            {categories.map(category => (
                                <Option key={category.code} value={category.code}>
                                    {category.name}
                                </Option>
                            ))}
                        </Select>
                    </Form.Item>
                    <Form.Item name="keyword" label="关键字">
                        <Input placeholder="请输入疾病名称或编码" />
                    </Form.Item>
                    <Form.Item>
                        <Button type="primary" htmlType="submit">
                            搜索
                        </Button>
                    </Form.Item>
                </Form>

                {/* 疾病列表 */}
                <Table
                    columns={columns}
                    dataSource={diseases}
                    rowKey="code"
                    loading={loading}
                    className="disease-table"
                />

                {/* 问题和答案展示 */}
                {question && (
                    <Card title="问题详情" className="question-card">
                        <div className="question-content">
                            <h3>{question.content}</h3>
                            <p>问题类型：{question.question_type === '1' ? '单选' : '多选'}</p>
                        </div>
                        <div className="answer-list">
                            <h4>答案选项：</h4>
                            {answers.map(answer => (
                                <div key={answer.code} className="answer-item">
                                    <p>{answer.content}</p>
                                    <p>决策结果：{answer.decision}</p>
                                    {answer.em_value && <p>额外费率：{answer.em_value}</p>}
                                </div>
                            ))}
                        </div>
                    </Card>
                )}
            </Card>
        </div>
    );
};

export default UnderwritingRules; 