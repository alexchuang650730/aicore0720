import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  User, 
  CreditCard, 
  TrendingUp, 
  Shield, 
  Zap, 
  Star,
  Mail,
  Lock,
  Eye,
  EyeOff,
  Crown,
  Gift
} from 'lucide-react';

const MembershipSystem = () => {
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [user, setUser] = useState(null);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    username: ''
  });

  // 模擬用戶數據
  const [userStats, setUserStats] = useState({
    currentPoints: 8500,
    dailyLimit: 10000,
    monthlyLimit: 300000,
    tier: 'pro',
    totalSaved: 156.78,
    commandsUsed: 234,
    k2Usage: 85.2
  });

  // 會員等級配置
  const membershipTiers = {
    free: {
      name: '體驗版',
      price: '¥0',
      dailyPoints: 1000,
      monthlyPoints: 30000,
      features: ['基礎AI對話', '基本UI生成', '社區支持'],
      color: 'bg-gray-100 text-gray-800',
      badge: 'bg-gray-500'
    },
    pro: {
      name: '專業版',
      price: '¥299',
      dailyPoints: 10000,
      monthlyPoints: 300000,
      features: ['無限AI對話', '高級UI生成', '記憶RAG', '工作流自動化', '優先支持'],
      color: 'bg-gradient-to-br from-blue-500 to-purple-600 text-white',
      badge: 'bg-blue-500'
    },
    enterprise: {
      name: '企業版',
      price: '¥2999',
      dailyPoints: 100000,
      monthlyPoints: 3000000,
      features: ['全部功能', '私有部署', '定制工作流', '1對1技術支持', '數據分析'],
      color: 'bg-gradient-to-br from-purple-600 to-pink-600 text-white',
      badge: 'bg-purple-500'
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // 模擬登錄/註冊
    const mockUser = {
      id: '1',
      email: formData.email,
      username: formData.username || formData.email.split('@')[0],
      tier: 'pro',
      points: userStats.currentPoints
    };
    
    setUser(mockUser);
    localStorage.setItem('powerautomation_user', JSON.stringify(mockUser));
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const upgradeTier = (tierName) => {
    // 模擬升級
    console.log(`升級到 ${tierName}`);
  };

  const LoginForm = () => (
    <Card className="w-full max-w-md mx-auto bg-white/90 backdrop-blur-sm shadow-2xl">
      <CardHeader className="text-center">
        <CardTitle className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          {isLoginMode ? '歡迎回來' : '開始體驗'}
        </CardTitle>
        <p className="text-gray-600 mt-2">
          {isLoginMode ? '登錄到 PowerAutomation' : '創建您的 PowerAutomation 賬戶'}
        </p>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">郵箱</label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                name="email"
                type="email"
                placeholder="請輸入您的郵箱"
                value={formData.email}
                onChange={handleInputChange}
                className="pl-10"
                required
              />
            </div>
          </div>

          {!isLoginMode && (
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">用戶名</label>
              <div className="relative">
                <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  name="username"
                  type="text"
                  placeholder="請輸入用戶名"
                  value={formData.username}
                  onChange={handleInputChange}
                  className="pl-10"
                  required
                />
              </div>
            </div>
          )}

          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">密碼</label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                name="password"
                type={showPassword ? "text" : "password"}
                placeholder="請輸入密碼"
                value={formData.password}
                onChange={handleInputChange}
                className="pl-10 pr-10"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-3 h-4 w-4 text-gray-400 hover:text-gray-600"
              >
                {showPassword ? <EyeOff /> : <Eye />}
              </button>
            </div>
          </div>

          <Button 
            type="submit" 
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-medium py-2 px-4 rounded-lg transition-all duration-200"
          >
            {isLoginMode ? '登錄' : '註冊'}
          </Button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            {isLoginMode ? '還沒有賬戶？' : '已有賬戶？'}
            <button
              onClick={() => setIsLoginMode(!isLoginMode)}
              className="ml-1 text-blue-600 hover:text-blue-800 font-medium"
            >
              {isLoginMode ? '立即註冊' : '立即登錄'}
            </button>
          </p>
        </div>

        <div className="mt-4 text-center">
          <p className="text-xs text-gray-500">
            註冊即表示您同意我們的 
            <a href="#" className="text-blue-600 hover:underline">服務條款</a> 和 
            <a href="#" className="text-blue-600 hover:underline">隱私政策</a>
          </p>
        </div>
      </CardContent>
    </Card>
  );

  const DashboardView = () => (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* 用戶狀態卡片 */}
      <Card className="bg-gradient-to-r from-blue-500 to-purple-600 text-white">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center">
                <User className="h-8 w-8" />
              </div>
              <div>
                <h2 className="text-2xl font-bold">{user?.username}</h2>
                <p className="text-blue-100">{user?.email}</p>
                <div className="flex items-center mt-2">
                  <Crown className="h-4 w-4 mr-1" />
                  <Badge className={membershipTiers[userStats.tier].badge}>
                    {membershipTiers[userStats.tier].name}
                  </Badge>
                </div>
              </div>
            </div>
            <div className="text-right">
              <p className="text-3xl font-bold">{userStats.currentPoints.toLocaleString()}</p>
              <p className="text-blue-100">可用積分</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 積分使用統計 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">今日使用</p>
                <p className="text-2xl font-bold text-gray-900">
                  {(userStats.dailyLimit - userStats.currentPoints).toLocaleString()}
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-blue-500" />
            </div>
            <Progress 
              value={((userStats.dailyLimit - userStats.currentPoints) / userStats.dailyLimit) * 100} 
              className="mt-2"
            />
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">成本節省</p>
                <p className="text-2xl font-bold text-green-600">¥{userStats.totalSaved}</p>
              </div>
              <Gift className="h-8 w-8 text-green-500" />
            </div>
            <p className="text-sm text-gray-500 mt-2">相比Claude直接使用</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">命令執行</p>
                <p className="text-2xl font-bold text-gray-900">{userStats.commandsUsed}</p>
              </div>
              <Zap className="h-8 w-8 text-yellow-500" />
            </div>
            <p className="text-sm text-gray-500 mt-2">本月總計</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">K2使用率</p>
                <p className="text-2xl font-bold text-purple-600">{userStats.k2Usage}%</p>
              </div>
              <Shield className="h-8 w-8 text-purple-500" />
            </div>
            <p className="text-sm text-gray-500 mt-2">智能路由效率</p>
          </CardContent>
        </Card>
      </div>

      {/* 會員等級 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Crown className="h-5 w-5 mr-2" />
            會員等級
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(membershipTiers).map(([tierKey, tier]) => (
              <Card 
                key={tierKey} 
                className={`${tier.color} ${userStats.tier === tierKey ? 'ring-2 ring-blue-500' : ''}`}
              >
                <CardContent className="p-6">
                  <div className="text-center">
                    <h3 className="text-xl font-bold mb-2">{tier.name}</h3>
                    <div className="text-3xl font-bold mb-4">{tier.price}</div>
                    <div className="space-y-2 text-sm mb-4">
                      <p>每日 {tier.dailyPoints.toLocaleString()} 積分</p>
                      <p>每月 {tier.monthlyPoints.toLocaleString()} 積分</p>
                    </div>
                    <ul className="space-y-1 text-sm mb-4">
                      {tier.features.map((feature, index) => (
                        <li key={index} className="flex items-center">
                          <Star className="h-3 w-3 mr-1" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                    {userStats.tier !== tierKey && (
                      <Button 
                        onClick={() => upgradeTier(tierKey)}
                        className="w-full bg-white/20 hover:bg-white/30"
                      >
                        {tierKey === 'free' ? '降級' : '升級'}
                      </Button>
                    )}
                    {userStats.tier === tierKey && (
                      <Badge className="bg-white/20">當前方案</Badge>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 使用說明 */}
      <Card>
        <CardHeader>
          <CardTitle>如何使用 PowerAutomation</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold mb-2">🚀 在 Claude Code Tool 中使用</h4>
              <ul className="space-y-1 text-sm text-gray-600">
                <li>• 所有命令自動路由到 K2 模型</li>
                <li>• 與 Claude 完全相同的使用體驗</li>
                <li>• 成本節省 60-80%</li>
                <li>• 支持所有 Claude Code 命令</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-2">🌐 在 ClaudeEditor 中使用</h4>
              <ul className="space-y-1 text-sm text-gray-600">
                <li>• 可視化的項目管理界面</li>
                <li>• 六大工作流一鍵啟動</li>
                <li>• 實時部署和監控</li>
                <li>• 更便捷的文件操作</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center p-4">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-purple-500/10 to-pink-500/10" />
        <div className="relative z-10 w-full max-w-md">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              PowerAutomation
            </h1>
            <p className="text-gray-600 mt-2">智能開發助手，讓AI為您節省成本</p>
          </div>
          <LoginForm />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 p-4">
      <div className="relative z-10">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            PowerAutomation Dashboard
          </h1>
          <Button 
            onClick={() => {
              setUser(null);
              localStorage.removeItem('powerautomation_user');
            }}
            variant="outline"
          >
            退出登錄
          </Button>
        </div>
        <DashboardView />
      </div>
    </div>
  );
};

export default MembershipSystem;