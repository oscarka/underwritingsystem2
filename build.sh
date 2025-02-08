#!/bin/bash

# 设置变量
IMAGE_NAME="underwriting-system"
REGISTRY="registry.cn-shanghai.aliyuncs.com/your-namespace"  # 替换为你的镜像仓库地址
VERSION=$(git describe --tags --always)
LATEST_TAG="latest"

# 显示构建信息
echo "开始构建 ${IMAGE_NAME} 镜像..."
echo "版本: ${VERSION}"
echo "仓库: ${REGISTRY}"

# 构建Docker镜像
echo "=== 构建Docker镜像 ==="
docker build -t ${IMAGE_NAME}:${VERSION} \
    --build-arg VERSION=${VERSION} \
    --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
    .

# 标记镜像
echo "=== 标记镜像 ==="
docker tag ${IMAGE_NAME}:${VERSION} ${REGISTRY}/${IMAGE_NAME}:${VERSION}
docker tag ${IMAGE_NAME}:${VERSION} ${REGISTRY}/${IMAGE_NAME}:${LATEST_TAG}

# 推送镜像到仓库
if [ "$1" = "--push" ]; then
    echo "=== 推送镜像到仓库 ==="
    docker push ${REGISTRY}/${IMAGE_NAME}:${VERSION}
    docker push ${REGISTRY}/${IMAGE_NAME}:${LATEST_TAG}
    echo "镜像已推送到仓库"
fi

echo "构建完成!"
echo "镜像标签: ${REGISTRY}/${IMAGE_NAME}:${VERSION}"
echo "使用方法:"
echo "1. 本地运行: docker run -p 5000:5000 ${IMAGE_NAME}:${VERSION}"
echo "2. 推送到仓库: ./build.sh --push"
