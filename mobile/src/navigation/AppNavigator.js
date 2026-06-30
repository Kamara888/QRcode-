import React from 'react';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import {createNativeStackNavigator} from '@react-navigation/native-stack';
import {NavigationContainer} from '@react-navigation/native';
import Icon from 'react-native-vector-icons/Ionicons';

import LoginScreen from '../screens/LoginScreen';
import RegisterScreen from '../screens/RegisterScreen';
import DashboardScreen from '../screens/DashboardScreen';
import ScannerScreen from '../screens/ScannerScreen';
import HistoryScreen from '../screens/HistoryScreen';
import ProfileScreen from '../screens/ProfileScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

const AuthStack = () => (
  <Stack.Navigator screenOptions={{headerShown: false}}>
    <Stack.Screen name="Login" component={LoginScreen} />
    <Stack.Screen name="Register" component={RegisterScreen} />
  </Stack.Navigator>
);

const MainTabs = () => (
  <Tab.Navigator
    screenOptions={({route}) => ({
      tabBarIcon: ({focused, color, size}) => {
        const icons = {
          Dashboard: focused ? 'grid' : 'grid-outline',
          Scanner: focused ? 'camera' : 'camera-outline',
          History: focused ? 'time' : 'time-outline',
          Profile: focused ? 'person' : 'person-outline',
        };
        return <Icon name={icons[route.name]} size={size} color={color} />;
      },
      tabBarActiveTintColor: '#2563eb',
      tabBarInactiveTintColor: '#94a3b8',
      headerStyle: {backgroundColor: '#2563eb'},
      headerTintColor: '#fff',
    })}>
    <Tab.Screen name="Dashboard" component={DashboardScreen} options={{title: 'My Courses'}} />
    <Tab.Screen name="Scanner" component={ScannerScreen} options={{title: 'Scan QR'}} />
    <Tab.Screen name="History" component={HistoryScreen} options={{title: 'History'}} />
    <Tab.Screen name="Profile" component={ProfileScreen} options={{title: 'Profile'}} />
  </Tab.Navigator>
);

const AppNavigator = () => (
  <NavigationContainer>
    <Stack.Navigator screenOptions={{headerShown: false}}>
      <Stack.Screen name="Auth" component={AuthStack} />
      <Stack.Screen name="Dashboard" component={MainTabs} />
    </Stack.Navigator>
  </NavigationContainer>
);

export default AppNavigator;
