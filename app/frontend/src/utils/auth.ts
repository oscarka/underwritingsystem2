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
    console.log('获取token:', token)
    return token
}

export function setToken(token: string): void {
    console.log('保存token:', token)
    localStorage.setItem(TOKEN_KEY, token)
}

export function removeToken(): void {
    console.log('移除token')
    localStorage.removeItem(TOKEN_KEY)
}

export function getUser(): User | null {
    const userStr = localStorage.getItem(USER_KEY)
    console.log('获取用户信息字符串:', userStr)

    if (!userStr) {
        console.log('未找到用户信息')
        return null
    }

    try {
        const user = JSON.parse(userStr)
        console.log('解析用户信息成功:', user)
        return user
    } catch (error) {
        console.error('解析用户信息失败:', error)
        return null
    }
}

export function setUser(user: User): void {
    console.log('保存用户信息:', user)
    localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function removeUser(): void {
    console.log('移除用户信息')
    localStorage.removeItem(USER_KEY)
}

export function isLoggedIn(): boolean {
    const hasToken = !!getToken()
    const hasUser = !!getUser()
    console.log('检查登录状态:', { hasToken, hasUser })
    return hasToken && hasUser
}

export function isAdmin(): boolean {
    const user = getUser()
    return user ? user.is_admin : false
}

export function logout(): void {
    console.log('执行登出操作')
    removeToken()
    removeUser()
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