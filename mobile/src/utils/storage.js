import AsyncStorage from '@react-native-async-storage/async-storage';

export const saveTokens = async (access, refresh) => {
  await AsyncStorage.setItem('access_token', access);
  await AsyncStorage.setItem('refresh_token', refresh);
};

export const saveUser = async user => {
  await AsyncStorage.setItem('user', JSON.stringify(user));
};

export const getUser = async () => {
  const data = await AsyncStorage.getItem('user');
  return data ? JSON.parse(data) : null;
};

export const logout = async () => {
  await AsyncStorage.multiRemove(['access_token', 'refresh_token', 'user']);
};
