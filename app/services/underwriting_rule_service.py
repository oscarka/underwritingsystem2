from typing import Optional, List, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
from app import db
from app.models import UnderwritingRule, Disease, RuleVersion
from app.models.base.enums import StatusEnum
import logging
import traceback

logger = logging.getLogger(__name__)

class UnderwritingRuleService:
    @staticmethod
    def create_rule(data: Dict[str, Any]) -> tuple[UnderwritingRule, str]:
        """
        创建新的核保规则
        
        Args:
            data: 包含规则信息的字典
            
        Returns:
            tuple: (规则对象, 错误信息)
        """
        try:
            logger.info('服务层 - 创建规则开始，原始数据:')
            for key, value in data.items():
                logger.info(f'  原始数据 - {key}: {value}')
            
            # 验证必填字段
            if not data.get('name'):
                logger.error('服务层 - 规则创建失败: 规则名称不能为空')
                return None, '规则名称不能为空'
            if not data.get('version'):
                logger.error('服务层 - 规则创建失败: 规则版本不能为空')
                return None, '规则版本不能为空'
                
            # 检查规则名称和版本是否已存在
            existing_rule = UnderwritingRule.query.filter_by(
                name=data['name'], 
                version=data['version']
            ).first()
            if existing_rule:
                logger.error(f'服务层 - 规则创建失败: 规则已存在 name={data["name"]}, version={data["version"]}')
                return None, '相同名称和版本的规则已存在'
            
            # 创建规则
            rule = UnderwritingRule(
                name=data['name'],
                version=data['version'],
                description=data.get('description', ''),
                status=StatusEnum.DRAFT.value
            )
            
            # 如果提供了rule_version_id，设置关联
            if 'rule_version_id' in data:
                rule.rule_version_id = data['rule_version_id']
            
            db.session.add(rule)
            db.session.commit()
            logger.info(f'服务层 - 规则创建成功: id={rule.id}')
            
            return rule, ''
            
        except SQLAlchemyError as e:
            logger.error(f'服务层 - 规则创建失败: {str(e)}')
            logger.error(f'服务层 - 错误类型: {type(e).__name__}')
            logger.error(f'服务层 - 错误详情: {str(e)}')
            logger.error(traceback.format_exc())
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def update_rule(rule_id: int, data: Dict[str, Any]) -> tuple[Optional[UnderwritingRule], str]:
        """
        更新核保规则
        
        Args:
            rule_id: 规则ID
            data: 更新的数据
            
        Returns:
            tuple: (更新后的规则对象, 错误信息)
        """
        try:
            logger.info(f'服务层 - 更新规则开始: id={rule_id}')
            logger.info('更新数据:')
            for key, value in data.items():
                logger.info(f'  {key}: {value}')
            
            rule = UnderwritingRule.query.get(rule_id)
            if not rule:
                logger.error(f'服务层 - 规则更新失败: 规则不存在 id={rule_id}')
                return None, '规则不存在'
            
            # 如果更新名称或版本，检查是否存在重复
            if ('name' in data and data['name'] != rule.name) or \
               ('version' in data and data['version'] != rule.version):
                existing_rule = UnderwritingRule.query.filter_by(
                    name=data.get('name', rule.name),
                    version=data.get('version', rule.version)
                ).filter(UnderwritingRule.id != rule_id).first()
                if existing_rule:
                    logger.error(f'服务层 - 规则更新失败: 规则已存在 name={data.get("name")}, version={data.get("version")}')
                    return None, '相同名称和版本的规则已存在'
            
            # 更新字段
            for key, value in data.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
            
            db.session.commit()
            logger.info(f'服务层 - 规则更新成功: id={rule_id}')
            return rule, ''
            
        except SQLAlchemyError as e:
            logger.error(f'服务层 - 规则更新失败: {str(e)}')
            logger.error(traceback.format_exc())
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def delete_rule(rule_id: int) -> tuple[bool, str]:
        """
        删除核保规则
        
        Args:
            rule_id: 规则ID
            
        Returns:
            tuple: (是否成功, 错误信息)
        """
        try:
            logger.info(f'服务层 - 删除规则开始: id={rule_id}')
            
            rule = UnderwritingRule.query.get(rule_id)
            if not rule:
                logger.error(f'服务层 - 规则删除失败: 规则不存在 id={rule_id}')
                return False, '规则不存在'
            
            db.session.delete(rule)
            db.session.commit()
            logger.info(f'服务层 - 规则删除成功: id={rule_id}')
            return True, ''
            
        except SQLAlchemyError as e:
            logger.error(f'服务层 - 规则删除失败: {str(e)}')
            logger.error(traceback.format_exc())
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def get_rule_by_id(rule_id: int) -> Optional[UnderwritingRule]:
        """获取指定ID的规则"""
        try:
            logger.info(f'服务层 - 获取规则: id={rule_id}')
            rule = UnderwritingRule.query.get(rule_id)
            if not rule:
                logger.warning(f'服务层 - 规则不存在: id={rule_id}')
            return rule
        except SQLAlchemyError as e:
            logger.error(f'服务层 - 获取规则失败: {str(e)}')
            logger.error(traceback.format_exc())
            return None
    
    @staticmethod
    def get_rules(filters: Dict[str, Any] = None) -> List[UnderwritingRule]:
        """
        获取规则列表
        
        Args:
            filters: 过滤条件
            
        Returns:
            List[UnderwritingRule]: 规则列表
        """
        try:
            logger.info('服务层 - 获取规则列表开始')
            if filters:
                logger.info('过滤条件:')
                for key, value in filters.items():
                    logger.info(f'  {key}: {value}')
            
            query = UnderwritingRule.query
            
            if filters:
                if 'name' in filters:
                    query = query.filter(UnderwritingRule.name.like(f"%{filters['name']}%"))
                if 'version' in filters:
                    query = query.filter(UnderwritingRule.version.like(f"%{filters['version']}%"))
                if 'status' in filters:
                    query = query.filter(UnderwritingRule.status == filters['status'])
                if 'rule_version_id' in filters:
                    query = query.filter(UnderwritingRule.rule_version_id == filters['rule_version_id'])
            
            rules = query.order_by(UnderwritingRule.created_at.desc()).all()
            logger.info(f'服务层 - 获取规则列表成功: count={len(rules)}')
            return rules
            
        except SQLAlchemyError as e:
            logger.error(f'服务层 - 获取规则列表失败: {str(e)}')
            logger.error(traceback.format_exc())
            return []
    
    @staticmethod
    def update_rule_status(rule_id: int, status: str) -> tuple[Optional[UnderwritingRule], str]:
        """
        更新规则状态
        
        Args:
            rule_id: 规则ID
            status: 新状态
            
        Returns:
            tuple: (更新后的规则对象, 错误信息)
        """
        try:
            logger.info(f'服务层 - 更新规则状态开始: id={rule_id}, status={status}')
            
            rule = UnderwritingRule.query.get(rule_id)
            if not rule:
                logger.error(f'服务层 - 更新状态失败: 规则不存在 id={rule_id}')
                return None, '规则不存在'
            
            if status not in [e.value for e in StatusEnum]:
                logger.error(f'服务层 - 更新状态失败: 无效的状态值 status={status}')
                return None, '无效的状态值'
            
            rule.status = status
            db.session.commit()
            logger.info(f'服务层 - 更新规则状态成功: id={rule_id}, status={status}')
            return rule, ''
            
        except SQLAlchemyError as e:
            logger.error(f'服务层 - 更新规则状态失败: {str(e)}')
            logger.error(traceback.format_exc())
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def associate_diseases(rule_id: int, disease_ids: List[int]) -> tuple[bool, str]:
        """
        关联疾病到规则
        
        Args:
            rule_id: 规则ID
            disease_ids: 疾病ID列表
            
        Returns:
            tuple: (是否成功, 错误信息)
        """
        try:
            rule = UnderwritingRule.query.get(rule_id)
            if not rule:
                return False, '规则不存在'
            
            diseases = Disease.query.filter(Disease.id.in_(disease_ids)).all()
            if len(diseases) != len(disease_ids):
                return False, '部分疾病不存在'
            
            rule.diseases = diseases
            db.session.commit()
            return True, ''
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def export_rule(rule_id: int) -> tuple[Optional[Dict[str, Any]], str]:
        """
        导出规则
        
        Args:
            rule_id: 规则ID
            
        Returns:
            tuple: (规则数据字典, 错误信息)
        """
        try:
            rule = UnderwritingRule.query.get(rule_id)
            if not rule:
                return None, '规则不存在'
            
            # 构建导出数据
            export_data = rule.to_dict()
            
            # 添加关联数据
            export_data['diseases'] = [
                {'id': d.id, 'name': d.name} 
                for d in rule.diseases.all()
            ]
            export_data['questions'] = [
                q.to_dict() for q in rule.questions.all()
            ]
            export_data['conclusions'] = [
                c.to_dict() for c in rule.conclusions.all()
            ]
            export_data['ai_parameters'] = [
                p.to_dict() for p in rule.ai_parameters.all()
            ]
            
            return export_data, ''
            
        except SQLAlchemyError as e:
            return None, str(e)
    
    @staticmethod
    def import_rule(data: Dict[str, Any]) -> tuple[Optional[UnderwritingRule], str]:
        """
        导入规则
        
        Args:
            data: 规则数据字典
            
        Returns:
            tuple: (规则对象, 错误信息)
        """
        try:
            # 验证必填字段
            if not data.get('name'):
                return None, '规则名称不能为空'
            if not data.get('version'):
                return None, '规则版本不能为空'
            
            # 检查是否已存在
            existing_rule = UnderwritingRule.query.filter_by(
                name=data['name'],
                version=data['version']
            ).first()
            
            if existing_rule:
                return None, '相同名称和版本的规则已存在'
            
            # 创建规则
            rule = UnderwritingRule(
                name=data['name'],
                version=data['version'],
                description=data.get('description', ''),
                status=StatusEnum.DRAFT.value  # 导入的规则默认为草稿状态
            )
            
            # 如果提供了rule_version_id，设置关联
            if 'rule_version_id' in data:
                rule.rule_version_id = data['rule_version_id']
            
            db.session.add(rule)
            
            # 导入关联数据
            if 'diseases' in data:
                disease_ids = [d['id'] for d in data['diseases']]
                diseases = Disease.query.filter(Disease.id.in_(disease_ids)).all()
                rule.diseases = diseases
            
            db.session.commit()
            return rule, ''
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return None, str(e) 