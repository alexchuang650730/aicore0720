import React, { useState, useEffect, createContext, useContext } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  User, 
  Code, 
  Settings, 
  Shield, 
  Crown, 
  Wrench,
  Eye,
  EyeOff,
  Users,
  Database,
  TrendingUp,
  Activity
} from 'lucide-react';

// 權限上下文
const AuthContext = createContext();

// 角色定義
const ROLES = {
  user: {
    name: '使用者',
    icon: User,
    color: 'bg-blue-500',
    permissions: [
      'use_claudeditor',
      'use_k2_model',
      'basic_ui_generation',
      'view_own_stats',
      'use_workflows'
    ],
    features: [
      'ClaudeEditor Web界面',
      'K2模型使用',
      '基礎UI生成',
      '個人統計查看',
      '工作流執行'
    ]
  },
  developer: {
    name: '開發者',
    icon: Code,
    color: 'bg-purple-500',
    permissions: [
      'use_claudeditor',
      'use_k2_model',
      'advanced_ui_generation',
      'view_own_stats',
      'use_workflows',
      'create_workflows',
      'access_apis',
      'debug_mode',
      'code_analysis',
      'deployment'
    ],
    features: [
      '所有使用者功能',
      '高級UI生成',
      '工作流創建',
      'API訪問',
      '調試模式',
      '代碼分析',
      '部署管理'
    ]
  },
  admin: {
    name: '管理者',
    icon: Settings,
    color: 'bg-red-500',
    permissions: [
      'use_claudeditor',
      'use_k2_model',
      'advanced_ui_generation',
      'view_own_stats',
      'use_workflows',
      'create_workflows',
      'access_apis',
      'debug_mode',
      'code_analysis',
      'deployment',
      'manage_users',
      'view_all_stats',
      'system_config',
      'billing_management',
      'data_collection'
    ],
    features: [
      '所有開發者功能',
      '用戶管理',
      '全局統計',
      '系統配置',
      '計費管理',
      '數據收集管理'
    ]
  }
};

// 權限檢查Hook
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// 權限檢查函數
export const hasPermission = (userRole, permission) => {
  return ROLES[userRole]?.permissions.includes(permission) || false;
};

// 權限組件
export const PermissionGuard = ({ permission, children, fallback = null }) => {
  const { user } = useAuth();
  
  if (!user || !hasPermission(user.role, permission)) {
    return fallback;
  }
  
  return children;
};

