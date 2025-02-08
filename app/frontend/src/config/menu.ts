// 核保管理菜单
console.log('加载菜单配置...');
export const menuConfig = [
    {
        path: '/product',
        name: '产品管理',
        icon: 'ProductIcon',
        children: [
            {
                path: '/product/channels',
                name: '渠道管理'
            },
            {
                path: '/product/companies',
                name: '保司管理'
            },
            {
                path: '/product/config',
                name: '产品配置'
            }
        ]
    },
    {
        path: '/underwriting',
        name: '核保管理',
        icon: 'UnderwritingIcon',
        children: [
            {
                path: '/underwriting/rules',
                name: '核保规则管理'
            },
            {
                path: '/underwriting/ai-parameter',
                name: '智核参数管理'
            }
        ]
    }
];
console.log('菜单配置加载完成:', menuConfig);