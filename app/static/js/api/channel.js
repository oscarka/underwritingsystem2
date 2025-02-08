// 渠道管理API
import request from '../utils/request';

const channelApi = {
    // 获取公开渠道列表
    getPublicChannels(params) {
        return request.get('/business/channels/public', { params });
    },

    // 获取所有渠道列表
    getChannels(params) {
        return request.get('/business/channels', { params });
    },

    // 获取渠道详情
    getChannel(id) {
        return request.get(`/business/channels/${id}`);
    },

    // 创建渠道
    createChannel(data) {
        return request.post('/business/channels', data);
    },

    // 更新渠道
    updateChannel(id, data) {
        return request.put(`/business/channels/${id}`, data);
    },

    // 更新渠道状态
    updateChannelStatus(id, data) {
        return request.patch(`/business/channels/${id}/status`, data);
    },

    // 删除渠道
    deleteChannel(id) {
        return request.delete(`/business/channels/${id}`);
    }
};

export default channelApi; 