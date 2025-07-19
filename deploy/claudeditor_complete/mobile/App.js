import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  StatusBar,
  TouchableOpacity,
  ScrollView,
  TextInput,
  Modal,
  Alert,
  Dimensions,
  Platform
} from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';

const { width, height } = Dimensions.get('window');
const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

// 顏色主題
const colors = {
  primary: '#667eea',
  secondary: '#764ba2',
  background: '#1a1a1a',
  surface: '#262626',
  text: '#ffffff',
  textSecondary: '#cccccc',
  accent: '#10b981',
  warning: '#f59e0b',
  error: '#ef4444',
  border: '#404040'
};

// 工作流數據
const workflows = [
  {
    id: 'goal-driven',
    title: '🎯 目標驅動開發',
    description: '確保開發始終對齊用戶目標',
    status: 'running',
    progress: 75
  },
  {
    id: 'code-generation',
    title: '🤖 智能代碼生成',
    description: 'AI驅動的代碼生成',
    status: 'pending',
    progress: 0
  },
  {
    id: 'testing',
    title: '🧪 自動化測試',
    description: '自動化測試驗證',
    status: 'pending',
    progress: 0
  },
  {
    id: 'quality',
    title: '📊 質量保證',
    description: '持續質量監控',
    status: 'pending',
    progress: 0
  },
  {
    id: 'deployment',
    title: '🚀 智能部署',
    description: '自動化部署運維',
    status: 'pending',
    progress: 0
  },
  {
    id: 'learning',
    title: '🧠 自適應學習',
    description: '持續學習優化',
    status: 'pending',
    progress: 0
  }
];

