import React from 'react';
import {StatusBar} from 'react-native';
import AppNavigator from './src/navigation/AppNavigator';

const App = () => (
  <>
    <StatusBar barStyle="light-content" backgroundColor="#2563eb" />
    <AppNavigator />
  </>
);

export default App;