// 角色管理組件
const RoleManagement = ({ user, onRoleChange }) => {
  const [selectedRole, setSelectedRole] = useState(user?.role || 'user');
  
  const handleRoleChange = (newRole) => {
    setSelectedRole(newRole);
    onRoleChange(newRole);
  };
  
  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center">
          <Shield className="h-6 w-6 mr-2" />
          權限管理系統
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {Object.entries(ROLES).map(([roleKey, role]) => {
            const IconComponent = role.icon;
            const isSelected = selectedRole === roleKey;
            
            return (
              <Card 
                key={roleKey}
                className={`cursor-pointer transition-all duration-200 ${
                  isSelected 
                    ? 'ring-2 ring-blue-500 shadow-lg' 
                    : 'hover:shadow-md'
                }`}
                onClick={() => handleRoleChange(roleKey)}
              >
                <CardContent className="p-6">
                  <div className="text-center">
                    <div className={`${role.color} w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4`}>
                      <IconComponent className="h-8 w-8 text-white" />
                    </div>
                    <h3 className="text-lg font-semibold mb-2">{role.name}</h3>
                    <Badge 
                      variant={isSelected ? "default" : "secondary"}
                      className="mb-4"
                    >
                      {roleKey.toUpperCase()}
                    </Badge>
                    
                    <div className="text-left space-y-2">
                      <h4 className="font-medium text-sm text-gray-600">功能權限：</h4>
                      <ul className="text-sm space-y-1">
                        {role.features.map((feature, index) => (
                          <li key={index} className="flex items-start">
                            <span className="text-green-500 mr-2">✓</span>
                            <span>{feature}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

// 用戶儀表板
const UserDashboard = () => {
  const { user } = useAuth();
  
  if (!user) return null;
  
  const role = ROLES[user.role];
  const IconComponent = role.icon;
  
  return (
    <div className="space-y-6">
      {/* 用戶信息卡片 */}
      <Card className="bg-gradient-to-r from-blue-500 to-purple-600 text-white">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center">
                <IconComponent className="h-8 w-8" />
              </div>
              <div>
                <h2 className="text-2xl font-bold">{user.username}</h2>
                <p className="text-blue-100">{user.email}</p>
                <Badge className="mt-2 bg-white/20">
                  {role.name}
                </Badge>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-blue-100">當前權限級別</p>
              <p className="text-3xl font-bold">{role.name}</p>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* 權限功能展示 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <PermissionGuard permission="use_claudeditor">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">ClaudeEditor</p>
                  <p className="text-2xl font-bold text-blue-600">可用</p>
                </div>
                <Code className="h-8 w-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>
        </PermissionGuard>
        
        <PermissionGuard permission="manage_users">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">用戶管理</p>
                  <p className="text-2xl font-bold text-purple-600">高級</p>
                </div>
                <Users className="h-8 w-8 text-purple-500" />
              </div>
            </CardContent>
          </Card>
        </PermissionGuard>
        
        <PermissionGuard permission="system_config">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">系統配置</p>
                  <p className="text-2xl font-bold text-red-600">管理員</p>
                </div>
                <Settings className="h-8 w-8 text-red-500" />
              </div>
            </CardContent>
          </Card>
        </PermissionGuard>
        
        <PermissionGuard permission="view_all_stats">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">全局統計</p>
                  <p className="text-2xl font-bold text-green-600">開放</p>
                </div>
                <TrendingUp className="h-8 w-8 text-green-500" />
              </div>
            </CardContent>
          </Card>
        </PermissionGuard>
        
        <PermissionGuard permission="data_collection">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">數據收集</p>
                  <p className="text-2xl font-bold text-orange-600">活躍</p>
                </div>
                <Database className="h-8 w-8 text-orange-500" />
              </div>
            </CardContent>
          </Card>
        </PermissionGuard>
        
        <PermissionGuard permission="debug_mode">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">調試模式</p>
                  <p className="text-2xl font-bold text-yellow-600">開發</p>
                </div>
                <Activity className="h-8 w-8 text-yellow-500" />
              </div>
            </CardContent>
          </Card>
        </PermissionGuard>
      </div>
    </div>
  );
};

// 主要的權限系統組件
const RoleBasedAuth = () => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    // 模擬從localStorage或API獲取用戶信息
    const savedUser = localStorage.getItem('powerautomation_user');
    if (savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setUser(userData);
      } catch (error) {
        console.error('Error parsing user data:', error);
      }
    }
    setIsLoading(false);
  }, []);
  
  const handleRoleChange = (newRole) => {
    const updatedUser = { ...user, role: newRole };
    setUser(updatedUser);
    localStorage.setItem('powerautomation_user', JSON.stringify(updatedUser));
  };
  
  const authContextValue = {
    user,
    setUser,
    isLoading,
    hasPermission: (permission) => hasPermission(user?.role, permission),
    isRole: (role) => user?.role === role
  };
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }
  
  return (
    <AuthContext.Provider value={authContextValue}>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 p-4">
        <div className="max-w-7xl mx-auto space-y-6">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              PowerAutomation 權限系統
            </h1>
            <p className="text-gray-600 mt-2">使用者 • 開發者 • 管理者</p>
          </div>
          
          {user ? (
            <UserDashboard />
          ) : (
            <div className="text-center">
              <p className="text-gray-600 mb-4">請先登錄以查看權限系統</p>
              <Button onClick={() => {
                // 模擬登錄
                const mockUser = {
                  id: '1',
                  username: 'Demo User',
                  email: 'demo@powerautomation.ai',
                  role: 'user'
                };
                setUser(mockUser);
                localStorage.setItem('powerautomation_user', JSON.stringify(mockUser));
              }}>
                模擬登錄
              </Button>
            </div>
          )}
          
          {user && (
            <RoleManagement user={user} onRoleChange={handleRoleChange} />
          )}
        </div>
      </div>
    </AuthContext.Provider>
  );
};

export default RoleBasedAuth;
export { AuthContext, ROLES };