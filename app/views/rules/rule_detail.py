from flask import Blueprint, render_template
from app.models.rules.core.underwriting_rule import UnderwritingRule
from app.models.rules.disease.disease import Disease
from app.models.rules.question.question import Question
from app.models.rules.answer.answer_option import AnswerOption
from app.models.rules.import_record import ImportRecord
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('rule_detail', __name__)

@bp.route('/rule/<int:rule_id>')
def view_rule(rule_id):
    """查看规则详情"""
    # 获取规则信息
    rule = UnderwritingRule.query.get_or_404(rule_id)
    
    # 获取最新的导入记录
    import_record = ImportRecord.query.filter_by(
        rule_id=rule_id
    ).order_by(ImportRecord.created_at.desc()).first()
    
    if not import_record:
        return render_template('rules/underwriting/rule_detail.html',
                             rule=rule,
                             diseases_by_category={},
                             questions=[],
                             answers_by_question={})
    
    # 获取该批次的所有疾病，按大类分组
    diseases = Disease.query.filter_by(batch_no=import_record.batch_no).all()
    diseases_by_category = defaultdict(lambda: {'name': '', 'diseases': []})
    
    for disease in diseases:
        category = diseases_by_category[disease.category_code]
        category['name'] = disease.category_name
        category['diseases'].append(disease)
    
    # 获取所有问题
    questions = Question.query.filter_by(rule_id=rule_id).all()
    
    # 获取所有答案并按问题分组
    answers = AnswerOption.query.join(
        Question, AnswerOption.question_id == Question.id
    ).filter(
        Question.rule_id == rule_id
    ).all()
    
    # 将答案按问题ID分组
    answers_by_question = defaultdict(list)
    for answer in answers:
        answers_by_question[answer.question_id].append(answer)
    
    return render_template('rules/underwriting/rule_detail.html',
                         rule=rule,
                         diseases_by_category=dict(diseases_by_category),
                         questions=questions,
                         answers_by_question=dict(answers_by_question)) 