interface User {
    id: number
    username: string
    is_admin: boolean
    tenant_id: number
}

export const TOKEN_KEY = 'token'
export const USER_KEY = 'user'

export function getToken(): string | null {
    const token = localStorage.getItem(TOKEN_KEY)
    console.log('[Token获取]', {
        exists: !!token,
        length: token?.length || 0,
        timestamp: new Date().toISOString()
    })
    return token
}

export function setToken(token: string): void {
    console.log('[Token保存]', {
        length: token.length,
        timestamp: new Date().toISOString()
    })
    localStorage.setItem(TOKEN_KEY, token)
}

export function removeToken(): void {
    console.log('[Token移除]', {
        timestamp: new Date().toISOString()
    })
    localStorage.removeItem(TOKEN_KEY)
}

export function getUser(): User | null {
    const userStr = localStorage.getItem(USER_KEY)
    console.log('[用户信息获取]', {
        exists: !!userStr,
        length: userStr?.length || 0,
        timestamp: new Date().toISOString()
    })

    if (!userStr) {
        console.warn('[用户信息缺失]', {
            timestamp: new Date().toISOString()
        })
        return null
    }

    try {
        const user = JSON.parse(userStr)
        console.log('[用户信息解析]', {
            id: user.id,
            username: user.username,
            isAdmin: user.is_admin,
            tenantId: user.tenant_id,
            timestamp: new Date().toISOString()
        })
        return user
    } catch (error: any) {
        console.error('[用户信息解析失败]', {
            error: error.message,
            rawData: userStr,
            timestamp: new Date().toISOString()
        })
        return null
    }
}

export function setUser(user: User): void {
    console.log('[用户信息保存]', {
        id: user.id,
        username: user.username,
        isAdmin: user.is_admin,
        tenantId: user.tenant_id,
        timestamp: new Date().toISOString()
    })
    localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function removeUser(): void {
    console.log('[用户信息移除]', {
        timestamp: new Date().toISOString()
    })
    localStorage.removeItem(USER_KEY)
}

export function isLoggedIn(): boolean {
    const hasToken = !!getToken()
    const hasUser = !!getUser()
    console.log('[登录状态检查]', {
        hasToken,
        hasUser,
        pathname: window.location.pathname,
        timestamp: new Date().toISOString()
    })
    return hasToken && hasUser
}

export function isAdmin(): boolean {
    const user = getUser()
    const isAdminUser = user ? user.is_admin : false
    console.log('[管理员权限检查]', {
        hasUser: !!user,
        isAdmin: isAdminUser,
        timestamp: new Date().toISOString()
    })
    return isAdminUser
}

export function logout(): void {
    console.log('[登出操作开始]', {
        pathname: window.location.pathname,
        timestamp: new Date().toISOString()
    })
    removeToken()
    removeUser()
    console.log('[登出操作完成]', {
        timestamp: new Date().toISOString()
    })
}

export default {
    getToken,
    setToken,
    removeToken,
    getUser,
    setUser,
    removeUser,
    isLoggedIn,
    isAdmin,
    logout
} 