import React, { useEffect, useState } from 'react';
import {
  StyleSheet,
  View,
  StatusBar,
  Platform,
  Alert,
  BackHandler,
} from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import NetInfo from '@react-native-community/netinfo';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialIcons';

// Redux Store
import { store, persistor } from './store';

// Screens
import SplashScreen from './screens/SplashScreen';
import LoginScreen from './screens/LoginScreen';
import RegisterScreen from './screens/RegisterScreen';
import HomeScreen from './screens/HomeScreen';
import EditorScreen from './screens/EditorScreen';
import ChatScreen from './screens/ChatScreen';
import WorkflowScreen from './screens/WorkflowScreen';
import ProfileScreen from './screens/ProfileScreen';
import SettingsScreen from './screens/SettingsScreen';

// Components
import LoadingSpinner from './components/LoadingSpinner';
import NetworkStatus from './components/NetworkStatus';

// Services
import { authService } from './services/authService';
import { socketService } from './services/socketService';

// Types
import { RootStackParamList, TabParamList } from './types/navigation';

const Stack = createNativeStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator<TabParamList>();

const TabNavigator = () => {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: string;

          switch (route.name) {
            case 'Home':
              iconName = 'home';
              break;
            case 'Editor':
              iconName = 'code';
              break;
            case 'Chat':
              iconName = 'chat';
              break;
            case 'Workflows':
              iconName = 'account-tree';
              break;
            case 'Profile':
              iconName = 'person';
              break;
            default:
              iconName = 'help';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#4A90E2',
        tabBarInactiveTintColor: '#8E8E93',
        tabBarStyle: {
          backgroundColor: '#FFFFFF',
          borderTopWidth: 1,
          borderTopColor: '#E1E1E1',
          paddingBottom: Platform.OS === 'ios' ? 20 : 5,
          height: Platform.OS === 'ios' ? 80 : 60,
        },
        headerStyle: {
          backgroundColor: '#4A90E2',
        },
        headerTintColor: '#FFFFFF',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      })}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen} 
        options={{ title: '首頁' }}
      />
      <Tab.Screen 
        name="Editor" 
        component={EditorScreen} 
        options={{ title: '編輯器' }}
      />
      <Tab.Screen 
        name="Chat" 
        component={ChatScreen} 
        options={{ title: 'AI助手' }}
      />
      <Tab.Screen 
        name="Workflows" 
        component={WorkflowScreen} 
        options={{ title: '工作流' }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen} 
        options={{ title: '個人資料' }}
      />
    </Tab.Navigator>
  );
};

const App: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isConnected, setIsConnected] = useState(true);

  useEffect(() => {
    initializeApp();
    
    // 網路狀態監聽
    const unsubscribe = NetInfo.addEventListener(state => {
      setIsConnected(state.isConnected ?? false);
    });

    // 返回鍵處理
    const backHandler = BackHandler.addEventListener('hardwareBackPress', () => {
      Alert.alert(
        '退出應用',
        '確定要退出PowerAutomation嗎？',
        [
          { text: '取消', style: 'cancel' },
          { text: '確定', onPress: () => BackHandler.exitApp() }
        ]
      );
      return true;
    });

    return () => {
      unsubscribe();
      backHandler.remove();
    };
  }, []);

  const initializeApp = async () => {
    try {
      // 檢查用戶認證狀態
      const token = await authService.getToken();
      if (token) {
        const isValid = await authService.validateToken(token);
        if (isValid) {
          setIsAuthenticated(true);
          // 初始化 Socket 連接
          await socketService.connect();
        }
      }
    } catch (error) {
      console.error('App initialization failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogin = async () => {
    setIsAuthenticated(true);
    await socketService.connect();
  };

  const handleLogout = async () => {
    setIsAuthenticated(false);
    await socketService.disconnect();
    await authService.logout();
  };

  if (isLoading) {
    return (
      <SafeAreaProvider>
        <SplashScreen />
      </SafeAreaProvider>
    );
  }

  return (
    <Provider store={store}>
      <PersistGate loading={<LoadingSpinner />} persistor={persistor}>
        <SafeAreaProvider>
          <StatusBar
            barStyle="light-content"
            backgroundColor="#4A90E2"
            translucent={false}
          />
          <NavigationContainer>
            {!isConnected && <NetworkStatus />}
            <Stack.Navigator
              screenOptions={{
                headerShown: false,
                animation: 'slide_from_right',
              }}
            >
              {isAuthenticated ? (
                <>
                  <Stack.Screen name="Main" component={TabNavigator} />
                  <Stack.Screen 
                    name="Settings" 
                    component={SettingsScreen}
                    options={{
                      headerShown: true,
                      title: '設置',
                      headerStyle: { backgroundColor: '#4A90E2' },
                      headerTintColor: '#FFFFFF',
                    }}
                  />
                </>
              ) : (
                <>
                  <Stack.Screen name="Login">
                    {(props) => (
                      <LoginScreen {...props} onLogin={handleLogin} />
                    )}
                  </Stack.Screen>
                  <Stack.Screen name="Register" component={RegisterScreen} />
                </>
              )}
            </Stack.Navigator>
          </NavigationContainer>
        </SafeAreaProvider>
      </PersistGate>
    </Provider>
  );
};

export default App;