from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
import logging
from app.extensions import db
from app.models.business.company.insurance_company import InsuranceCompany
from app.models.base.enums import StatusEnum

logger = logging.getLogger(__name__)

class CompanyService:
    """保险公司服务"""
    
    @staticmethod
    def get_company_list(
        page: int = 1,
        per_page: int = 10,
        name: str = None,
        code: str = None,
        status: str = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        获取保险公司列表
        
        Args:
            page: 页码
            per_page: 每页数量
            name: 公司名称(模糊查询)
            code: 公司编码(模糊查询)
            status: 状态
            
        Returns:
            Tuple[List[Dict[str, Any]], int]: (公司列表, 总数)
        """
        try:
            query = InsuranceCompany.query
            
            # 应用过滤条件
            if name:
                query = query.filter(InsuranceCompany.name.like(f'%{name}%'))
            if code:
                query = query.filter(InsuranceCompany.code.like(f'%{code}%'))
            if status:
                query = query.filter(InsuranceCompany.status == status)
            
            # 获取总数
            total = query.count()
            
            # 分页
            companies = query.order_by(InsuranceCompany.created_at.desc()) \
                .offset((page - 1) * per_page) \
                .limit(per_page) \
                .all()
            
            return [company.to_dict() for company in companies], total
            
        except SQLAlchemyError as e:
            logger.error(f'获取保险公司列表失败: {str(e)}')
            return [], 0
    
    @staticmethod
    def get_company_by_id(company_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取保险公司
        
        Args:
            company_id: 公司ID
            
        Returns:
            Optional[Dict[str, Any]]: 公司信息字典
        """
        try:
            company = InsuranceCompany.query.get(company_id)
            return company.to_dict() if company else None
        except SQLAlchemyError as e:
            logger.error(f'获取保险公司详情失败: {str(e)}')
            return None
    
    @staticmethod
    def create_company(data: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        创建保险公司
        
        Args:
            data: 公司信息
            
        Returns:
            Tuple[Optional[Dict[str, Any]], str]: (公司信息字典, 错误信息)
        """
        try:
            # 创建公司实例
            company = InsuranceCompany(**data)
            
            # 验证数据
            is_valid, errors = company.validate_create()
            if not is_valid:
                return None, '; '.join(errors)
            
            # 检查编码是否已存在
            if InsuranceCompany.query.filter_by(code=data['code']).first():
                return None, '公司编码已存在'
            
            # 保存到数据库
            db.session.add(company)
            db.session.commit()
            
            return company.to_dict(), ''
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f'创建保险公司失败: {str(e)}')
            return None, str(e)
    
    @staticmethod
    def update_company(company_id: int, data: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        更新保险公司
        
        Args:
            company_id: 公司ID
            data: 更新的数据
            
        Returns:
            Tuple[Optional[Dict[str, Any]], str]: (更新后的公司信息字典, 错误信息)
        """
        try:
            company = InsuranceCompany.query.get(company_id)
            if not company:
                return None, '公司不存在'
            
            # 如果更新了编码，检查是否存在重复
            if 'code' in data and data['code'] != company.code:
                if InsuranceCompany.query.filter_by(code=data['code']).first():
                    return None, '公司编码已存在'
            
            # 更新字段
            for key, value in data.items():
                if hasattr(company, key):
                    setattr(company, key, value)
            
            # 验证数据
            is_valid, errors = company.validate_update()
            if not is_valid:
                return None, '; '.join(errors)
            
            db.session.commit()
            return company.to_dict(), ''
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f'更新保险公司失败: {str(e)}')
            return None, str(e)
    
    @staticmethod
    def delete_company(company_id: int) -> Tuple[bool, str]:
        """
        删除保险公司
        
        Args:
            company_id: 公司ID
            
        Returns:
            Tuple[bool, str]: (是否成功, 错误信息)
        """
        try:
            company = InsuranceCompany.query.get(company_id)
            if not company:
                return False, '公司不存在'
            
            # 检查是否有关联的产品
            if company.products:
                return False, '该公司下存在关联的产品，无法删除'
            
            db.session.delete(company)
            db.session.commit()
            return True, ''
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f'删除保险公司失败: {str(e)}')
            return False, str(e) 