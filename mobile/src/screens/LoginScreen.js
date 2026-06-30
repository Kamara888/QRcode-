import React, {useState} from 'react';
import {
  View, Text, TextInput, StyleSheet, KeyboardAvoidingView,
  Platform, Alert, TouchableOpacity,
} from 'react-native';
import {authAPI} from '../services/api';
import {saveTokens, saveUser} from '../utils/storage';
import LoadingButton from '../components/LoadingButton';

const LoginScreen = ({navigation}) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!username || !password) {
      Alert.alert('Error', 'Please fill all fields');
      return;
    }
    setLoading(true);
    try {
      const res = await authAPI.login(username, password);
      await saveTokens(res.data.access, res.data.refresh);
      const profile = await authAPI.profile();
      await saveUser(profile.data);
      navigation.reset({index: 0, routes: [{name: 'Dashboard'}]});
    } catch (e) {
      Alert.alert('Login Failed', 'Invalid username or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
      <View style={styles.header}>
        <Text style={styles.icon}>📷</Text>
        <Text style={styles.title}>QR Attendance</Text>
        <Text style={styles.subtitle}>Student Mobile App</Text>
      </View>
      <View style={styles.form}>
        <TextInput
          style={styles.input}
          placeholder="Username"
          value={username}
          onChangeText={setUsername}
          autoCapitalize="none"
        />
        <TextInput
          style={styles.input}
          placeholder="Password"
          value={password}
          onChangeText={setPassword}
          secureTextEntry
        />
        <LoadingButton title="Sign In" onPress={handleLogin} loading={loading} />
        <TouchableOpacity onPress={() => navigation.navigate('Register')}>
          <Text style={styles.link}>Don't have an account? Register</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#f0f4ff', justifyContent: 'center'},
  header: {alignItems: 'center', marginBottom: 40},
  icon: {fontSize: 60, marginBottom: 10},
  title: {fontSize: 28, fontWeight: 'bold', color: '#1e3a5f'},
  subtitle: {fontSize: 14, color: '#64748b', marginTop: 5},
  form: {paddingHorizontal: 30},
  input: {
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 10,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    fontSize: 16,
  },
  link: {textAlign: 'center', color: '#2563eb', marginTop: 15, fontSize: 14},
});

export default LoginScreen;
