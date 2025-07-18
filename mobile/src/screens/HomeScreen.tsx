import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  Alert,
  Dimensions,
} from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { LineChart } from 'react-native-chart-kit';

// Components
import StatsCard from '../components/StatsCard';
import QuickActions from '../components/QuickActions';
import RecentProjects from '../components/RecentProjects';
import WorkflowProgress from '../components/WorkflowProgress';
import AIAssistantCard from '../components/AIAssistantCard';

// Services
import { apiService } from '../services/apiService';
import { notificationService } from '../services/notificationService';

// Types
import { RootState } from '../store';
import { HomeTabScreenProps } from '../types/navigation';

const { width } = Dimensions.get('window');

const HomeScreen: React.FC<HomeTabScreenProps<'Home'>> = ({ navigation }) => {
  const [refreshing, setRefreshing] = useState(false);
  const [stats, setStats] = useState({
    totalProjects: 0,
    activeWorkflows: 0,
    completedTasks: 0,
    aiInteractions: 0,
    codeGenerated: 0,
    goalsAchieved: 0,
  });
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [{ data: [] }],
  });
  const [quickActions, setQuickActions] = useState([]);
  const [recentProjects, setRecentProjects] = useState([]);
  const [activeWorkflows, setActiveWorkflows] = useState([]);

  const user = useSelector((state: RootState) => state.auth.user);
  const dispatch = useDispatch();

  useEffect(() => {
    loadDashboardData();
    
    // 設置自動刷新
    const interval = setInterval(loadDashboardData, 30000); // 30秒刷新一次
    
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      const [
        statsResponse,
        chartResponse,
        projectsResponse,
        workflowsResponse,
      ] = await Promise.all([
        apiService.getDashboardStats(),
        apiService.getProductivityChart(),
        apiService.getRecentProjects(),
        apiService.getActiveWorkflows(),
      ]);

      setStats(statsResponse.data);
      setChartData(chartResponse.data);
      setRecentProjects(projectsResponse.data);
      setActiveWorkflows(workflowsResponse.data);
      
      // 設置快速操作
      setQuickActions([
        {
          id: 'new-project',
          title: '新建項目',
          icon: 'add-circle',
          color: '#4A90E2',
          onPress: () => navigation.navigate('Editor'),
        },
        {
          id: 'ai-chat',
          title: 'AI對話',
          icon: 'chat',
          color: '#50C878',
          onPress: () => navigation.navigate('Chat'),
        },
        {
          id: 'workflow',
          title: '工作流',
          icon: 'account-tree',
          color: '#FF6B6B',
          onPress: () => navigation.navigate('Workflows'),
        },
        {
          id: 'settings',
          title: '設置',
          icon: 'settings',
          color: '#FFA500',
          onPress: () => navigation.navigate('Settings'),
        },
      ]);

    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      Alert.alert('錯誤', '加載儀表板數據失敗');
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const switchToK2Mode = async () => {
    try {
      await apiService.switchAIMode('k2');
      notificationService.showSuccess('已切換到K2中文模式');
    } catch (error) {
      notificationService.showError('切換AI模式失敗');
    }
  };

  const switchToClaudeMode = async () => {
    try {
      await apiService.switchAIMode('claude');
      notificationService.showSuccess('已切換到Claude模式');
    } catch (error) {
      notificationService.showError('切換AI模式失敗');
    }
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* 用戶歡迎區域 */}
      <View style={styles.welcomeSection}>
        <Text style={styles.welcomeText}>
          歡迎回來，{user?.username || '用戶'}！
        </Text>
        <Text style={styles.membershipText}>
          {user?.membership_tier === 'enterprise' ? '企業版' : 
           user?.membership_tier === 'team' ? '團隊版' : 
           user?.membership_tier === 'pro' ? '專業版' : '免費版'}
        </Text>
        <Text style={styles.pointsText}>
          積分: {user?.points || 0}
        </Text>
      </View>

      {/* AI模式切換 */}
      <View style={styles.aiModeSection}>
        <Text style={styles.sectionTitle}>AI 模式</Text>
        <View style={styles.aiModeButtons}>
          <TouchableOpacity
            style={[styles.aiModeButton, styles.claudeButton]}
            onPress={switchToClaudeMode}
          >
            <Icon name="psychology" size={20} color="#fff" />
            <Text style={styles.aiModeButtonText}>Claude</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.aiModeButton, styles.k2Button]}
            onPress={switchToK2Mode}
          >
            <Icon name="translate" size={20} color="#fff" />
            <Text style={styles.aiModeButtonText}>K2 中文</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* 統計卡片 */}
      <View style={styles.statsSection}>
        <Text style={styles.sectionTitle}>統計概覽</Text>
        <View style={styles.statsGrid}>
          <StatsCard
            title="總項目"
            value={stats.totalProjects}
            icon="folder"
            color="#4A90E2"
          />
          <StatsCard
            title="活動工作流"
            value={stats.activeWorkflows}
            icon="account-tree"
            color="#50C878"
          />
          <StatsCard
            title="完成任務"
            value={stats.completedTasks}
            icon="check-circle"
            color="#FF6B6B"
          />
          <StatsCard
            title="AI互動"
            value={stats.aiInteractions}
            icon="chat"
            color="#FFA500"
          />
        </View>
      </View>

      {/* 生產力圖表 */}
      <View style={styles.chartSection}>
        <Text style={styles.sectionTitle}>生產力趨勢</Text>
        <LineChart
          data={chartData}
          width={width - 40}
          height={220}
          chartConfig={{
            backgroundColor: '#ffffff',
            backgroundGradientFrom: '#ffffff',
            backgroundGradientTo: '#ffffff',
            decimalPlaces: 0,
            color: (opacity = 1) => `rgba(74, 144, 226, ${opacity})`,
            labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
            style: {
              borderRadius: 16,
            },
            propsForDots: {
              r: '6',
              strokeWidth: '2',
              stroke: '#4A90E2',
            },
          }}
          bezier
          style={styles.chart}
        />
      </View>

      {/* 快速操作 */}
      <View style={styles.quickActionsSection}>
        <Text style={styles.sectionTitle}>快速操作</Text>
        <QuickActions actions={quickActions} />
      </View>

      {/* AI助手卡片 */}
      <AIAssistantCard
        onChatPress={() => navigation.navigate('Chat')}
        onK2Press={switchToK2Mode}
        onClaudePress={switchToClaudeMode}
      />

      {/* 最近項目 */}
      <View style={styles.recentProjectsSection}>
        <Text style={styles.sectionTitle}>最近項目</Text>
        <RecentProjects
          projects={recentProjects}
          onProjectPress={(project) => {
            navigation.navigate('Editor', { projectId: project.id });
          }}
        />
      </View>

      {/* 工作流進度 */}
      <View style={styles.workflowSection}>
        <Text style={styles.sectionTitle}>工作流進度</Text>
        <WorkflowProgress
          workflows={activeWorkflows}
          onWorkflowPress={(workflow) => {
            navigation.navigate('Workflows', { workflowId: workflow.id });
          }}
        />
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  welcomeSection: {
    backgroundColor: '#4A90E2',
    padding: 20,
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
    marginBottom: 20,
  },
  welcomeText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 5,
  },
  membershipText: {
    fontSize: 16,
    color: '#fff',
    opacity: 0.9,
  },
  pointsText: {
    fontSize: 14,
    color: '#fff',
    opacity: 0.8,
    marginTop: 5,
  },
  aiModeSection: {
    backgroundColor: '#fff',
    margin: 20,
    padding: 20,
    borderRadius: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  aiModeButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 15,
  },
  aiModeButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 15,
    borderRadius: 10,
    marginHorizontal: 5,
  },
  claudeButton: {
    backgroundColor: '#4A90E2',
  },
  k2Button: {
    backgroundColor: '#50C878',
  },
  aiModeButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    marginLeft: 8,
  },
  statsSection: {
    margin: 20,
    marginTop: 0,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  chartSection: {
    backgroundColor: '#fff',
    margin: 20,
    padding: 20,
    borderRadius: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  quickActionsSection: {
    margin: 20,
    marginTop: 0,
  },
  recentProjectsSection: {
    margin: 20,
    marginTop: 0,
  },
  workflowSection: {
    margin: 20,
    marginTop: 0,
    marginBottom: 40,
  },
});

export default HomeScreen;