from flask import request
from app.services.business.company import CompanyService
from app.utils.response import success_response, error_response
from app.decorators import login_required
import traceback
from app.extensions import db
import logging

logger = logging.getLogger(__name__)

company_service = CompanyService()

@login_required
def get_companies():
    """获取保险公司列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('pageSize', 10, type=int)
        name = request.args.get('name', '')
        code = request.args.get('code', '')
        status = request.args.get('status', '')
        
        logger.info(f'API层 - 获取保险公司列表，请求参数: page={page}, per_page={per_page}, name={name}, code={code}, status={status}')
        
        # 获取数据
        items, total = company_service.get_company_list(
            page=page,
            per_page=per_page,
            name=name,
            code=code,
            status=status
        )
        
        # 返回结果
        result = {
            'list': items,
            'pagination': {
                'current': page,
                'pageSize': per_page,
                'total': total
            }
        }
        logger.info(f'API层 - 获取保险公司列表成功: total={total}')
        return success_response(result)
    except Exception as e:
        logger.error(f'API层 - 获取保险公司列表失败: {str(e)}')
        logger.error(traceback.format_exc())
        db.session.rollback()
        return error_response(500, f'获取保险公司列表失败: {str(e)}')

@login_required
def get_company(id):
    """获取保险公司详情"""
    try:
        logger.info(f'API层 - 获取保险公司详情: id={id}')
        company = company_service.get_company_by_id(id)
        if not company:
            logger.warning(f'API层 - 保险公司不存在: id={id}')
            return error_response(404, '保险公司不存在')
        
        logger.info(f'API层 - 获取保险公司详情成功: id={id}')
        return success_response(company)
    except Exception as e:
        logger.error(f'API层 - 获取保险公司详情失败: {str(e)}')
        logger.error(traceback.format_exc())
        db.session.rollback()
        return error_response(500, f'获取保险公司详情失败: {str(e)}')

@login_required
def create_company():
    """创建保险公司"""
    try:
        data = request.get_json()
        logger.info('API层 - 创建保险公司，原始请求数据:')
        for key, value in data.items():
            logger.info(f'  {key}: {value}')
        
        # 参数验证
        if not data.get('name'):
            logger.warning('API层 - 创建保险公司失败 - 公司名称为空')
            return error_response(400, '公司名称不能为空')
        if not data.get('code'):
            logger.warning('API层 - 创建保险公司失败 - 公司编码为空')
            return error_response(400, '公司编码不能为空')
        
        # 创建保险公司
        company, error = company_service.create_company(data)
        if error:
            logger.error(f'API层 - 保险公司创建失败: {error}')
            return error_response(400, error)
            
        logger.info(f'API层 - 保险公司创建成功: id={company["id"]}')
        return success_response(company)
    except Exception as e:
        logger.error(f'API层 - 处理创建保险公司请求失败: {str(e)}')
        logger.error(traceback.format_exc())
        return error_response(500, f'处理创建保险公司请求失败: {str(e)}')

@login_required
def update_company(id):
    """更新保险公司"""
    try:
        data = request.get_json()
        logger.info(f'API层 - 更新保险公司，请求数据: id={id}, data={data}')
        
        company, error = company_service.update_company(id, data)
        if error:
            logger.error(f'API层 - 保险公司更新失败: {error}')
            return error_response(400, error)
        
        logger.info(f'API层 - 更新保险公司成功: id={id}')
        return success_response(company)
    except Exception as e:
        logger.error(f'API层 - 更新保险公司失败: {str(e)}')
        logger.error(traceback.format_exc())
        db.session.rollback()
        return error_response(500, f'更新保险公司失败: {str(e)}')

@login_required
def delete_company(id):
    """删除保险公司"""
    try:
        logger.info(f'API层 - 删除保险公司: id={id}')
        success, error = company_service.delete_company(id)
        if not success:
            logger.warning(f'API层 - 保险公司删除失败: {error}')
            return error_response(400, error)
        
        logger.info(f'API层 - 删除保险公司成功: id={id}')
        return success_response()
    except Exception as e:
        logger.error(f'API层 - 删除保险公司失败: {str(e)}')
        logger.error(traceback.format_exc())
        db.session.rollback()
        return error_response(500, f'删除保险公司失败: {str(e)}') 