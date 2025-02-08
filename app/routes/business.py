@business_bp.route('/product/create', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        logger.info(f"Received data: {data}")
        
        # 保留原有的数据验证逻辑
        if not all(key in data for key in ['name', 'code', 'type', 'company_id', 'channel_id']):
            return jsonify({
                'code': 400,
                'message': '缺少必要参数'
            }), 400

        # 保留原有的产品代码查重逻辑
        existing_product = Product.query.filter_by(product_code=data['code']).first()
        if existing_product:
            return jsonify({
                'code': 400,
                'message': f'创建失败：产品代码 {data["code"]} 已存在，请使用其他代码'
            }), 400

        # 原有的产品创建逻辑
        product_type = ProductType.query.filter_by(name=data['type']).first()
        if not product_type:
            return jsonify({
                'code': 400,
                'message': f'产品类型 {data["type"]} 不存在'
            }), 400

        product = Product(
            name=data['name'],
            product_code=data['code'],
            product_type_id=product_type.id,
            insurance_company_id=data['company_id'],
            channel_id=data['channel_id'],
            ai_parameter_id=data['ai_params_id'] if data['ai_params_id'] else None,
            status='enabled'
        )
        
        logger.info(f"Created product object: {product.__dict__}")
        
        try:
            db.session.add(product)
            db.session.commit()
            return jsonify({
                'code': 200,
                'message': '产品创建成功'
            })
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Error creating product: {e}")
            return jsonify({
                'code': 400,
                'message': f'创建失败：产品代码 {data["code"]} 已存在，请使用其他代码'
            }), 400
            
    except Exception as e:
        logger.error(f"Error in create_product: {e}")
        return jsonify({
            'code': 500,
            'message': f'创建失败：{str(e)}'
        }), 500 