// 主屏幕組件
const HomeScreen = () => {
  const [currentMode, setCurrentMode] = useState('claude');
  const [alignmentScore, setAlignmentScore] = useState(92);
  const [costStats, setCostStats] = useState({
    input: 12.5,
    output: 48.3,
    efficiency: 3.9
  });

  const switchMode = (mode) => {
    setCurrentMode(mode);
    // 模擬成本統計更新
    if (mode === 'k2') {
      setCostStats({
        input: costStats.input,
        output: costStats.input * 4,
        efficiency: 4.0
      });
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={colors.background} />
      
      <ScrollView style={styles.scrollView}>
        {/* 頭部信息 */}
        <View style={styles.header}>
          <View style={styles.logoContainer}>
            <View style={styles.logo}>
              <Text style={styles.logoText}>CE</Text>
            </View>
            <Text style={styles.appName}>ClaudeEditor</Text>
          </View>
          
          <View style={styles.statusContainer}>
            <View style={styles.statusItem}>
              <Text style={styles.statusLabel}>對齊度</Text>
              <Text style={[styles.statusValue, { color: colors.accent }]}>
                {alignmentScore}%
              </Text>
            </View>
            <View style={styles.statusItem}>
              <Text style={styles.statusLabel}>模式</Text>
              <Text style={styles.statusValue}>
                {currentMode === 'claude' ? 'Claude' : 'K2中文'}
              </Text>
            </View>
          </View>
        </View>

        {/* AI模式切換 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>AI助手模式</Text>
          <View style={styles.modeSwitcher}>
            <TouchableOpacity
              style={[
                styles.modeButton,
                currentMode === 'claude' && styles.modeButtonActive
              ]}
              onPress={() => switchMode('claude')}
            >
              <Text style={[
                styles.modeButtonText,
                currentMode === 'claude' && styles.modeButtonTextActive
              ]}>
                Claude
              </Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={[
                styles.modeButton,
                currentMode === 'k2' && styles.modeButtonActive
              ]}
              onPress={() => switchMode('k2')}
            >
              <Text style={[
                styles.modeButtonText,
                currentMode === 'k2' && styles.modeButtonTextActive
              ]}>
                K2中文
              </Text>
              <View style={styles.badge}>
                <Text style={styles.badgeText}>2→8元</Text>
              </View>
            </TouchableOpacity>
          </View>
        </View>

        {/* 成本統計 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>成本統計</Text>
          <View style={styles.statsContainer}>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>輸入成本</Text>
              <Text style={styles.statValue}>¥{costStats.input.toFixed(1)}</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>輸出價值</Text>
              <Text style={[styles.statValue, { color: colors.accent }]}>
                ¥{costStats.output.toFixed(1)}
              </Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>效益比</Text>
              <Text style={[styles.statValue, { color: colors.warning }]}>
                1:{costStats.efficiency.toFixed(1)}
              </Text>
            </View>
          </View>
        </View>

        {/* 快速操作 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>快速操作</Text>
          <View style={styles.quickActions}>
            <TouchableOpacity style={styles.actionButton}>
              <Text style={styles.actionButtonText}>🎯 新建項目</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.actionButton}>
              <Text style={styles.actionButtonText}>📂 打開項目</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.actionButton}>
              <Text style={styles.actionButtonText}>🔄 同步工作流</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.actionButton}>
              <Text style={styles.actionButtonText}>📊 查看報告</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

// 工作流屏幕組件
const WorkflowScreen = () => {
  const [activeWorkflow, setActiveWorkflow] = useState('goal-driven');
  const [workflowData, setWorkflowData] = useState(workflows);

  const executeWorkflow = (workflowId) => {
    setWorkflowData(prev => 
      prev.map(workflow => 
        workflow.id === workflowId 
          ? { ...workflow, status: 'running', progress: 25 }
          : workflow
      )
    );
    
    // 模擬執行進度
    setTimeout(() => {
      setWorkflowData(prev => 
        prev.map(workflow => 
          workflow.id === workflowId 
            ? { ...workflow, progress: 75 }
            : workflow
        )
      );
    }, 2000);
    
    setTimeout(() => {
      setWorkflowData(prev => 
        prev.map(workflow => 
          workflow.id === workflowId 
            ? { ...workflow, status: 'completed', progress: 100 }
            : workflow
        )
      );
    }, 4000);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return colors.warning;
      case 'completed': return colors.accent;
      case 'pending': return colors.textSecondary;
      default: return colors.textSecondary;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'running': return '運行中';
      case 'completed': return '已完成';
      case 'pending': return '待執行';
      default: return '未知';
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>六大工作流</Text>
          <Text style={styles.headerSubtitle}>智能開發流程管理</Text>
        </View>

        {workflowData.map((workflow) => (
          <TouchableOpacity
            key={workflow.id}
            style={[
              styles.workflowCard,
              activeWorkflow === workflow.id && styles.workflowCardActive
            ]}
            onPress={() => setActiveWorkflow(workflow.id)}
          >
            <View style={styles.workflowHeader}>
              <Text style={styles.workflowTitle}>{workflow.title}</Text>
              <View style={[
                styles.workflowStatus,
                { backgroundColor: getStatusColor(workflow.status) }
              ]}>
                <Text style={styles.workflowStatusText}>
                  {getStatusText(workflow.status)}
                </Text>
              </View>
            </View>
            
            <Text style={styles.workflowDescription}>
              {workflow.description}
            </Text>
            
            <View style={styles.workflowProgress}>
              <View style={styles.progressBar}>
                <View style={[
                  styles.progressFill,
                  { width: `${workflow.progress}%` }
                ]} />
              </View>
              <Text style={styles.progressText}>{workflow.progress}%</Text>
            </View>
            
            <TouchableOpacity
              style={[
                styles.executeButton,
                workflow.status === 'running' && styles.executeButtonDisabled
              ]}
              onPress={() => executeWorkflow(workflow.id)}
              disabled={workflow.status === 'running'}
            >
              <Text style={styles.executeButtonText}>
                {workflow.status === 'running' ? '執行中...' : '執行工作流'}
              </Text>
            </TouchableOpacity>
          </TouchableOpacity>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
};

// 聊天屏幕組件
const ChatScreen = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: '👋 你好！我是ClaudeEditor的AI助手。我可以幫助你進行代碼開發、審查和優化。',
      isUser: false,
      timestamp: new Date()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [currentMode, setCurrentMode] = useState('claude');

  const sendMessage = async () => {
    if (!inputText.trim()) return;

    // 添加用戶消息
    const userMessage = {
      id: Date.now(),
      text: inputText,
      isUser: true,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsTyping(true);

    // 模擬AI回復
    setTimeout(() => {
      const aiResponse = {
        id: Date.now() + 1,
        text: generateAIResponse(inputText, currentMode),
        isUser: false,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, aiResponse]);
      setIsTyping(false);
    }, 1500);
  };

  const generateAIResponse = (message, mode) => {
    const responses = {
      claude: [
        '🤖 I understand your request. Let me help you with that.',
        '💡 Here\'s a solution to your problem...',
        '🔍 Let me analyze this for you...',
        '✨ I can help you optimize this code.'
      ],
      k2: [
        '🤖 我理解你的需求。讓我來幫助你解決這個問題。',
        '💡 這裡有一個解決方案...',
        '🔍 讓我為你分析一下...',
        '✨ 我可以幫你優化這段代碼。'
      ]
    };
    
    const modeResponses = responses[mode];
    return modeResponses[Math.floor(Math.random() * modeResponses.length)];
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.chatHeader}>
        <Text style={styles.chatTitle}>AI助手</Text>
        <View style={styles.chatMode}>
          <TouchableOpacity
            style={[
              styles.chatModeButton,
              currentMode === 'claude' && styles.chatModeButtonActive
            ]}
            onPress={() => setCurrentMode('claude')}
          >
            <Text style={styles.chatModeText}>Claude</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[
              styles.chatModeButton,
              currentMode === 'k2' && styles.chatModeButtonActive
            ]}
            onPress={() => setCurrentMode('k2')}
          >
            <Text style={styles.chatModeText}>K2</Text>
          </TouchableOpacity>
        </View>
      </View>

      <ScrollView style={styles.chatMessages}>
        {messages.map((message) => (
          <View
            key={message.id}
            style={[
              styles.messageContainer,
              message.isUser ? styles.userMessage : styles.aiMessage
            ]}
          >
            <Text style={styles.messageText}>{message.text}</Text>
            <Text style={styles.messageTime}>
              {message.timestamp.toLocaleTimeString()}
            </Text>
          </View>
        ))}
        
        {isTyping && (
          <View style={styles.typingIndicator}>
            <Text style={styles.typingText}>AI正在輸入...</Text>
          </View>
        )}
      </ScrollView>

      <View style={styles.chatInput}>
        <TextInput
          style={styles.chatInputField}
          value={inputText}
          onChangeText={setInputText}
          placeholder="輸入你的問題..."
          placeholderTextColor={colors.textSecondary}
          multiline
          onSubmitEditing={sendMessage}
        />
        <TouchableOpacity
          style={styles.sendButton}
          onPress={sendMessage}
          disabled={!inputText.trim()}
        >
          <Text style={styles.sendButtonText}>發送</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

// 設置屏幕組件
const SettingsScreen = () => {
  const [settings, setSettings] = useState({
    autoSave: true,
    notifications: true,
    theme: 'dark',
    language: 'zh-CN'
  });

  const toggleSetting = (key) => {
    setSettings(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>設置</Text>
          <Text style={styles.headerSubtitle}>個性化配置</Text>
        </View>

        <View style={styles.settingsSection}>
          <Text style={styles.settingsSectionTitle}>一般設置</Text>
          
          <View style={styles.settingItem}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingTitle}>自動保存</Text>
              <Text style={styles.settingDescription}>自動保存編輯的文件</Text>
            </View>
            <TouchableOpacity
              style={[
                styles.settingSwitch,
                settings.autoSave && styles.settingSwitchActive
              ]}
              onPress={() => toggleSetting('autoSave')}
            >
              <View style={[
                styles.settingSwitchThumb,
                settings.autoSave && styles.settingSwitchThumbActive
              ]} />
            </TouchableOpacity>
          </View>

          <View style={styles.settingItem}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingTitle}>推送通知</Text>
              <Text style={styles.settingDescription}>接收系統通知</Text>
            </View>
            <TouchableOpacity
              style={[
                styles.settingSwitch,
                settings.notifications && styles.settingSwitchActive
              ]}
              onPress={() => toggleSetting('notifications')}
            >
              <View style={[
                styles.settingSwitchThumb,
                settings.notifications && styles.settingSwitchThumbActive
              ]} />
            </TouchableOpacity>
          </View>
        </View>

        <View style={styles.settingsSection}>
          <Text style={styles.settingsSectionTitle}>關於</Text>
          
          <View style={styles.settingItem}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingTitle}>版本</Text>
              <Text style={styles.settingDescription}>v1.0.0</Text>
            </View>
          </View>

          <TouchableOpacity style={styles.settingItem}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingTitle}>幫助和反饋</Text>
              <Text style={styles.settingDescription}>獲取幫助或提供反饋</Text>
            </View>
            <Text style={styles.settingArrow}>›</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

// 主導航組件
const MainNavigator = () => {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;
          switch (route.name) {
            case 'Home':
              iconName = '🏠';
              break;
            case 'Workflow':
              iconName = '🔄';
              break;
            case 'Chat':
              iconName = '💬';
              break;
            case 'Settings':
              iconName = '⚙️';
              break;
          }
          return <Text style={{ fontSize: 20 }}>{iconName}</Text>;
        },
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textSecondary,
        tabBarStyle: {
          backgroundColor: colors.surface,
          borderTopColor: colors.border,
          height: Platform.OS === 'ios' ? 88 : 68,
          paddingTop: 8,
          paddingBottom: Platform.OS === 'ios' ? 32 : 8
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '500'
        },
        headerShown: false
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} options={{ title: '首頁' }} />
      <Tab.Screen name="Workflow" component={WorkflowScreen} options={{ title: '工作流' }} />
      <Tab.Screen name="Chat" component={ChatScreen} options={{ title: '聊天' }} />
      <Tab.Screen name="Settings" component={SettingsScreen} options={{ title: '設置' }} />
    </Tab.Navigator>
  );
};

// 主應用組件
const App = () => {
  return (
    <NavigationContainer>
      <MainNavigator />
    </NavigationContainer>
  );
};

// 樣式定義
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background
  },
  scrollView: {
    flex: 1,
    padding: 16
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: colors.border
  },
  logoContainer: {
    flexDirection: 'row',
    alignItems: 'center'
  },
  logo: {
    width: 40,
    height: 40,
    borderRadius: 8,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12
  },
  logoText: {
    color: colors.text,
    fontSize: 16,
    fontWeight: 'bold'
  },
  appName: {
    color: colors.text,
    fontSize: 20,
    fontWeight: '600'
  },
  statusContainer: {
    flexDirection: 'row',
    gap: 16
  },
  statusItem: {
    alignItems: 'center'
  },
  statusLabel: {
    color: colors.textSecondary,
    fontSize: 12,
    marginBottom: 4
  },
  statusValue: {
    color: colors.text,
    fontSize: 14,
    fontWeight: '600'
  },
  section: {
    marginBottom: 24
  },
  sectionTitle: {
    color: colors.text,
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 12
  },
  modeSwitcher: {
    flexDirection: 'row',
    backgroundColor: colors.surface,
    borderRadius: 8,
    padding: 4
  },
  modeButton: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 6,
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'center'
  },
  modeButtonActive: {
    backgroundColor: colors.primary
  },
  modeButtonText: {
    color: colors.textSecondary,
    fontSize: 14,
    fontWeight: '500'
  },
  modeButtonTextActive: {
    color: colors.text
  },
  badge: {
    backgroundColor: colors.warning,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
    marginLeft: 8
  },
  badgeText: {
    color: colors.text,
    fontSize: 10,
    fontWeight: '600'
  },
  statsContainer: {
    flexDirection: 'row',
    backgroundColor: colors.surface,
    borderRadius: 8,
    padding: 16
  },
  statItem: {
    flex: 1,
    alignItems: 'center'
  },
  statLabel: {
    color: colors.textSecondary,
    fontSize: 12,
    marginBottom: 4
  },
  statValue: {
    color: colors.text,
    fontSize: 16,
    fontWeight: '600'
  },
  quickActions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8
  },
  actionButton: {
    backgroundColor: colors.surface,
    padding: 16,
    borderRadius: 8,
    width: (width - 40) / 2,
    alignItems: 'center'
  },
  actionButtonText: {
    color: colors.text,
    fontSize: 14,
    fontWeight: '500'
  },
  headerTitle: {
    color: colors.text,
    fontSize: 24,
    fontWeight: '700'
  },
  headerSubtitle: {
    color: colors.textSecondary,
    fontSize: 14,
    marginTop: 4
  },
  workflowCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: colors.border
  },
  workflowCardActive: {
    borderColor: colors.primary
  },
  workflowHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8
  },
  workflowTitle: {
    color: colors.text,
    fontSize: 16,
    fontWeight: '600',
    flex: 1
  },
  workflowStatus: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12
  },
  workflowStatusText: {
    color: colors.text,
    fontSize: 10,
    fontWeight: '500'
  },
  workflowDescription: {
    color: colors.textSecondary,
    fontSize: 14,
    marginBottom: 12
  },
  workflowProgress: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12
  },
  progressBar: {
    flex: 1,
    height: 6,
    backgroundColor: colors.border,
    borderRadius: 3,
    marginRight: 8
  },
  progressFill: {
    height: '100%',
    backgroundColor: colors.accent,
    borderRadius: 3
  },
  progressText: {
    color: colors.textSecondary,
    fontSize: 12,
    minWidth: 40
  },
  executeButton: {
    backgroundColor: colors.primary,
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 6,
    alignItems: 'center'
  },
  executeButtonDisabled: {
    backgroundColor: colors.border
  },
  executeButtonText: {
    color: colors.text,
    fontSize: 14,
    fontWeight: '500'
  },
  chatHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: colors.border
  },
  chatTitle: {
    color: colors.text,
    fontSize: 18,
    fontWeight: '600'
  },
  chatMode: {
    flexDirection: 'row',
    backgroundColor: colors.surface,
    borderRadius: 6,
    padding: 2
  },
  chatModeButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 4
  },
  chatModeButtonActive: {
    backgroundColor: colors.primary
  },
  chatModeText: {
    color: colors.textSecondary,
    fontSize: 12
  },
  chatMessages: {
    flex: 1,
    padding: 16
  },
  messageContainer: {
    marginBottom: 16,
    maxWidth: '80%'
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: colors.primary,
    borderRadius: 16,
    borderBottomRightRadius: 4,
    padding: 12
  },
  aiMessage: {
    alignSelf: 'flex-start',
    backgroundColor: colors.surface,
    borderRadius: 16,
    borderBottomLeftRadius: 4,
    padding: 12
  },
  messageText: {
    color: colors.text,
    fontSize: 14,
    lineHeight: 20
  },
  messageTime: {
    color: colors.textSecondary,
    fontSize: 10,
    marginTop: 4
  },
  typingIndicator: {
    alignSelf: 'flex-start',
    backgroundColor: colors.surface,
    borderRadius: 16,
    padding: 12,
    marginBottom: 16
  },
  typingText: {
    color: colors.textSecondary,
    fontSize: 12,
    fontStyle: 'italic'
  },
  chatInput: {
    flexDirection: 'row',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    alignItems: 'flex-end'
  },
  chatInputField: {
    flex: 1,
    backgroundColor: colors.surface,
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginRight: 8,
    color: colors.text,
    maxHeight: 100
  },
  sendButton: {
    backgroundColor: colors.primary,
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 12
  },
  sendButtonText: {
    color: colors.text,
    fontSize: 14,
    fontWeight: '500'
  },
  settingsSection: {
    marginBottom: 24
  },
  settingsSectionTitle: {
    color: colors.text,
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 12
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: colors.surface,
    padding: 16,
    borderRadius: 8,
    marginBottom: 8
  },
  settingInfo: {
    flex: 1
  },
  settingTitle: {
    color: colors.text,
    fontSize: 14,
    fontWeight: '500'
  },
  settingDescription: {
    color: colors.textSecondary,
    fontSize: 12,
    marginTop: 2
  },
  settingSwitch: {
    width: 44,
    height: 24,
    backgroundColor: colors.border,
    borderRadius: 12,
    padding: 2
  },
  settingSwitchActive: {
    backgroundColor: colors.primary
  },
  settingSwitchThumb: {
    width: 20,
    height: 20,
    backgroundColor: colors.text,
    borderRadius: 10
  },
  settingSwitchThumbActive: {
    transform: [{ translateX: 20 }]
  },
  settingArrow: {
    color: colors.textSecondary,
    fontSize: 18
  }
});

export default App;